import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  TrendingUp,
  ShieldAlert,
  Info,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Compass,
  Sliders,
  Database,
  Calendar,
  ChevronDown,
  ChevronUp,
  Eye,
  Activity,
  ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine
} from 'recharts';
import { CryoApi, formatApiError } from '../api/client';
import {
  ScenarioItem,
  FutureModelInfoResponse,
  AvailabilityResponse,
  ProjectionTrajectoryResponse,
  TrajectoryPoint
} from '../api/types';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { StatCard } from '../components/common/StatCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const FutureProjectionsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Scenario & Spatial State (synced with search params)
  const initialScenario = searchParams.get('scenario') || 'RCP8.5';
  const initialRegion = searchParams.get('region') || 'Domain_A';
  const initialMetric = (searchParams.get('metric') === 'sle' ? 'sle' : 'vaf') as 'vaf' | 'sle';
  const initialShow90 = searchParams.get('show90') === 'true';

  const [selectedScenario, setSelectedScenario] = useState<string>(initialScenario);
  const [selectedRegion, setSelectedRegion] = useState<string>(initialRegion);
  const [targetMetric, setTargetMetric] = useState<'vaf' | 'sle'>(initialMetric);
  const [show90Envelope, setShow90Envelope] = useState<boolean>(initialShow90);
  const [showFoldTable, setShowFoldTable] = useState<boolean>(false);

  // Sync state to URL params
  const handleScenarioChange = (scen: string) => {
    setSelectedScenario(scen);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set('scenario', scen);
      return next;
    });
  };

  const handleRegionChange = (reg: string) => {
    setSelectedRegion(reg);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set('region', reg);
      return next;
    });
  };

  const handleMetricChange = (metric: 'vaf' | 'sle') => {
    setTargetMetric(metric);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set('metric', metric);
      return next;
    });
  };

  const handleToggle90 = (show: boolean) => {
    setShow90Envelope(show);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (show) next.set('show90', 'true');
      else next.delete('show90');
      return next;
    });
  };

  // Data fetching state
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [modelInfo, setModelInfo] = useState<FutureModelInfoResponse | null>(null);
  const [availability, setAvailability] = useState<AvailabilityResponse | null>(null);
  const [trajectoryData, setTrajectoryData] = useState<ProjectionTrajectoryResponse | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [trajectoryLoading, setTrajectoryLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initial metadata fetch
  useEffect(() => {
    let isMounted = true;
    const loadMetadata = async () => {
      try {
        setLoading(true);
        const [scenRes, modelRes, availRes] = await Promise.all([
          CryoApi.getProjectionScenarios(),
          CryoApi.getProjectionModelInfo(),
          CryoApi.getProjectionAvailability(),
        ]);
        if (isMounted) {
          setScenarios(scenRes);
          setModelInfo(modelRes);
          setAvailability(availRes);
        }
      } catch (err) {
        if (isMounted) {
          setError(formatApiError(err));
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadMetadata();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch trajectory when scenario or region changes
  useEffect(() => {
    let isMounted = true;
    const fetchTrajectory = async () => {
      try {
        setTrajectoryLoading(true);
        const traj = await CryoApi.getProjectionTrajectory({
          scenario: selectedScenario,
          spatial_unit: selectedRegion,
          start_year: 2015,
          end_year: 2100,
        });
        if (isMounted) {
          setTrajectoryData(traj);
        }
      } catch (err) {
        if (isMounted) {
          setError(formatApiError(err));
        }
      } finally {
        if (isMounted) setTrajectoryLoading(false);
      }
    };
    fetchTrajectory();
    return () => {
      isMounted = false;
    };
  }, [selectedScenario, selectedRegion]);

  // Current Scenario metadata
  const currentScenarioMeta = useMemo(() => {
    return scenarios.find((s) => s.id === selectedScenario);
  }, [scenarios, selectedScenario]);

  // Chart data formatting
  const chartData = useMemo(() => {
    if (!trajectoryData?.trajectory) return [];
    return trajectoryData.trajectory.map((pt: TrajectoryPoint) => {
      const isVaf = targetMetric === 'vaf';
      // Values for target
      const median = isVaf ? pt.delta_vaf_median_km3 : pt.delta_sle_median_mm;
      const q16 = isVaf ? pt.delta_vaf_16th_km3 : pt.delta_sle_16th_mm;
      const q84 = isVaf ? pt.delta_vaf_84th_km3 : pt.delta_sle_84th_mm;
      const q10 = isVaf ? pt.delta_vaf_10th_km3 : pt.delta_sle_10th_mm;
      const q90 = isVaf ? pt.delta_vaf_90th_km3 : pt.delta_sle_90th_mm;

      // Recharts range representation: [min, max]
      const band68 = [Math.min(q16, q84), Math.max(q16, q84)];
      const band90 = [Math.min(q10, q90), Math.max(q10, q90)];

      return {
        year: pt.year,
        median,
        q16,
        q84,
        q10,
        q90,
        band68,
        band90,
      };
    });
  }, [trajectoryData, targetMetric]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <LoadingSpinner message="Loading Stage 7.1 Multi-Model Projection Engine..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <Badge variant="cyan">Pillar 2 Research</Badge>
            <Badge variant="warning">Stage 7.1 Multi-Model Emulator</Badge>
            <Badge variant="success">Conditional Pass</Badge>
            <Badge variant="purple">LOMFO Validated</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white flex items-center gap-3">
            <TrendingUp className="w-7 h-7 text-cryo-cyan" />
            <span>Future Projections (2015–2100)</span>
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Multi-decadal projections of Volume Above Flotation (ΔVAF) and derived Sea-Level Equivalent (SLE) across
            the Antarctic Peninsula, emulating 16 ice-sheet models from the Seroussi et al. (2020) ISMIP6 archive.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge
            variant={trajectoryData?.scenario_watermark === 'NATIVE_ISMIP6' ? 'cyan' : 'warning'}
            className="px-3 py-1 font-mono text-xs"
          >
            {trajectoryData?.scenario_watermark || 'NATIVE_ISMIP6'}
          </Badge>
        </div>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Prominent Mandatory Scientific Disclosures Banner */}
      <Card className="border-amber-500/30 bg-amber-950/20">
        <div className="flex items-start gap-3.5">
          <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1.5 text-xs font-mono text-slate-300">
            <div className="font-semibold text-amber-300 uppercase tracking-wide flex items-center gap-2">
              <span>Mandatory Glaciological Target Disclosure</span>
              <Badge variant="warning" size="sm">Scientific Protocol</Badge>
            </div>
            <p className="text-slate-200 font-medium">
              "These projections represent changes in Volume Above Flotation (ΔVAF) and derived Sea-Level Equivalent (SLE).
              They do not represent total grounded solid-ice volume."
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-2 border-t border-amber-500/20 text-[11px] text-slate-400">
              <div>
                • <strong className="text-slate-300">Target Accounting:</strong> VAF measures the column thickness exceeding hydrostatic flotation. Standalone total grounded solid ice ($V_g$) is not provided in ISMIP6 scalar outputs.
              </div>
              <div>
                • <strong className="text-slate-300">Physical Solver Scope:</strong> The 2D SSA model is a transient historical diagnostic tool, not certified for unconstrained centennial projections.
              </div>
              <div>
                • <strong className="text-slate-300">Scenario Provenance:</strong> RCP8.5 and RCP2.6 are native ISMIP6 simulations. SSP2-4.5 is a scaled emulator synthesis (α = 0.35).
              </div>
              <div>
                • <strong className="text-slate-300">Prediction Intervals:</strong> Empirical out-of-family quantile bounds, NOT fully calibrated Bayesian credible intervals.
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Control Toolbar: Scenario, Spatial Unit, Target Metric */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Scenario Selector */}
        <div className="lg:col-span-5">
          <Card className="h-full flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <Sliders className="w-3.5 h-3.5 text-cryo-cyan" />
                  <span>Climate Scenario</span>
                </span>
                {currentScenarioMeta && (
                  <Badge
                    variant={currentScenarioMeta.scenario_type === 'NATIVE_ISMIP6' ? 'cyan' : 'warning'}
                    size="sm"
                  >
                    {currentScenarioMeta.scenario_watermark}
                  </Badge>
                )}
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {scenarios.map((scen) => (
                  <button
                    key={scen.id}
                    onClick={() => handleScenarioChange(scen.id)}
                    className={`px-3 py-2 rounded text-xs font-mono font-medium border transition-all text-left ${
                      selectedScenario === scen.id
                        ? 'bg-cryo-cyan/20 border-cryo-cyan text-cryo-cyan shadow-sm shadow-cryo-cyan/10'
                        : 'bg-cryo-card/60 border-cryo-border text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-bold">{scen.id}</div>
                    <div className="text-[10px] text-slate-400 truncate">{scen.tier}</div>
                  </button>
                ))}
              </div>
              <p className="text-[11px] font-mono text-cryo-muted leading-relaxed">
                {currentScenarioMeta?.description}
              </p>
            </div>
            {currentScenarioMeta?.scaling_coefficient_alpha && (
              <div className="mt-3 pt-2 border-t border-cryo-border/60 text-[10px] font-mono text-amber-400 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                <span>Pattern Scaling: α = {currentScenarioMeta.scaling_coefficient_alpha} between RCP2.6 & RCP8.5</span>
              </div>
            )}
          </Card>
        </div>

        {/* Spatial Unit Selector */}
        <div className="lg:col-span-4">
          <Card className="h-full flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-cryo-cyan" />
                  <span>Spatial Domain</span>
                </span>
                <span className="text-[10px] font-mono text-slate-400">IMBIE / Region 3</span>
              </div>
              <div className="grid grid-cols-2 gap-2 mb-3">
                {[
                  { id: 'Domain_A', label: 'Domain A', sub: 'Entire Peninsula' },
                  { id: 'Hp-I', label: 'Hp-I', sub: 'Palmer Land West' },
                  { id: 'I-Ipp', label: 'I-Ipp', sub: 'Graham Land' },
                  { id: 'Ipp-J', label: 'Ipp-J', sub: 'Palmer Land East' },
                ].map((unit) => (
                  <button
                    key={unit.id}
                    onClick={() => handleRegionChange(unit.id)}
                    className={`px-3 py-2 rounded text-xs font-mono font-medium border transition-all text-left ${
                      selectedRegion === unit.id
                        ? 'bg-cryo-cyan/20 border-cryo-cyan text-cryo-cyan shadow-sm shadow-cryo-cyan/10'
                        : 'bg-cryo-card/60 border-cryo-border text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-bold">{unit.label}</div>
                    <div className="text-[10px] text-slate-400 truncate">{unit.sub}</div>
                  </button>
                ))}
              </div>
              <p className="text-[11px] font-mono text-cryo-muted">
                {selectedRegion === 'Domain_A'
                  ? 'Aggregate Region 3 covering all three drainage sectors (Hp-I + I-Ipp + Ipp-J).'
                  : selectedRegion === 'Hp-I'
                  ? 'Sector 16: Western Palmer Land & English Coast (Bellingshausen Sea drainage).'
                  : selectedRegion === 'I-Ipp'
                  ? 'Sector 17: Northern Antarctic Peninsula / Graham Land marine-terminating glaciers.'
                  : 'Sector 18: Eastern Palmer Land & Larsen Coast (Weddell Sea drainage).'}
              </p>
            </div>
          </Card>
        </div>

        {/* Target & Envelope Controls */}
        <div className="lg:col-span-3">
          <Card className="h-full flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-cryo-cyan" />
                <span>Display Metric</span>
              </div>
              <div className="grid grid-cols-2 gap-2 mb-3">
                <button
                  onClick={() => handleMetricChange('vaf')}
                  className={`px-2.5 py-2 rounded text-xs font-mono font-medium border text-center transition-all ${
                    targetMetric === 'vaf'
                      ? 'bg-sky-500/20 border-sky-400 text-sky-300'
                      : 'bg-cryo-card/60 border-cryo-border text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="font-bold">ΔVAF</div>
                  <div className="text-[10px] text-slate-400">km³ (Ice)</div>
                </button>
                <button
                  onClick={() => handleMetricChange('sle')}
                  className={`px-2.5 py-2 rounded text-xs font-mono font-medium border text-center transition-all ${
                    targetMetric === 'sle'
                      ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                      : 'bg-cryo-card/60 border-cryo-border text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="font-bold">SLE</div>
                  <div className="text-[10px] text-slate-400">mm (Sea Level)</div>
                </button>
              </div>

              {/* Envelope Toggle */}
              <div className="pt-2 border-t border-cryo-border/60">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={show90Envelope}
                    onChange={(e) => handleToggle90(e.target.checked)}
                    className="w-3.5 h-3.5 rounded bg-slate-900 border-cryo-border text-cryo-cyan focus:ring-cryo-cyan focus:ring-offset-0"
                  />
                  <span className="text-xs font-mono text-slate-300">Show Central 80% Prediction Interval (q10–q90)</span>
                </label>
                <p className="text-[10px] font-mono text-cryo-muted mt-1">
                  Central 68% prediction interval (q16–q84) is displayed by default per scientific protocol.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Main Trajectory Visualization Card */}
      <Card glow>
        <CardHeader
          title={`2015–2100 Future Trajectory: ${trajectoryData?.spatial_unit_name || selectedRegion}`}
          subtitle={`Target: ${
            targetMetric === 'vaf' ? 'Volume Above Flotation Change (ΔVAF, km³)' : 'Sea-Level Equivalent Contribution (SLE, mm)'
          } | Scenario: ${selectedScenario}`}
          icon={<TrendingUp className="w-5 h-5 text-cryo-cyan" />}
          action={
            <div className="flex items-center gap-2">
              <Badge variant="cyan" size="sm">
                {trajectoryData?.scenario_watermark || 'NATIVE_ISMIP6'}
              </Badge>
              <Badge variant="neutral" size="sm">
                86 Annual Steps
              </Badge>
            </div>
          }
        />

        {trajectoryLoading ? (
          <div className="flex flex-col items-center justify-center h-80">
            <LoadingSpinner message="Querying precomputed multi-quantile trajectory..." />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="h-[420px] min-h-[420px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
                  <XAxis
                    dataKey="year"
                    type="number"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                    domain={[2015, 2100]}
                    tickCount={10}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
                    domain={['auto', 'auto']}
                    label={{
                      value: targetMetric === 'vaf' ? 'ΔVAF (km³ ice)' : 'Sea-Level Rise SLE (mm)',
                      angle: -90,
                      position: 'insideLeft',
                      fill: '#94a3b8',
                      fontSize: 12,
                      fontFamily: 'monospace',
                    }}
                  />
                  <ReferenceLine y={0} stroke="#475569" strokeDasharray="4 4" />
                  <Tooltip content={<CustomTooltip targetMetric={targetMetric} show90={show90Envelope} />} />
                  <Legend
                    verticalAlign="top"
                    align="right"
                    wrapperStyle={{ paddingBottom: '12px', fontSize: '11px', fontFamily: 'monospace' }}
                  />

                  {/* Central 80% Prediction Interval (q10 - q90) */}
                  {show90Envelope && (
                    <Area
                      name="Central 80% Prediction Interval (q10–q90)"
                      dataKey="band90"
                      stroke="#818cf8"
                      strokeWidth={1}
                      strokeDasharray="2 2"
                      fill="#6366f1"
                      fillOpacity={0.12}
                      isAnimationActive={false}
                    />
                  )}

                  {/* Central 68% Prediction Interval (q16 - q84, Default) */}
                  <Area
                    name="Central 68% Prediction Interval (q16–q84)"
                    dataKey="band68"
                    stroke="#38bdf8"
                    strokeWidth={1.5}
                    strokeDasharray="4 4"
                    fill="#0284c7"
                    fillOpacity={0.22}
                    isAnimationActive={false}
                  />

                  {/* Median Line (q50) */}
                  <Line
                    type="monotone"
                    name="Median Projection (q50)"
                    dataKey="median"
                    stroke="#00f0ff"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: '#00f0ff', stroke: '#0f172a', strokeWidth: 2 }}
                    isAnimationActive={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Chart Footer Information */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-cryo-border/60 text-xs font-mono text-cryo-muted">
              <div className="flex items-center gap-2">
                <span className="inline-block w-3 h-0.5 bg-cryo-cyan" />
                <span>Solid Cyan: Median (q50)</span>
                <span className="inline-block w-3 h-2 bg-sky-600/30 border border-sky-400 border-dashed ml-3" />
                <span>Shaded Blue: Central 68% Interval (q16–q84)</span>
                {show90Envelope && (
                  <>
                    <span className="inline-block w-3 h-2 bg-indigo-600/20 border border-indigo-400 border-dotted ml-3" />
                    <span>Shaded Purple: Central 80% Interval (q10–q90)</span>
                  </>
                )}
              </div>
              <div className="text-slate-400">
                Conversion: SLE (mm) = - (ΔVAF × 0.917) / 361.8
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Mid-Century (2050) & End-of-Century (2100) Endpoint Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 2050 Summary */}
        <Card>
          <div className="flex items-center justify-between mb-3 border-b border-cryo-border/60 pb-2">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cryo-cyan" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-mono">
                Mid-Century Milestone (2050)
              </h3>
            </div>
            <Badge variant="cyan" size="sm">2050 Horizon</Badge>
          </div>
          {trajectoryData?.summary_2050 ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded bg-cryo-surface/60 border border-cryo-border/60">
                  <div className="text-[11px] text-cryo-muted uppercase">Median ΔVAF (q50)</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {trajectoryData.summary_2050.delta_vaf_median_km3 > 0 ? '+' : ''}
                    {trajectoryData.summary_2050.delta_vaf_median_km3.toFixed(2)}{' '}
                    <span className="text-xs text-cryo-muted font-normal">km³</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Central 68% PI: [{trajectoryData.summary_2050.delta_vaf_16th_km3.toFixed(1)}, {trajectoryData.summary_2050.delta_vaf_84th_km3.toFixed(1)}]
                  </div>
                </div>

                <div className="p-3 rounded bg-cryo-surface/60 border border-cryo-border/60">
                  <div className="text-[11px] text-cryo-muted uppercase">Sea-Level (SLE)</div>
                  <div className="text-lg font-bold text-cryo-cyan mt-0.5">
                    {trajectoryData.summary_2050.sle_median_mm > 0 ? '+' : ''}
                    {trajectoryData.summary_2050.sle_median_mm.toFixed(3)}{' '}
                    <span className="text-xs text-cryo-muted font-normal">mm</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Central 68% PI: [{trajectoryData.summary_2050.sle_16th_mm.toFixed(3)}, {trajectoryData.summary_2050.sle_84th_mm.toFixed(3)}]
                  </div>
                </div>
              </div>

              <div className="p-2.5 rounded bg-cryo-dark/80 border border-cryo-border/40 text-[11px] text-slate-400 flex items-center justify-between">
                <span>Central 80% Prediction Interval (q10–q90):</span>
                <span className="text-slate-200">
                  [{trajectoryData.summary_2050.delta_vaf_10th_km3.toFixed(1)}, {trajectoryData.summary_2050.delta_vaf_90th_km3.toFixed(1)}] km³
                  {' '}(SLE: [{trajectoryData.summary_2050.sle_10th_mm.toFixed(3)}, {trajectoryData.summary_2050.sle_90th_mm.toFixed(3)}] mm)
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs font-mono text-slate-500">2050 summary unavailable.</p>
          )}
        </Card>

        {/* 2100 Summary */}
        <Card glow>
          <div className="flex items-center justify-between mb-3 border-b border-cryo-border/60 pb-2">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-100 font-mono">
                End-of-Century Projection (2100)
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="success" size="sm">2100 Horizon</Badge>
              <Badge
                variant={trajectoryData?.summary_2100?.scenario_watermark === 'NATIVE_ISMIP6' ? 'cyan' : 'warning'}
                size="sm"
              >
                {trajectoryData?.summary_2100?.scenario_watermark}
              </Badge>
            </div>
          </div>
          {trajectoryData?.summary_2100 ? (
            <div className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded bg-cryo-surface/60 border border-cryo-border/60">
                  <div className="text-[11px] text-cryo-muted uppercase">Median ΔVAF (q50)</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {trajectoryData.summary_2100.delta_vaf_median_km3 > 0 ? '+' : ''}
                    {trajectoryData.summary_2100.delta_vaf_median_km3.toFixed(2)}{' '}
                    <span className="text-xs text-cryo-muted font-normal">km³</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Central 68% PI: [{trajectoryData.summary_2100.delta_vaf_16th_km3.toFixed(1)}, {trajectoryData.summary_2100.delta_vaf_84th_km3.toFixed(1)}]
                  </div>
                </div>

                <div className="p-3 rounded bg-cryo-surface/60 border border-cryo-border/60">
                  <div className="text-[11px] text-cryo-muted uppercase">Sea-Level (SLE)</div>
                  <div className="text-lg font-bold text-cryo-cyan mt-0.5">
                    {trajectoryData.summary_2100.sle_median_mm > 0 ? '+' : ''}
                    {trajectoryData.summary_2100.sle_median_mm.toFixed(3)}{' '}
                    <span className="text-xs text-cryo-muted font-normal">mm</span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Central 68% PI: [{trajectoryData.summary_2100.sle_16th_mm.toFixed(3)}, {trajectoryData.summary_2100.sle_84th_mm.toFixed(3)}]
                  </div>
                </div>
              </div>

              <div className="p-2.5 rounded bg-cryo-dark/80 border border-cryo-border/40 text-[11px] text-slate-400 flex items-center justify-between">
                <span>Central 80% Prediction Interval (q10–q90):</span>
                <span className="text-slate-200">
                  [{trajectoryData.summary_2100.delta_vaf_10th_km3.toFixed(1)}, {trajectoryData.summary_2100.delta_vaf_90th_km3.toFixed(1)}] km³
                  {' '}(SLE: [{trajectoryData.summary_2100.sle_10th_mm.toFixed(3)}, {trajectoryData.summary_2100.sle_90th_mm.toFixed(3)}] mm)
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs font-mono text-slate-500">2100 summary unavailable.</p>
          )}
        </Card>
      </div>

      {/* Model Validation & LOMFO Evidence Panel */}
      <Card>
        <CardHeader
          title="Emulator Architecture & Cross-Validation Rigor"
          subtitle="Leave-One-Model-Family-Out (LOMFO) evaluation across 10 independent ice sheet model families"
          icon={<CheckCircle2 className="w-5 h-5 text-cryo-cyan" />}
          action={
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowFoldTable(!showFoldTable)}
              className="text-xs font-mono flex items-center gap-1.5"
            >
              <span>{showFoldTable ? 'Hide 10-Fold Breakdown' : 'View 10-Fold Breakdown'}</span>
              {showFoldTable ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </Button>
          }
        />

        {/* Validation Metric Highlights */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
          <StatCard
            label="LOMFO Out-of-Family R²"
            value={`+${modelInfo?.overall_metrics.oof_r2.toFixed(4) || '0.4843'}`}
            subtext="Beats linear models by > 25x"
            highlight
          />
          <StatCard
            label="Out-of-Family RMSE"
            value={`${modelInfo?.overall_metrics.oof_rmse_km3.toFixed(1) || '567.2'}`}
            unit="km³"
            subtext="63,920 held-out evaluations"
          />
          <StatCard
            label="Out-of-Family MAE"
            value={`${modelInfo?.overall_metrics.oof_mae_km3.toFixed(1) || '256.9'}`}
            unit="km³"
            subtext="Median absolute error"
          />
          <StatCard
            label="Mean Systematic Bias"
            value={`${modelInfo?.overall_metrics.oof_bias_km3.toFixed(1) || '-12.7'}`}
            unit="km³"
            subtext="Minimal persistent bias"
          />
          <StatCard
            label="Empirical 68% Coverage"
            value={`${modelInfo?.overall_metrics.empirical_coverage_pct.toFixed(1) || '62.6'}%`}
            subtext="Nominal target: 68.0%"
            highlight
          />
          <StatCard
            label="Mean Interval Width"
            value={`${modelInfo?.overall_metrics.mean_interval_width_km3.toFixed(1) || '492.3'}`}
            unit="km³"
            subtext="Spread across families"
          />
        </div>

        {/* Candidate Model Comparison Table */}
        <div className="overflow-x-auto mb-4 border border-cryo-border/60 rounded">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-cryo-surface/80 border-b border-cryo-border text-slate-300">
              <tr>
                <th className="px-3 py-2">Candidate Model</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">OOF RMSE (km³)</th>
                <th className="px-3 py-2">OOF MAE (km³)</th>
                <th className="px-3 py-2">OOF R²</th>
                <th className="px-3 py-2">MAE @ 2050</th>
                <th className="px-3 py-2">MAE @ 2100</th>
                <th className="px-3 py-2">Non-Gaussian Quantiles</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cryo-border/40 text-slate-300">
              {modelInfo?.candidate_comparisons.map((c, idx) => {
                const isSelected = c.recommendation.includes('SELECTED');
                return (
                  <tr
                    key={idx}
                    className={isSelected ? 'bg-cryo-cyan/5 font-semibold text-white' : 'hover:bg-slate-900/40'}
                  >
                    <td className="px-3 py-2 flex items-center gap-1.5">
                      {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-cryo-cyan" />}
                      <span>{c.candidate_model_name}</span>
                    </td>
                    <td className="px-3 py-2 text-slate-400">{c.model_type}</td>
                    <td className="px-3 py-2">{c.oof_rmse_km3.toFixed(1)}</td>
                    <td className="px-3 py-2">{c.oof_mae_km3.toFixed(1)}</td>
                    <td className="px-3 py-2 text-cryo-cyan">{c.oof_r2 > 0 ? '+' : ''}{c.oof_r2.toFixed(4)}</td>
                    <td className="px-3 py-2 text-slate-400">{c.mae_2050_km3.toFixed(1)}</td>
                    <td className="px-3 py-2 text-slate-400">{c.mae_2100_km3.toFixed(1)}</td>
                    <td className="px-3 py-2">
                      <Badge variant={c.supports_non_gaussian_quantiles ? 'success' : 'neutral'} size="sm">
                        {c.supports_non_gaussian_quantiles ? 'Yes (Direct)' : 'No'}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">
                      <Badge variant={isSelected ? 'cyan' : 'neutral'} size="sm">
                        {isSelected ? 'SELECTED ENGINE' : 'BENCHMARK'}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Collapsible 10-Fold Breakdown Table */}
        {showFoldTable && (
          <div className="mt-4 pt-4 border-t border-cryo-border/60">
            <h4 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Fold-by-Fold Leave-One-Model-Family-Out Validation Results
            </h4>
            <div className="overflow-x-auto border border-cryo-border/60 rounded">
              <table className="w-full text-left font-mono text-[11px]">
                <thead className="bg-cryo-surface/80 border-b border-cryo-border text-slate-300">
                  <tr>
                    <th className="px-3 py-1.5">Fold</th>
                    <th className="px-3 py-1.5">Withheld Family</th>
                    <th className="px-3 py-1.5">Models List</th>
                    <th className="px-3 py-1.5">Test Rows</th>
                    <th className="px-3 py-1.5">RMSE (km³)</th>
                    <th className="px-3 py-1.5">MAE (km³)</th>
                    <th className="px-3 py-1.5">Bias (km³)</th>
                    <th className="px-3 py-1.5">R²</th>
                    <th className="px-3 py-1.5">68% Coverage</th>
                    <th className="px-3 py-1.5">Spread (km³)</th>
                    <th className="px-3 py-1.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cryo-border/40 text-slate-400">
                  {modelInfo?.lomfo_folds.map((f) => (
                    <tr key={f.fold_index} className="hover:bg-slate-900/40">
                      <td className="px-3 py-1.5 text-white">{f.fold_index}</td>
                      <td className="px-3 py-1.5 font-bold text-slate-200">{f.held_out_family}</td>
                      <td className="px-3 py-1.5 truncate max-w-xs text-[10px] text-slate-500">{f.member_models_list}</td>
                      <td className="px-3 py-1.5">{f.test_records_count.toLocaleString()}</td>
                      <td className="px-3 py-1.5">{f.rmse_km3.toFixed(1)}</td>
                      <td className="px-3 py-1.5">{f.mae_km3.toFixed(1)}</td>
                      <td className="px-3 py-1.5">{f.bias_km3 > 0 ? '+' : ''}{f.bias_km3.toFixed(1)}</td>
                      <td className="px-3 py-1.5 text-cryo-cyan">{f.r2 > 0 ? '+' : ''}{f.r2.toFixed(3)}</td>
                      <td className="px-3 py-1.5 text-slate-200 font-semibold">{f.empirical_coverage_68pct.toFixed(1)}%</td>
                      <td className="px-3 py-1.5">{f.mean_interval_width_km3.toFixed(1)}</td>
                      <td className="px-3 py-1.5">
                        <Badge variant={f.validation_gate_status === 'PASS' ? 'success' : 'neutral'} size="sm">
                          {f.validation_gate_status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Calibration Disclosure Note */}
        <div className="mt-4 p-3 rounded bg-cryo-dark/80 border border-cryo-border/40 text-xs font-mono text-slate-400 flex items-start gap-2.5">
          <Info className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-slate-200">Formal Uncertainty Disclosure:</strong> The nominal 68% prediction interval
            achieved an empirical coverage of <strong>62.6%</strong> across strictly withheld model families. In accordance
            with glaciological reporting standards, these bounds are formally designated as empirical <em>Prediction Intervals</em>,
            not fully calibrated Bayesian credible intervals.
          </div>
        </div>
      </Card>

      {/* Regional Glaciological Interpretation */}
      <Card>
        <CardHeader
          title="Regional Glaciological Contrast & Scientific Interpretation"
          subtitle="Interpreting the modelled divergence between western marine drawdown and eastern snowfall buffering"
          icon={<Compass className="w-5 h-5 text-cryo-cyan" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono text-slate-300">
          <div className="p-4 rounded bg-cryo-surface/40 border border-cryo-border/60 space-y-2">
            <div className="flex items-center gap-2 text-rose-400 font-semibold uppercase tracking-wider">
              <span>Western Marine Drawdown: Sector 17 (I-Ipp)</span>
            </div>
            <p className="leading-relaxed text-slate-400">
              In Graham Land (<strong className="text-slate-200">I-Ipp</strong>), glaciers terminate in deep marine troughs
              on retrograde bedrock slopes directly exposed to upwelling Circumpolar Deep Water (CDW). Under RCP8.5, the median projection
              indicates persistent mass loss (<strong className="text-rose-300">-240.02 km³</strong> by 2100), with the 16th percentile
              reaching <strong className="text-rose-300">-846.82 km³</strong> (contributing <strong className="text-rose-300">+2.15 mm</strong> to global mean sea-level rise).
            </p>
            <div className="text-[11px] text-slate-500 pt-2 border-t border-cryo-border/40">
              Key Mechanism: Marine Ice Sheet Instability (MISI) & sub-shelf cavity melting.
            </div>
          </div>

          <div className="p-4 rounded bg-cryo-surface/40 border border-cryo-border/60 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold uppercase tracking-wider">
              <span>Eastern Snowfall Buffering: Sector 18 (Ipp-J)</span>
            </div>
            <p className="leading-relaxed text-slate-400">
              In Palmer Land East (<strong className="text-slate-200">Ipp-J</strong>), higher atmospheric temperatures in CMIP5 GCMs
              (NorESM1-M and MIROC-ESM-CHEM) drive dramatic increases in precipitation via Clausius-Clapeyron scaling. In coarse continental
              ice models (16–32 km grids), narrow outlet glaciers cannot evacuate mass rapidly, resulting in apparent volume gains
              (<strong className="text-emerald-300">+1,248.58 km³</strong> median by 2100 under RCP8.5).
            </p>
            <div className="text-[11px] text-slate-500 pt-2 border-t border-cryo-border/40">
              Key Mechanism: High-elevation snowfall accumulation outstripping discharge.
            </div>
          </div>
        </div>

        <div className="mt-4 p-3 rounded bg-amber-950/20 border border-amber-500/20 text-[11px] font-mono text-amber-300/80 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>
            <strong>Caveat:</strong> This regional contrast is an interpretation of the modelled multi-model ensemble results,
            not an independently established physical causal finding. Coarse models may systematically overestimate the accumulation buffer.
          </span>
        </div>
      </Card>

      {/* Scientific Disclaimer Footer */}
      <ScientificDisclaimer />
    </div>
  );
};

/**
 * Custom Tooltip for Recharts displaying all quantiles cleanly.
 */
interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string | number;
  targetMetric: 'vaf' | 'sle';
  show90: boolean;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label, targetMetric, show90 }) => {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0]?.payload;
  if (!data) return null;

  const isVaf = targetMetric === 'vaf';
  const unit = isVaf ? 'km³' : 'mm';
  const formatVal = (v: number) => `${v > 0 ? '+' : ''}${v.toFixed(isVaf ? 1 : 3)} ${unit}`;

  return (
    <div className="p-3 bg-slate-950/95 border border-cryo-border rounded shadow-xl font-mono text-xs space-y-1.5 min-w-[200px]">
      <div className="font-bold text-white border-b border-cryo-border/60 pb-1 flex items-center justify-between">
        <span>Year {label}</span>
        <span className="text-[10px] text-cryo-cyan font-normal uppercase">{isVaf ? 'ΔVAF' : 'SLE'}</span>
      </div>
      <div className="space-y-1 text-slate-300 text-[11px]">
        <div className="flex items-center justify-between font-bold text-cryo-cyan">
          <span>Median (q50):</span>
          <span>{formatVal(data.median)}</span>
        </div>
        <div className="flex items-center justify-between text-slate-400">
          <span>Central 68% Interval:</span>
          <span>[{formatVal(data.q16)}, {formatVal(data.q84)}]</span>
        </div>
        {show90 && (
          <div className="flex items-center justify-between text-indigo-300">
            <span>Central 80% Interval:</span>
            <span>[{formatVal(data.q10)}, {formatVal(data.q90)}]</span>
          </div>
        )}
      </div>
    </div>
  );
};
