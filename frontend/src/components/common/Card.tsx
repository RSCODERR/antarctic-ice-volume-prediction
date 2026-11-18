import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className, glow = false, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx(
          'bg-cryo-dark/80 backdrop-blur border border-cryo-border rounded-lg p-5 transition-colors',
          glow && 'border-cryo-cyan/40 shadow-lg shadow-cryo-cyan/5',
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, action, icon, className }) => (
  <div className={twMerge('flex items-start justify-between mb-4 border-b border-cryo-border/60 pb-3', className)}>
    <div className="flex items-center gap-2.5">
      {icon && <div className="text-cryo-cyan flex-shrink-0">{icon}</div>}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-100">{title}</h3>
        {subtitle && <p className="text-xs text-cryo-muted mt-0.5">{subtitle}</p>}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);
