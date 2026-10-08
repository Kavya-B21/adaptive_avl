import pytest

from backend.modules.avl_tree import AVLTree
from backend.modules.canonical_representation import (
    CanonicalRepresentation,
)


# ---------------------------------------------------------
# Basic representation
# ---------------------------------------------------------

def test_empty_tree_representation():
    tree = AVLTree()

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["tree"]["node_count"] == 0
    assert representation["tree"]["tree_height"] == 0

    assert representation["workload"]["total_operations"] == 0

    assert representation["symmetry"]["canonical_ll_count"] == 0
    assert representation["symmetry"]["canonical_lr_count"] == 0

    assert representation["symmetry"]["total_imbalance_cases"] == 0


def test_insert_representation():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["tree"]["node_count"] == 3

    assert representation["workload"]["insert_count"] == 3
    assert representation["workload"]["total_operations"] == 3

    assert representation["workload"]["insert_ratio"] == 1.0
    assert representation["workload"]["delete_ratio"] == 0.0
    assert representation["workload"]["search_ratio"] == 0.0


# ---------------------------------------------------------
# Symmetry integration
# ---------------------------------------------------------

def test_rr_is_canonicalized_to_ll():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(20)
    tree.insert(30)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["symmetry"]["canonical_ll_count"] == 1
    assert representation["symmetry"]["canonical_lr_count"] == 0


def test_ll_is_canonicalized_to_ll():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["symmetry"]["canonical_ll_count"] == 1
    assert representation["symmetry"]["canonical_lr_count"] == 0


def test_lr_is_canonicalized_to_lr():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(10)
    tree.insert(20)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["symmetry"]["canonical_ll_count"] == 0
    assert representation["symmetry"]["canonical_lr_count"] == 1


def test_rl_is_canonicalized_to_lr():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(30)
    tree.insert(20)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert representation["symmetry"]["canonical_ll_count"] == 0
    assert representation["symmetry"]["canonical_lr_count"] == 1


# ---------------------------------------------------------
# Feature vector
# ---------------------------------------------------------

def test_feature_vector_length():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    vector = analyzer.get_feature_vector(tree)

    assert len(vector) == 13


def test_feature_names_length():
    analyzer = CanonicalRepresentation()

    names = analyzer.get_feature_names()

    assert len(names) == 13


def test_feature_names_match_vector():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    vector = analyzer.get_feature_vector(tree)
    names = analyzer.get_feature_names()

    assert len(vector) == len(names)


def test_feature_dict():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    feature_dict = analyzer.get_feature_dict(tree)

    assert feature_dict["node_count"] == 3.0
    assert feature_dict["tree_height"] == 2.0
    assert feature_dict["insert_ratio"] == 1.0
    assert feature_dict["delete_ratio"] == 0.0
    assert feature_dict["search_ratio"] == 0.0


# ---------------------------------------------------------
# Canonical case conversion
# ---------------------------------------------------------

def test_canonicalize_case():
    analyzer = CanonicalRepresentation()

    assert analyzer.canonicalize_case("LL") == {
        "canonical_case": "LL",
        "mirrored": False,
    }

    assert analyzer.canonicalize_case("RR") == {
        "canonical_case": "LL",
        "mirrored": True,
    }

    assert analyzer.canonicalize_case("LR") == {
        "canonical_case": "LR",
        "mirrored": False,
    }

    assert analyzer.canonicalize_case("RL") == {
        "canonical_case": "LR",
        "mirrored": True,
    }


# ---------------------------------------------------------
# Representation validation
# ---------------------------------------------------------

def test_valid_representation():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert analyzer.validate_representation(
        representation
    ) is True


def test_invalid_representation():
    analyzer = CanonicalRepresentation()

    assert analyzer.validate_representation({}) is False
    assert analyzer.validate_representation(None) is False
    assert analyzer.validate_representation([]) is False


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

def test_summary():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    summary = analyzer.get_summary(tree)

    assert summary["node_count"] == 3
    assert summary["tree_height"] == 2
    assert summary["dominant_operation"] == "insert"
    assert summary["dominant_operation_ratio"] == 1.0
    assert summary["feature_count"] == 13


def test_empty_summary():
    tree = AVLTree()

    analyzer = CanonicalRepresentation()

    summary = analyzer.get_summary(tree)

    assert summary["dominant_operation"] == "none"
    assert summary["dominant_operation_ratio"] == 0.0


# ---------------------------------------------------------
# State reuse
# ---------------------------------------------------------

def test_last_representation():
    tree = AVLTree()

    tree.insert(50)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    assert analyzer.get_last_representation() == representation


def test_feature_vector_from_last_representation():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    vector_1 = analyzer.get_feature_vector(
        representation=representation
    )

    vector_2 = analyzer.get_feature_vector()

    assert vector_1 == vector_2


# ---------------------------------------------------------
# Direct representation input
# ---------------------------------------------------------

def test_feature_vector_from_representation():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    vector = analyzer.get_feature_vector(
        representation=representation
    )

    assert len(vector) == 13


def test_feature_dict_from_representation():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    analyzer = CanonicalRepresentation()

    representation = analyzer.analyze(tree)

    features = analyzer.get_feature_dict(
        representation=representation
    )

    assert features["node_count"] == 3.0


# ---------------------------------------------------------
# Tree safety
# ---------------------------------------------------------

def test_analyzer_does_not_modify_tree():
    tree = AVLTree()

    values = [
        50,
        30,
        70,
        20,
        40,
        60,
        80,
    ]

    for value in values:
        tree.insert(value)

    before_inorder = tree.inorder()
    before_height = tree.get_height(tree.root)
    before_count = tree.count_nodes()
    before_valid = tree.validate_avl()

    analyzer = CanonicalRepresentation()

    analyzer.analyze(tree)

    assert tree.inorder() == before_inorder
    assert tree.get_height(tree.root) == before_height
    assert tree.count_nodes() == before_count
    assert tree.validate_avl() == before_valid


# ---------------------------------------------------------
# Error handling
# ---------------------------------------------------------

def test_none_tree():
    analyzer = CanonicalRepresentation()

    with pytest.raises(ValueError):
        analyzer.analyze(None)


def test_missing_feature_source():
    analyzer = CanonicalRepresentation()

    with pytest.raises(ValueError):
        analyzer.get_feature_vector()


def test_invalid_representation_structure():
    analyzer = CanonicalRepresentation()

    bad_representation = {
        "tree": {},
        "workload": {},
        "symmetry": {},
        "overhead": {},
    }

    with pytest.raises(KeyError):
        analyzer.get_feature_vector(
            representation=bad_representation
        )