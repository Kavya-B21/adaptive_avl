import { useState } from "react";
import { generateDataset } from "../services/api";

export default function DatasetControls({ onDatasetGenerated }) {
  const [workloadType, setWorkloadType] = useState("random");
  const [size, setSize] = useState(100);
  const [seed, setSeed] = useState(42);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError("");

      console.log("Generating dataset...");
      console.log({
        workloadType,
        size,
        seed,
      });

      const result = await generateDataset(
        workloadType,
        size,
        seed
      );

      console.log("Dataset generated:", result);

      if (!result || !result.data) {
        throw new Error("Backend returned an invalid dataset.");
      }

      onDatasetGenerated(result);
    } catch (err) {
      console.error("Dataset generation failed:", err);

      setError(
        err.message || "Failed to generate dataset."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="dataset-controls">
      <h2>Dataset Configuration</h2>

      <div className="controls-grid">

        <div className="control-group">
          <label htmlFor="workload">
            Workload Type
          </label>

          <select
            id="workload"
            value={workloadType}
            onChange={(e) =>
              setWorkloadType(e.target.value)
            }
          >
            <option value="random">Random</option>
            <option value="ascending">Ascending</option>
            <option value="descending">Descending</option>
            <option value="alternating">Alternating</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="size">
            Dataset Size
          </label>

          <input
            id="size"
            type="number"
            min="1"
            max="100000"
            value={size}
            onChange={(e) =>
              setSize(e.target.value)
            }
          />
        </div>

        <div className="control-group">
          <label htmlFor="seed">
            Seed
          </label>

          <input
            id="seed"
            type="number"
            value={seed}
            onChange={(e) =>
              setSeed(e.target.value)
            }
          />
        </div>

      </div>

      {error && (
        <div className="error-message">
          <strong>Generation Error:</strong>{" "}
          {error}
        </div>
      )}

      <button
        type="button"
        className="generate-button"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading
          ? "Generating..."
          : "Generate Dataset"}
      </button>
    </section>
  );
}