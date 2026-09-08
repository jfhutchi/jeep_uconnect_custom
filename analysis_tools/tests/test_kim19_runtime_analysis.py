import json
from pathlib import Path
import unittest

from analysis_tools.java_classfile import parse_class
from analysis_tools.kim19_runtime_analysis import (
    NOTES, encode, javap_blocks, known_predicates_match, method_record,
    network_categories, parse_show_conditions, validate_labels,
)
from analysis_tools.tests.test_java_classfile import class_fixture


class Kim19RuntimeTests(unittest.TestCase):
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
