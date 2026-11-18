import React, { useState } from 'react';
import {
  Layers,
  Activity,
  Workflow,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  Gauge,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const PhysicalModelPage: React.FC = () => {
  const [selectedTopic, setSelectedTopic] = useState<'equations' | 'friction' | 'conservation' | 'solver'>('equations');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Physical Solver Architecture</Badge>
            <Badge variant="neutral">2D Shallow Shelf Approximation (SSA)</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Reduced-Complexity 2D SSA Ice Dynamics Framework
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Non-linear finite-volume momentum solver and transient mass continuity formulation across
            866,358 grounded cells in Antarctic Peninsula Domain A (Stage 5.1).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="primary" className="px-3 py-1">Finite-Volume FV-SSA</Badge>
        </div>
      </div>

      {/* Interactive Architecture Topic Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { id: 'equations', title: '1. Governing Momentum & Viscosity', icon: <FileCode className="w-4 h-4" /> },
          { id: 'friction', title: '2. Regional Basal Friction Inversion', icon: <Gauge className="w-4 h-4" /> },
          { id: 'conservation', title: '3. Finite-Volume Mass Conservation', icon: <Workflow className="w-4 h-4" /> },
          { id: 'solver', title: '4. Numerical Safeguards & Rollback', icon: <AlertTriangle className="w-4 h-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedTopic(tab.id as any)}
            className={`p-3 rounded-lg border text-left font-mono text-xs transition-all flex items-center gap-2.5 ${
              selectedTopic === tab.id
                ? 'bg-cryo-card border-cryo-cyan text-white shadow-md shadow-cryo-cyan/5 ring-1 ring-cryo-cyan/40'
                : 'bg-cryo-dark/80 border-cryo-border text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <span className={selectedTopic === tab.id ? 'text-cryo-cyan' : 'text-slate-500'}>
              {tab.icon}
            </span>
            <span className="font-semibold truncate">{tab.title}</span>
          </button>
        ))}
      </div>

      {/* Topic Content Panel */}
      {selectedTopic === 'equations' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-5">
            <Card>
              <CardHeader
                title="Governing SSA Momentum Balance Equations"
                subtitle="Depth-integrated non-linear momentum equations for fast-flowing ice."
                icon={<FileCode className="w-4 h-4" />}
              />
              <div className="space-y-3.5 text-xs font-mono text-slate-300 leading-relaxed">
                <p>
                  In fast-flowing ice streams and floating shelves where basal sliding dominates vertical shear,
                  the Shallow Shelf Approximation (SSA) reduces the Stokes equations to depth-integrated 2D stress balance:
                </p>

                <div className="p-3.5 rounded bg-cryo-surface border border-cryo-border font-mono text-xs text-sky-300 space-y-2">
                  <div className="font-semibold text-slate-200 text-[11px] uppercase tracking-wider">
                    Horizontal Momentum Equations (x and y directions):
                  </div>
                  <div className="text-slate-100">
                    ∂/∂x [2 H ν̄ (2 ∂u/∂x + ∂v/∂y)] + ∂/∂y [H ν̄ (∂u/∂y + ∂v/∂x)] - τ_bx = ρ_i g H ∂s/∂x
                  </div>
                  <div className="text-slate-100">
                    ∂/∂y [2 H ν̄ (2 ∂v/∂y + ∂u/∂x)] + ∂/∂x [H ν̄ (∂u/∂y + ∂v/∂x)] - τ_by = ρ_i g H ∂s/∂y
                  </div>
                </div>

                <div className="space-y-2 pt-1">
                  <h4 className="text-sm font-semibold text-white">Glen's Flow Law & Effective Viscosity</h4>
                  <p>
                    Effective depth-averaged viscosity ν̄ obeys non-linear Glen's rheology with Glen exponent n = 3:
                  </p>
                  <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-slate-200">
                    ν̄ = 1/2 A^(-1/n) · (ε̇_eff^2 + ε̇_0^2)^((1-n)/2n)
                  </div>
                  <p className="text-cryo-muted text-[11px]">
                    where A is the frozen rate factor, ε̇_0 = 10⁻¹⁰ s⁻¹ is the numerical strain rate regularizer,
                    and ε̇_eff² = ε̇_xx² + ε̇_yy² + ε̇_xx·ε̇_yy + ε̇_xy².
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <CardHeader
                title="Grounding-Line Boundary Coupling (Schoof Flux Formula)"
                subtitle="Analytical flux formulation across grounded-to-floating transition boundaries."
                icon={<Workflow className="w-4 h-4" />}
              />
              <div className="space-y-2.5 text-xs font-mono text-slate-300 leading-relaxed">
                <p>
                  Grounding-line ice flux is governed by the Schoof boundary condition, ensuring smooth flux coupling
                  independent of spatial grid resolution:
                </p>
                <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-sky-300">
                  q_gl = [ (ρ_i g)^(n+1) · (1 - ρ_i/ρ_w)^n · A / (4^n C_bed) ]^(1 / (m+1)) · H_gl^((m+n+3)/(m+1))
                </div>
                <p className="text-[11px] text-cryo-muted">
                  Flotation thickness criterion: H_float = -( ρ_ocean / ρ_ice ) · b,
                  where ρ_ice = 917 kg/m³, ρ_ocean = 1028 kg/m³, and b is bedrock elevation.
                </p>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-5 space-y-5">
            <Card className="bg-cryo-darkest p-4">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-cryo-border">
                <span className="text-xs font-mono font-semibold text-white">Velocity Solution (Stage 4.6)</span>
                <Badge variant="cyan">MEaSUREs Constrained</Badge>
              </div>
              <img
                src="/figures/stage4_6_velocity_field.png"
                alt="2D SSA Surface Velocity Field"
                className="w-full h-auto rounded border border-cryo-border object-contain"
                loading="lazy"
              />
              <p className="text-[11px] font-mono text-cryo-muted mt-2">
                Simulated 2D surface velocity field matching observed satellite InSAR ice stream tributaries.
              </p>
            </Card>
          </div>
        </div>
      )}

      {selectedTopic === 'friction' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-5">
            <Card>
              <CardHeader
                title="Calibrated Regional Basal Friction Inversion (Stage 4.7)"
                subtitle="Weertman power law parameters inverted against observed satellite ice velocity fields."
                icon={<Gauge className="w-4 h-4" />}
              />
              <div className="space-y-3.5 text-xs font-mono text-slate-300 leading-relaxed">
                <p>
                  Basal shear traction τ_b is parameterized by a regularized Weertman sliding law:
                </p>
                <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-sky-300">
                  τ_b = - C_bed · |u|^(m-1) · u
                </div>
                <p>
                  with sliding exponent m = 1/3. Regional basal friction coefficients (C_bed) were calibrated
                  and frozen across the three study sectors:
                </p>

                {/* Calibrated Values Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-cryo-surface text-slate-400 border-b border-cryo-border">
                      <tr>
                        <th className="py-2 px-3">Basin ID</th>
                        <th className="py-2 px-3">Drainage Region</th>
                        <th className="py-2 px-3">Calibrated C_bed [Pa·(m/s)^(-1/3)]</th>
                        <th className="py-2 px-3">Calibration Anchor</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-cryo-border/60 text-slate-200">
                      <tr>
                        <td className="py-2 px-3 font-semibold text-cryo-cyan">Hp-I</td>
                        <td className="py-2 px-3">Palmer Land West</td>
                        <td className="py-2 px-3 font-mono font-semibold text-white">8.168 × 10⁶</td>
                        <td className="py-2 px-3 text-slate-400">Ryder Bay Anchor (Stage 4.7)</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-semibold text-amber-400">I-Ipp</td>
                        <td className="py-2 px-3">Graham Land</td>
                        <td className="py-2 px-3 font-mono font-semibold text-white">1.200 × 10⁷</td>
                        <td className="py-2 px-3 text-slate-400">Larsen A/B Tributaries</td>
                      </tr>
                      <tr>
                        <td className="py-2 px-3 font-semibold text-indigo-400">Ipp-J</td>
                        <td className="py-2 px-3">Palmer Land East</td>
                        <td className="py-2 px-3 font-mono font-semibold text-white">1.550 × 10⁷</td>
                        <td className="py-2 px-3 text-slate-400">Weddell Sea Flank</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <p className="text-[11px] text-cryo-muted pt-2 border-t border-cryo-border/60">
                  Parameter freeze ensures complete numerical reproducibility without arbitrary spatial tuning parameters.
                </p>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-5 space-y-5">
            <Card className="bg-cryo-darkest p-4">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-cryo-border">
                <span className="text-xs font-mono font-semibold text-white">Friction Inversion Map (Stage 4.7)</span>
                <Badge variant="cyan">Regional Inversion</Badge>
              </div>
              <img
                src="/figures/stage4_7_regional_inversion_maps.png"
                alt="Regional Basal Friction Maps"
                className="w-full h-auto rounded border border-cryo-border object-contain"
                loading="lazy"
              />
              <p className="text-[11px] font-mono text-cryo-muted mt-2">
                Spatial distribution of basal shear resistance across grounded bed topography.
              </p>
            </Card>
          </div>
        </div>
      )}

      {selectedTopic === 'conservation' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-5">
            <Card>
              <CardHeader
                title="Finite-Volume Mass Continuity & Geometric Conservation"
                subtitle="Conservation of mass across moving grounding lines and cut-cell boundaries."
                icon={<Workflow className="w-4 h-4" />}
              />
              <div className="space-y-3.5 text-xs font-mono text-slate-300 leading-relaxed">
                <p>
                  Ice thickness evolution is governed by the depth-integrated continuity equation discretized via
                  finite-volume flux updates:
                </p>
                <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-sky-300">
                  ∂H/∂t = - ∇ · (ū H) + SMB - M_basal - Calving
                </div>
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-white">Conservation Verification Suite (Stage 4.4.2)</h4>
                  <p>
                    All 6 synthetic conservation gate tests were audited and passed with 100% precision:
                  </p>
                  <ul className="space-y-1 pl-4 list-disc marker:text-cryo-cyan text-slate-300 text-[11px]">
                    <li>Shared-face flux cancellation across internal cell interfaces (machine precision: &lt; 10⁻¹⁴).</li>
                    <li>Adaptive mesh refinement (AMR) interface flux conservation.</li>
                    <li>Cut-cell moving boundary mass accounting during floating/grounded transitions.</li>
                    <li>WGS84 area and metric distortion invariance across all latitude parallels.</li>
                    <li>Volume-Above-Flotation (VAF) closed ledger tracking without artificial sink terms.</li>
                  </ul>
                </div>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-5 space-y-5">
            <Card className="bg-cryo-darkest p-4">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-cryo-border">
                <span className="text-xs font-mono font-semibold text-white">Mass Budget Assessment (Stage 4.8)</span>
                <Badge variant="cyan">Flux Divergence</Badge>
              </div>
              <img
                src="/figures/stage4_8_mass_budget_maps.png"
                alt="Mass Budget Assessment Maps"
                className="w-full h-auto rounded border border-cryo-border object-contain"
                loading="lazy"
              />
              <p className="text-[11px] font-mono text-cryo-muted mt-2">
                Spatial reconciliation of RACMO surface mass accumulation and satellite gate outflow.
              </p>
            </Card>
          </div>
        </div>
      )}

      {selectedTopic === 'solver' && (
        <div className="space-y-5">
          <Card>
            <CardHeader
              title="Numerical Diagnostics, Safeguards & Known Solver Limitations"
              subtitle="Formal disclosure of numerical stabilization, extreme slopes, and validation scope."
              icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs font-mono text-slate-300 leading-relaxed">
              <div className="space-y-3 p-4 rounded bg-cryo-surface border border-cryo-border">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  <span>Extreme-Slope Driving Stress Regularizer</span>
                </h4>
                <p>
                  In rugged alpine fjords with steep surface gradients, driving shear stress is capped by a numerical regularizer:
                </p>
                <div className="p-2 rounded bg-cryo-dark border border-cryo-border text-slate-100 text-[11px]">
                  τ_d,reg = τ_d / [ 1 + (|τ_d| / 350 kPa)² ]
                </div>
                <p className="text-cryo-muted text-[11px]">
                  <strong>Forensic Audit Note:</strong> This is a numerical stabilization limiter, NOT a validated physical yield criterion.
                  It prevents singular matrix divergence at steep coastal nunataks.
                </p>
              </div>

              <div className="space-y-3 p-4 rounded bg-cryo-surface border border-cryo-border">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>MISMIP+ Benchmark & Rollback Engine</span>
                </h4>
                <p>
                  The SSA solver successfully passed the international MISMIP+ benchmark experiments:
                </p>
                <ul className="space-y-1 pl-4 list-disc marker:text-emerald-400 text-[11px] text-slate-300">
                  <li><strong>Ice0:</strong> Steady-state grounding line equilibrium preservation.</li>
                  <li><strong>Ice1r:</strong> Forced retreat under ocean melt perturbation.</li>
                  <li><strong>Ice1ra:</strong> Grounding-line re-advance hysteresis dynamics.</li>
                </ul>
                <p className="text-cryo-muted text-[11px]">
                  Non-linear Picard iterations incorporate adaptive time-step cutback rollback upon divergence.
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Mandatory Disclaimer */}
      <ScientificDisclaimer />
    </div>
  );
};
