from backend.modules.avl_tree import AVLTree


def test_ll_rotation():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(20)
    tree.insert(10)

    assert tree.root is not None
    assert tree.root.key == 20

    assert tree.root.left is not None
    assert tree.root.left.key == 10

    assert tree.root.right is not None
    assert tree.root.right.key == 30

    assert tree.validate_avl()

    stats = tree.get_statistics()

    assert stats["case_counts"]["LL"] == 1
    assert stats["physical_rotation_count"] == 1


def test_rr_rotation():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(20)
    tree.insert(30)

    assert tree.root is not None
    assert tree.root.key == 20

    assert tree.root.left is not None
    assert tree.root.left.key == 10

    assert tree.root.right is not None
    assert tree.root.right.key == 30

    assert tree.validate_avl()

    stats = tree.get_statistics()

    assert stats["case_counts"]["RR"] == 1
    assert stats["physical_rotation_count"] == 1


def test_lr_rotation():
    tree = AVLTree()

    tree.insert(30)
    tree.insert(10)
    tree.insert(20)

    assert tree.root is not None
    assert tree.root.key == 20

    assert tree.root.left is not None
    assert tree.root.left.key == 10

    assert tree.root.right is not None
    assert tree.root.right.key == 30

    assert tree.validate_avl()

    stats = tree.get_statistics()

    assert stats["case_counts"]["LR"] == 1
    assert stats["physical_rotation_count"] == 2


def test_rl_rotation():
    tree = AVLTree()

    tree.insert(10)
    tree.insert(30)
    tree.insert(20)

    assert tree.root is not None
    assert tree.root.key == 20

    assert tree.root.left is not None
    assert tree.root.left.key == 10

    assert tree.root.right is not None
    assert tree.root.right.key == 30

    assert tree.validate_avl()

    stats = tree.get_statistics()

    assert stats["case_counts"]["RL"] == 1
    assert stats["physical_rotation_count"] == 2


def test_search():
    tree = AVLTree()

    tree.insert(50)
    tree.insert(30)
    tree.insert(70)

    assert tree.search(50) is not None
    assert tree.search(30) is not None
    assert tree.search(70) is not None

    assert tree.search(100) is None


def test_duplicate_insertion():
    tree = AVLTree()

    assert tree.insert(50) is True
    assert tree.insert(50) is False

    assert tree.count_nodes() == 1
    assert tree.validate_avl()


def test_inorder():
    tree = AVLTree()

    values = [50, 30, 70, 20, 40, 60, 80]

    for value in values:
        tree.insert(value)

    assert tree.inorder() == sorted(values)


def test_deletion_leaf():
    tree = AVLTree()

    values = [50, 30, 70]

    for value in values:
        tree.insert(value)

    assert tree.delete(30) is True
    assert tree.search(30) is None

    assert tree.validate_avl()


def test_deletion_node_with_two_children():
    tree = AVLTree()

    values = [
        50,
        30,
        70,
        20,
        40,
        60,
        80
    ]

    for value in values:
        tree.insert(value)

    assert tree.delete(50) is True

    assert tree.search(50) is None

    assert tree.inorder() == [
        20,
        30,
        40,
        60,
        70,
        80
    ]

    assert tree.validate_avl()


def test_delete_missing_key():
    tree = AVLTree()

    tree.insert(50)

    assert tree.delete(100) is False

    assert tree.validate_avl()


def test_large_random_insertion():
    tree = AVLTree()

    values = [
        37, 12, 89, 4, 25,
        63, 91, 18, 42, 77,
        3, 8, 15, 22, 50
    ]

    for value in values:
        tree.insert(value)

        # Critical research invariant:
        assert tree.validate_avl()

    assert tree.count_nodes() == len(values)
    assert tree.inorder() == sorted(values)
def test_dynamic_workload():
    tree = AVLTree()

    operations = [
        ("insert", 50),
        ("insert", 30),
        ("insert", 70),
        ("insert", 20),
        ("insert", 40),
        ("insert", 60),
        ("insert", 80),
        ("search", 40),
        ("delete", 20),
        ("insert", 10),
        ("delete", 70),
        ("insert", 65),
        ("search", 65),
    ]

    for operation, value in operations:

        if operation == "insert":
            tree.insert(value)

        elif operation == "delete":
            tree.delete(value)

        elif operation == "search":
            tree.search(value)

        # AVL must remain valid after EVERY operation.
        assert tree.validate_avl()

    print(tree.get_statistics())