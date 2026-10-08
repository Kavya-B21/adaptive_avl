from typing import Dict, Any, Optional, List

from backend.modules.context_analyzer import ContextAnalyzer
from backend.modules.symmetry_analyzer import SymmetryAnalyzer


class CanonicalRepresentation:
    """
    Combines workload context and AVL symmetry information into
    a normalized representation for the evolutionary optimizer.

    This module does not modify the AVL tree and does not perform
    optimization.
    """

    CONTEXT_FEATURES = [
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
        "imbalance_frequency",
    ]

    CANONICAL_FEATURES = [
        "node_count",
        "tree_height",
        "insert_ratio",
        "delete_ratio",
        "search_ratio",
        "canonical_ll_count",
        "canonical_lr_count",
        "single_symmetry_ratio",
        "double_symmetry_ratio",
        "physical_rotation_count",
        "balance_calculation_count",
        "rotation_frequency",
        "imbalance_frequency",
    ]

    def __init__(
        self,
        context_analyzer: Optional[ContextAnalyzer] = None,
        symmetry_analyzer: Optional[SymmetryAnalyzer] = None,
    ):
        self.context_analyzer = (
            context_analyzer
            if context_analyzer is not None
            else ContextAnalyzer()
        )

        self.symmetry_analyzer = (
            symmetry_analyzer
            if symmetry_analyzer is not None
            else SymmetryAnalyzer()
        )

        self.last_representation: Optional[Dict[str, Any]] = None

    # ---------------------------------------------------------
    # Main analysis
    # ---------------------------------------------------------

    def analyze(self, avl_tree) -> Dict[str, Any]:
        """
        Build the complete canonical representation from an AVL tree.

        The tree is only observed and never modified.
        """
        if avl_tree is None:
            raise ValueError("AVL tree cannot be None.")

        context = self.context_analyzer.analyze(avl_tree)
        symmetry = self.symmetry_analyzer.analyze_context(context)

        representation = self._build_representation(
            context,
            symmetry,
        )

        self.last_representation = representation

        return representation

    # ---------------------------------------------------------
    # Build representation
    # ---------------------------------------------------------

    def _build_representation(
        self,
        context: Dict[str, Any],
        symmetry: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combine context and symmetry information into one
        structured representation.
        """

        tree = context["tree"]
        operations = context["operations"]
        ratios = context["ratios"]
        overhead = context["overhead"]
        derived = context["derived"]

        canonical_cases = symmetry["canonical_cases"]
        symmetry_ratios = symmetry["ratios"]

        representation = {
            "tree": {
                "node_count": tree["node_count"],
                "tree_height": tree["tree_height"],
            },

            "workload": {
                "insert_count": operations["insert_count"],
                "delete_count": operations["delete_count"],
                "search_count": operations["search_count"],
                "total_operations": operations["total_operations"],
                "insert_ratio": ratios["insert_ratio"],
                "delete_ratio": ratios["delete_ratio"],
                "search_ratio": ratios["search_ratio"],
            },

            "symmetry": {
                "canonical_ll_count": canonical_cases["LL"],
                "canonical_lr_count": canonical_cases["LR"],
                "single_symmetry_ratio": symmetry_ratios["single_ratio"],
                "double_symmetry_ratio": symmetry_ratios["double_ratio"],
                "total_imbalance_cases": symmetry["total_cases"],
            },

            "overhead": {
                "physical_rotation_count": (
                    overhead["physical_rotation_count"]
                ),
                "balance_calculation_count": (
                    overhead["balance_calculation_count"]
                ),
                "rotation_frequency": derived["rotation_frequency"],
                "imbalance_frequency": derived["imbalance_frequency"],
            },
        }

        return representation

    # ---------------------------------------------------------
    # Flat optimization vector
    # ---------------------------------------------------------

    def get_feature_vector(
        self,
        avl_tree=None,
        representation: Optional[Dict[str, Any]] = None,
    ) -> List[float]:
        """
        Return a flat numerical feature vector suitable for
        the future evolutionary optimizer.

        If representation is supplied, the tree does not need
        to be analyzed again.
        """

        if representation is None:
            if avl_tree is None:
                if self.last_representation is None:
                    raise ValueError(
                        "Provide an AVL tree or a representation."
                    )

                representation = self.last_representation
            else:
                representation = self.analyze(avl_tree)

        tree = representation["tree"]
        workload = representation["workload"]
        symmetry = representation["symmetry"]
        overhead = representation["overhead"]

        vector = [
            float(tree["node_count"]),
            float(tree["tree_height"]),

            float(workload["insert_ratio"]),
            float(workload["delete_ratio"]),
            float(workload["search_ratio"]),

            float(symmetry["canonical_ll_count"]),
            float(symmetry["canonical_lr_count"]),

            float(symmetry["single_symmetry_ratio"]),
            float(symmetry["double_symmetry_ratio"]),

            float(overhead["physical_rotation_count"]),
            float(overhead["balance_calculation_count"]),

            float(overhead["rotation_frequency"]),
            float(overhead["imbalance_frequency"]),
        ]

        return vector

    # ---------------------------------------------------------
    # Feature names
    # ---------------------------------------------------------

    def get_feature_names(self) -> List[str]:
        """
        Return the names corresponding to get_feature_vector().
        """
        return self.CANONICAL_FEATURES.copy()

    # ---------------------------------------------------------
    # Feature dictionary
    # ---------------------------------------------------------

    def get_feature_dict(
        self,
        avl_tree=None,
        representation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, float]:
        """
        Return the optimization features as a dictionary.
        """

        vector = self.get_feature_vector(
            avl_tree=avl_tree,
            representation=representation,
        )

        names = self.get_feature_names()

        return dict(zip(names, vector))

    # ---------------------------------------------------------
    # Canonical rotation classification
    # ---------------------------------------------------------

    def canonicalize_case(
        self,
        rotation_case: str,
    ) -> Dict[str, Any]:
        """
        Convert one raw AVL rotation case into its canonical form.

        Example:

            RR -> {
                "canonical_case": "LL",
                "mirrored": True
            }
        """

        return self.symmetry_analyzer.get_canonical_representation(
            rotation_case
        )

    # ---------------------------------------------------------
    # Representation validation
    # ---------------------------------------------------------

    def validate_representation(
        self,
        representation: Dict[str, Any],
    ) -> bool:
        """
        Validate that a canonical representation contains the
        required structure and numerical feature values.
        """

        if not isinstance(representation, dict):
            return False

        required_sections = {
            "tree",
            "workload",
            "symmetry",
            "overhead",
        }

        if not required_sections.issubset(representation.keys()):
            return False

        feature_dict = self.get_feature_dict(
            representation=representation
        )

        for value in feature_dict.values():
            if not isinstance(value, (int, float)):
                return False

        return True

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def get_summary(
        self,
        avl_tree=None,
        representation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Return a compact summary for logging or the dashboard.
        """

        if representation is None:
            if avl_tree is None:
                representation = self.last_representation
            else:
                representation = self.analyze(avl_tree)

        if representation is None:
            raise ValueError(
                "Provide an AVL tree or a representation."
            )

        workload = representation["workload"]
        symmetry = representation["symmetry"]

        dominant_operation = max(
            (
                ("insert", workload["insert_ratio"]),
                ("delete", workload["delete_ratio"]),
                ("search", workload["search_ratio"]),
            ),
            key=lambda item: item[1],
        )

        if workload["total_operations"] == 0:
            dominant_operation = ("none", 0.0)

        return {
            "node_count": representation["tree"]["node_count"],
            "tree_height": representation["tree"]["tree_height"],
            "dominant_operation": dominant_operation[0],
            "dominant_operation_ratio": dominant_operation[1],
            "canonical_ll_count": symmetry["canonical_ll_count"],
            "canonical_lr_count": symmetry["canonical_lr_count"],
            "total_imbalance_cases": symmetry["total_imbalance_cases"],
            "feature_count": len(self.CANONICAL_FEATURES),
        }

    # ---------------------------------------------------------
    # Last representation
    # ---------------------------------------------------------

    def get_last_representation(self) -> Optional[Dict[str, Any]]:
        """
        Return the most recently generated representation.
        """
        return self.last_representation