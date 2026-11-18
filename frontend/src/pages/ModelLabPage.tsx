import React, { useEffect, useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  BarChart3,
  Sliders,
  Layers,
  ArrowRight,
  TrendingDown,
  Info,
  Award,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  Legend,
  LineChart,
  Line
} from 'recharts';
import { CryoApi } from '../api/client';
import { ModelSummary, ModelDetailResponse, HistoricalPredictionItem } from '../api/types';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const ModelLabPage: React.FC = () => {
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('MOD-04');
  const [modelDetail, setModelDetail] = useState<ModelDetailResponse | null>(null);
  const [timeseries, setTimeseries] = useState<HistoricalPredictionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchModels = async () => {
      try {
        setLoading(true);
        const [modelsList, tsData] = await Promise.all([
          CryoApi.getModels(),
          CryoApi.getHistoricalPredictions(),
        ]);
        if (isMounted) {
          setModels(modelsList);
          setTimeseries(tsData);
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to load candidate models from backend.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchModels();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchDetail = async () => {
      try {
        setDetailLoading(true);
        const detail = await CryoApi.getModelDetail(selectedModelId);
        if (isMounted) setModelDetail(detail);
      } catch (err) {
        if (isMounted) {
          console.error('Failed to fetch model detail', err);
        }
      } finally {
        if (isMounted) setDetailLoading(false);
      }
    };

    if (selectedModelId) {
      fetchDetail();
    }
    return () => {
      isMounted = false;
    };
  }, [selectedModelId]);

  if (loading) {
    return <LoadingSpinner message="Loading machine-learning candidate benchmark suite..." />;
  }

  if (error || models.length === 0) {
    return (
      <ErrorMessage
        title="Model Benchmark Unavailable"
        message={error || 'Unable to retrieve evaluated ML candidates.'}
        onRetry={() => window.location.reload()}
      />
    );
  }

  const selectedModel = models.find((m) => m.model_id === selectedModelId) || models[0];

  // Comparison Bar Chart Data (Test MAE across all 6 models)
  const comparisonChartData = models.map((m) => ({
    name: m.model_name,
    id: m.model_id,
    testMAE: m.test_trainonly_mae_gt_yr,
    valMAE: m.validation_mae_gt_yr,
    r2: m.test_trainonly_r2,
    isSelected: m.model_id === selectedModelId,
    isPrimary: m.model_id === 'MOD-04',
  }));

  // Feature weights data for the selected model
  let featureWeightData: { feature: string; value: number }[] = [];
  if (modelDetail?.feature_coefficients) {
    featureWeightData = Object.entries(modelDetail.feature_coefficients)
      .map(([feature, value]) => ({ feature, value: parseFloat(value.toFixed(4)) }))
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  } else if (modelDetail?.feature_importances) {
    featureWeightData = Object.entries(modelDetail.feature_importances)
      .map(([feature, value]) => ({ feature, value: parseFloat(value.toFixed(4)) }))
      .sort((a, b) => b.value - a.value);
  }

  // Model-specific actual vs predicted timeseries
  const modelKeyMap: Record<string, string> = {
    'MOD-01': 'Historical_Basin_Mean',
    'MOD-02': 'Persistence',
    'MOD-03': 'Bayesian_Ridge',
    'MOD-04': 'ElasticNet',
    'MOD-05': 'Random_Forest',
    'MOD-06': 'Gradient_Boosting',
  };
  const activePredKey = modelKeyMap[selectedModelId] || 'ElasticNet';

  // Aggregate annual mean across basins for this model
  const years = Array.from(new Set(timeseries.map((t) => t.year))).sort((a, b) => a - b);
  const actualVsPredData = years.map((yr) => {
    const yrRows = timeseries.filter((t) => t.year === yr);
    const obsTotal = yrRows.reduce((sum, r) => sum + r.observed_mass_balance_gt_yr, 0);
    const predTotal = yrRows.reduce((sum, r) => {
      const pred = r.model_predictions[activePredKey];
      return sum + (pred?.pred_mb_gt_yr ?? 0);
    }, 0);

    return {
      year: yr,
      observed: parseFloat(obsTotal.toFixed(2)),
      predicted: parseFloat(predTotal.toFixed(2)),
      split: yrRows[0]?.split_status ?? 'TRAINING',
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Supervised Benchmark</Badge>
            <Badge variant="neutral">Chronological Split (1979-2024)</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Model Laboratory & Evaluation Suite
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Multi-model architectural benchmarking against observed Antarctic Peninsula basin mass balances.
            ElasticNet (MOD-04) frozen as the primary operational benchmark.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="success" className="px-3 py-1">Zero Data Leakage</Badge>
        </div>
      </div>

      {/* Model Selector Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {models.map((m) => {
          const isSelected = m.model_id === selectedModelId;
          const isPrimary = m.model_id === 'MOD-04';

          return (
            <button
              key={m.model_id}
              onClick={() => setSelectedModelId(m.model_id)}
              className={`p-3 rounded-lg border text-left transition-all relative flex flex-col justify-between ${
                isSelected
                  ? 'bg-cryo-card border-cryo-cyan shadow-lg shadow-cryo-cyan/5 ring-1 ring-cryo-cyan/50'
                  : 'bg-cryo-dark/80 border-cryo-border hover:border-slate-700 hover:bg-slate-900/60'
              }`}
            >
              {isPrimary && (
                <div className="absolute top-2 right-2">
                  <Award className="w-3.5 h-3.5 text-emerald-400" />
                </div>
              )}
              <div>
                <span className="text-[10px] font-mono text-cryo-muted uppercase tracking-wider block">
                  {m.model_id}
                </span>
                <span className="text-xs font-bold font-mono text-white block mt-0.5 truncate">
                  {m.model_name}
                </span>
              </div>
              <div className="mt-3 pt-2 border-t border-cryo-border/40 text-[11px] font-mono flex items-center justify-between">
                <span className="text-slate-400">Test MAE:</span>
                <span className={`font-semibold ${isPrimary ? 'text-emerald-400' : 'text-slate-200'}`}>
                  {m.test_trainonly_mae_gt_yr.toFixed(2)}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Model Evaluation Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Selected Model Detailed Spec */}
        <Card className="lg:col-span-1 flex flex-col justify-between">
          <div>
            <CardHeader
              title={selectedModel.model_name}
              subtitle={selectedModel.model_class}
              icon={<Cpu className="w-4 h-4" />}
              action={
                selectedModel.model_id === 'MOD-04' ? (
                  <Badge variant="success">Primary Selected</Badge>
                ) : (
                  <Badge variant="neutral">{selectedModel.model_id}</Badge>
                )
              }
            />

            <div className="space-y-3 text-xs font-mono">
              <div className="p-3 rounded bg-cryo-surface border border-cryo-border">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Hyperparameters:
                </span>
                <span className="text-xs text-cryo-cyan font-mono break-words leading-relaxed mt-1 block">
                  {selectedModel.hyperparameters}
                </span>
              </div>

              {/* Metric Breakdown Table */}
              <div className="space-y-1.5 pt-1">
                <div className="flex justify-between py-1 border-b border-cryo-border/40">
                  <span className="text-slate-400">Held-Out Test MAE:</span>
                  <span className="font-semibold text-slate-100">{selectedModel.test_trainonly_mae_gt_yr} Gt/yr</span>
                </div>
                <div className="flex justify-between py-1 border-b border-cryo-border/40">
                  <span className="text-slate-400">Held-Out Test RMSE:</span>
                  <span className="font-semibold text-slate-100">{selectedModel.test_trainonly_rmse_gt_yr} Gt/yr</span>
                </div>
                <div className="flex justify-between py-1 border-b border-cryo-border/40">
                  <span className="text-slate-400">Held-Out Test R²:</span>
                  <span className={`font-semibold ${selectedModel.test_trainonly_r2 > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {selectedModel.test_trainonly_r2.toFixed(3)}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-cryo-border/40">
                  <span className="text-slate-400">Validation MAE:</span>
                  <span className="font-semibold text-slate-100">{selectedModel.validation_mae_gt_yr} Gt/yr</span>
                </div>
                <div className="flex justify-between py-1 border-b border-cryo-border/40">
                  <span className="text-slate-400">Validation Bias:</span>
                  <span className="font-semibold text-slate-100">{selectedModel.validation_bias_gt_yr} Gt/yr</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Improvement vs Baseline:</span>
                  <span className="font-semibold text-cryo-cyan">
                    +{selectedModel.test_mae_improvement_pct.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-cryo-border/60 text-[11px] font-mono text-cryo-muted flex items-center justify-between">
            <span>Inference Support:</span>
            <Badge variant="cyan">Available in API</Badge>
          </div>
        </Card>

        {/* Model Comparative Benchmark Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Held-Out Test Performance Across All Six Candidates"
            subtitle="Mean Absolute Error (Gt/year) evaluated on untouched 2016-2024 test window."
            icon={<BarChart3 className="w-4 h-4" />}
          />
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonChartData} margin={{ top: 15, right: 20, left: -10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#64748B"
                  tick={{ fontSize: 10, fontFamily: 'monospace' }}
                  interval={0}
                  angle={-15}
                  textAnchor="end"
                />
                <YAxis
                  stroke="#64748B"
                  tick={{ fontSize: 11, fontFamily: 'monospace' }}
                  unit=" Gt/yr"
                  domain={[0, 16]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#1E293B',
                    borderRadius: '6px',
                    fontFamily: 'monospace',
                    fontSize: '12px',
                  }}
                  formatter={(val: any) => [`${val} Gt/year`, 'Test MAE']}
                />
                <Bar dataKey="testMAE" radius={[4, 4, 0, 0]}>
                  {comparisonChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.id === 'MOD-04'
                          ? '#10B981'
                          : entry.isSelected
                          ? '#38BDF8'
                          : '#334155'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-6 mt-2 text-[11px] font-mono text-cryo-muted">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-emerald-500" />
              <span>ElasticNet (Selected Primary: 9.61 Gt/yr)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-sky-400" />
              <span>Active Selection</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-slate-700" />
              <span>Evaluated Candidates</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Actual vs Predicted Historical Results for Selected Model */}
      <Card>
        <CardHeader
          title={`Observed vs Predicted Trajectory — ${selectedModel.model_name}`}
          subtitle={`Annual integrated mass balance (Gt/yr) across all 3 basins over the 1979-2024 observation timeline.`}
          icon={<TrendingDown className="w-4 h-4" />}
        />
        <div className="h-72 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={actualVsPredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="year" stroke="#64748B" tick={{ fontSize: 11, fontFamily: 'monospace' }} />
              <YAxis stroke="#64748B" tick={{ fontSize: 11, fontFamily: 'monospace' }} unit=" Gt/yr" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0F172A',
                  borderColor: '#1E293B',
                  borderRadius: '6px',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ paddingTop: '10px', fontFamily: 'monospace', fontSize: '11px' }} />
              <Line
                type="monotone"
                dataKey="observed"
                name="Observed Mass Balance (Gt/yr)"
                stroke="#38BDF8"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="predicted"
                name={`${selectedModel.model_name} Prediction (Gt/yr)`}
                stroke="#10B981"
                strokeWidth={1.75}
                strokeDasharray="4 3"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Per-Basin Performance Breakdown Table */}
      {modelDetail?.basin_performance && modelDetail.basin_performance.length > 0 && (
        <Card>
          <CardHeader
            title="Per-Basin Fold Validation Breakdown"
            subtitle="Evaluation across individual Peninsula drainage sectors."
            icon={<Sliders className="w-4 h-4" />}
          />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-cryo-surface text-slate-400 border-b border-cryo-border uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Basin ID</th>
                  <th className="py-2.5 px-3">Basin Name</th>
                  <th className="py-2.5 px-3">Evaluation Fold</th>
                  <th className="py-2.5 px-3">True Mean (Gt/yr)</th>
                  <th className="py-2.5 px-3">Pred Mean (Gt/yr)</th>
                  <th className="py-2.5 px-3">RMSE (Gt/yr)</th>
                  <th className="py-2.5 px-3">MAE (Gt/yr)</th>
                  <th className="py-2.5 px-3">Bias (Gt/yr)</th>
                  <th className="py-2.5 px-3">R²</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cryo-border/60 text-slate-200">
                {modelDetail.basin_performance.map((bp, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 font-semibold text-cryo-cyan">{bp.basin_id}</td>
                    <td className="py-2.5 px-3 text-slate-300">{bp.basin_name}</td>
                    <td className="py-2.5 px-3 text-slate-400">{bp.evaluation_fold}</td>
                    <td className="py-2.5 px-3">{bp.true_mean_gt_yr.toFixed(2)}</td>
                    <td className="py-2.5 px-3">{bp.pred_mean_gt_yr.toFixed(2)}</td>
                    <td className="py-2.5 px-3">{bp.rmse_gt_yr.toFixed(2)}</td>
                    <td className="py-2.5 px-3 font-semibold text-white">{bp.mae_gt_yr.toFixed(2)}</td>
                    <td className="py-2.5 px-3">{bp.mean_bias_gt_yr.toFixed(2)}</td>
                    <td className={`py-2.5 px-3 font-semibold ${bp.r2 >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {bp.r2.toFixed(3)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Feature Importance / Coefficient Bar Chart */}
      {featureWeightData.length > 0 && (
        <Card>
          <CardHeader
            title={
              modelDetail?.feature_coefficients
                ? `Learned Coefficients — ${selectedModel.model_name}`
                : `Feature Importance — ${selectedModel.model_name}`
            }
            subtitle={
              modelDetail?.feature_coefficients
                ? 'Standardized linear model regression weights under L1/L2 regularization.'
                : 'Ensemble Gini feature impurity reduction across decision trees.'
            }
            icon={<Sliders className="w-4 h-4" />}
          />
          <div className="h-80 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={featureWeightData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 180, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                <XAxis
                  type="number"
                  stroke="#64748B"
                  tick={{ fontSize: 10, fontFamily: 'monospace' }}
                />
                <YAxis
                  dataKey="feature"
                  type="category"
                  stroke="#94A3B8"
                  tick={{ fontSize: 10, fontFamily: 'monospace' }}
                  width={170}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#1E293B',
                    borderRadius: '6px',
                    fontFamily: 'monospace',
                    fontSize: '11px',
                  }}
                />
                <Bar dataKey="value" name="Coefficient / Importance" radius={[0, 4, 4, 0]}>
                  {featureWeightData.map((entry, index) => (
                    <Cell
                      key={`feat-${index}`}
                      fill={
                        entry.value === 0
                          ? '#334155'
                          : entry.value > 0
                          ? '#10B981'
                          : '#F43F5E'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-cryo-border/60 text-[11px] font-mono text-cryo-muted">
            <div>
              <span className="text-emerald-400">Green: Positive Effect</span> &bull;{' '}
              <span className="text-rose-400">Red: Negative Effect</span> &bull;{' '}
              <span className="text-slate-500">Grey: Zero / Sparsity Pruned</span>
            </div>
            <div className="text-slate-400">
              Active Features: {featureWeightData.filter((f) => f.value !== 0).length} of 14
            </div>
          </div>
        </Card>
      )}

      {/* Scientific Disclaimer */}
      <ScientificDisclaimer />
    </div>
  );
};
