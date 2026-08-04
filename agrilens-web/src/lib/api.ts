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
  user_id: number | null;
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

export interface UserResponse {
  id: number;
  username: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  username: string;
  role: string;
}

export interface SettingResponse {
  key: string;
  value: string;
}

/**
 * Get authorization header from localStorage if running in browser
 */
function getAuthHeaders(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("agrilens_token");
    if (token) {
      return { "Authorization": `Bearer ${token}` };
    }
  }
  return {};
}

/**
 * Register a new user account
 */
export async function registerUser(username: string, password: string): Promise<UserResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Registrasi gagal" }));
    throw new Error(err.detail || "Registrasi gagal");
  }

  return response.json();
}

/**
 * Authenticate user and save token info
 */
export async function loginUser(username: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Nama pengguna atau kata sandi salah" }));
    throw new Error(err.detail || "Login gagal");
  }

  const data: TokenResponse = await response.json();
  if (typeof window !== "undefined") {
    localStorage.setItem("agrilens_token", data.access_token);
    localStorage.setItem("agrilens_username", data.username);
    localStorage.setItem("agrilens_role", data.role);
  }
  return data;
}

/**
 * Logout and clear local session info
 */
export function logoutUser(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("agrilens_token");
    localStorage.removeItem("agrilens_username");
    localStorage.removeItem("agrilens_role");
  }
}

/**
 * Get active logged-in user profile
 */
export async function getMe(): Promise<UserResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/me`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      ...getAuthHeaders(),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Gagal mengambil profil pengguna");
  }

  return response.json();
}

/**
 * Get list of all registered users (Admin only)
 */
export async function getAllUsers(): Promise<UserResponse[]> {
  const response = await fetch(`${API_URL}/api/v1/users`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      ...getAuthHeaders(),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Gagal mengambil daftar pengguna");
  }

  return response.json();
}

/**
 * Delete a specific user account (Admin only)
 */
export async function deleteUser(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/users/${id}`, {
    method: "DELETE",
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Gagal menghapus pengguna" }));
    throw new Error(err.detail || "Gagal menghapus pengguna");
  }
}

/**
 * Upload image and predict disease.
 */
export async function detectDisease(file: File): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/api/v1/detect`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
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
      ...getAuthHeaders(),
    },
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
      ...getAuthHeaders(),
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
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    throw new Error("Failed to delete history record");
  }
}

/**
 * Fetch an application setting by key.
 */
export async function getSetting(key: string): Promise<SettingResponse> {
  const response = await fetch(`${API_URL}/api/v1/settings/${key}`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      ...getAuthHeaders(),
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
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ value }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update setting: ${key}`);
  }

  return response.json();
}
