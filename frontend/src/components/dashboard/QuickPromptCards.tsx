"use client";

import React from "react";
import { Sparkles, ArrowRight, ShieldCheck, Scale, PiggyBank, FileText } from "lucide-react";

interface QuickPromptCardsProps {
  onSelectPrompt: (prompt: string, tab: "advisor" | "knowledge") => void;
}

export function QuickPromptCards({ onSelectPrompt }: QuickPromptCardsProps) {
  const prompts = [
    {
      title: "Gold Jewellery GST & Making Charges",
      category: "Taxation & Tariffs",
      query: "What is the total GST applicable when purchasing 22-karat gold jewellery in India, and how does the CBIC GST Ready Reckoner treat making charges?",
      tab: "advisor" as const,
      icon: <Scale className="w-4 h-4 text-[#24483A]" />,
      actionText: "Ask Odysseus",
    },
    {
      title: "Saving vs. Investing Fundamentals",
      category: "Financial Literacy",
      query: "Explain the fundamental difference between capital preservation in savings accounts and wealth generation in mutual funds, referencing SEBI financial guidance.",
      tab: "advisor" as const,
      icon: <PiggyBank className="w-4 h-4 text-[#24483A]" />,
      actionText: "Ask Odysseus",
    },
    {
      title: "CBIC GST Tariff Ready Reckoner",
      category: "Document Search",
      query: "Articles of natural or cultured pearls, precious or semi-precious stones CGST schedule",
      tab: "knowledge" as const,
      icon: <FileText className="w-4 h-4 text-[#111713]" />,
      actionText: "Search Vault",
    },
    {
      title: "SEBI Investor Protection & Redressal",
      category: "Regulatory Rights",
      query: "What is SEBI SCORES mechanism for investor grievance redressal in securities markets?",
      tab: "knowledge" as const,
      icon: <ShieldCheck className="w-4 h-4 text-[#111713]" />,
      actionText: "Search Vault",
    },
  ];

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-headline text-xl font-medium text-[#111713]">
            Curated Inquiries & Knowledge Vault
          </h3>
          <p className="text-xs text-[#858E83] mt-0.5 font-interface">
            Select a verified question to test real Gemini orchestration or Chroma semantic vector retrieval.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {prompts.map((p, idx) => (
          <div
            key={idx}
            onClick={() => onSelectPrompt(p.query, p.tab)}
            className="ledger-card p-5 rounded-xl flex flex-col justify-between hover:border-[rgba(17,23,19,0.25)] hover:shadow-md transition-all cursor-pointer group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="p-2 rounded-md bg-[#F5F3EC] group-hover:bg-[#EAE6DB] transition-colors">
                  {p.icon}
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-[#858E83] font-interface">
                  {p.category}
                </span>
              </div>
              <h4 className="font-interface text-sm font-semibold text-[#111713] group-hover:text-[#24483A] transition-colors leading-snug">
                {p.title}
              </h4>
              <p className="text-xs text-[#858E83] mt-2 line-clamp-2 font-interface leading-relaxed">
                &ldquo;{p.query}&rdquo;
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-[rgba(17,23,19,0.06)] flex items-center justify-between text-xs font-interface font-medium text-[#111713] group-hover:text-[#24483A]">
              <span>{p.actionText}</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
