import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'cyan' | 'neutral' | 'success' | 'warning' | 'danger' | 'purple' | 'primary';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'sm',
  className,
}) => {
  const variantStyles = {
    cyan: 'bg-cryo-cyan/10 text-cryo-cyan border-cryo-cyan/30',
    primary: 'bg-sky-500/15 text-sky-300 border-sky-500/40 font-semibold',
    neutral: 'bg-slate-800 text-slate-300 border-slate-700',
    success: 'bg-emerald-950/60 text-emerald-400 border-emerald-800/40',
    warning: 'bg-amber-950/60 text-amber-400 border-amber-800/40',
    danger: 'bg-rose-950/60 text-rose-400 border-rose-800/40',
    purple: 'bg-indigo-950/60 text-indigo-300 border-indigo-800/40',
  };

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center font-mono font-medium rounded border uppercase tracking-wider',
          variantStyles[variant],
          sizeStyles[size],
          className
        )
      )}
    >
      {children}
    </span>
  );
};
