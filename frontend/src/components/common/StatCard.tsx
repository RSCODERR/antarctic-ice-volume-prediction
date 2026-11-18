import React from 'react';
import { Card } from './Card';
import { clsx } from 'clsx';

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  highlight?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  unit,
  subtext,
  icon,
  highlight = false,
}) => {
  return (
    <Card className={clsx('relative overflow-hidden p-4', highlight && 'border-cryo-cyan/50 bg-cryo-card/60')}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-wider text-cryo-muted">{label}</p>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
              {value}
            </span>
            {unit && <span className="text-xs text-cryo-cyan font-mono">{unit}</span>}
          </div>
          {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
        </div>
        {icon && (
          <div className="p-2 rounded bg-cryo-surface/80 border border-cryo-border text-cryo-cyan">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};
