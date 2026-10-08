from backend.modules.avl_tree import AVLTree
from backend.modules.context_analyzer import ContextAnalyzer


# ================================================================
# EMPTY TREE
# ================================================================

def test_empty_tree_context():
    tree = AVLTree()

    analyzer = ContextAnalyzer()

    context = analyzer.analyze(tree)

    assert context["tree"]["node_count"] == 0
    assert context["tree"]["tree_height"] == 0

    assert context["operations"]["insert_count"] == 0
    assert context["operations"]["delete_count"] == 0
    assert context["operations"]["search_count"] == 0

    assert context["operations"]["total_operations"] == 0

    assert context["ratios"]["insert_ratio"] == 0.0
    assert context["ratios"]["delete_ratio"] == 0.0
    assert context["ratios"]["search_ratio"] == 0.0

    assert analyzer.classify_workload() == "empty"

    assert analyzer.get_dominant_operation() == "none"


# ================================================================
# INSERT WORKLOAD
# ================================================================

def test_insert_context():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    analyzer = ContextAnalyzer()

    context = analyzer.analyze(tree)

    assert context["tree"]["node_count"] == 3
    assert context["tree"]["tree_height"] == 2

    assert context["operations"]["insert_count"] == 3

    assert context["operations"]["total_operations"] == 3

    assert context["ratios"]["insert_ratio"] == 1.0
    assert context["ratios"]["delete_ratio"] == 0.0
    assert context["ratios"]["search_ratio"] == 0.0

    assert context["rotation_cases"]["LL"] == 1

    assert context["overhead"][
        "physical_rotation_count"
    ] == 1

    assert analyzer.get_dominant_operation() == "insert"

    assert analyzer.classify_workload() == "insert_heavy"


# ================================================================
# SEARCH WORKLOAD
# ================================================================

def test_search_context():
    tree = AVLTree()

    # 3 insert operations
    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    # 8 search operations
    tree.search(50)
    tree.search(30)
    tree.search(70)
    tree.search(100)
    tree.search(200)
    tree.search(30)
    tree.search(70)
    tree.search(50)

    analyzer = ContextAnalyzer()

    context = analyzer.analyze(tree)

    assert context["operations"]["insert_count"] == 3

    assert context["operations"]["search_count"] == 8

    assert context["operations"]["delete_count"] == 0

    assert context["operations"]["total_operations"] == 11

    assert context["ratios"]["insert_ratio"] == 3 / 11

    assert context["ratios"]["search_ratio"] == 8 / 11

    assert context["ratios"]["delete_ratio"] == 0.0

    assert analyzer.get_dominant_operation() == "search"

    # 8 / 11 = 72.7%, which is above
    # the 70% heavy-workload threshold.
    assert analyzer.classify_workload() == "search_heavy"
# ================================================================
# DELETE WORKLOAD
# ================================================================

def test_delete_context():
    tree = AVLTree()

    for value in [
        50,
        30,
        70,
        20,
        40
    ]:
        tree.insert(value)

    tree.delete(20)
    tree.delete(40)
    tree.delete(30)

    analyzer = ContextAnalyzer()

    context = analyzer.analyze(tree)

    assert context["operations"]["insert_count"] == 5

    assert context["operations"]["delete_count"] == 3

    assert context["operations"]["total_operations"] == 8

    assert context["ratios"]["delete_ratio"] == 3 / 8

    assert analyzer.get_dominant_operation() == "insert"

    assert analyzer.classify_workload() == "mixed"


# ================================================================
# MIXED WORKLOAD
# ================================================================

def test_mixed_workload():
    tree = AVLTree()

    # 5 inserts
    for value in [
        50,
        30,
        70,
        20,
        40
    ]:
        tree.insert(value)

    # 2 searches
    tree.search(40)
    tree.search(100)

    # 1 deletion
    tree.delete(20)

    analyzer = ContextAnalyzer()

    context = analyzer.analyze(tree)

    assert context["operations"]["insert_count"] == 5

    assert context["operations"]["search_count"] == 2

    assert context["operations"]["delete_count"] == 1

    assert context["operations"]["total_operations"] == 8

    assert context["ratios"]["insert_ratio"] == 5 / 8

    assert context["ratios"]["search_ratio"] == 2 / 8

    assert context["ratios"]["delete_ratio"] == 1 / 8

    # 5/8 = 62.5%, which is below the 70% threshold.
    assert analyzer.classify_workload() == "mixed"


# ================================================================
# ROTATION DISTRIBUTION
# ================================================================

def test_rotation_distribution():
    tree = AVLTree()

    # LL
    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    analyzer = ContextAnalyzer()

    # Analyze the tree before requesting derived information.
    analyzer.analyze(tree)

    distribution = (
        analyzer.get_rotation_distribution()
    )

    assert distribution["LL"] == 1.0
    assert distribution["RR"] == 0.0
    assert distribution["LR"] == 0.0
    assert distribution["RL"] == 0.0


# ================================================================
# CONTEXT VECTOR
# ================================================================

def test_context_vector():
    tree = AVLTree()

    for value in [
        30,
        20,
        10
    ]:
        tree.insert(value)

    analyzer = ContextAnalyzer()

    analyzer.analyze(tree)

    vector = analyzer.get_context_vector()

    expected_keys = {
        "node_count",
        "tree_height",

        "insert_ratio",
        "delete_ratio",
        "search_ratio",

        "ll_count",
        "rr_count",
        "lr_count",
        "rl_count",

        "physical_rotation_count",
        "balance_calculation_count",

        "rotation_frequency",
        "imbalance_frequency"
    }

    assert set(vector.keys()) == expected_keys

    assert vector["node_count"] == 3.0

    assert vector["tree_height"] == 2.0

    assert vector["insert_ratio"] == 1.0

    assert vector["delete_ratio"] == 0.0

    assert vector["search_ratio"] == 0.0

    assert vector["ll_count"] == 1.0

    assert vector["rr_count"] == 0.0

    assert vector["lr_count"] == 0.0

    assert vector["rl_count"] == 0.0

    assert vector["physical_rotation_count"] == 1.0


# ================================================================
# SUMMARY
# ================================================================

def test_summary():
    tree = AVLTree()

    for value in [
        10,
        20,
        30
    ]:
        tree.insert(value)

    analyzer = ContextAnalyzer()

    analyzer.analyze(tree)

    summary = analyzer.get_summary()

    assert summary["node_count"] == 3

    assert summary["tree_height"] == 2

    assert summary["total_operations"] == 3

    assert summary["dominant_operation"] == "insert"

    assert summary["workload_class"] == "insert_heavy"

    assert summary["physical_rotation_count"] == 1


# ================================================================
# ANALYZER MUST NOT MODIFY TREE
# ================================================================

def test_analyzer_does_not_modify_tree():
    tree = AVLTree()

    values = [
        50,
        30,
        70,
        20,
        40
    ]

    for value in values:
        tree.insert(value)

    before_inorder = tree.inorder()

    before_height = tree.get_tree_height()

    before_node_count = tree.count_nodes()

    analyzer = ContextAnalyzer()

    analyzer.analyze(tree)

    analyzer.get_context_vector()

    analyzer.get_summary()

    analyzer.get_rotation_distribution()

    analyzer.get_dominant_operation()

    analyzer.classify_workload()

    after_inorder = tree.inorder()

    after_height = tree.get_tree_height()

    after_node_count = tree.count_nodes()

    assert before_inorder == after_inorder

    assert before_height == after_height

    assert before_node_count == after_node_count

    assert tree.validate_avl()


# ================================================================
# DIRECT TREE ARGUMENT TEST
# ================================================================

def test_methods_can_analyze_directly():
    tree = AVLTree()

    for value in [
        30,
        20,
        10
    ]:
        tree.insert(value)

    analyzer = ContextAnalyzer()

    # These methods should work without an earlier
    # explicit analyzer.analyze(tree).

    vector = analyzer.get_context_vector(tree)

    summary = analyzer.get_summary(tree)

    distribution = (
        analyzer.get_rotation_distribution(tree)
    )

    dominant = analyzer.get_dominant_operation(tree)

    workload = analyzer.classify_workload(tree)

    assert vector["node_count"] == 3.0

    assert summary["node_count"] == 3

    assert distribution["LL"] == 1.0

    assert dominant == "insert"

    assert workload == "insert_heavy"