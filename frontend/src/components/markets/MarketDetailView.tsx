"use client";

import React, { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { PriceResponse } from "@/types/api";
import { formatINR, formatDateTime, formatRelativeTime } from "@/lib/formatters";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  TrendingUp,
  RefreshCw,
  Scale,
  Calculator,
  Info,
  Clock,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";

export function MarketDetailView() {
  const [gold, setGold] = useState<PriceResponse | null>(null);
  const [silver, setSilver] = useState<PriceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState<string | null>(null);

  // Bullion Calculator state
  const [calcAsset, setCalcAsset] = useState<"gold" | "silver">("gold");
  const [calcGrams, setCalcGrams] = useState<number>(10);
  const [includeGst, setIncludeGst] = useState<boolean>(true);

  const fetchMarkets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [goldRes, silverRes] = await Promise.all([
        api.getGoldPrice(),
        api.getSilverPrice(),
      ]);
      setGold(goldRes);
      setSilver(silverRes);
      setLastFetchTime(new Date().toISOString());
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load live commodity spot rates from upstream."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMarkets();
  }, [fetchMarkets]);

  // Calculator calculations
  const activePricePerGram =
    calcAsset === "gold" ? gold?.price_per_gram || 0 : silver?.price_per_gram || 0;
  const subtotalValue = activePricePerGram * (calcGrams || 0);
  const gstValue = includeGst ? subtotalValue * 0.03 : 0;
  const totalValue = subtotalValue + gstValue;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Page Title & Status Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[rgba(17,23,19,0.06)]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-headline text-3xl md:text-4xl font-medium tracking-tight text-[#111713]">
              Bullion Spot Rates & Conversion
            </h1>
            <Badge variant="success">Wholesale Spot</Badge>
          </div>
          <p className="text-xs text-[#858E83] mt-1.5 font-interface">
            Real-time precious metal spot benchmarks for Indian markets, quoted in Indian Rupees (INR) per bullion standard divisors.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-figures text-[#858E83] flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {lastFetchTime ? `Fetched ${formatRelativeTime(lastFetchTime)}` : "Connecting..."}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchMarkets}
            isLoading={loading}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh Rates
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 rounded-xl bg-[#FAECE8] border border-[#F1D4CD] text-[#B65F4A]">
          <p className="text-sm font-semibold">Unable to fetch bullion prices</p>
          <p className="text-xs mt-1">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchMarkets} className="mt-3 text-xs">
            Retry Connection
          </Button>
        </div>
      )}

      {/* Main Bullion Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* GOLD SECTION */}
        <div className="ledger-card p-6 sm:p-7 rounded-2xl flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[rgba(17,23,19,0.06)]">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-[#858E83] font-interface">
                  Commodity Benchmark
                </span>
                <h2 className="font-headline text-2xl font-semibold text-[#111713] mt-0.5">
                  Gold Bullion (XAU / INR)
                </h2>
              </div>
              <Badge variant="dark" className="font-figures text-xs">
                24K 999 Purity
              </Badge>
            </div>

            {loading && !gold ? (
              <div className="space-y-4 py-6">
                <Skeleton height="40px" width="70%" />
                <Skeleton height="100px" width="100%" />
              </div>
            ) : gold ? (
              <div className="space-y-6 pt-4">
                {/* Hero 10g Price */}
                <div>
                  <span className="text-xs text-[#858E83] font-interface block">
                    Indian Benchmark Rate (10 Grams / 1 Tola)
                  </span>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="font-figures text-4xl sm:text-5xl font-semibold text-[#111713] tracking-tight">
                      {formatINR(gold.price_per_10g)}
                    </span>
                    <span className="text-xs font-figures text-[#858E83]">/ 10g</span>
                  </div>
                </div>

                {/* Table of Units */}
                <div className="rounded-xl overflow-hidden border border-[rgba(17,23,19,0.08)] bg-[#F5F3EC]">
                  <table className="w-full text-xs font-interface">
                    <thead className="border-b border-[rgba(17,23,19,0.08)] bg-[rgba(17,23,19,0.04)] text-[#858E83] font-semibold">
                      <tr>
                        <th className="py-2.5 px-3 text-left">Unit Denomination</th>
                        <th className="py-2.5 px-3 text-right">Spot Price (INR)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[rgba(17,23,19,0.06)] font-figures text-[#252B27]">
                      <tr>
                        <td className="py-2.5 px-3">Per 1 Gram</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(gold.price_per_gram)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per 10 Grams</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(gold.price_per_10g)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per 1 Kilogram (1,000g)</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(gold.price_per_kg)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per Troy Ounce (31.1035g)</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(gold.price_per_troy_ounce)}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Metadata details */}
                <div className="text-[11px] text-[#858E83] space-y-1 font-figures">
                  <p>Provider: {gold.metadata.source} API</p>
                  <p>Upstream Updated: {formatDateTime(gold.metadata.source_updated_at)}</p>
                  <p className="italic font-interface text-[11px] text-[#252B27] mt-2">
                    {gold.metadata.market_note}
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* SILVER SECTION */}
        <div className="ledger-card p-6 sm:p-7 rounded-2xl flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[rgba(17,23,19,0.06)]">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-[#858E83] font-interface">
                  Commodity Benchmark
                </span>
                <h2 className="font-headline text-2xl font-semibold text-[#111713] mt-0.5">
                  Silver Bullion (XAG / INR)
                </h2>
              </div>
              <Badge variant="dark" className="font-figures text-xs">
                999 Fine Grade
              </Badge>
            </div>

            {loading && !silver ? (
              <div className="space-y-4 py-6">
                <Skeleton height="40px" width="70%" />
                <Skeleton height="100px" width="100%" />
              </div>
            ) : silver ? (
              <div className="space-y-6 pt-4">
                {/* Hero 1kg & 10g Price */}
                <div>
                  <span className="text-xs text-[#858E83] font-interface block">
                    Indian Benchmark Rate (Per 1 Kilogram)
                  </span>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="font-figures text-4xl sm:text-5xl font-semibold text-[#111713] tracking-tight">
                      {formatINR(silver.price_per_kg)}
                    </span>
                    <span className="text-xs font-figures text-[#858E83]">/ 1 kg</span>
                  </div>
                </div>

                {/* Table of Units */}
                <div className="rounded-xl overflow-hidden border border-[rgba(17,23,19,0.08)] bg-[#F5F3EC]">
                  <table className="w-full text-xs font-interface">
                    <thead className="border-b border-[rgba(17,23,19,0.08)] bg-[rgba(17,23,19,0.04)] text-[#858E83] font-semibold">
                      <tr>
                        <th className="py-2.5 px-3 text-left">Unit Denomination</th>
                        <th className="py-2.5 px-3 text-right">Spot Price (INR)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[rgba(17,23,19,0.06)] font-figures text-[#252B27]">
                      <tr>
                        <td className="py-2.5 px-3">Per 1 Gram</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(silver.price_per_gram)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per 10 Grams</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(silver.price_per_10g)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per 1 Kilogram (1,000g)</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(silver.price_per_kg)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2.5 px-3">Per Troy Ounce (31.1035g)</td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatINR(silver.price_per_troy_ounce)}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Metadata details */}
                <div className="text-[11px] text-[#858E83] space-y-1 font-figures">
                  <p>Provider: {silver.metadata.source} API</p>
                  <p>Upstream Updated: {formatDateTime(silver.metadata.source_updated_at)}</p>
                  <p className="italic font-interface text-[11px] text-[#252B27] mt-2">
                    {silver.metadata.market_note}
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* INTERACTIVE BULLION VALUATION & GST CALCULATOR */}
      <div className="ledger-card p-6 sm:p-8 rounded-2xl bg-[#FFFEFA]">
        <div className="flex items-center gap-2.5 pb-4 border-b border-[rgba(17,23,19,0.06)]">
          <Calculator className="w-5 h-5 text-[#24483A]" />
          <div>
            <h3 className="font-headline text-xl font-medium text-[#111713]">
              Bullion Spot Valuation & GST Estimator
            </h3>
            <p className="text-xs text-[#858E83] font-interface">
              Calculate the theoretical raw bullion value and 3% Goods and Services Tax (GST) for any custom weight.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          {/* Controls */}
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-[#858E83] uppercase tracking-wider font-interface block mb-1.5">
                Select Metal
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setCalcAsset("gold")}
                  className={`py-2 px-3 rounded-lg text-xs font-interface font-medium border transition-colors cursor-pointer ${
                    calcAsset === "gold"
                      ? "bg-[#111713] text-[#FFFEFA] border-[#111713]"
                      : "bg-[#F5F3EC] text-[#252B27] border-[rgba(17,23,19,0.08)] hover:bg-[#EAE6DB]"
                  }`}
                >
                  Gold (24K)
                </button>
                <button
                  type="button"
                  onClick={() => setCalcAsset("silver")}
                  className={`py-2 px-3 rounded-lg text-xs font-interface font-medium border transition-colors cursor-pointer ${
                    calcAsset === "silver"
                      ? "bg-[#111713] text-[#FFFEFA] border-[#111713]"
                      : "bg-[#F5F3EC] text-[#252B27] border-[rgba(17,23,19,0.08)] hover:bg-[#EAE6DB]"
                  }`}
                >
                  Silver (999)
                </button>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-[#858E83] uppercase tracking-wider font-interface block mb-1.5">
                Weight in Grams
              </label>
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={calcGrams}
                onChange={(e) => setCalcGrams(parseFloat(e.target.value) || 0)}
                className="w-full p-2.5 rounded-lg border border-[rgba(17,23,19,0.15)] bg-[#F5F3EC] text-sm font-figures text-[#111713] focus:outline-none focus:ring-1 focus:ring-[#111713]"
              />
            </div>

            <div className="flex items-center gap-2 pt-2">
              <input
                type="checkbox"
                id="includeGst"
                checked={includeGst}
                onChange={(e) => setIncludeGst(e.target.checked)}
                className="w-4 h-4 rounded text-[#111713] accent-[#111713] cursor-pointer"
              />
              <label htmlFor="includeGst" className="text-xs font-interface text-[#252B27] cursor-pointer">
                Include 3% Bullion GST (CGST 1.5% + SGST 1.5%)
              </label>
            </div>
          </div>

          {/* Results Summary Box */}
          <div className="md:col-span-2 p-6 rounded-xl bg-[#F5F3EC] border border-[rgba(17,23,19,0.08)] flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-interface text-[#858E83] pb-2 border-b border-[rgba(17,23,19,0.08)]">
                <span>Spot Price Applied:</span>
                <span className="font-figures font-medium text-[#111713]">
                  {formatINR(activePricePerGram)} / gram
                </span>
              </div>

              <div className="flex items-center justify-between text-xs font-interface text-[#858E83]">
                <span>Pure Metal Spot Value ({calcGrams}g):</span>
                <span className="font-figures font-medium text-[#111713]">
                  {formatINR(subtotalValue)}
                </span>
              </div>

              {includeGst && (
                <div className="flex items-center justify-between text-xs font-interface text-[#858E83]">
                  <span>GST Payable (3% Tariff Schedule):</span>
                  <span className="font-figures font-medium text-[#B65F4A]">
                    +{formatINR(gstValue)}
                  </span>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-[rgba(17,23,19,0.12)] mt-4">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#858E83] block font-interface">
                Estimated Theoretical Landed Value
              </span>
              <div className="font-figures text-3xl font-semibold text-[#24483A] mt-1">
                {formatINR(totalValue)}
              </div>
              <p className="text-[10px] text-[#858E83] mt-2 font-interface">
                * Note: Retail jewellery incurs additional jeweller making charges (typically 8% - 25%) and 18% GST on making charge craftsmanship.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
