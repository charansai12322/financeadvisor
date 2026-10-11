import React from "react";

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
}

export function Skeleton({ className = "", width, height }: SkeletonProps) {
  return (
    <div
      style={{ width, height }}
      className={`animate-pulse rounded bg-[rgba(17,23,19,0.08)] ${className}`}
    />
  );
}
