"use client";

import React, { useState } from "react";
import { AppHeader, ActiveTab } from "@/components/layout/AppHeader";
import { MarketOverviewCard } from "@/components/dashboard/MarketOverviewCard";
import { QuickPromptCards } from "@/components/dashboard/QuickPromptCards";
import { AdvisorWorkspace } from "@/components/advisor/AdvisorWorkspace";
import { MarketDetailView } from "@/components/markets/MarketDetailView";
import { KnowledgeSearchView } from "@/components/knowledge/KnowledgeSearchView";
import { Compass, Sparkles, ShieldCheck, Scale, ArrowRight } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");
  const [advisorPrompt, setAdvisorPrompt] = useState<string | undefined>(undefined);
  const [knowledgeQuery, setKnowledgeQuery] = useState<string | undefined>(undefined);

  const handleSelectPrompt = (prompt: string, targetTab: "advisor" | "knowledge") => {
    if (targetTab === "advisor") {
      setAdvisorPrompt(prompt);
      setActiveTab("advisor");
    } else {
      setKnowledgeQuery(prompt);
      setActiveTab("knowledge");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F3EC]">
      {/* Universal Header with Navigation & Live Health Pulse */}
      <AppHeader activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-10 animate-fade-in">
            {/* Hero Editorial Welcome */}
            <div className="max-w-3xl space-y-4">
              <span className="text-xs font-semibold uppercase tracking-widest text-[#858E83] font-interface">
                Personal Finance Intelligence
              </span>
              <h1 className="font-headline text-4xl sm:text-5xl lg:text-6xl font-normal text-[#111713] tracking-tight leading-[1.15]">
                Precision bullion data. Grounded tax guidance.
              </h1>
              <p className="font-interface text-sm sm:text-base text-[#858E83] leading-relaxed max-w-2xl">
                A verified financial advisory workspace for Indian markets. Live spot Gold & Silver rates in INR, official CBIC GST schedules, and Gemini-orchestrated conversational intelligence.
              </p>

              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  onClick={() => setActiveTab("advisor")}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#111713] text-[#FFFEFA] hover:bg-[#252B27] text-xs font-interface font-medium transition-all shadow-sm cursor-pointer"
                >
                  <Compass className="w-3.5 h-3.5 text-[#D8FF57]" />
                  Ask Odysseus
                </button>
                <button
                  onClick={() => setActiveTab("knowledge")}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#FFFEFA] text-[#252B27] hover:bg-[#EAE6DB] border border-[rgba(17,23,19,0.12)] text-xs font-interface font-medium transition-all shadow-xs cursor-pointer"
                >
                  Explore Knowledge Vault
                  <ArrowRight className="w-3.5 h-3.5 text-[#858E83]" />
                </button>
              </div>
            </div>

            {/* Live Bullion Spot Cards */}
            <MarketOverviewCard onNavigateToMarkets={() => setActiveTab("markets")} />

            {/* Curated Inquiries & Quick Launchpads */}
            <QuickPromptCards onSelectPrompt={handleSelectPrompt} />
          </div>
        )}

        {/* AI ADVISOR TAB */}
        {activeTab === "advisor" && (
          <div className="animate-fade-in">
            <AdvisorWorkspace
              initialPrompt={advisorPrompt}
              onClearInitialPrompt={() => setAdvisorPrompt(undefined)}
            />
          </div>
        )}

        {/* BULLION MARKETS TAB */}
        {activeTab === "markets" && (
          <div className="animate-fade-in">
            <MarketDetailView />
          </div>
        )}

        {/* KNOWLEDGE SEARCH TAB */}
        {activeTab === "knowledge" && (
          <div className="animate-fade-in">
            <KnowledgeSearchView
              initialQuery={knowledgeQuery}
              onClearInitialQuery={() => setKnowledgeQuery(undefined)}
            />
          </div>
        )}
      </main>

      {/* Editorial Footer */}
      <footer className="border-t border-[rgba(17,23,19,0.08)] bg-[#FFFEFA] py-8 text-xs text-[#858E83]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-headline font-semibold text-[#111713] text-sm">
              Obsidian Ledger
            </span>
            <span className="text-[10px] uppercase tracking-wider font-figures">
              v1.0 Monorepo
            </span>
          </div>

          <p className="text-[11px] text-center font-interface">
            Strictly informational & educational. All bullion rates quoted in INR from public spot sources. Excludes retail making charges.
          </p>

          <div className="flex items-center gap-4 font-interface text-[11px]">
            <span>FastAPI Backend Live</span>
            <span className="w-1 h-1 rounded-full bg-[#858E83]" />
            <span>Vercel / Next.js 16</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
