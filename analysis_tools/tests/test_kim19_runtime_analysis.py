import json
import copy
import struct
from pathlib import Path
import unittest

from analysis_tools.java_classfile import parse_class
from analysis_tools.kim19_runtime_analysis import (
    NOTES, dependency_graph, encode, javap_blocks, known_predicates_match, method_record,
    native_window, network_categories, parse_show_conditions, validate_labels,
)
from analysis_tools.arm_elf_analysis import ArmElfAnalyzer, Elf32Image
from analysis_tools.tests.test_arm_elf_analysis import _elf32
from analysis_tools.tests.test_java_classfile import class_fixture


class Kim19RuntimeTests(unittest.TestCase):
    def graph_fixture(self):
        call = dict(bci=7, owner='service/S', name='send', descriptor='(I)V')
        identity = dict(jar='a.jar', **{'class': 'app/A'}, method='run', descriptor='()V')
        record = dict(**identity, calls=[call], jar_sha256='jarhash', class_sha256='classhash')
        spec = dict(nodes=[dict(id='a'), dict(id='s')], shared_state_limits=[], edges=[
            dict(id='send', source='a', target='s', label='PROVED', condition='service running',
                 sites=[dict(**identity, call=call)])])
        return spec, [record]

    def test_graph_binds_source_hashes_without_inventing_runtime_reachability(self):
        spec, records = self.graph_fixture()
        result = dependency_graph(spec, records)
        self.assertEqual(result['edges'][0]['sites'][0]['class_sha256'], 'classhash')
        self.assertEqual(result['edges'][0]['condition'], 'service running')
        self.assertNotIn('class_sha256', spec['edges'][0]['sites'][0])
        self.assertEqual(encode(result), encode(dependency_graph(spec, records)))

    def test_graph_rejects_wrong_jar_overload_bci_or_callee(self):
        spec, records = self.graph_fixture()
        mutations = [('jar', 'b.jar'), ('descriptor', '(I)V'), ('bci', 8),
                     ('owner', 'service/T'), ('name', 'receive')]
        for key, value in mutations:
            changed = copy.deepcopy(spec)
            site = changed['edges'][0]['sites'][0]
            (site if key in ('jar', 'descriptor') else site['call'])[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'does not match'):
                dependency_graph(changed, records)

    def test_graph_rejects_unknown_nodes_duplicate_ids_and_empty_evidence(self):
        for mutation in ('node', 'duplicate_node', 'duplicate_edge', 'empty'):
            spec, records = self.graph_fixture()
            if mutation == 'node': spec['edges'][0]['target'] = 'missing'
            elif mutation == 'duplicate_node': spec['nodes'].append(spec['nodes'][0])
            elif mutation == 'duplicate_edge': spec['edges'].append(spec['edges'][0])
            else: spec['edges'][0]['sites'] = []
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                dependency_graph(spec, records)

    def test_native_windows_bind_addresses_file_offsets_and_complete_decode(self):
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(struct.pack('<II', 0xE3A00001, 0xE12FFF1E))))
        row = native_window(analyzer, 0x1000, 0x1008)
        self.assertEqual(row['file_offset'], '0x100')
        self.assertEqual(row['instructions'], [['0x1000', 'mov', 'r0, #1'], ['0x1004', 'bx', 'lr']])
        self.assertEqual(row, native_window(analyzer, 0x1000, 0x1008))
        for start, end in [(0x1001, 0x1008), (0x1000, 0x1007), (0x1004, 0x1004), (0x1000, 0x100c)]:
            with self.assertRaises(ValueError):
                native_window(analyzer, start, end)

    def test_native_undecoded_bytes_are_not_reported_as_complete(self):
        analyzer = ArmElfAnalyzer(Elf32Image.from_bytes(_elf32(b'\xff' * 4)))
        with self.assertRaisesRegex(ValueError, 'undecoded'):
            native_window(analyzer, 0x1000, 0x1004)

    def test_canonical_notes_digest_input_is_line_ending_independent(self):
        lf = '{\n  "label": "UNKNOWN"\n}\n'
        self.assertEqual(encode(json.loads(lf)), encode(json.loads(lf.replace('\n', '\r\n'))))

    def test_vehicle_predicates_and_string_comparison(self):
        p = parse_show_conditions('/pps/can/vehcfg/VC_PP_Prsnt:1,/pps/can/vehcfg/VC_VEH_LINE:{44;41;2}')
        self.assertEqual(p[1]['accepted_strings'], ['44', '41', '2'])
        for line in ('44', '41', '2'):
            self.assertTrue(known_predicates_match(p, {p[0]['attribute']: '1', p[1]['attribute']: line}))
        self.assertFalse(known_predicates_match(p, {p[0]['attribute']: '1', p[1]['attribute']: '1'}))
        self.assertFalse(known_predicates_match(p, {p[0]['attribute']: '01', p[1]['attribute']: '44'}))

    def test_missing_pps_is_not_silently_false_or_true(self):
        p = parse_show_conditions('/pps/can/a:1,/pps/can/b:2')
        self.assertIsNone(known_predicates_match(p, {'/pps/can/b': '2'}))
        self.assertIsNone(known_predicates_match(p, {'/pps/can/b': '9'}))
        self.assertEqual(parse_show_conditions(''), [])

    def test_rejects_malformed_duplicate_and_executable_predicates(self):
        for text in ('a:1', '/pps/can/a:', '/pps/can/a:{1;}', '/pps/can/a:1,/pps/can/a:2',
                     '/pps/can/a:1;run()', '/pps/can/a:{1,2}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_show_conditions(text)

    def test_api_classification_does_not_conflate_resources_and_execution(self):
        self.assertNotIn('dynamic_class', network_categories('java/lang/ClassLoader', 'getResourceAsStream'))
        self.assertIn('resource', network_categories('java/lang/ClassLoader', 'getResourceAsStream'))
        self.assertIn('server_socket', network_categories('java/net/ServerSocket', 'accept'))
        self.assertIn('native_library', network_categories('java/lang/System', 'load'))
        self.assertNotIn('process', network_categories('example/Executor', 'start'))
        self.assertIn('wireless_messaging', network_categories('konax/wireless/messaging/MessageConnection'))

    def test_selected_method_keeps_descriptors_and_excludes_unapproved_literals(self):
        model = parse_class(class_fixture())
        records = [method_record(model, m, set()) for m in model.methods]
        self.assertTrue(any(c['owner'] == 'java/net/ServerSocket' for r in records for c in r['calls']))
        self.assertTrue(all(r['constants'] == [] for r in records))
        self.assertTrue(all('descriptor' in c and 'bci' in c for r in records for c in r['calls']))
        self.assertEqual(encode(records), encode([method_record(model, m, set()) for m in model.methods]))

    def test_javap_checks_cannot_borrow_bci_from_another_overload(self):
        output = '''public class sample.A {
  public sample.A();
    descriptor: ()V
    Code:
       1: invokespecial #1 // Method java/lang/Object."<init>":()V
  public void run();
    descriptor: ()V
    Code:
       7: invokestatic #2 // Method first:()V
  public void run(int);
    descriptor: (I)V
    Code:
       7: invokestatic #3 // Method second:()V
  static {};
    descriptor: ()V
    Code:
       0: return
}
'''
        blocks = javap_blocks(output, 'sample/A')
        self.assertIn(('<init>', '()V'), blocks)
        self.assertIn(('<clinit>', '()V'), blocks)
        self.assertNotIn('second:', blocks['run', '()V'])
        self.assertNotIn('first:', blocks['run', '(I)V'])

    def test_notes_use_exact_labels_and_cover_nine_identities_and_six_cases(self):
        notes = json.loads(NOTES.read_text(encoding='utf-8'))
        validate_labels(notes)
        self.assertEqual(len(notes['applications']), 9)
        self.assertEqual({c['case'] for c in notes['yelp']['cases']}, set('ABCDEF'))
        self.assertEqual(set(notes['applications']), set(notes['method_selections']))
        with self.assertRaises(ValueError):
            validate_labels([{'label': 'CONFIRMED'}])

    def test_committed_activation_predicates_match_baseline_descriptors(self):
        root = Path(__file__).resolve().parents[2]
        baseline = json.loads((root / 'reports/target_production_state/package_inventory.json').read_text())
        reports = json.loads((root / 'reports/kim19_runtime_analysis/application_activation_matrix.json').read_text())
        by_id = {a['package_identity']: a for a in reports['applications']}
        for app in baseline['applications']:
            row = by_id[app['package_identity']]
            self.assertEqual(row['properties'], app['properties'])
            self.assertEqual(row['show_predicates'], parse_show_conditions(app['properties'].get('xlet.showConditions', '')))
            self.assertEqual(row['registered_on_target'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
