export default function DatasetPreview({ dataset }) {
  if (!dataset || !Array.isArray(dataset.data)) {
    return null;
  }

  const preview = dataset.data.slice(0, 50);

  return (
    <section className="dataset-preview">
      <h2>Dataset Preview</h2>

      <div className="dataset-values">
        {preview.map((value, index) => (
          <span
            className="dataset-value"
            key={`${value}-${index}`}
          >
            {value}
          </span>
        ))}
      </div>

      <p className="dataset-preview-note">
        Showing first {preview.length} of{" "}
        {dataset.data.length} values.
      </p>
    </section>
  );
}