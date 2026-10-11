/**
 * Authoritative TypeScript contracts matching FastAPI backend schemas exactly.
 */

export interface HealthResponse {
  status: string;
  service: string;
}

export interface PriceMetadata {
  source: string;
  source_updated_at?: string | null;
  source_updated_at_readable?: string | null;
  retrieved_at: string;
  exchange_rate_usd_inr?: number | null;
  market_note: string;
}

export interface PriceResponse {
  asset: string;
  symbol: string;
  currency: string;
  currency_symbol: string;
  price_per_troy_ounce: number;
  price_per_gram: number;
  price_per_10g: number;
  price_per_kg: number;
  formatted: string;
  metadata: PriceMetadata;
}

export interface DocumentChunk {
  content: string;
  source: string;
  page?: number | null;
  page_label: string;
  score?: number | null;
}

export interface DocumentSearchRequest {
  question: string;
  top_k?: number;
}

export interface DocumentSearchResponse {
  question: string;
  total_results: number;
  chunks: DocumentChunk[];
}

export interface DocumentStatusResponse {
  indexed: boolean;
  collection_name: string;
  total_chunks: number;
  available_documents: string[];
}

export interface AdvisorRequest {
  question: string;
}

export interface AdvisorSourceItem {
  title: string;
  source_file: string;
  page_label: string;
  snippet: string;
}

export interface AdvisorMarketItem {
  asset: string;
  symbol: string;
  price_per_gram: number;
  price_per_10g: number;
  currency: string;
  source: string;
}

export interface AdvisorResponse {
  answer: string;
  sources: AdvisorSourceItem[];
  market_data: AdvisorMarketItem[];
  model: string;
  request_id: string;
  disclaimer?: string;
}

export interface ApiError {
  error: string;
  status_code: number;
  message: string;
  details?: Record<string, unknown> | null;
  request_id?: string | null;
}
