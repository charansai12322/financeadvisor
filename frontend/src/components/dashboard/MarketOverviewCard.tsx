"use client";

import React, { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { PriceResponse } from "@/types/api";
import { formatINR, formatRelativeTime } from "@/lib/formatters";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { RefreshCw, AlertCircle, ArrowUpRight, Scale } from "lucide-react";

interface MarketOverviewCardProps {
  onNavigateToMarkets?: () => void;
}

export function MarketOverviewCard({ onNavigateToMarkets }: MarketOverviewCardProps) {
  const [gold, setGold] = useState<PriceResponse | null>(null);
  const [silver, setSilver] = useState<PriceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<string | null>(null);

  const fetchPrices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [goldRes, silverRes] = await Promise.all([
        api.getGoldPrice(),
        api.getSilverPrice(),
      ]);
      setGold(goldRes);
      setSilver(silverRes);
      setLastRefreshed(new Date().toISOString());
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch live bullion prices from Gold-API backend service."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrices();
    const timer = setInterval(fetchPrices, 60000);
    return () => clearInterval(timer);
  }, [fetchPrices]);

  return (
    <div className="ledger-card rounded-xl p-6 md:p-8">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[rgba(17,23,19,0.06)]">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="font-headline text-2xl md:text-3xl font-medium tracking-tight text-[#111713]">
              Bullion Spot Market
            </h2>
            <Badge variant="success" icon={<span className="w-1.5 h-1.5 rounded-full bg-[#24483A]" />}>
              Live Spot
            </Badge>
          </div>
          <p className="text-xs text-[#858E83] mt-1 font-interface">
            Real-time wholesale market spot rates in Indian Rupees (INR) via Gold-API.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-figures text-[#858E83]">
            {lastRefreshed ? `Updated ${formatRelativeTime(lastRefreshed)}` : "Fetching..."}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchPrices}
            isLoading={loading}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <div className="mt-6 p-4 rounded-lg bg-[#FAECE8] border border-[#F1D4CD] text-[#B65F4A] flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold font-interface">Market Data Temporarily Unavailable</p>
            <p className="text-xs opacity-90 mt-0.5 font-interface">{error}</p>
            <button
              onClick={fetchPrices}
              className="mt-2 text-xs font-semibold underline underline-offset-2 hover:opacity-80"
            >
              Try reconnecting
            </button>
          </div>
        </div>
      )}

      {/* Grid of Commodity Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {/* GOLD CARD */}
        <div className="p-5 rounded-lg bg-[#F5F3EC] border border-[rgba(17,23,19,0.06)] flex flex-col justify-between hover:border-[rgba(17,23,19,0.15)] transition-all">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#858E83] font-interface">
                Gold Bullion (XAU)
              </span>
              <span className="text-xs font-figures text-[#858E83]">999 Pure (24 Karat)</span>
            </div>

            {loading && !gold ? (
              <div className="space-y-3 mt-4">
                <Skeleton height="36px" width="60%" />
                <Skeleton height="16px" width="80%" />
              </div>
            ) : gold ? (
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="font-figures text-3xl sm:text-4xl font-semibold text-[#111713] tracking-tight">
                    {formatINR(gold.price_per_10g)}
                  </span>
                  <span className="text-xs font-figures text-[#858E83]">/ 10 grams</span>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-[rgba(17,23,19,0.08)]">
                  <div>
                    <span className="text-[11px] text-[#858E83] font-interface block">Per 1 Gram</span>
                    <span className="font-figures text-sm font-medium text-[#252B27]">
                      {formatINR(gold.price_per_gram)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-[#858E83] font-interface block">Per Troy Ounce</span>
                    <span className="font-figures text-sm font-medium text-[#252B27]">
                      {formatINR(gold.price_per_troy_ounce)}
                    </span>
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <div className="mt-4 pt-3 flex items-center justify-between text-xs text-[#858E83]">
            <span className="flex items-center gap-1 font-figures text-[11px]">
              <Scale className="w-3 h-3" /> Excl. 3% GST & Making Charges
            </span>
          </div>
        </div>

        {/* SILVER CARD */}
        <div className="p-5 rounded-lg bg-[#F5F3EC] border border-[rgba(17,23,19,0.06)] flex flex-col justify-between hover:border-[rgba(17,23,19,0.15)] transition-all">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#858E83] font-interface">
                Silver Bullion (XAG)
              </span>
              <span className="text-xs font-figures text-[#858E83]">999 Pure Grade</span>
            </div>

            {loading && !silver ? (
              <div className="space-y-3 mt-4">
                <Skeleton height="36px" width="60%" />
                <Skeleton height="16px" width="80%" />
              </div>
            ) : silver ? (
              <div className="mt-3">
                <div className="flex items-baseline gap-2">
                  <span className="font-figures text-3xl sm:text-4xl font-semibold text-[#111713] tracking-tight">
                    {formatINR(silver.price_per_10g)}
                  </span>
                  <span className="text-xs font-figures text-[#858E83]">/ 10 grams</span>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-[rgba(17,23,19,0.08)]">
                  <div>
                    <span className="text-[11px] text-[#858E83] font-interface block">Per 1 Gram</span>
                    <span className="font-figures text-sm font-medium text-[#252B27]">
                      {formatINR(silver.price_per_gram)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-[#858E83] font-interface block">Per 1 Kilogram</span>
                    <span className="font-figures text-sm font-medium text-[#252B27]">
                      {formatINR(silver.price_per_kg)}
                    </span>
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <div className="mt-4 pt-3 flex items-center justify-between text-xs text-[#858E83]">
            <span className="flex items-center gap-1 font-figures text-[11px]">
              <Scale className="w-3 h-3" /> Excl. 3% GST & Making Charges
            </span>
          </div>
        </div>
      </div>

      {/* Footer Navigation Link */}
      {onNavigateToMarkets && (
        <div className="mt-6 pt-4 border-t border-[rgba(17,23,19,0.06)] flex justify-end">
          <button
            onClick={onNavigateToMarkets}
            className="inline-flex items-center gap-1.5 text-xs font-interface font-medium text-[#111713] hover:text-[#24483A] transition-colors cursor-pointer group"
          >
            <span>View Full Bullion Conversion & Tariff Breakdown</span>
            <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </button>
        </div>
      )}
    </div>
  );
}
