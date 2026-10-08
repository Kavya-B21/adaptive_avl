from typing import Dict, Any, Optional


class ContextAnalyzer:
    """
    Analyzes the current state and workload of an AVL tree.

    Responsibilities:
    - Read statistics from AVLTree
    - Calculate operation ratios
    - Calculate rotation statistics
    - Calculate derived workload metrics
    - Classify the workload
    - Generate a flat context vector for future optimization

    Important:
    This class does NOT modify the AVL tree.
    """

    def __init__(self):
        """
        Initialize the context analyzer.

        last_context stores the most recently analyzed context.
        """

        self.last_context: Optional[Dict[str, Any]] = None

    # ============================================================
    # MAIN ANALYSIS
    # ============================================================

    def analyze(self, avl_tree) -> Dict[str, Any]:
        """
        Analyze an AVLTree object.

        Parameters
        ----------
        avl_tree:
            An AVLTree instance.

        Returns
        -------
        Dict[str, Any]
            Structured workload context.
        """

        if avl_tree is None:
            raise ValueError("AVL tree cannot be None.")

        # --------------------------------------------------------
        # Obtain statistics from AVL tree
        # --------------------------------------------------------

        stats = avl_tree.get_statistics()

        # --------------------------------------------------------
        # Tree state
        # --------------------------------------------------------

        node_count = stats["node_count"]
        tree_height = stats["tree_height"]

        # --------------------------------------------------------
        # Operation counts
        # --------------------------------------------------------

        insert_count = stats["insert_count"]
        delete_count = stats["delete_count"]
        search_count = stats["search_count"]

        total_operations = (
            insert_count
            + delete_count
            + search_count
        )

        # --------------------------------------------------------
        # Operation ratios
        # --------------------------------------------------------

        insert_ratio = self._calculate_ratio(
            insert_count,
            total_operations
        )

        delete_ratio = self._calculate_ratio(
            delete_count,
            total_operations
        )

        search_ratio = self._calculate_ratio(
            search_count,
            total_operations
        )

        # --------------------------------------------------------
        # Rotation case statistics
        # --------------------------------------------------------

        case_counts = stats.get(
            "case_counts",
            {}
        )

        ll_count = case_counts.get("LL", 0)
        rr_count = case_counts.get("RR", 0)
        lr_count = case_counts.get("LR", 0)
        rl_count = case_counts.get("RL", 0)

        total_imbalance_cases = (
            ll_count
            + rr_count
            + lr_count
            + rl_count
        )

        # --------------------------------------------------------
        # Physical rotation statistics
        # --------------------------------------------------------

        physical_rotation_count = (
            stats["physical_rotation_count"]
        )

        balance_calculation_count = (
            stats["balance_calculation_count"]
        )

        # --------------------------------------------------------
        # Derived metrics
        # --------------------------------------------------------

        rotation_frequency = self._calculate_ratio(
            physical_rotation_count,
            total_operations
        )

        imbalance_frequency = self._calculate_ratio(
            total_imbalance_cases,
            total_operations
        )

        # --------------------------------------------------------
        # Build structured context
        # --------------------------------------------------------

        context = {
            "tree": {
                "node_count": node_count,
                "tree_height": tree_height
            },

            "operations": {
                "insert_count": insert_count,
                "delete_count": delete_count,
                "search_count": search_count,
                "total_operations": total_operations
            },

            "ratios": {
                "insert_ratio": insert_ratio,
                "delete_ratio": delete_ratio,
                "search_ratio": search_ratio
            },

            "rotation_cases": {
                "LL": ll_count,
                "RR": rr_count,
                "LR": lr_count,
                "RL": rl_count,
                "total_imbalance_cases":
                    total_imbalance_cases
            },

            "overhead": {
                "physical_rotation_count":
                    physical_rotation_count,

                "balance_calculation_count":
                    balance_calculation_count
            },

            "derived": {
                "rotation_frequency":
                    rotation_frequency,

                "imbalance_frequency":
                    imbalance_frequency
            }
        }

        # --------------------------------------------------------
        # Store latest context
        # --------------------------------------------------------

        self.last_context = context

        return context

    # ============================================================
    # RATIO CALCULATION
    # ============================================================

    @staticmethod
    def _calculate_ratio(
        numerator: int,
        denominator: int
    ) -> float:
        """
        Safely calculate numerator / denominator.

        Returns 0.0 when denominator is zero.
        """

        if denominator == 0:
            return 0.0

        return numerator / denominator

    # ============================================================
    # CONTEXT AVAILABILITY
    # ============================================================

    def _get_context(
        self,
        avl_tree=None
    ) -> Dict[str, Any]:
        """
        Return current context.

        If an AVL tree is supplied, analyze it first.

        Otherwise use the most recently analyzed context.
        """

        if avl_tree is not None:
            return self.analyze(avl_tree)

        if self.last_context is not None:
            return self.last_context

        raise ValueError(
            "No context available. "
            "Run analyze(avl_tree) first."
        )

    # ============================================================
    # FLAT CONTEXT VECTOR
    # ============================================================

    def get_context_vector(
        self,
        avl_tree=None
    ) -> Dict[str, float]:
        """
        Return a flat numerical context representation.

        This representation will later be useful for:
        - evolutionary optimization
        - ML models
        - numerical analysis
        - experiment logging
        """

        context = self._get_context(avl_tree)

        return {
            # ----------------------------------------------------
            # Tree state
            # ----------------------------------------------------

            "node_count": float(
                context["tree"]["node_count"]
            ),

            "tree_height": float(
                context["tree"]["tree_height"]
            ),

            # ----------------------------------------------------
            # Operation ratios
            # ----------------------------------------------------

            "insert_ratio": float(
                context["ratios"]["insert_ratio"]
            ),

            "delete_ratio": float(
                context["ratios"]["delete_ratio"]
            ),

            "search_ratio": float(
                context["ratios"]["search_ratio"]
            ),

            # ----------------------------------------------------
            # Rotation case counts
            # ----------------------------------------------------

            "ll_count": float(
                context["rotation_cases"]["LL"]
            ),

            "rr_count": float(
                context["rotation_cases"]["RR"]
            ),

            "lr_count": float(
                context["rotation_cases"]["LR"]
            ),

            "rl_count": float(
                context["rotation_cases"]["RL"]
            ),

            # ----------------------------------------------------
            # Physical overhead
            # ----------------------------------------------------

            "physical_rotation_count": float(
                context["overhead"][
                    "physical_rotation_count"
                ]
            ),

            "balance_calculation_count": float(
                context["overhead"][
                    "balance_calculation_count"
                ]
            ),

            # ----------------------------------------------------
            # Derived metrics
            # ----------------------------------------------------

            "rotation_frequency": float(
                context["derived"]["rotation_frequency"]
            ),

            "imbalance_frequency": float(
                context["derived"]["imbalance_frequency"]
            )
        }

    # ============================================================
    # DOMINANT OPERATION
    # ============================================================

    def get_dominant_operation(
        self,
        avl_tree=None
    ) -> str:
        """
        Determine the operation with the highest count.

        Returns:
            "insert"
            "delete"
            "search"
            "none"
        """

        context = self._get_context(avl_tree)

        operations = context["operations"]

        counts = {
            "insert": operations["insert_count"],
            "delete": operations["delete_count"],
            "search": operations["search_count"]
        }

        total_operations = sum(
            counts.values()
        )

        if total_operations == 0:
            return "none"

        return max(
            counts,
            key=counts.get
        )

    # ============================================================
    # WORKLOAD CLASSIFICATION
    # ============================================================

    def classify_workload(
        self,
        avl_tree=None
    ) -> str:
        """
        Classify the current workload.

        Classification:

            empty
            insert_heavy
            delete_heavy
            search_heavy
            mixed

        A workload is considered heavy when the
        operation represents at least 70% of all operations.
        """

        context = self._get_context(avl_tree)

        total_operations = (
            context["operations"]["total_operations"]
        )

        if total_operations == 0:
            return "empty"

        ratios = context["ratios"]

        insert_ratio = ratios["insert_ratio"]
        delete_ratio = ratios["delete_ratio"]
        search_ratio = ratios["search_ratio"]

        # --------------------------------------------------------
        # Workload classification threshold
        # --------------------------------------------------------

        threshold = 0.70

        if insert_ratio >= threshold:
            return "insert_heavy"

        if delete_ratio >= threshold:
            return "delete_heavy"

        if search_ratio >= threshold:
            return "search_heavy"

        return "mixed"

    # ============================================================
    # ROTATION DISTRIBUTION
    # ============================================================

    def get_rotation_distribution(
        self,
        avl_tree=None
    ) -> Dict[str, float]:
        """
        Calculate the relative distribution of:

            LL
            RR
            LR
            RL

        Returns values between 0.0 and 1.0.
        """

        context = self._get_context(avl_tree)

        rotation_cases = context["rotation_cases"]

        total = rotation_cases[
            "total_imbalance_cases"
        ]

        if total == 0:
            return {
                "LL": 0.0,
                "RR": 0.0,
                "LR": 0.0,
                "RL": 0.0
            }

        return {
            "LL": (
                rotation_cases["LL"] / total
            ),

            "RR": (
                rotation_cases["RR"] / total
            ),

            "LR": (
                rotation_cases["LR"] / total
            ),

            "RL": (
                rotation_cases["RL"] / total
            )
        }

    # ============================================================
    # SUMMARY
    # ============================================================

    def get_summary(
        self,
        avl_tree=None
    ) -> Dict[str, Any]:
        """
        Return a compact context summary.

        Suitable for:
        - API responses
        - dashboard cards
        - experiment logging
        """

        context = self._get_context(avl_tree)

        return {
            "node_count":
                context["tree"]["node_count"],

            "tree_height":
                context["tree"]["tree_height"],

            "total_operations":
                context["operations"]["total_operations"],

            "dominant_operation":
                self.get_dominant_operation(),

            "workload_class":
                self.classify_workload(),

            "rotation_frequency":
                context["derived"][
                    "rotation_frequency"
                ],

            "imbalance_frequency":
                context["derived"][
                    "imbalance_frequency"
                ],

            "physical_rotation_count":
                context["overhead"][
                    "physical_rotation_count"
                ],

            "balance_calculation_count":
                context["overhead"][
                    "balance_calculation_count"
                ]
        }

    # ============================================================
    # LATEST CONTEXT
    # ============================================================

    def get_last_context(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Return the most recently calculated context.

        Returns None if analyze() has not been called.
        """

        return self.last_context