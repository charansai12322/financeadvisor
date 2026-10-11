"use client";

import React, { useState, useEffect } from "react";
import { api, ApiClientError } from "@/lib/api";
import { DocumentChunk, DocumentStatusResponse } from "@/types/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  BookOpen,
  Search,
  FileText,
  AlertCircle,
  Database,
  ExternalLink,
  Layers,
  Sparkles,
} from "lucide-react";

interface KnowledgeSearchViewProps {
  initialQuery?: string;
  onClearInitialQuery?: () => void;
}

export function KnowledgeSearchView({
  initialQuery,
  onClearInitialQuery,
}: KnowledgeSearchViewProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<DocumentStatusResponse | null>(null);
  const [results, setResults] = useState<DocumentChunk[]>([]);
  const [searchedQuestion, setSearchedQuestion] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch vector store status on mount
  useEffect(() => {
    async function loadStatus() {
      try {
        const res = await api.getDocumentStatus();
        setStatus(res);
      } catch {
        // Status is diagnostic, non-fatal
      }
    }
    loadStatus();
  }, []);

  // Handle incoming query from props
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      handleSearch(initialQuery);
      onClearInitialQuery?.();
    }
  }, [initialQuery, onClearInitialQuery]);

  const handleSearch = async (overrideQuery?: string) => {
    const q = (overrideQuery || query).trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    setSearchedQuestion(q);

    try {
      const res = await api.searchDocuments(q, 4);
      setResults(res.chunks);
    } catch (err: unknown) {
      let msg = "Document search failed. Please verify backend Chroma service.";
      if (err instanceof ApiClientError) {
        msg = err.message;
      } else if (err instanceof Error) {
        msg = err.message;
      }
      setError(msg);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    "GST rate on gold and silver jewellery",
    "Articles of natural or cultured pearls, precious or semi-precious stones",
    "Difference between saving and investment in SEBI booklet",
    "Investor rights and grievance mechanism under SCORES",
    "What are the benefits of diversified mutual fund investments?",
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header & Status Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[rgba(17,23,19,0.06)]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-headline text-3xl md:text-4xl font-medium tracking-tight text-[#111713]">
              Regulatory Knowledge Vault
            </h1>
            <Badge variant="dark" icon={<Layers className="w-3 h-3 text-[#D8FF57]" />}>
              Chroma RAG
            </Badge>
          </div>
          <p className="text-xs text-[#858E83] mt-1.5 font-interface">
            Vector similarity retrieval across official Indian government GST tariff schedules and SEBI investor education booklets.
          </p>
        </div>

        {status && (
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#FFFEFA] border border-[rgba(17,23,19,0.08)] text-xs font-figures">
            <Database className="w-3.5 h-3.5 text-[#24483A]" />
            <span className="font-medium text-[#111713]">
              {status.total_chunks} Chunks Indexed
            </span>
          </div>
        )}
      </div>

      {/* Search Input Box */}
      <div className="ledger-card p-4 sm:p-5 rounded-2xl bg-[#FFFEFA]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#858E83] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search GST provisions, precious metal tariffs, SEBI investor guidance..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[rgba(17,23,19,0.15)] bg-[#F5F3EC] text-sm font-interface text-[#111713] placeholder:text-[#858E83] focus:outline-none focus:ring-1 focus:ring-[#111713]"
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            disabled={!query.trim() || loading}
            isLoading={loading}
            icon={<Search className="w-4 h-4" />}
          >
            Search Documents
          </Button>
        </form>

        {/* Suggestion Chips */}
        <div className="mt-4 pt-3 border-t border-[rgba(17,23,19,0.06)] flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold text-[#858E83] uppercase tracking-wider font-interface">
            Popular Topics:
          </span>
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="text-xs font-interface px-2.5 py-1 rounded-md bg-[#F5F3EC] hover:bg-[#EAE6DB] text-[#252B27] border border-[rgba(17,23,19,0.06)] transition-colors cursor-pointer"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 rounded-xl bg-[#FAECE8] border border-[#F1D4CD] text-[#B65F4A] flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div className="text-sm font-interface">
            <p className="font-semibold">Retrieval Error</p>
            <p className="text-xs mt-0.5 opacity-90">{error}</p>
          </div>
        </div>
      )}

      {/* Loading Skeletons */}
      {loading && (
        <div className="space-y-4">
          <Skeleton height="140px" width="100%" className="rounded-xl" />
          <Skeleton height="140px" width="100%" className="rounded-xl" />
        </div>
      )}

      {/* Search Results Display */}
      {!loading && searchedQuestion && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-interface text-[#858E83]">
            <span>
              Showing {results.length} relevant excerpt{results.length !== 1 ? "s" : ""} for &ldquo;{searchedQuestion}&rdquo;
            </span>
            <span className="font-figures">Vector Metric: Cosine</span>
          </div>

          {results.length === 0 ? (
            <div className="ledger-card p-8 rounded-xl text-center text-[#858E83] text-sm font-interface">
              No matching document passages found in indexed collections. Try broader terms or check spelling.
            </div>
          ) : (
            results.map((chunk, index) => (
              <div
                key={index}
                className="ledger-card p-6 rounded-xl space-y-3 hover:border-[rgba(17,23,19,0.2)] transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[rgba(17,23,19,0.06)]">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#24483A]" />
                    <span className="text-xs font-semibold text-[#111713] font-interface">
                      {chunk.source.replace(/_/g, " ").replace(".pdf", "")}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[11px] font-figures">
                      {chunk.page_label}
                    </Badge>
                    <span className="text-[10px] text-[#858E83] font-figures">
                      File: {chunk.source}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-[#252B27] leading-relaxed font-interface whitespace-pre-wrap bg-[#F5F3EC] p-4 rounded-lg border border-[rgba(17,23,19,0.04)]">
                  {chunk.content}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Document Library Index Summary */}
      {status && status.available_documents && (
        <div className="p-6 rounded-2xl bg-[#FFFEFA] border border-[rgba(17,23,19,0.06)] space-y-3">
          <h3 className="font-headline text-lg font-medium text-[#111713]">
            Knowledge Base Catalog
          </h3>
          <p className="text-xs text-[#858E83] font-interface">
            All documents below are persistently indexed in Chroma and cited during AI Advisory synthesis:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
            {status.available_documents.map((doc, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-[#F5F3EC] border border-[rgba(17,23,19,0.06)] flex items-center gap-3 text-xs font-interface"
              >
                <FileText className="w-4 h-4 text-[#24483A] shrink-0" />
                <div>
                  <p className="font-semibold text-[#111713]">{doc}</p>
                  <p className="text-[10px] text-[#858E83]">Central Board of Indirect Taxes & Customs / SEBI</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
