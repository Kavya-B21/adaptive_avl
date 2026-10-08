from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.modules.dataset_manager import DatasetManager
from backend.modules.avl_tree import AVLTree
from backend.modules.context_analyzer import ContextAnalyzer
from backend.modules.symmetry_analyzer import SymmetryAnalyzer
from backend.modules.canonical_representation import CanonicalRepresentation


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Adaptive AVL Optimizer API",
    version="1.0.0",
    description=(
        "Backend API for symmetry-aware evolutionary "
        "optimization of AVL trees."
    ),
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Module instances
# ---------------------------------------------------------

dataset_manager = DatasetManager()

context_analyzer = ContextAnalyzer()

symmetry_analyzer = SymmetryAnalyzer()

canonical_representation = CanonicalRepresentation(
    context_analyzer=context_analyzer,
    symmetry_analyzer=symmetry_analyzer,
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class DatasetRequest(BaseModel):
    workload_type: str
    size: int = Field(gt=0, le=100000)
    seed: int | None = None


class AVLAnalysisRequest(BaseModel):
    data: list[int]


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Adaptive AVL Optimizer API",
        "phase": "Phase 1",
    }


# ---------------------------------------------------------
# Dataset endpoints
# ---------------------------------------------------------

@app.get("/api/datasets/workload-types")
def get_workload_types():
    return {
        "success": True,
        "workload_types": [
            "random",
            "ascending",
            "descending",
            "alternating",
        ],
    }


@app.post("/api/datasets/generate")
def generate_dataset(request: DatasetRequest):
    try:
        data = dataset_manager.generate(
            workload_type=request.workload_type,
            size=request.size,
            seed=request.seed,
        )

        statistics = dataset_manager.get_statistics(data)

        return {
            "success": True,
            "metadata": {
                "workload_type": request.workload_type,
                "size": request.size,
                "seed": request.seed,
            },
            "statistics": statistics,
            "data": data,
        }

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ---------------------------------------------------------
# AVL analysis endpoint
# ---------------------------------------------------------

@app.post("/api/avl/analyze")
def analyze_avl(request: AVLAnalysisRequest):
    if not request.data:
        raise HTTPException(
            status_code=400,
            detail="Dataset cannot be empty.",
        )

    try:
        # Build a fresh AVL tree from the supplied dataset.
        tree = AVLTree()

        for value in request.data:
            tree.insert(value)

        # AVL statistics.
        avl_stats = tree.get_statistics()

        # Context analysis.
        context = context_analyzer.analyze(tree)

        # Symmetry analysis.
        symmetry = symmetry_analyzer.analyze_tree(tree)

        # Canonical representation.
        canonical = canonical_representation.analyze(tree)

        # Final correctness check.
        is_valid_avl = tree.validate_avl()

        return {
            "success": True,
            "avl": avl_stats,
            "valid_avl": is_valid_avl,
            "context": context,
            "symmetry": symmetry,
            "canonical": canonical,
        }

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Adaptive AVL Optimizer API",
        "status": "running",
        "docs": "/docs",
    }