export default function DatasetSummary({ dataset }) {
  if (!dataset || !Array.isArray(dataset.data)) {
    return null;
  }

  const data = dataset.data;

  const size = data.length;

  const minimum =
    data.length > 0
      ? Math.min(...data)
      : "-";

  const maximum =
    data.length > 0
      ? Math.max(...data)
      : "-";

  const uniqueValues =
    new Set(data).size;

  return (
    <section className="dataset-summary">
      <h2>Dataset Summary</h2>

      <div className="summary-grid">

        <div className="summary-card">
          <span className="summary-label">
            Size
          </span>

          <strong className="summary-value">
            {size}
          </strong>
        </div>

        <div className="summary-card">
          <span className="summary-label">
            Minimum
          </span>

          <strong className="summary-value">
            {minimum}
          </strong>
        </div>

        <div className="summary-card">
          <span className="summary-label">
            Maximum
          </span>

          <strong className="summary-value">
            {maximum}
          </strong>
        </div>

        <div className="summary-card">
          <span className="summary-label">
            Unique Values
          </span>

          <strong className="summary-value">
            {uniqueValues}
          </strong>
        </div>

      </div>
    </section>
  );
}