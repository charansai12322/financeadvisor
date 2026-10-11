import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "accent" | "outline" | "dark";
  className?: string;
  icon?: React.ReactNode;
}

export function Badge({
  children,
  variant = "default",
  className = "",
  icon,
}: BadgeProps) {
  const base =
    "inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium tracking-wide rounded-full font-interface transition-colors";

  const variants = {
    default: "bg-[#EAE6DB] text-[#252B27] border border-[#DDD8CA]",
    success: "bg-[#E7F0EB] text-[#24483A] border border-[#C5DCD0]",
    warning: "bg-[#FAECE8] text-[#B65F4A] border border-[#F1D4CD]",
    accent: "bg-[#D8FF57] text-[#111713] border border-[#C2E943] font-semibold",
    outline: "border border-[rgba(17,23,19,0.15)] text-[#252B27] bg-transparent",
    dark: "bg-[#111713] text-[#FFFEFA] border border-[rgba(255,255,255,0.12)]",
  };

  return (
    <span className={`${base} ${variants[variant]} ${className}`}>
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  );
}
