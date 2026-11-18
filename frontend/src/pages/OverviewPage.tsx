import React, { useEffect, useState } from 'react';
import {
  Compass,
  Layers,
  Database,
  ShieldCheck,
  TrendingDown,
  Activity,
  ArrowUpRight,
  Info,
  Calendar,
  Box
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  BarChart,
  Bar
} from 'recharts';
import { CryoApi } from '../api/client';
import { OverviewResponse, HistoricalPredictionItem } from '../api/types';
import { Card, CardHeader } from '../components/common/Card';
import { StatCard } from '../components/common/StatCard';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const OverviewPage: React.FC = () => {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [timeseries, setTimeseries] = useState<HistoricalPredictionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBasin, setSelectedBasin] = useState<string>('ALL');

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [ovData, tsData] = await Promise.all([
          CryoApi.getOverview(),
          CryoApi.getHistoricalPredictions(),
        ]);
        if (isMounted) {
          setOverview(ovData);
          setTimeseries(tsData);
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to fetch overview research data from the backend.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchData();
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return <LoadingSpinner message="Querying Antarctic Peninsula glaciological baseline..." />;
  }

  if (error || !overview) {
    return (
      <ErrorMessage
        title="Failed to Load Overview Data"
        message={error || 'Unable to connect to the backend research API.'}
        onRetry={() => window.location.reload()}
      />
    );
  }

  // Aggregate annual timeseries across all 3 basins or filter by selectedBasin
  const years = Array.from(new Set(timeseries.map((t) => t.year))).sort((a, b) => a - b);
  const chartData = years.map((year) => {
    const yearRows = timeseries.filter(
      (t) => t.year === year && (selectedBasin === 'ALL' || t.basin_id === selectedBasin)
    );
    const totalObsMB = yearRows.reduce((acc, curr) => acc + curr.observed_mass_balance_gt_yr, 0);
    const totalObsVol = yearRows.reduce((acc, curr) => acc + curr.observed_volume_change_km3_yr, 0);
    const elasticNetMB = yearRows.reduce(
      (acc, curr) => acc + (curr.model_predictions.ElasticNet?.pred_mb_gt_yr ?? 0),
      0
    );
    const elasticNetVol = yearRows.reduce(
      (acc, curr) => acc + (curr.model_predictions.ElasticNet?.pred_vol_km3_yr ?? 0),
      0
    );

    return {
      year,
      observedMassBalance: parseFloat(totalObsMB.toFixed(2)),
      observedVolumeChange: parseFloat(totalObsVol.toFixed(2)),
      elasticNetMassBalance: parseFloat(elasticNetMB.toFixed(2)),
      elasticNetVolumeChange: parseFloat(elasticNetVol.toFixed(2)),
    };
  });

  return (
    <div className="space-y-6">
      {/* Top Banner / Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Academic Research Platform</Badge>
            <Badge variant="neutral">Domain A (866,358 Cells)</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Antarctic Peninsula Ice Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Physics-informed cryospheric modeling and supervised machine-learning historical benchmarking
            across drainage basins Hp-I, I-Ipp, and Ipp-J (1979–2024).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="success" className="px-3 py-1">Baseline Frozen</Badge>
        </div>
      </div>

      {/* Primary Glaciological Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Grounded Area"
          value={overview.total_grounded_area_km2.toLocaleString()}
          unit="km²"
          subtext="BedMachine v4.1 reconciled mask"
          icon={<Compass className="w-4 h-4" />}
          highlight
        />
        <StatCard
          label="Baseline Ice Volume"
          value={overview.total_ice_volume_km3.toLocaleString()}
          unit="km³"
          subtext="140,702.51 km³ solid-ice equivalent"
          icon={<Box className="w-4 h-4" />}
        />
        <StatCard
          label="Historical Period"
          value={overview.temporal_coverage}
          unit="46 Yrs"
          subtext="Annual observations (1979-2024)"
          icon={<Calendar className="w-4 h-4" />}
        />
        <StatCard
          label="Ice Density Metric"
          value={overview.solid_ice_density_kg_m3}
          unit="kg/m³"
          subtext="ΔV = ΔM / 0.917 Gt/km³ conversion"
          icon={<Activity className="w-4 h-4" />}
        />
      </div>

      {/* Historical Ice Volume Change Chart Card */}
      <Card>
        <CardHeader
          title="Historical Mass Balance & Volume Change Dynamics (1979–2024)"
          subtitle="Observed historical trajectory compared against regularized ElasticNet primary benchmark predictions."
          icon={<TrendingDown className="w-4 h-4" />}
          action={
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-cryo-muted mr-1">Filter Basin:</span>
              {(['ALL', 'Hp-I', 'I-Ipp', 'Ipp-J'] as const).map((b) => (
                <button
                  key={b}
                  onClick={() => setSelectedBasin(b)}
                  className={`px-2.5 py-1 rounded text-[11px] font-semibold border transition-colors ${
                    selectedBasin === b
                      ? 'bg-cryo-cyan/20 border-cryo-cyan text-cryo-cyan'
                      : 'border-cryo-border bg-cryo-surface text-slate-400 hover:text-white'
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>
          }
        />

        <div className="h-80 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="obsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="predGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="year" stroke="#64748B" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis
                stroke="#64748B"
                tick={{ fontSize: 11, fontFamily: 'monospace' }}
                unit=" Gt/yr"
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0F172A',
                  borderColor: '#1E293B',
                  borderRadius: '6px',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                }}
              />
              <Legend
                wrapperStyle={{
                  paddingTop: '12px',
                  fontFamily: 'monospace',
                  fontSize: '11px',
                }}
              />
              <Area
                type="monotone"
                dataKey="observedMassBalance"
                name="Observed Mass Balance (Gt/yr)"
                stroke="#38BDF8"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#obsGradient)"
              />
              <Area
                type="monotone"
                dataKey="elasticNetMassBalance"
                name="ElasticNet Model (Gt/yr)"
                stroke="#10B981"
                strokeWidth={1.5}
                strokeDasharray="4 2"
                fillOpacity={1}
                fill="url(#predGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-3 pt-3 border-t border-cryo-border/60 flex flex-wrap items-center justify-between text-[11px] font-mono text-cryo-muted">
          <div>
            Domain Total Grounded Area: <span className="text-slate-200">216,062.17 km²</span> &bull; 
            Total Observations: <span className="text-slate-200">138 Basin-Years</span>
          </div>
          <div className="text-cryo-cyan">
            ElasticNet Refit MAE: 9.52 Gt/yr (21.0% improvement over historical baseline)
          </div>
        </div>
      </Card>

      {/* Three Study Basins Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {overview.basins.map((b) => (
          <Card key={b.basin_id} className="relative flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <Badge variant={b.basin_id === 'Hp-I' ? 'cyan' : b.basin_id === 'I-Ipp' ? 'warning' : 'purple'}>
                  {b.basin_id}
                </Badge>
                <span className="text-xs font-mono text-slate-400">
                  {((b.grounded_area_km2 / overview.total_grounded_area_km2) * 100).toFixed(1)}% of Domain
                </span>
              </div>
              <h3 className="text-base font-bold font-mono text-white mb-1">{b.name}</h3>
              <p className="text-xs text-cryo-muted font-mono leading-relaxed mb-4">
                {b.description}
              </p>
            </div>

            <div className="pt-3 border-t border-cryo-border/60 space-y-1.5 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-slate-500">Grounded Area:</span>
                <span className="text-slate-200 font-semibold">{b.grounded_area_km2.toLocaleString()} km²</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Physical Regime:</span>
                <span className="text-cryo-ice">
                  {b.basin_id === 'Hp-I'
                    ? 'Marine-Terminating'
                    : b.basin_id === 'I-Ipp'
                    ? 'Alpine Tributary'
                    : 'Weddell Embayment'}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Scientific Methodology & Architecture Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card>
          <CardHeader
            title="Physical Modeling Framework (Stage 5.1)"
            subtitle="2D Shallow Shelf Approximation (SSA) Finite-Volume Formulation"
            icon={<Layers className="w-4 h-4" />}
          />
          <div className="space-y-3 text-xs font-mono text-slate-300 leading-relaxed">
            <p>
              The physical foundation employs a non-linear Shallow Shelf Approximation (SSA) solver discretized on a
              regular finite-volume grid across 866,358 grounded cells in Antarctic Peninsula Domain A.
            </p>
            <div className="grid grid-cols-2 gap-2 p-3 rounded bg-cryo-surface border border-cryo-border text-[11px]">
              <div>
                <span className="text-slate-500 block">Glen's Exponent:</span>
                <span className="text-white font-semibold">n = 3 (Glen Rheology)</span>
              </div>
              <div>
                <span className="text-slate-500 block">Basal Traction Law:</span>
                <span className="text-white font-semibold">Weertman / Schoof Regularized</span>
              </div>
              <div>
                <span className="text-slate-500 block">Grounding-Line Flux:</span>
                <span className="text-white font-semibold">Schoof Boundary Formulation</span>
              </div>
              <div>
                <span className="text-slate-500 block">Mass Conservation:</span>
                <span className="text-white font-semibold">Finite-Volume Divergence Gate</span>
              </div>
            </div>
            <p className="text-cryo-muted text-[11px]">
              Solver configuration enforces calibrated friction coefficients (C_bed) anchored to Ryder Bay
              and Larsen tributary diagnostics, with full WGS84 face-length metrics.
            </p>
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Machine-Learning Benchmark Status"
            subtitle="Stage 6.1 Supervised Evaluation & Stage 6.2 Reproducibility Freeze"
            icon={<ShieldCheck className="w-4 h-4" />}
          />
          <div className="space-y-3 text-xs font-mono text-slate-300 leading-relaxed">
            <p>
              Six candidate architectures were rigorously evaluated against a chronological split (1979–2005 training,
              2008–2014 validation, 2016–2024 held-out test) with multi-year embargos:
            </p>
            <div className="p-3 rounded bg-cryo-surface border border-cryo-border space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-emerald-400">Selected Primary: ElasticNet (MOD-04)</span>
                <Badge variant="success">Test MAE: 9.61 Gt/yr</Badge>
              </div>
              <p className="text-[11px] text-cryo-muted">
                Outperformed historical mean baseline by 21.0% on held-out test data. Selected over non-linear tree
                ensembles to mitigate severe overfit risks in high-noise altimetry regimes.
              </p>
            </div>
            <p className="text-cryo-muted text-[11px]">
              All 14 features adhere strictly to frozen physical definitions (RACMO SMB, satellite flux gates,
              BedMachine baseline geometry).
            </p>
          </div>
        </Card>
      </div>

      {/* Mandatory Scientific Disclosures */}
      <ScientificDisclaimer
        title="Scientific Disclosures & Scope Governance"
        disclosures={overview.scientific_disclosures}
      />
    </div>
  );
};
