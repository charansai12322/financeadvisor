/**
 * Type-safe API client for Finance Advisor FastAPI backend.
 * Uses native fetch with timeout support and structured error parsing.
 */
import {
  AdvisorRequest,
  AdvisorResponse,
  ApiError,
  DocumentSearchRequest,
  DocumentSearchResponse,
  DocumentStatusResponse,
  HealthResponse,
  PriceResponse,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = 30000;
const ADVISOR_TIMEOUT_MS = 60000;

class ApiClientError extends Error {
  statusCode: number;
  errorCategory: string;
  requestId?: string | null;
  details?: Record<string, unknown> | null;

  constructor(apiError: ApiError) {
    super(apiError.message);
    this.name = "ApiClientError";
    this.statusCode = apiError.status_code;
    this.errorCategory = apiError.error;
    this.requestId = apiError.request_id;
    this.details = apiError.details;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let errorPayload: ApiError;
      try {
        const json = await response.json();
        errorPayload = {
          error: json.error || `HTTP_${response.status}`,
          status_code: json.status_code || response.status,
          message: json.message || response.statusText || "Request failed",
          details: json.details || null,
          request_id: json.request_id || null,
        };
      } catch {
        errorPayload = {
          error: `HTTP_${response.status}`,
          status_code: response.status,
          message: `Server returned HTTP ${response.status}: ${response.statusText}`,
          details: null,
          request_id: null,
        };
      }
      throw new ApiClientError(errorPayload);
    }

    return (await response.json()) as T;
  } catch (error: unknown) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiClientError({
        error: "TIMEOUT",
        status_code: 504,
        message: `Request to ${path} timed out after ${Math.round(timeoutMs / 1000)} seconds.`,
      });
    }
    const message =
      error instanceof Error
        ? error.message
        : "Failed to connect to Finance Advisor backend. Ensure the server is running.";
    throw new ApiClientError({
      error: "NETWORK_ERROR",
      status_code: 0,
      message,
    });
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  /**
   * Health status check endpoint
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health", { method: "GET" }, 5000);
  },

  /**
   * Live spot Gold (XAU) price in INR
   */
  async getGoldPrice(): Promise<PriceResponse> {
    return request<PriceResponse>("/api/v1/prices/gold", { method: "GET" }, 15000);
  },

  /**
   * Live spot Silver (XAG) price in INR
   */
  async getSilverPrice(): Promise<PriceResponse> {
    return request<PriceResponse>("/api/v1/prices/silver", { method: "GET" }, 15000);
  },

  /**
   * Knowledge base vector collection ingestion status
   */
  async getDocumentStatus(): Promise<DocumentStatusResponse> {
    return request<DocumentStatusResponse>("/api/v1/documents/status", { method: "GET" }, 10000);
  },

  /**
   * Vector similarity document search across GST and financial booklets
   */
  async searchDocuments(question: string, top_k = 3): Promise<DocumentSearchResponse> {
    const payload: DocumentSearchRequest = { question, top_k };
    return request<DocumentSearchResponse>(
      "/api/v1/documents/search",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      15000
    );
  },

  /**
   * Gemini-orchestrated financial advisory with grounding
   */
  async askAdvisor(question: string): Promise<AdvisorResponse> {
    const payload: AdvisorRequest = { question };
    return request<AdvisorResponse>(
      "/api/v1/advisor/ask",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      ADVISOR_TIMEOUT_MS
    );
  },
};

export { ApiClientError };
