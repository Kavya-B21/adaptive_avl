from typing import Dict, Any, List, Optional


class SymmetryAnalyzer:
    """
    Analyzes AVL rotation cases using structural symmetry.

    Symmetry relationships:

        LL <-> RR
        LR <-> RL

    Canonical representation:

        LL -> LL, mirrored=False
        RR -> LL, mirrored=True

        LR -> LR, mirrored=False
        RL -> LR, mirrored=True
    """

    VALID_CASES = {"LL", "RR", "LR", "RL"}

    # Maps every rotation case to its canonical representative.
    CANONICAL_MAP = {
        "LL": "LL",
        "RR": "LL",
        "LR": "LR",
        "RL": "LR",
    }

    # Indicates whether the original case is the mirrored form
    # of the canonical representation.
    MIRROR_MAP = {
        "LL": False,
        "RR": True,
        "LR": False,
        "RL": True,
    }

    # Direct symmetry pairs.
    SYMMETRY_MAP = {
        "LL": "RR",
        "RR": "LL",
        "LR": "RL",
        "RL": "LR",
    }

    def __init__(self):
        self.last_analysis: Optional[Dict[str, Any]] = None

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate_case(self, rotation_case: str) -> str:
        """
        Validate and normalize an AVL rotation case.

        Returns:
            Uppercase rotation case.

        Raises:
            ValueError: If the case is invalid.
            TypeError: If the input is not a string.
        """
        if not isinstance(rotation_case, str):
            raise TypeError("Rotation case must be a string.")

        rotation_case = rotation_case.strip().upper()

        if rotation_case not in self.VALID_CASES:
            raise ValueError(
                f"Invalid rotation case '{rotation_case}'. "
                f"Expected one of {sorted(self.VALID_CASES)}."
            )

        return rotation_case

    # ---------------------------------------------------------
    # Basic symmetry operations
    # ---------------------------------------------------------

    def get_symmetric_case(self, rotation_case: str) -> str:
        """
        Return the mirror-symmetric AVL rotation case.

        Examples:
            LL -> RR
            RR -> LL
            LR -> RL
            RL -> LR
        """
        rotation_case = self.validate_case(rotation_case)
        return self.SYMMETRY_MAP[rotation_case]

    def get_canonical_case(self, rotation_case: str) -> str:
        """
        Convert an AVL rotation case to its canonical symmetry class.

        Examples:
            LL -> LL
            RR -> LL
            LR -> LR
            RL -> LR
        """
        rotation_case = self.validate_case(rotation_case)
        return self.CANONICAL_MAP[rotation_case]

    def is_mirrored(self, rotation_case: str) -> bool:
        """
        Determine whether the rotation case is the mirrored
        representation of its canonical case.

        Examples:
            LL -> False
            RR -> True
            LR -> False
            RL -> True
        """
        rotation_case = self.validate_case(rotation_case)
        return self.MIRROR_MAP[rotation_case]

    # ---------------------------------------------------------
    # Detailed analysis
    # ---------------------------------------------------------

    def analyze_case(self, rotation_case: str) -> Dict[str, Any]:
        """
        Analyze one AVL rotation case.

        Returns a structured symmetry representation.
        """
        rotation_case = self.validate_case(rotation_case)

        symmetric_case = self.get_symmetric_case(rotation_case)
        canonical_case = self.get_canonical_case(rotation_case)
        mirrored = self.is_mirrored(rotation_case)

        analysis = {
            "original_case": rotation_case,
            "symmetric_case": symmetric_case,
            "canonical_case": canonical_case,
            "mirrored": mirrored,
        }

        self.last_analysis = analysis

        return analysis

    # ---------------------------------------------------------
    # Canonical representation
    # ---------------------------------------------------------

    def get_canonical_representation(
        self,
        rotation_case: str
    ) -> Dict[str, Any]:
        """
        Return the compact representation used by later
        optimization modules.
        """
        analysis = self.analyze_case(rotation_case)

        return {
            "canonical_case": analysis["canonical_case"],
            "mirrored": analysis["mirrored"],
        }

    # ---------------------------------------------------------
    # Batch analysis
    # ---------------------------------------------------------

    def analyze_cases(
        self,
        rotation_cases: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple rotation cases.
        """
        if not isinstance(rotation_cases, list):
            raise TypeError("Rotation cases must be provided as a list.")

        return [
            self.analyze_case(rotation_case)
            for rotation_case in rotation_cases
        ]

    # ---------------------------------------------------------
    # Case classification
    # ---------------------------------------------------------

    def get_symmetry_class(self, rotation_case: str) -> str:
        """
        Return the canonical symmetry class.

        Returns:
            'single' for LL/RR family
            'double' for LR/RL family
        """
        canonical_case = self.get_canonical_case(rotation_case)

        if canonical_case == "LL":
            return "single"

        return "double"

    # ---------------------------------------------------------
    # Context integration
    # ---------------------------------------------------------

    def analyze_context(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze rotation-case information from ContextAnalyzer output.

        Expected context structure:

            context["rotation_cases"] = {
                "LL": ...,
                "RR": ...,
                "LR": ...,
                "RL": ...
            }

        Returns aggregated symmetry information.
        """
        if not isinstance(context, dict):
            raise TypeError("Context must be a dictionary.")

        rotation_cases = context.get("rotation_cases")

        if not isinstance(rotation_cases, dict):
            raise ValueError(
                "Context must contain a 'rotation_cases' dictionary."
            )

        ll_count = rotation_cases.get("LL", 0)
        rr_count = rotation_cases.get("RR", 0)
        lr_count = rotation_cases.get("LR", 0)
        rl_count = rotation_cases.get("RL", 0)

        canonical_ll_count = ll_count + rr_count
        canonical_lr_count = lr_count + rl_count

        total_cases = (
            ll_count
            + rr_count
            + lr_count
            + rl_count
        )

        if total_cases > 0:
            single_ratio = canonical_ll_count / total_cases
            double_ratio = canonical_lr_count / total_cases
        else:
            single_ratio = 0.0
            double_ratio = 0.0

        return {
            "original_cases": {
                "LL": ll_count,
                "RR": rr_count,
                "LR": lr_count,
                "RL": rl_count,
            },
            "canonical_cases": {
                "LL": canonical_ll_count,
                "LR": canonical_lr_count,
            },
            "symmetry_classes": {
                "single": canonical_ll_count,
                "double": canonical_lr_count,
            },
            "ratios": {
                "single_ratio": single_ratio,
                "double_ratio": double_ratio,
            },
            "total_cases": total_cases,
        }

    # ---------------------------------------------------------
    # Tree integration
    # ---------------------------------------------------------

    def analyze_tree(self, avl_tree) -> Dict[str, Any]:
        """
        Analyze symmetry information directly from an AVL tree.

        The tree is only read; it is never modified.
        """
        if avl_tree is None:
            raise ValueError("AVL tree cannot be None.")

        stats = avl_tree.get_statistics()

        context = {
            "rotation_cases": stats.get(
                "case_counts",
                {}
            )
        }

        return self.analyze_context(context)

    # ---------------------------------------------------------
    # Utility methods
    # ---------------------------------------------------------

    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Return the most recent single-case analysis.
        """
        return self.last_analysis

    def get_supported_cases(self) -> List[str]:
        """
        Return all supported AVL rotation cases.
        """
        return sorted(self.VALID_CASES)