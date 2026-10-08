import pytest

from backend.modules.avl_tree import AVLTree
from backend.modules.symmetry_analyzer import SymmetryAnalyzer


# ---------------------------------------------------------
# Basic case validation
# ---------------------------------------------------------

def test_supported_cases():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_supported_cases() == [
        "LL",
        "LR",
        "RL",
        "RR",
    ]


def test_invalid_case():
    analyzer = SymmetryAnalyzer()

    with pytest.raises(ValueError):
        analyzer.get_canonical_case("XX")


def test_non_string_case():
    analyzer = SymmetryAnalyzer()

    with pytest.raises(TypeError):
        analyzer.get_canonical_case(123)


def test_case_normalization():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_canonical_case("ll") == "LL"
    assert analyzer.get_canonical_case(" rr ") == "LL"


# ---------------------------------------------------------
# Symmetry pairs
# ---------------------------------------------------------

def test_ll_rr_symmetry():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_symmetric_case("LL") == "RR"
    assert analyzer.get_symmetric_case("RR") == "LL"


def test_lr_rl_symmetry():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_symmetric_case("LR") == "RL"
    assert analyzer.get_symmetric_case("RL") == "LR"


# ---------------------------------------------------------
# Canonical representation
# ---------------------------------------------------------

def test_canonical_cases():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_canonical_case("LL") == "LL"
    assert analyzer.get_canonical_case("RR") == "LL"

    assert analyzer.get_canonical_case("LR") == "LR"
    assert analyzer.get_canonical_case("RL") == "LR"


def test_mirror_flags():
    analyzer = SymmetryAnalyzer()

    assert analyzer.is_mirrored("LL") is False
    assert analyzer.is_mirrored("RR") is True

    assert analyzer.is_mirrored("LR") is False
    assert analyzer.is_mirrored("RL") is True


def test_canonical_representation():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_canonical_representation("LL") == {
        "canonical_case": "LL",
        "mirrored": False,
    }

    assert analyzer.get_canonical_representation("RR") == {
        "canonical_case": "LL",
        "mirrored": True,
    }

    assert analyzer.get_canonical_representation("LR") == {
        "canonical_case": "LR",
        "mirrored": False,
    }

    assert analyzer.get_canonical_representation("RL") == {
        "canonical_case": "LR",
        "mirrored": True,
    }


# ---------------------------------------------------------
# Detailed analysis
# ---------------------------------------------------------

def test_analyze_case():
    analyzer = SymmetryAnalyzer()

    result = analyzer.analyze_case("RR")

    assert result["original_case"] == "RR"
    assert result["symmetric_case"] == "LL"
    assert result["canonical_case"] == "LL"
    assert result["mirrored"] is True


def test_last_analysis():
    analyzer = SymmetryAnalyzer()

    analyzer.analyze_case("LR")

    assert analyzer.get_last_analysis() == {
        "original_case": "LR",
        "symmetric_case": "RL",
        "canonical_case": "LR",
        "mirrored": False,
    }


# ---------------------------------------------------------
# Symmetry classes
# ---------------------------------------------------------

def test_symmetry_classes():
    analyzer = SymmetryAnalyzer()

    assert analyzer.get_symmetry_class("LL") == "single"
    assert analyzer.get_symmetry_class("RR") == "single"

    assert analyzer.get_symmetry_class("LR") == "double"
    assert analyzer.get_symmetry_class("RL") == "double"


# ---------------------------------------------------------
# Batch analysis
# ---------------------------------------------------------

def test_analyze_cases():
    analyzer = SymmetryAnalyzer()

    cases = ["LL", "RR", "LR", "RL"]

    results = analyzer.analyze_cases(cases)

    assert len(results) == 4

    assert results[0]["canonical_case"] == "LL"
    assert results[1]["canonical_case"] == "LL"
    assert results[2]["canonical_case"] == "LR"
    assert results[3]["canonical_case"] == "LR"


def test_analyze_cases_invalid_input():
    analyzer = SymmetryAnalyzer()

    with pytest.raises(TypeError):
        analyzer.analyze_cases("LL")


# ---------------------------------------------------------
# Context integration
# ---------------------------------------------------------

def test_analyze_context():
    analyzer = SymmetryAnalyzer()

    context = {
        "rotation_cases": {
            "LL": 4,
            "RR": 3,
            "LR": 2,
            "RL": 1,
        }
    }

    result = analyzer.analyze_context(context)

    assert result["original_cases"]["LL"] == 4
    assert result["original_cases"]["RR"] == 3
    assert result["original_cases"]["LR"] == 2
    assert result["original_cases"]["RL"] == 1

    assert result["canonical_cases"]["LL"] == 7
    assert result["canonical_cases"]["LR"] == 3

    assert result["symmetry_classes"]["single"] == 7
    assert result["symmetry_classes"]["double"] == 3

    assert result["total_cases"] == 10

    assert result["ratios"]["single_ratio"] == 0.7
    assert result["ratios"]["double_ratio"] == 0.3


def test_analyze_empty_context():
    analyzer = SymmetryAnalyzer()

    context = {
        "rotation_cases": {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0,
        }
    }

    result = analyzer.analyze_context(context)

    assert result["total_cases"] == 0
    assert result["ratios"]["single_ratio"] == 0.0
    assert result["ratios"]["double_ratio"] == 0.0


# ---------------------------------------------------------
# AVL tree integration
# ---------------------------------------------------------

def test_ll_tree_symmetry():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    analyzer = SymmetryAnalyzer()

    result = analyzer.analyze_tree(tree)

    assert result["original_cases"]["LL"] == 1
    assert result["canonical_cases"]["LL"] == 1
    assert result["canonical_cases"]["LR"] == 0
    assert result["total_cases"] == 1


def test_rr_tree_symmetry():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(20)
    tree.insert(30)

    analyzer = SymmetryAnalyzer()

    result = analyzer.analyze_tree(tree)

    assert result["original_cases"]["RR"] == 1
    assert result["canonical_cases"]["LL"] == 1
    assert result["canonical_cases"]["LR"] == 0


def test_lr_tree_symmetry():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(10)
    tree.insert(20)

    analyzer = SymmetryAnalyzer()

    result = analyzer.analyze_tree(tree)

    assert result["original_cases"]["LR"] == 1
    assert result["canonical_cases"]["LR"] == 1
    assert result["canonical_cases"]["LL"] == 0


def test_rl_tree_symmetry():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(30)
    tree.insert(20)

    analyzer = SymmetryAnalyzer()

    result = analyzer.analyze_tree(tree)

    assert result["original_cases"]["RL"] == 1
    assert result["canonical_cases"]["LR"] == 1
    assert result["canonical_cases"]["LL"] == 0


# ---------------------------------------------------------
# Tree safety
# ---------------------------------------------------------

def test_analyzer_does_not_modify_tree():
    tree = AVLTree()

    values = [50, 30, 70, 20, 40, 60, 80]

    for value in values:
        tree.insert(value)

    before_inorder = tree.inorder()
    before_height = tree.get_height(tree.root)
    before_node_count = tree.count_nodes()
    before_valid = tree.validate_avl()

    analyzer = SymmetryAnalyzer()
    analyzer.analyze_tree(tree)

    assert tree.inorder() == before_inorder
    assert tree.get_height(tree.root) == before_height
    assert tree.count_nodes() == before_node_count
    assert tree.validate_avl() == before_valid


# ---------------------------------------------------------
# Error handling
# ---------------------------------------------------------

def test_invalid_context():
    analyzer = SymmetryAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze_context({})


def test_none_tree():
    analyzer = SymmetryAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze_tree(None)