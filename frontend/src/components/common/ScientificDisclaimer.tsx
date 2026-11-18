import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

interface ScientificDisclaimerProps {
  title?: string;
  disclosures?: string[];
  compact?: boolean;
}

export const ScientificDisclaimer: React.FC<ScientificDisclaimerProps> = ({
  title = 'Glaciological Boundary & Scientific Protocols',
  disclosures = [
    'CryoPredict models are regularized 1-year ahead historical autoregressive benchmarks (1979–2024).',
    'These models are NOT 2100 climate projection engines and must NOT be extrapolated for multi-decadal sea-level rise forecasting.',
    'CryoSat-2 altimetry (+60.52 Gt/yr regional offset) remains on formal HOLD pending firn air content and compaction adjustments.',
  ],
  compact = false,
}) => {
  if (compact) {
    return (
      <div className="flex items-center gap-2 p-2.5 rounded border border-amber-900/40 bg-amber-950/20 text-amber-200/90 text-xs font-mono">
        <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span>Notice: Historical 1-yr ahead ML predictor. Centennial 2100 extrapolations strictly prohibited.</span>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-lg border border-cryo-border bg-cryo-dark/60 text-slate-300">
      <div className="flex items-center gap-2.5 text-cryo-cyan font-mono text-xs uppercase tracking-wider font-semibold mb-2">
        <Info className="w-4 h-4" />
        <span>{title}</span>
      </div>
      <ul className="space-y-1.5 text-xs text-cryo-muted font-mono leading-relaxed pl-4 list-disc marker:text-cryo-cyan">
        {disclosures.map((d, i) => (
          <li key={i}>{d}</li>
        ))}
      </ul>
    </div>
  );
};
