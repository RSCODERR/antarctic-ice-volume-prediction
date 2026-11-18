import React from 'react';
import {
  CheckCircle2,
  ShieldCheck,
  AlertTriangle,
  FileCheck,
  GitCommit,
  FlaskConical,
  Award,
  Layers,
  Info
} from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { StatCard } from '../components/common/StatCard';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const ValidationPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Scientific Audit & Verification</Badge>
            <Badge variant="success">Stage 6.2 Freeze</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Validation, Limitations & Forensic Audit
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Forensic audit trail, test suite certification, reproducibility benchmarks, observational anomalies,
            and formal limitations of the CryoPredict research platform.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="neutral" className="px-3 py-1 font-mono">
            Audit Hash: SHA-256 Verified
          </Badge>
        </div>
      </div>

      {/* Verification Stat Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Research Test Suite"
          value="80 / 80"
          unit="Passed"
          subtext="Full physical & ML unit tests (100% pass)"
          icon={<CheckCircle2 className="w-4 h-4 text-emerald-400" />}
          highlight
        />
        <StatCard
          label="Backend Test Suite"
          value="24 / 24"
          unit="Passed"
          subtext="FastAPI endpoints & live inference (100% pass)"
          icon={<FileCheck className="w-4 h-4 text-sky-400" />}
        />
        <StatCard
          label="Primary Model (ElasticNet)"
          value="9.61"
          unit="Gt/yr MAE"
          subtext="21.0% improvement over historical baseline"
          icon={<Award className="w-4 h-4 text-emerald-400" />}
        />
        <StatCard
          label="Altimetry Offset Status"
          value="+60.52"
          unit="Gt/yr"
          subtext="CryoSat-2 on formal HOLD (firn hazard)"
          icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
        />
      </div>

      {/* Test Suite Distinction Callout */}
      <Card className="border-sky-500/40 bg-cryo-surface/40">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-cryo-cyan flex-shrink-0 mt-0.5" />
          <div className="text-xs font-mono space-y-1.5 leading-relaxed">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">
              Verification Test Suite Architecture Distinction
            </h4>
            <p className="text-slate-300">
              Per the repository cleanup audit, testing is strictly stratified between two independent test harnesses:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div className="p-3 rounded bg-cryo-dark border border-cryo-border">
                <span className="text-slate-400 font-semibold block text-[11px] uppercase">
                  1. Core Research & Physical Solver Suite (`tests/`):
                </span>
                <span className="text-emerald-400 font-bold text-sm">80 Tests Passed</span>
                <p className="text-cryo-muted text-[10px] mt-1">
                  Comprises 28 ML artifact / baseline tests and 52 SSA 2D physical solver, MISMIP+ benchmarking, cut-cell divergence, and synthetic conservation tests.
                </p>
              </div>
              <div className="p-3 rounded bg-cryo-dark border border-cryo-border">
                <span className="text-slate-400 font-semibold block text-[11px] uppercase">
                  2. Web API Integration Suite (`backend/tests/`):
                </span>
                <span className="text-sky-400 font-bold text-sm">24 Tests Passed (52 combined)</span>
                <p className="text-cryo-muted text-[10px] mt-1">
                  Verifies FastAPI application startup, live scikit-learn artifact execution across all 6 models, non-finite checks, and the centennial 2100 forecast rejection guardrail.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Forensic Audit Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stage 6.1 & 6.2 ML Verification */}
        <Card>
          <CardHeader
            title="Stage 6.1 & 6.2 ML Reproducibility Audit"
            subtitle="Strict validation against data leakage and parameter contamination."
            icon={<ShieldCheck className="w-4 h-4 text-emerald-400" />}
          />
          <div className="space-y-3 text-xs font-mono text-slate-300 leading-relaxed">
            <p>
              The machine-learning benchmark was locked against strict chronological splits:
            </p>
            <div className="space-y-1.5 p-3 rounded bg-cryo-surface border border-cryo-border text-[11px]">
              <div className="flex justify-between">
                <span className="text-slate-400">Training Period:</span>
                <span className="text-white">1979–2005 (81 basin-year observations)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Embargo Buffer 1:</span>
                <span className="text-amber-400">2006–2007 (2 years excluded to prevent leakage)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Validation Period:</span>
                <span className="text-white">2008–2014 (21 basin-year observations)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Embargo Buffer 2:</span>
                <span className="text-amber-400">2015 (1 year excluded)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Held-Out Test Period:</span>
                <span className="text-emerald-400 font-semibold">2016–2024 (27 basin-year observations)</span>
              </div>
            </div>
            <p className="text-[11px] text-cryo-muted">
              <strong>Audit Finding:</strong> The held-out test window (2016–2024) was completely untouched during
              feature selection and hyperparameter optimization. The ElasticNet model achieved an exact reproduced
              RMSE of 13.56 Gt/yr, MAE of 9.61 Gt/yr, and R² of +0.069.
            </p>
          </div>
        </Card>

        {/* CryoSat-2 Discrepancy & Altimetry Hazard */}
        <Card>
          <CardHeader
            title="CryoSat-2 Altimetry Discrepancy & Firn Hazard"
            subtitle="Empirical offset (+60.52 Gt/yr) relative to gravimetry and mass budget."
            icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
          />
          <div className="space-y-3 text-xs font-mono text-slate-300 leading-relaxed">
            <p>
              During Stage 3 and Phase 4 audits, satellite radar altimetry (CryoSat-2) exhibited an apparent mass gain
              offset of <strong>+60.52 Gt/year</strong> relative to independent GRACE gravimetry and input-output flux gates:
            </p>
            <div className="p-3 rounded bg-amber-950/20 border border-amber-900/40 text-amber-200/90 text-[11px] space-y-1">
              <div className="font-semibold text-amber-300">Formal Research Action: HOLD Status</div>
              <p>
                CryoSat-2 altimetry was placed on formal HOLD and excluded from primary ML target generation.
                Uncorrected radar penetration into surface firn layers and unmodeled firn air compaction produce
                spurious elevation changes that do not represent solid-ice mass accumulation.
              </p>
            </div>
            <p className="text-[11px] text-cryo-muted">
              Target mass balance is strictly anchored to satellite input-output flux gates and reconciled IMBIE-3 observations.
            </p>
          </div>
        </Card>
      </div>

      {/* Explicit Statement on 2100 Projections & Limitations */}
      <Card className="border-rose-900/40 bg-cryo-dark">
        <CardHeader
          title="Formal Limitations & Prohibition of 2100 Climate Projections"
          subtitle="Mandatory scientific boundaries governing model validity and operational scope."
          icon={<AlertTriangle className="w-4 h-4 text-rose-400" />}
        />
        <div className="space-y-3 text-xs font-mono text-slate-300 leading-relaxed">
          <div className="p-4 rounded border border-rose-800/40 bg-rose-950/20 text-rose-200">
            <h4 className="font-bold text-sm text-rose-300 uppercase tracking-wider mb-1">
              NO VALIDATED 2100 PREDICTION EXISTS
            </h4>
            <p className="text-xs text-rose-200/90 leading-relaxed">
              CryoPredict machine-learning models are historical 1-year ahead autoregressive benchmarks regularized on
              1979–2024 observations. They are <strong>NOT coupled climate projection engines</strong>.
              Extrapolating these statistical models to century-scale projections (e.g. year 2100) under hypothetical
              SSP climate scenarios without physically coupled atmospheric/oceanic forcing is scientifically invalid
              and is strictly blocked by the backend API.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-[11px]">
              <span className="font-semibold text-white block mb-1">Spatial Aggregation:</span>
              <span>Predictor features are integrated at regional drainage basin scales (Hp-I, I-Ipp, Ipp-J) rather than sub-kilometer glacier fjords.</span>
            </div>
            <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-[11px]">
              <span className="font-semibold text-white block mb-1">Ice Shelf Back-Stress:</span>
              <span>Larsen C and George VI ice-shelf buttressing changes are captured via operational boundary stress indices rather than full 3D Stokes physics.</span>
            </div>
            <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-[11px]">
              <span className="font-semibold text-white block mb-1">Marine Ice Cliff Instability:</span>
              <span>Potential rapid structural calving (MICI) is not modeled in the 2D Shallow Shelf Approximation framework.</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Final Scientific Disclaimer */}
      <ScientificDisclaimer />
    </div>
  );
};
