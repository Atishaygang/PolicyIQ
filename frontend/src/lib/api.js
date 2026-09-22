const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class PolicyIQApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "PolicyIQApiError";
    this.status = status;
  }
}

async function request(path, options = {}, timeoutMs = 180000) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    if (!response.ok) {
      const message =
        payload?.detail ||
        payload?.message ||
        `PolicyIQ returned an error (${response.status}).`;
      throw new PolicyIQApiError(message, response.status);
    }

    return payload;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new PolicyIQApiError(
        "The request took longer than expected. Please try again.",
        408
      );
    }

    if (error instanceof PolicyIQApiError) throw error;

    throw new PolicyIQApiError(
      "PolicyIQ could not be reached. Make sure the backend is running.",
      0
    );
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function checkPolicyIQStatus() {
  const health = await request("/health", {}, 10000);
  const ready = await request("/ready", {}, 10000);

  return {
    running: health?.status === "running",
    ready: Boolean(ready?.ready),
    version: health?.version || "—",
  };
}

export async function askPolicyIQ(question) {
  return request("/api/v1/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
