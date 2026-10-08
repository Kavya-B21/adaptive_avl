from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any


@dataclass
class Node:
    """
    Represents a single node in the AVL tree.
    """

    key: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    height: int = 1


class AVLTree:
    """
    Standard AVL Tree implementation.

    Responsibilities:
    - Insert keys
    - Search keys
    - Delete keys
    - Detect AVL imbalance cases
    - Perform rotations
    - Track operation statistics
    - Validate AVL correctness
    """

    def __init__(self):
        self.root: Optional[Node] = None

        # Operation counters
        self.insert_count = 0
        self.delete_count = 0
        self.search_count = 0

        # Internal calculation statistics
        self.balance_calculation_count = 0

        # Physical rotations
        self.physical_rotation_count = 0

        # Logical AVL imbalance cases
        self.case_counts = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0
        }

    # ============================================================
    # BASIC NODE / HEIGHT FUNCTIONS
    # ============================================================

    def get_height(self, node: Optional[Node]) -> int:
        """
        Return the height of a node.

        Empty subtree has height 0.
        Leaf node has height 1.
        """

        if node is None:
            return 0

        return node.height

    def update_height(self, node: Node) -> None:
        """
        Recalculate the height of a node.
        """

        left_height = self.get_height(node.left)
        right_height = self.get_height(node.right)

        node.height = 1 + max(left_height, right_height)

    def get_balance(self, node: Optional[Node]) -> int:
        """
        Calculate balance factor.

        BF = height(left subtree) - height(right subtree)

        Valid AVL values:
        -1
         0
        +1
        """

        if node is None:
            return 0

        self.balance_calculation_count += 1

        return (
            self.get_height(node.left)
            - self.get_height(node.right)
        )

    # ============================================================
    # ROTATIONS
    # ============================================================

    def right_rotate(self, y: Node) -> Node:
        """
        Perform a right rotation.

              y
             /
            x
             \
              T2

        becomes:

            x
             \
              y
             /
            T2
        """

        x = y.left

        if x is None:
            return y

        t2 = x.right

        # Rotation
        x.right = y
        y.left = t2

        # Update heights
        self.update_height(y)
        self.update_height(x)

        self.physical_rotation_count += 1

        return x

    def left_rotate(self, x: Node) -> Node:
        """
        Perform a left rotation.

          x
           \
            y
           /
          T2

        becomes:

            y
           /
          x
           \
            T2
        """

        y = x.right

        if y is None:
            return x

        t2 = y.left

        # Rotation
        y.left = x
        x.right = t2

        # Update heights
        self.update_height(x)
        self.update_height(y)

        self.physical_rotation_count += 1

        return y

    # ============================================================
    # ROTATION CASE DETECTION
    # ============================================================

    def detect_rotation_case(
        self,
        node: Node,
        balance: Optional[int] = None
    ) -> Optional[str]:
        """
        Detect the logical AVL imbalance case.

        Returns:
            LL
            RR
            LR
            RL
            None
        """

        if balance is None:
            balance = self.get_balance(node)

        # Left-heavy
        if balance > 1:

            child_balance = self.get_balance(node.left)

            if child_balance >= 0:
                return "LL"

            return "LR"

        # Right-heavy
        if balance < -1:

            child_balance = self.get_balance(node.right)

            if child_balance <= 0:
                return "RR"

            return "RL"

        return None

    # ============================================================
    # INSERT
    # ============================================================

    def insert(self, key: int) -> bool:
        """
        Insert a key into the AVL tree.

        Returns:
            True  -> inserted successfully
            False -> key already exists
        """

        self.insert_count += 1

        self.root, inserted = self._insert(self.root, key)

        return inserted

    def _insert(
        self,
        node: Optional[Node],
        key: int
    ) -> Tuple[Optional[Node], bool]:

        # Empty position found
        if node is None:
            return Node(key=key), True

        # Ignore duplicates
        if key == node.key:
            return node, False

        # Insert into left subtree
        if key < node.key:

            node.left, inserted = self._insert(
                node.left,
                key
            )

        # Insert into right subtree
        else:

            node.right, inserted = self._insert(
                node.right,
                key
            )

        # No structural change
        if not inserted:
            return node, False

        # Update height
        self.update_height(node)

        # Calculate balance
        balance = self.get_balance(node)

        # Tree is balanced
        if -1 <= balance <= 1:
            return node, True

        # Detect logical case
        rotation_case = self.detect_rotation_case(
            node,
            balance
        )

        if rotation_case is not None:
            self.case_counts[rotation_case] += 1

        # --------------------------------------------------------
        # LL
        # --------------------------------------------------------

        if rotation_case == "LL":
            return self.right_rotate(node), True

        # --------------------------------------------------------
        # RR
        # --------------------------------------------------------

        if rotation_case == "RR":
            return self.left_rotate(node), True

        # --------------------------------------------------------
        # LR
        # --------------------------------------------------------

        if rotation_case == "LR":

            if node.left is not None:
                node.left = self.left_rotate(node.left)

            return self.right_rotate(node), True

        # --------------------------------------------------------
        # RL
        # --------------------------------------------------------

        if rotation_case == "RL":

            if node.right is not None:
                node.right = self.right_rotate(node.right)

            return self.left_rotate(node), True

        return node, True

    # ============================================================
    # SEARCH
    # ============================================================

    def search(self, key: int) -> Optional[Node]:
        """
        Search for a key.

        Returns:
            Node if found
            None otherwise
        """

        self.search_count += 1

        current = self.root

        while current is not None:

            if key == current.key:
                return current

            if key < current.key:
                current = current.left
            else:
                current = current.right

        return None

    # ============================================================
    # DELETE
    # ============================================================

    def delete(self, key: int) -> bool:
        """
        Delete a key from the AVL tree.

        Returns:
            True  -> key deleted
            False -> key not found
        """

        self.delete_count += 1

        self.root, deleted = self._delete(
            self.root,
            key
        )

        return deleted

    def _delete(
        self,
        node: Optional[Node],
        key: int
    ) -> Tuple[Optional[Node], bool]:

        if node is None:
            return None, False

        # Search left
        if key < node.key:

            node.left, deleted = self._delete(
                node.left,
                key
            )

        # Search right
        elif key > node.key:

            node.right, deleted = self._delete(
                node.right,
                key
            )

        # Node found
        else:

            # Case 1: no child
            if node.left is None and node.right is None:
                return None, True

            # Case 2: only right child
            if node.left is None:
                return node.right, True

            # Case 3: only left child
            if node.right is None:
                return node.left, True

            # Case 4: two children
            successor = self._get_min_node(
                node.right
            )

            node.key = successor.key

            node.right, _ = self._delete(
                node.right,
                successor.key
            )

            deleted = True

        # Key wasn't found
        if not deleted:
            return node, False

        # Update height
        self.update_height(node)

        # Calculate balance
        balance = self.get_balance(node)

        # Already balanced
        if -1 <= balance <= 1:
            return node, True

        # Detect imbalance
        rotation_case = self.detect_rotation_case(
            node,
            balance
        )

        if rotation_case is not None:
            self.case_counts[rotation_case] += 1

        # LL
        if rotation_case == "LL":
            return self.right_rotate(node), True

        # RR
        if rotation_case == "RR":
            return self.left_rotate(node), True

        # LR
        if rotation_case == "LR":

            if node.left is not None:
                node.left = self.left_rotate(node.left)

            return self.right_rotate(node), True

        # RL
        if rotation_case == "RL":

            if node.right is not None:
                node.right = self.right_rotate(node.right)

            return self.left_rotate(node), True

        return node, True

    def _get_min_node(self, node: Node) -> Node:
        """
        Return the smallest node in a subtree.
        """

        current = node

        while current.left is not None:
            current = current.left

        return current

    # ============================================================
    # TREE INFORMATION
    # ============================================================

    def count_nodes(self) -> int:
        """
        Return total number of nodes.
        """

        return self._count_nodes(self.root)

    def _count_nodes(
        self,
        node: Optional[Node]
    ) -> int:

        if node is None:
            return 0

        return (
            1
            + self._count_nodes(node.left)
            + self._count_nodes(node.right)
        )

    def get_tree_height(self) -> int:
        """
        Return current tree height.
        """

        return self.get_height(self.root)

    def inorder(self) -> list[int]:
        """
        Return keys in sorted order.
        """

        result = []

        self._inorder(self.root, result)

        return result

    def _inorder(
        self,
        node: Optional[Node],
        result: list[int]
    ) -> None:

        if node is None:
            return

        self._inorder(node.left, result)

        result.append(node.key)

        self._inorder(node.right, result)

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return AVL tree statistics.
        """

        return {
            "node_count": self.count_nodes(),
            "tree_height": self.get_tree_height(),

            "insert_count": self.insert_count,
            "delete_count": self.delete_count,
            "search_count": self.search_count,

            "balance_calculation_count":
                self.balance_calculation_count,

            "physical_rotation_count":
                self.physical_rotation_count,

            "case_counts": self.case_counts.copy()
        }

    # ============================================================
    # AVL VALIDATION
    # ============================================================

    def validate_avl(self) -> bool:
        """
        Validate complete AVL tree.

        Checks:
        1. BST ordering
        2. Correct stored heights
        3. Balance factor <= 1
        """

        valid, _, _, _ = self._validate_node(
            self.root,
            None,
            None
        )

        return valid

    def _validate_node(
        self,
        node: Optional[Node],
        min_key: Optional[int],
        max_key: Optional[int]
    ) -> Tuple[bool, int, Optional[int], Optional[int]]:

        if node is None:
            return True, 0, None, None

        # --------------------------------------------------------
        # BST validation
        # --------------------------------------------------------

        if min_key is not None and node.key <= min_key:
            return False, 0, None, None

        if max_key is not None and node.key >= max_key:
            return False, 0, None, None

        # --------------------------------------------------------
        # Validate left subtree
        # --------------------------------------------------------

        left_valid, left_height, left_min, left_max = (
            self._validate_node(
                node.left,
                min_key,
                node.key
            )
        )

        if not left_valid:
            return False, 0, None, None

        # --------------------------------------------------------
        # Validate right subtree
        # --------------------------------------------------------

        right_valid, right_height, right_min, right_max = (
            self._validate_node(
                node.right,
                node.key,
                max_key
            )
        )

        if not right_valid:
            return False, 0, None, None

        # --------------------------------------------------------
        # Calculate expected height
        # --------------------------------------------------------

        expected_height = (
            1 + max(left_height, right_height)
        )

        if node.height != expected_height:
            return False, 0, None, None

        # --------------------------------------------------------
        # Validate balance factor
        # --------------------------------------------------------

        balance = left_height - right_height

        if abs(balance) > 1:
            return False, 0, None, None

        # --------------------------------------------------------
        # Determine subtree min/max
        # --------------------------------------------------------

        subtree_min = (
            left_min
            if left_min is not None
            else node.key
        )

        subtree_max = (
            right_max
            if right_max is not None
            else node.key
        )

        return (
            True,
            expected_height,
            subtree_min,
            subtree_max
        )

    # ============================================================
    # RESET
    # ============================================================

    def reset_statistics(self) -> None:
        """
        Reset operation counters without destroying the tree.
        """

        self.insert_count = 0
        self.delete_count = 0
        self.search_count = 0

        self.balance_calculation_count = 0
        self.physical_rotation_count = 0

        self.case_counts = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0
        }

    def clear(self) -> None:
        """
        Remove the complete tree and reset statistics.
        """

        self.root = None

        self.reset_statistics()