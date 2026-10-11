"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import {
  Compass,
  Sparkles,
  TrendingUp,
  BookOpen,
  LayoutDashboard,
  Menu,
  X,
  RefreshCw,
} from "lucide-react";

export type ActiveTab = "overview" | "advisor" | "markets" | "knowledge";

interface AppHeaderProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
}

export function AppHeader({ activeTab, onSelectTab }: AppHeaderProps) {
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const checkHealth = async () => {
    setIsCheckingHealth(true);
    try {
      const res = await api.getHealth();
      setIsBackendHealthy(res.status === "ok");
    } catch {
      setIsBackendHealthy(false);
    } finally {
      setIsCheckingHealth(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: "advisor", label: "Odysseus", icon: <Compass className="w-4 h-4" /> },
    { id: "markets", label: "Bullion Spot", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "knowledge", label: "Knowledge Vault", icon: <BookOpen className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#111713] text-[#FFFEFA] border-b border-[rgba(255,255,255,0.08)] shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Wordmark */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => onSelectTab("overview")}
              className="flex items-baseline gap-2.5 text-left group cursor-pointer focus:outline-none"
            >
              <span className="font-headline text-2xl font-semibold tracking-tight text-[#FFFEFA] group-hover:text-[#D8FF57] transition-colors">
                Obsidian Ledger
              </span>
              <span className="hidden sm:inline-block text-[10px] uppercase tracking-widest font-figures text-[#858E83] border-l border-[rgba(255,255,255,0.15)] pl-2.5">
                Finance Advisor
              </span>
            </button>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1 bg-[rgba(255,255,255,0.04)] p-1 rounded-lg border border-[rgba(255,255,255,0.06)]">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-interface font-medium transition-all duration-150 cursor-pointer ${
                    isActive
                      ? "bg-[#D8FF57] text-[#111713] shadow-xs font-semibold"
                      : "text-[#858E83] hover:text-[#FFFEFA] hover:bg-[rgba(255,255,255,0.06)]"
                  }`}
                >
                  {item.icon}
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Backend Status Indicator */}
          <div className="hidden sm:flex items-center gap-3">
            <button
              onClick={checkHealth}
              title="Click to re-ping backend health endpoint"
              className="group flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-figures bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] transition-colors cursor-pointer"
            >
              <span className="relative flex h-2 w-2">
                {isBackendHealthy ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#24483A] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#D8FF57]"></span>
                  </>
                ) : isBackendHealthy === false ? (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#B65F4A]"></span>
                ) : (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#858E83]"></span>
                )}
              </span>

              <span className="text-[11px] text-[#858E83] group-hover:text-[#FFFEFA] transition-colors">
                {isBackendHealthy === null
                  ? "Connecting..."
                  : isBackendHealthy
                  ? "FastAPI Live"
                  : "API Offline"}
              </span>

              <RefreshCw
                className={`w-3 h-3 text-[#858E83] group-hover:text-[#FFFEFA] transition-transform ${
                  isCheckingHealth ? "animate-spin" : ""
                }`}
              />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-[#858E83] hover:text-[#FFFEFA] hover:bg-[rgba(255,255,255,0.06)]"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[rgba(255,255,255,0.08)] bg-[#111713] px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-interface font-medium ${
                  isActive
                    ? "bg-[#D8FF57] text-[#111713] font-semibold"
                    : "text-[#858E83] hover:text-[#FFFEFA] hover:bg-[rgba(255,255,255,0.06)]"
                }`}
              >
                {item.icon}
                {item.label}
              </button>
            );
          })}
          <div className="pt-2 border-t border-[rgba(255,255,255,0.08)] flex items-center justify-between text-xs text-[#858E83] px-3">
            <span>FastAPI Server (Port 8000)</span>
            <Badge variant={isBackendHealthy ? "success" : "warning"}>
              {isBackendHealthy ? "Connected" : "Offline"}
            </Badge>
          </div>
        </div>
      )}
    </header>
  );
}
