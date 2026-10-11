import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "accent" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center font-interface font-medium rounded-md transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none ledger-focus-ring cursor-pointer";

  const sizeClasses = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-5 py-2.5 text-base gap-2.5",
  };

  const variantClasses = {
    primary:
      "bg-[#111713] text-[#FFFEFA] hover:bg-[#252B27] border border-[#111713] shadow-sm",
    secondary:
      "bg-[#FFFEFA] text-[#252B27] hover:bg-[#F5F3EC] border border-[rgba(17,23,19,0.12)] shadow-xs",
    outline:
      "bg-transparent text-[#252B27] hover:bg-[rgba(17,23,19,0.04)] border border-[rgba(17,23,19,0.2)]",
    accent:
      "bg-[#D8FF57] text-[#111713] hover:bg-[#C8EE44] font-semibold border border-[#C2E943] shadow-xs",
    ghost:
      "bg-transparent text-[#252B27] hover:bg-[rgba(17,23,19,0.05)] border-transparent",
  };

  return (
    <button
      className={`${base} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
}
