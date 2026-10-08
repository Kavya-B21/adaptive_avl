import { useState } from "react";
import "./App.css";

import DatasetControls from "./components/DatasetControls";
import DatasetSummary from "./components/DatasetSummary";
import DatasetPreview from "./components/DatasetPreview";
import AVLAnalysis from "./components/AVLAnalysis";

import { analyzeAVL } from "./services/api";

function App() {
  const [dataset, setDataset] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleDatasetGenerated = (result) => {
    console.log("Received dataset:", result);

    setDataset(result);
    setAnalysis(null);
    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleAnalyze = async () => {
    if (!dataset || !dataset.data) {
      setError("Please generate a dataset first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      console.log(
        "Analyzing dataset:",
        dataset.data.length,
        "values"
      );

      const result = await analyzeAVL(
        dataset.data
      );

      console.log(
        "AVL analysis result:",
        result
      );

      setAnalysis(result);

      setTimeout(() => {
        document
          .getElementById("avl-analysis")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 100);

    } catch (err) {
      console.error(
        "AVL analysis failed:",
        err
      );

      setError(
        err.message ||
          "Failed to analyze AVL tree."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      <header className="app-header">
        <h1>
          Adaptive AVL Optimizer
        </h1>

        <p>
          Symmetry-Aware Evolutionary Optimization
          of AVL Trees
        </p>
      </header>

      <main className="app-container">

        <DatasetControls
          onDatasetGenerated={
            handleDatasetGenerated
          }
        />

        {error && (
          <div className="error-message">
            <strong>Error:</strong>{" "}
            {error}
          </div>
        )}

        {dataset && (
          <>
            <DatasetSummary
              dataset={dataset}
            />

            <DatasetPreview
              dataset={dataset}
            />

            <div className="analyze-container">

              <button
                type="button"
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze AVL Tree"}
              </button>

            </div>
          </>
        )}

        {analysis && (
          <div id="avl-analysis">
            <AVLAnalysis
              analysis={analysis}
            />
          </div>
        )}

      </main>
    </div>
  );
}

export default App;