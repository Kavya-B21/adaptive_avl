from modules.avl_tree import AVLTree


def print_tree_info(name, values):
    tree = AVLTree()

    for value in values:
        tree.insert(value)

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    print("Input:", values)
    print("Inorder:", tree.inorder())
    print("Root:", tree.root.key if tree.root else None)
    print("Height:", tree.get_tree_height())
    print("Valid AVL:", tree.validate_avl())

    print("Statistics:")

    stats = tree.get_statistics()

    for key, value in stats.items():
        print(f"  {key}: {value}")


print_tree_info(
    "LL CASE",
    [30, 20, 10]
)

print_tree_info(
    "RR CASE",
    [10, 20, 30]
)

print_tree_info(
    "LR CASE",
    [30, 10, 20]
)

print_tree_info(
    "RL CASE",
    [10, 30, 20]
)
