import unittest

from analysis_tools.activation_graph import (
    ActivationGraph,
    CallEdge,
    MethodNode,
    ROOT_CATEGORIES,
)


def node(identifier, class_name=None, roots=()):
    owner, method = identifier.split("#", 1)
    method_name = method.split("(", 1)[0]
    descriptor = method[len(method_name):]
    return MethodNode(
        id=identifier,
        class_name=class_name or owner,
        method_name=method_name,
        descriptor=descriptor,
        root_categories=tuple(roots),
        sources=(
            {
                "kind": "parsed_structure",
                "artifact": "resident/synthetic.jar",
                "member": owner + ".class",
                "offset": 0,
            },
        ),
    )


class ActivationGraphTests(unittest.TestCase):
    def graph(self):
        nodes = [
            node("example/MainXlet#startXlet()V", roots=("xlet_lifecycle",)),
            node("example/Factory#create()Ljava/lang/Object;", roots=("factory_provider",)),
            node("example/SocketSource#<init>()V"),
            node("example/SocketSource#run()V"),
            node("example/A#a()V"),
            node("example/B#b()V"),
            node("example/TestOnly#start()V", roots=("test_framework",)),
            node("example/Unresolved#invoke()V"),
        ]
        edges = [
            CallEdge(nodes[0].id, nodes[1].id, "invoke_static", True),
            CallEdge(nodes[1].id, nodes[2].id, "construct", True),
            CallEdge(nodes[2].id, nodes[3].id, "invoke_virtual", True),
            CallEdge(nodes[4].id, nodes[5].id, "invoke_virtual", True),
            CallEdge(nodes[5].id, nodes[4].id, "invoke_virtual", True),
            CallEdge(nodes[6].id, nodes[3].id, "invoke_virtual", True),
            CallEdge(nodes[7].id, nodes[3].id, "invoke_interface", False),
        ]
        return ActivationGraph(nodes, edges)

    def test_root_categories_are_explicit_and_locked(self):
        self.assertEqual(
            ROOT_CATEGORIES,
            (
                "xlet_lifecycle", "ui_callback", "service_callback",
                "configuration", "registration", "factory_provider",
                "feature_flag", "thread_runnable", "test_framework",
                "unknown_external_entry",
            ),
        )

    def test_reverse_paths_are_deterministic_and_keep_root_categories(self):
        paths = self.graph().reverse_paths(
            "example/SocketSource#run()V", max_depth=8,
            excluded_root_categories=("test_framework",),
        )
        self.assertEqual(
            [path.nodes for path in paths],
            [
                (
                    "example/Factory#create()Ljava/lang/Object;",
                    "example/SocketSource#<init>()V",
                    "example/SocketSource#run()V",
                ),
                (
                    "example/MainXlet#startXlet()V",
                    "example/Factory#create()Ljava/lang/Object;",
                    "example/SocketSource#<init>()V",
                    "example/SocketSource#run()V",
                ),
            ],
        )
        self.assertEqual(paths[0].root_categories, ("factory_provider",))
        self.assertFalse(any("Unresolved" in value for path in paths for value in path.nodes))

    def test_strong_components_report_recursion_without_unbounded_paths(self):
        self.assertEqual(
            self.graph().strong_components(),
            [("example/A#a()V", "example/B#b()V")],
        )

    def test_activation_ladder_does_not_promote_later_states(self):
        ladder = self.graph().activation_ladder(
            "example/SocketSource", excluded_root_categories=("test_framework",)
        )
        self.assertEqual(ladder["class_exists"]["classification"], "PROVED")
        self.assertEqual(ladder["statically_reachable"]["classification"], "PROVED")
        for state in (
            "activation_mechanism_exists", "activation_configured",
            "production_enabled", "listener_executable", "externally_reachable",
        ):
            self.assertEqual(ladder[state]["classification"], "UNKNOWN")
            self.assertEqual(ladder[state]["evidence"], [])

    def test_activation_ladder_deduplicates_class_presence_sources(self):
        shared_source = ({
            "kind": "parsed_structure",
            "artifact": "resident/synthetic.jar",
            "member": "example/SocketSource.class",
            "offset": 0,
        },)
        graph = ActivationGraph(
            [
                MethodNode(
                    "example/SocketSource#<init>()V", "example/SocketSource",
                    "<init>", "()V", sources=shared_source,
                ),
                MethodNode(
                    "example/SocketSource#run()V", "example/SocketSource",
                    "run", "()V", sources=shared_source,
                ),
            ],
            [],
        )

        ladder = graph.activation_ladder("example/SocketSource")

        self.assertEqual(ladder["class_exists"]["evidence"], list(shared_source))

    def test_explicit_later_state_evidence_is_preserved_independently(self):
        supplied = {
            "activation_mechanism_exists": {
                "classification": "STRONGLY INFERRED",
                "evidence": ["configured factory name"],
            }
        }
        ladder = self.graph().activation_ladder(
            "example/SocketSource", state_evidence=supplied
        )
        self.assertEqual(
            ladder["activation_mechanism_exists"]["classification"],
            "STRONGLY INFERRED",
        )
        self.assertEqual(ladder["activation_configured"]["classification"], "UNKNOWN")

    def test_bounds_and_unknown_nodes_fail_closed(self):
        graph = self.graph()
        with self.assertRaisesRegex(ValueError, "max_depth"):
            graph.reverse_paths("example/SocketSource#run()V", max_depth=0)
        with self.assertRaisesRegex(ValueError, "max_paths"):
            graph.reverse_paths("example/SocketSource#run()V", max_paths=0)
        with self.assertRaisesRegex(ValueError, "unknown target"):
            graph.reverse_paths("missing#method()V")
        with self.assertRaisesRegex(ValueError, "unknown edge"):
            ActivationGraph(
                [node("example/Only#run()V")],
                [CallEdge("example/Only#run()V", "missing#run()V", "invoke_static", True)],
            )
        duplicate = node("example/Duplicate#run()V")
        with self.assertRaisesRegex(ValueError, "duplicate method node"):
            ActivationGraph([duplicate, duplicate], [])


if __name__ == "__main__":
    unittest.main()
