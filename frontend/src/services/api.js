const API_URL = "http://127.0.0.1:8000";

export async function generateDataset(workloadType, size, seed) {
  const response = await fetch(
    `${API_URL}/api/datasets/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workload_type: workloadType,
        size: Number(size),
        seed: seed === "" ? null : Number(seed),
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to generate dataset."
    );
  }

  return data;
}

export async function analyzeAVL(data) {
  if (!Array.isArray(data) || data.length === 0) {
    throw new Error("Dataset is empty.");
  }

  console.log("Calling AVL API with", data.length, "values");

  const response = await fetch(
    `${API_URL}/api/avl/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        data: data,
      }),
    }
  );

  const result = await response.json();

  console.log("Backend response:", result);

  if (!response.ok) {
    throw new Error(
      result.detail || "Failed to analyze AVL tree."
    );
  }

  return result;
}

export async function checkHealth() {
  const response = await fetch(
    `${API_URL}/api/health`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Backend is unavailable."
    );
  }

  return data;
}