"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, ApiClientError } from "@/lib/api";
import { AdvisorResponse, AdvisorRequest } from "@/types/api";
import { formatINR } from "@/lib/formatters";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { OdysseusMark } from "@/components/ui/OdysseusMark";
import {
  Compass,
  Send,
  Copy,
  Check,
  FileText,
  AlertCircle,
  TrendingUp,
  ShieldAlert,
  Hash,
  RotateCcw,
} from "lucide-react";

interface MessageItem {
  id: string;
  role: "user" | "advisor";
  content: string;
  responsePayload?: AdvisorResponse;
  timestamp: string;
  error?: string;
}

interface AdvisorWorkspaceProps {
  initialPrompt?: string;
  onClearInitialPrompt?: () => void;
}

export function AdvisorWorkspace({
  initialPrompt,
  onClearInitialPrompt,
}: AdvisorWorkspaceProps) {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activeError, setActiveError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of conversation
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Handle incoming initial prompt from parent
  useEffect(() => {
    if (initialPrompt) {
      setInputQuestion(initialPrompt);
      onClearInitialPrompt?.();
      textareaRef.current?.focus();
    }
  }, [initialPrompt, onClearInitialPrompt]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const q = inputQuestion.trim();
    if (!q || isLoading) return;

    setActiveError(null);
    const userMsgId = `user-${Date.now()}`;
    const newUserMsg: MessageItem = {
      id: userMsgId,
      role: "user",
      content: q,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputQuestion("");
    setIsLoading(true);

    try {
      const response = await api.askAdvisor(q);
      const advisorMsgId = `advisor-${Date.now()}`;
      const newAdvisorMsg: MessageItem = {
        id: advisorMsgId,
        role: "advisor",
        content: response.answer,
        responsePayload: response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, newAdvisorMsg]);
    } catch (err: unknown) {
      let errMsg = "An unexpected error occurred during advisory inference.";
      if (err instanceof ApiClientError) {
        if (err.statusCode === 503) {
          errMsg = "Gemini API is in standby or API key is unconfigured in backend/.env.";
        } else if (err.statusCode === 504) {
          errMsg = "Inference request timed out. Upstream LLM provider latency exceeded threshold.";
        } else {
          errMsg = err.message;
        }
      } else if (err instanceof Error) {
        errMsg = err.message;
      }
      setActiveError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const examplePrompts = [
    "What is the current gold price in INR and what GST applies when buying jewellery?",
    "Explain the difference between saving in FDs vs investing in Mutual Funds in 2 sentences.",
    "What does the CBIC GST Ready Reckoner say about rates on precious stones and metals?",
    "What is the purpose of the SEBI Financial Education Booklet for individual investors?",
  ];

  return (
    <div className="max-w-4xl mx-auto flex flex-col min-h-[calc(100vh-12rem)]">
      {/* Workspace Header */}
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[rgba(17,23,19,0.06)]"
      >
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-1 rounded-md bg-[#111713] text-[#D8FF57]">
              <OdysseusMark className="w-4 h-4" />
            </span>
            <h2 className="font-headline text-2xl font-medium text-[#111713]">
              Meet Odysseus
            </h2>
            <Badge variant="dark" icon={<Compass className="w-3 h-3 text-[#D8FF57]" />}>
              Your AI Financial Navigator
            </Badge>
          </div>
          <p className="text-xs text-[#858E83] mt-1 font-interface">
            Navigate financial questions with grounded insights from market data and trusted reference documents.
          </p>
        </div>

        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMessages([])}
            icon={<RotateCcw className="w-3.5 h-3.5" />}
          >
            Clear Session
          </Button>
        )}
      </motion.div>

      {/* Message Area */}
      <div className="flex-1 space-y-6 mb-6">
        {messages.length === 0 ? (
          /* Empty state */
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className="ledger-card p-8 rounded-2xl text-center my-6"
          >
            <div className="inline-flex p-3.5 rounded-2xl bg-[#111713] text-[#D8FF57] mb-4 shadow-sm">
              <OdysseusMark className="w-7 h-7" size={28} />
            </div>
            <h3 className="font-headline text-2xl font-medium text-[#111713]">
              What would you like to understand today?
            </h3>
            <p className="text-xs text-[#858E83] max-w-md mx-auto mt-2 font-interface leading-relaxed">
              Navigate financial questions with grounded insights from market data and trusted reference documents.
            </p>

            {/* Quick Prompt Pills */}
            <div className="mt-8 text-left max-w-2xl mx-auto">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#858E83] block mb-3 font-interface">
                Suggested Financial Inquiries
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {examplePrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setInputQuestion(prompt);
                      textareaRef.current?.focus();
                    }}
                    className="p-3 rounded-lg text-left text-xs font-interface bg-[#F5F3EC] hover:bg-[#EAE6DB] border border-[rgba(17,23,19,0.06)] hover:border-[rgba(17,23,19,0.15)] text-[#252B27] transition-all cursor-pointer leading-relaxed"
                  >
                    &ldquo;{prompt}&rdquo;
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        ) : (
          /* Conversation Thread */
          messages.map((msg) => (
            <div key={msg.id} className="space-y-3">
              {msg.role === "user" ? (
                /* User Message */
                <div className="flex justify-end">
                  <div className="max-w-[85%] sm:max-w-xl p-4 rounded-xl rounded-tr-none bg-[#111713] text-[#FFFEFA] shadow-xs">
                    <p className="text-sm font-interface whitespace-pre-wrap leading-relaxed">
                      {msg.content}
                    </p>
                  </div>
                </div>
              ) : (
                /* Advisor Response Card */
                <div className="flex justify-start">
                  <div className="w-full ledger-card rounded-xl p-6 sm:p-7 space-y-5">
                    {/* Header info */}
                    <div className="flex items-center justify-between pb-3 border-b border-[rgba(17,23,19,0.06)]">
                      <div className="flex items-center gap-2">
                        <span className="p-1 rounded bg-[#111713] text-[#D8FF57]">
                          <OdysseusMark className="w-3.5 h-3.5" />
                        </span>
                        <div className="flex items-baseline gap-1.5">
                          <span className="text-xs font-semibold text-[#111713] font-interface">
                            Odysseus
                          </span>
                          <span className="text-[10px] text-[#858E83] font-interface hidden sm:inline">
                            · Your AI Financial Navigator
                          </span>
                        </div>
                        {msg.responsePayload?.model && (
                          <span className="text-[10px] font-figures text-[#858E83] bg-[#F5F3EC] px-2 py-0.5 rounded">
                            {msg.responsePayload.model}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => copyToClipboard(msg.content, msg.id)}
                          className="flex items-center gap-1 text-xs text-[#858E83] hover:text-[#111713] px-2 py-1 rounded hover:bg-[#F5F3EC] transition-colors cursor-pointer"
                          title="Copy response"
                        >
                          {copiedId === msg.id ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-[#24483A]" />
                              <span className="text-[11px] font-semibold text-[#24483A]">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" />
                              <span className="text-[11px]">Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Main Synthesized Text */}
                    <div className="text-sm text-[#252B27] leading-relaxed font-interface space-y-3 whitespace-pre-wrap">
                      {msg.content}
                    </div>

                    {/* Grounding Market Data (if utilized) */}
                    {msg.responsePayload?.market_data &&
                      msg.responsePayload.market_data.length > 0 && (
                        <div className="pt-3 border-t border-[rgba(17,23,19,0.06)]">
                          <span className="text-[11px] font-semibold uppercase tracking-wider text-[#858E83] block mb-2 font-interface flex items-center gap-1.5">
                            <TrendingUp className="w-3 h-3 text-[#24483A]" /> Live Bullion Grounding
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {msg.responsePayload.market_data.map((m, idx) => (
                              <div
                                key={idx}
                                className="px-3 py-1.5 rounded-lg bg-[#F5F3EC] border border-[rgba(17,23,19,0.08)] text-xs font-figures flex items-center gap-2"
                              >
                                <span className="font-semibold text-[#111713]">{m.asset}</span>
                                <span className="text-[#858E83]">10g:</span>
                                <span className="font-semibold text-[#24483A]">
                                  {m.price_per_10g ? formatINR(m.price_per_10g) : "Verified Spot"}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    {/* Grounding Sources (if cited) */}
                    {msg.responsePayload?.sources && msg.responsePayload.sources.length > 0 && (
                      <div className="pt-3 border-t border-[rgba(17,23,19,0.06)]">
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-[#858E83] block mb-2 font-interface flex items-center gap-1.5">
                          <FileText className="w-3 h-3 text-[#111713]" /> Grounding Evidence Sources
                        </span>
                        <div className="space-y-2">
                          {msg.responsePayload.sources.map((src, idx) => (
                            <div
                              key={idx}
                              className="p-3 rounded-lg bg-[#F5F3EC] border border-[rgba(17,23,19,0.08)] text-xs"
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-[#111713]">{src.title}</span>
                                <Badge variant="outline" className="text-[10px]">
                                  {src.page_label}
                                </Badge>
                              </div>
                              <p className="text-[11px] text-[#858E83] font-figures mb-1.5">
                                Source: {src.source_file}
                              </p>
                              {src.snippet && (
                                <p className="text-[11px] text-[#252B27] bg-[#FFFEFA] p-2 rounded border border-[rgba(17,23,19,0.05)] line-clamp-3 italic">
                                  &ldquo;{src.snippet}&rdquo;
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Regulatory Disclaimer & Correlation Request ID */}
                    <div className="pt-3 border-t border-[rgba(17,23,19,0.06)] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-[#858E83]">
                      <span className="flex items-center gap-1.5 font-interface">
                        <ShieldAlert className="w-3.5 h-3.5 text-[#858E83] shrink-0" />
                        Educational guidance only. Consult SEBI-registered professionals for execution.
                      </span>
                      {msg.responsePayload?.request_id && (
                        <span className="font-figures flex items-center gap-1 text-[10px] text-[#858E83]">
                          <Hash className="w-3 h-3" />
                          {msg.responsePayload.request_id.slice(0, 8)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="w-full max-w-lg ledger-card rounded-xl p-5 border-l-4 border-l-[#D8FF57] flex items-center gap-3 animate-pulse">
              <span className="p-1 rounded bg-[#111713] text-[#D8FF57]">
                <OdysseusMark className="w-4 h-4 animate-spin" />
              </span>
              <div className="text-xs font-interface text-[#252B27]">
                <p className="font-semibold">Odysseus is working through your question…</p>
                <p className="text-[#858E83] text-[11px] mt-0.5">
                  Synthesizing market rates & vector index (Gemini 3.8 Flash)
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {activeError && (
          <div className="p-4 rounded-xl bg-[#FAECE8] border border-[#F1D4CD] text-[#B65F4A] flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="text-xs font-interface flex-1">
              <p className="font-semibold text-sm">Odysseus was unable to complete this inquiry</p>
              <p className="mt-1 opacity-90">{activeError}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSubmit()}
                className="mt-3 text-xs border-[#B65F4A] text-[#B65F4A] hover:bg-[#F1D4CD]"
              >
                Retry Question
              </Button>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Composer */}
      <div className="sticky bottom-4 z-20">
        <form
          onSubmit={handleSubmit}
          className="ledger-card p-2 sm:p-3 rounded-2xl shadow-lg border border-[rgba(17,23,19,0.15)] bg-[#FFFEFA] flex flex-col gap-2"
        >
          <div className="relative">
            <textarea
              ref={textareaRef}
              rows={2}
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Odysseus a financial question…"
              disabled={isLoading}
              className="w-full resize-none p-2 sm:p-3 text-sm font-interface text-[#252B27] placeholder:text-[#858E83] bg-transparent focus:outline-none disabled:opacity-50"
            />
          </div>

          <div className="flex items-center justify-between px-2 pt-1 border-t border-[rgba(17,23,19,0.06)]">
            <span className="text-[11px] text-[#858E83] font-figures hidden sm:inline">
              Press <kbd className="px-1 py-0.5 bg-[#F5F3EC] rounded border text-[10px]">Enter</kbd> to send, <kbd className="px-1 py-0.5 bg-[#F5F3EC] rounded border text-[10px]">Shift+Enter</kbd> for newline
            </span>

            <div className="flex items-center gap-2 ml-auto">
              <span className="text-[11px] font-figures text-[#858E83]">
                {inputQuestion.length}/2000
              </span>
              <Button
                type="submit"
                variant="accent"
                size="sm"
                disabled={!inputQuestion.trim() || isLoading}
                isLoading={isLoading}
                icon={<Compass className="w-3.5 h-3.5" />}
              >
                Ask Odysseus
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
