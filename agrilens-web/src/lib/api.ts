const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DetectionResponse {
  disease: string;
  confidence: number;
  inference_time_ms: number;
  thinking: string | null;
  explanation: string | null;
  recommendation: string | null;
  severity: string | null;
  metadata: {
    model_name: string;
    num_classes: number;
    input_size: number[];
  } | null;
}

export interface HistoryItem {
  id: string;
  filename: string;
  image_path: string;
  disease: string;
  confidence: number;
  inference_time_ms: number;
  severity: string | null;
  created_at: string;
}

export interface HistoryDetail extends HistoryItem {
  thinking: string | null;
  explanation: string | null;
  recommendation: string | null;
}

export interface HistoryListResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  size: number;
}

/**
 * Upload image and predict disease.
 */
export async function detectDisease(file: File): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/v1/detect`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Inference failed" }));
    throw new Error(err.detail || "Inference failed");
  }

  return response.json();
}

/**
 * Fetch paginated history log items.
 */
export async function getHistory(page: number = 1, size: number = 10): Promise<HistoryListResponse> {
  const response = await fetch(`${API_URL}/api/v1/history?page=${page}&size=${size}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
    // Prevent Next.js from caching list responses permanently
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }

  return response.json();
}

/**
 * Fetch detail of a past diagnosis log.
 */
export async function getHistoryDetail(id: string): Promise<HistoryDetail> {
  const response = await fetch(`${API_URL}/api/v1/history/${id}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch history detail");
  }

  return response.json();
}

/**
 * Delete a specific history log record.
 */
export async function deleteHistory(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/history/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete history record");
  }
}

export interface SettingResponse {
  key: string;
  value: string;
}

/**
 * Fetch an application setting by key.
 */
export async function getSetting(key: string): Promise<SettingResponse> {
  const response = await fetch(`${API_URL}/api/v1/settings/${key}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch setting: ${key}`);
  }

  return response.json();
}

/**
 * Update an application setting by key.
 */
export async function updateSetting(key: string, value: string): Promise<SettingResponse> {
  const response = await fetch(`${API_URL}/api/v1/settings/${key}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ value }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update setting: ${key}`);
  }

  return response.json();
}
