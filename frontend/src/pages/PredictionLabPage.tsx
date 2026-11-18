import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Play,
  RotateCcw,
  ShieldAlert,
  CheckCircle,
  AlertTriangle,
  Info,
  Layers,
  Sparkles,
  ArrowRight,
  Database,
  Calendar,
  Sliders,
  HelpCircle,
  Copy,
  Clock,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { CryoApi, formatApiError } from '../api/client';
import {
  FeatureItem,
  InferenceRequest,
  InferenceResponse,
  ModelSummary,
  FeaturePayload,
  HistoricalFeaturesResponse
} from '../api/types';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

// Default initial features for manual mode (Hp-I 2020 baseline)
const DEFAULT_MANUAL_FEATURES: FeaturePayload = {
  Target_Volume_Change_Lag1_km3_yr: -17.52,
  Target_Volume_Change_Lag2_km3_yr: -16.48,
  Net_MB_Lag1_Gt_yr: -16.07,
  SMB_Lag1_Gt_yr: 72.45,
  Discharge_Lag1_Gt_yr: 88.52,
  SMB_Rolling3yr_Gt_yr: 74.20,
  SMB_Anomaly_Lag1_Gt_yr: -3.85,
  Grounded_Area_km2: 108945.63,
  Mean_Baseline_Ice_Thickness_m: 1482.40,
  Bed_Elevation_at_Gates_m: -124.20,
  Driving_Stress_Index_kPa: 105.40,
  is_Hp_I: 1.0,
  is_I_Ipp: 0.0,
  is_Ipp_J: 0.0,
};

export const PredictionLabPage: React.FC = () => {
  // Mode selection: Mode A (Historical) vs Mode B (Manual)
  const [activeMode, setActiveMode] = useState<'historical' | 'manual'>('historical');

  // Metadata State
  const [featureDict, setFeatureDict] = useState<FeatureItem[]>([]);
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [loadingMeta, setLoadingMeta] = useState<boolean>(true);
  const [initError, setInitError] = useState<string | null>(null);

  // Common Configuration
  const [selectedModelId, setSelectedModelId] = useState<string>('MOD-04');
  const [selectedBasin, setSelectedBasin] = useState<string>('Hp-I');

  // Mode A: Historical State
  const [historicalYear, setHistoricalYear] = useState<number>(2020);
  const [historicalData, setHistoricalData] = useState<HistoricalFeaturesResponse | null>(null);
  const [loadingHistorical, setLoadingHistorical] = useState<boolean>(false);
  const [historicalFetchError, setHistoricalFetchError] = useState<string | null>(null);

  // Mode B: Manual State
  const [manualFeatures, setManualFeatures] = useState<FeaturePayload>(DEFAULT_MANUAL_FEATURES);
  const [templateYear, setTemplateYear] = useState<number>(2020);
  const [templateBasin, setTemplateBasin] = useState<string>('Hp-I');
  const [loadingTemplate, setLoadingTemplate] = useState<boolean>(false);

  // Execution & Response State
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [predictionResult, setPredictionResult] = useState<InferenceResponse | null>(null);
  const [inferenceError, setInferenceError] = useState<string | null>(null);
  const [showFeatureVector, setShowFeatureVector] = useState<boolean>(false);

  // Initial metadata fetch
  useEffect(() => {
    let isMounted = true;
    const fetchMetadata = async () => {
      try {
        setLoadingMeta(true);
        const [features, modelsList] = await Promise.all([
          CryoApi.getFeatures(),
          CryoApi.getModels(),
        ]);
        if (isMounted) {
          setFeatureDict(features);
          setModels(modelsList);
        }
      } catch (err) {
        if (isMounted) {
          setInitError('Failed to load feature definitions and model catalog from backend.');
        }
      } finally {
        if (isMounted) setLoadingMeta(false);
      }
    };

    fetchMetadata();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch legitimate antecedent features for Mode A
  const fetchHistoricalRecord = useCallback(async (basin: string, year: number) => {
    try {
      setLoadingHistorical(true);
      setHistoricalFetchError(null);
      const data = await CryoApi.getHistoricalFeatures(basin, year);
      setHistoricalData(data);
    } catch (err) {
      setHistoricalFetchError(formatApiError(err));
      setHistoricalData(null);
    } finally {
      setLoadingHistorical(false);
    }
  }, []);

  // Sync historical features whenever basin or year changes in Mode A
  useEffect(() => {
    if (activeMode === 'historical') {
      fetchHistoricalRecord(selectedBasin, historicalYear);
    }
  }, [activeMode, selectedBasin, historicalYear, fetchHistoricalRecord]);

  // Handle Mode Change
  const handleModeSwitch = (newMode: 'historical' | 'manual') => {
    setActiveMode(newMode);
    setPredictionResult(null);
    setInferenceError(null);
  };

  // Handle manual basin change: keep indicator flags synchronized
  const handleManualBasinChange = (basin: string) => {
    setSelectedBasin(basin);
    setManualFeatures((prev) => ({
      ...prev,
      is_Hp_I: basin === 'Hp-I' ? 1.0 : 0.0,
      is_I_Ipp: basin === 'I-Ipp' ? 1.0 : 0.0,
      is_Ipp_J: basin === 'Ipp-J' ? 1.0 : 0.0,
    }));
  };

  // Handle manual feature input change
  const handleManualFeatureChange = (key: keyof FeaturePayload, valStr: string) => {
    const val = parseFloat(valStr);
    setManualFeatures((prev) => ({
      ...prev,
      [key]: isNaN(val) ? 0 : val,
    }));
  };

  // Load a historical year as template into Manual mode
  const handleLoadTemplate = async () => {
    try {
      setLoadingTemplate(true);
      const data = await CryoApi.getHistoricalFeatures(templateBasin, templateYear);
      setManualFeatures({ ...data.features });
      setSelectedBasin(templateBasin);
    } catch (err) {
      setInferenceError(`Could not load template: ${formatApiError(err)}`);
    } finally {
      setLoadingTemplate(false);
    }
  };

  // Run Inference Execution
  const handleExecuteInference = async () => {
    setSubmitting(true);
    setInferenceError(null);

    let payload: InferenceRequest;

    if (activeMode === 'historical') {
      if (!historicalData) {
        setInferenceError('Historical feature record is unavailable for the selected basin and year.');
        setSubmitting(false);
        return;
      }
      payload = {
        model_id: selectedModelId,
        basin_id: selectedBasin,
        features: historicalData.features,
        target_year: historicalYear,
        forecast_year: historicalYear,
        inference_mode: 'historical',
      };
    } else {
      payload = {
        model_id: selectedModelId,
        basin_id: selectedBasin,
        features: {
          ...manualFeatures,
          is_Hp_I: selectedBasin === 'Hp-I' ? 1.0 : 0.0,
          is_I_Ipp: selectedBasin === 'I-Ipp' ? 1.0 : 0.0,
          is_Ipp_J: selectedBasin === 'Ipp-J' ? 1.0 : 0.0,
        },
        target_year: undefined,
        forecast_year: undefined,
        inference_mode: 'manual',
      };
    }

    try {
      const response = await CryoApi.runInference(payload);
      setPredictionResult(response);
    } catch (err) {
      setInferenceError(formatApiError(err));
      setPredictionResult(null);
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingMeta) {
    return <LoadingSpinner message="Initializing live inference engine & feature schemas..." />;
  }

  if (initError) {
    return (
      <ErrorMessage
        title="Inference Engine Offline"
        message={initError}
        onRetry={() => window.location.reload()}
      />
    );
  }

  // Generate list of 46 historical years: 1979 - 2024
  const historicalYearsList = Array.from({ length: 46 }, (_, i) => 2024 - i);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Live ML Engine</Badge>
            <Badge variant="neutral">POST /api/predictions/run</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Prediction Laboratory & Inference Console
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Execute real-time model inference using verified serialized scikit-learn artifacts.
            Evaluate historical observational telemetry or explore custom physical scenario vectors.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="warning" className="px-2.5 py-1">
            Historical 1-Year Horizon
          </Badge>
        </div>
      </div>

      {/* Prominent Mode Switcher */}
      <div className="bg-cryo-surface border border-cryo-border rounded-xl p-1.5 flex flex-col sm:flex-row gap-1.5">
        <button
          type="button"
          onClick={() => handleModeSwitch('historical')}
          className={`flex-1 flex items-center justify-center gap-2.5 px-4 py-3 rounded-lg text-xs font-mono font-semibold transition-all ${
            activeMode === 'historical'
              ? 'bg-cryo-cyan/20 border border-cryo-cyan text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cryo-surface/60 border border-transparent'
          }`}
        >
          <Clock className={`w-4 h-4 ${activeMode === 'historical' ? 'text-cryo-cyan' : 'text-slate-500'}`} />
          <div className="text-left">
            <div>Mode A: Historical Inference</div>
            <div className="text-[10px] font-normal text-cryo-muted">
              Auto-resolves strictly antecedent features (1979–2024)
            </div>
          </div>
        </button>

        <button
          type="button"
          onClick={() => handleModeSwitch('manual')}
          className={`flex-1 flex items-center justify-center gap-2.5 px-4 py-3 rounded-lg text-xs font-mono font-semibold transition-all ${
            activeMode === 'manual'
              ? 'bg-cryo-cyan/20 border border-cryo-cyan text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-cryo-surface/60 border border-transparent'
          }`}
        >
          <Sliders className={`w-4 h-4 ${activeMode === 'manual' ? 'text-cryo-cyan' : 'text-slate-500'}`} />
          <div className="text-left">
            <div>Mode B: Manual Inference & Scenarios</div>
            <div className="text-[10px] font-normal text-cryo-muted">
              Configure arbitrary 14-feature physical vectors (Year N/A)
            </div>
          </div>
        </button>
      </div>

      {/* Scientific Clarification Notice */}
      <div className="p-3.5 rounded-lg border border-cryo-border bg-cryo-surface/60 text-xs font-mono space-y-1">
        <div className="flex items-center gap-2 text-cryo-cyan font-semibold">
          <Info className="w-4 h-4 flex-shrink-0" />
          <span>Glaciological Model Architecture Notice</span>
        </div>
        <p className="text-[11px] text-slate-300 leading-relaxed">
          <strong>Calendar year is NOT an input feature to the model.</strong> The trained benchmark operates on a 14-dimensional feature vector x &isin; &reals;<sup>14</sup>.
          In <strong>Historical Mode</strong>, selecting a year dynamically retrieves legitimate antecedent records (Lag-1 at t&minus;1, Lag-2 at t&minus;2, and rolling SMB at [t&minus;3, t&minus;1]) with zero future lookahead.
          Future projections (e.g., 2025+) require explicit scenario assumptions because external climate forcing (SMB, discharge) cannot be extrapolated from calendar year alone.
        </p>
      </div>

      {/* Main Workspace Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Control Panel: Form / Configuration */}
        <div className="lg:col-span-7 space-y-5">
          {/* Architecture & Basin Selectors */}
          <Card>
            <CardHeader
              title="Execution Setup"
              subtitle="Select model architecture and drainage basin."
              icon={<Layers className="w-4 h-4 text-cryo-cyan" />}
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <label className="text-slate-400 block mb-1">Architecture:</label>
                <select
                  value={selectedModelId}
                  onChange={(e) => setSelectedModelId(e.target.value)}
                  className="w-full bg-cryo-surface border border-cryo-border rounded px-3 py-2 text-white font-mono focus:outline-none focus:border-cryo-cyan"
                >
                  {models.map((m) => (
                    <option key={m.model_id} value={m.model_id}>
                      {m.model_id} — {m.model_name}
                    </option>
                  ))}
                </select>
                <span className="text-[10px] text-cryo-muted mt-1 block">
                  {selectedModelId === 'MOD-04' ? '★ Selected primary regularized benchmark' : 'Benchmarked candidate'}
                </span>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Drainage Basin:</label>
                <select
                  value={selectedBasin}
                  onChange={(e) => {
                    if (activeMode === 'historical') {
                      setSelectedBasin(e.target.value);
                    } else {
                      handleManualBasinChange(e.target.value);
                    }
                  }}
                  className="w-full bg-cryo-surface border border-cryo-border rounded px-3 py-2 text-white font-mono focus:outline-none focus:border-cryo-cyan"
                >
                  <option value="Hp-I">Hp-I (Palmer Land West)</option>
                  <option value="I-Ipp">I-Ipp (Graham Land)</option>
                  <option value="Ipp-J">Ipp-J (Palmer Land East)</option>
                </select>
                <span className="text-[10px] text-cryo-muted mt-1 block">
                  Fixed effect dummy variables align automatically
                </span>
              </div>
            </div>
          </Card>

          {/* MODE A: Historical Features Inspection & Execution */}
          {activeMode === 'historical' && (
            <Card>
              <CardHeader
                title="Historical Antecedent Telemetry (Mode A)"
                subtitle="Select historical year to resolve authentic observational antecedents."
                icon={<Clock className="w-4 h-4 text-cryo-cyan" />}
                action={
                  historicalData && (
                    <Badge variant={historicalData.split_status === 'TEST' ? 'warning' : 'neutral'} size="sm">
                      {historicalData.split_status} FOLD
                    </Badge>
                  )
                }
              />

              <div className="space-y-4 text-xs font-mono">
                {/* Year Selection Dropdown and Epoch Status */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">
                      Historical Target Year (1979–2024):
                    </label>
                    <select
                      value={historicalYear}
                      onChange={(e) => setHistoricalYear(parseInt(e.target.value))}
                      className="w-full bg-cryo-surface border border-cryo-border rounded px-3 py-2 text-white font-mono focus:outline-none focus:border-cryo-cyan"
                    >
                      {historicalYearsList.map((yr) => (
                        <option key={yr} value={yr}>
                          Year {yr} {yr >= 2016 ? '(Held-out Test: 2016–2024)' : yr === 2015 ? '(Embargo Buffer 2: 2015)' : yr >= 2008 ? '(Validation: 2008–2014)' : yr >= 2006 ? '(Embargo Buffer 1: 2006–2007)' : '(Training: 1979–2005)'}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="p-2.5 rounded border border-cryo-border bg-cryo-surface/40 flex flex-col justify-center">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Split Partition & Observational Epoch</span>
                    <div className="text-xs text-white font-semibold mt-0.5">
                      {historicalData ? (
                        <>
                          <span className={
                            historicalData.split_status === 'TEST' ? 'text-emerald-400' :
                            historicalData.split_status === 'VALIDATION' ? 'text-sky-400' :
                            historicalData.split_status.includes('EMBARGO') ? 'text-amber-400' : 'text-slate-200'
                          }>
                            {historicalData.split_status === 'TEST' ? 'Held-Out Test (2016–2024)' :
                             historicalData.split_status === 'VALIDATION' ? 'Validation (2008–2014)' :
                             historicalData.split_status === 'TRAINING' ? 'Training (1979–2005)' :
                             historicalData.split_status === 'EMBARGO_BUFFER_1' ? 'Embargo Buffer 1 (2006–2007)' :
                             historicalData.split_status === 'EMBARGO_BUFFER_2' ? 'Embargo Buffer 2 (2015)' :
                             historicalData.split_status}
                          </span>
                          <span className="text-[10px] text-slate-400 block mt-0.5 font-normal">
                            Sensor Era: {historicalData.epoch}
                          </span>
                        </>
                      ) : 'Loading...'}
                    </div>
                  </div>
                </div>

                {/* Antecedent Resolution Details */}
                {loadingHistorical ? (
                  <div className="py-6 text-center text-slate-400">
                    <LoadingSpinner message="Resolving 14 antecedent features from observational records..." />
                  </div>
                ) : historicalFetchError ? (
                  <div className="p-3 rounded border border-rose-900/50 bg-rose-950/20 text-rose-300 text-xs">
                    {historicalFetchError}
                  </div>
                ) : historicalData ? (
                  <div className="space-y-3.5">
                    {/* Antecedent Explanation Banner */}
                    <div className="p-3 rounded bg-cryo-darkest/80 border border-cryo-border text-[11px] leading-relaxed text-slate-300">
                      <div className="flex items-center gap-1.5 text-cryo-cyan font-semibold mb-1">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Antecedent Lag Provenance (Zero Lookahead)</span>
                      </div>
                      <p>{historicalData.temporal_explanation}</p>
                    </div>

                    {/* 14 Resolved Features Grid */}
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 font-semibold text-[11px] uppercase tracking-wider">
                          Resolved Predictor Vector ({Object.keys(historicalData.features).length} Features):
                        </span>
                        <span className="text-[10px] text-cryo-cyan">Passed to Model Pipeline</span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px]">
                        {Object.entries(historicalData.features).map(([key, val]) => {
                          const isLag = key.includes('Lag') || key.includes('Rolling');
                          const isDummy = key.startsWith('is_');
                          return (
                            <div
                              key={key}
                              className={`p-2 rounded border ${
                                isDummy
                                  ? 'bg-cryo-surface/20 border-cryo-border/40 text-slate-500'
                                  : isLag
                                  ? 'bg-cryo-surface/80 border-cryo-cyan/30 text-slate-200'
                                  : 'bg-cryo-surface/50 border-cryo-border text-slate-300'
                              }`}
                            >
                              <div className="text-[10px] text-cryo-muted truncate" title={key}>
                                {key.replace('Target_Volume_Change_', 'ΔV_').replace('_km3_yr', '').replace('_Gt_yr', '')}
                              </div>
                              <div className="font-semibold text-white mt-0.5 truncate">
                                {typeof val === 'number' ? val.toLocaleString(undefined, { maximumFractionDigits: 2 }) : val}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Historical Ground-Truth Preview */}
                    <div className="p-3 rounded bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px]">Actual Historical Target ({historicalYear})</span>
                        <span className="text-white font-bold text-sm">
                          {historicalData.observed_mass_balance_gt_yr > 0 ? '+' : ''}
                          {historicalData.observed_mass_balance_gt_yr.toFixed(2)} Gt/yr
                        </span>
                        <span className="text-slate-400 text-[10px] ml-2">
                          ({historicalData.observed_volume_change_km3_yr.toFixed(2)} km³/yr)
                        </span>
                      </div>
                      <Badge variant="neutral" size="sm">Ground Truth Observation</Badge>
                    </div>

                    <div className="pt-2">
                      <Button
                        type="button"
                        onClick={handleExecuteInference}
                        loading={submitting}
                        icon={<Play className="w-4 h-4" />}
                        className="w-full"
                        size="md"
                      >
                        Run Model on Year {historicalYear} Telemetry
                      </Button>
                    </div>
                  </div>
                ) : null}
              </div>
            </Card>
          )}

          {/* MODE B: Manual Scenario Customization */}
          {activeMode === 'manual' && (
            <Card>
              <CardHeader
                title="Custom Physical Scenario (Mode B)"
                subtitle="Manually define or perturb the 14-feature input vector (Year N/A)."
                icon={<Sliders className="w-4 h-4 text-cryo-cyan" />}
                action={<Badge variant="cyan" size="sm">Manual Mode</Badge>}
              />

              <div className="space-y-4 text-xs font-mono">
                {/* Template loader */}
                <div className="p-3 rounded-lg border border-cryo-border bg-cryo-surface/40 flex flex-col sm:flex-row items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Copy className="w-4 h-4 text-cryo-cyan flex-shrink-0" />
                    <span className="text-slate-300 text-xs">Load historical template as baseline:</span>
                  </div>
                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <select
                      value={templateBasin}
                      onChange={(e) => setTemplateBasin(e.target.value)}
                      className="bg-cryo-surface border border-cryo-border rounded px-2 py-1 text-white text-xs font-mono"
                    >
                      <option value="Hp-I">Hp-I</option>
                      <option value="I-Ipp">I-Ipp</option>
                      <option value="Ipp-J">Ipp-J</option>
                    </select>
                    <select
                      value={templateYear}
                      onChange={(e) => setTemplateYear(parseInt(e.target.value))}
                      className="bg-cryo-surface border border-cryo-border rounded px-2 py-1 text-white text-xs font-mono"
                    >
                      {historicalYearsList.map((yr) => (
                        <option key={yr} value={yr}>
                          {yr}
                        </option>
                      ))}
                    </select>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={handleLoadTemplate}
                      loading={loadingTemplate}
                    >
                      Populate
                    </Button>
                  </div>
                </div>

                {/* 14 Manual Inputs */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {featureDict.map((f) => {
                    const key = f.feature_name as keyof FeaturePayload;
                    const isDummy = key === 'is_Hp_I' || key === 'is_I_Ipp' || key === 'is_Ipp_J';

                    return (
                      <div
                        key={f.feature_id}
                        className={`p-2.5 rounded border ${
                          isDummy
                            ? 'border-cryo-border/40 bg-cryo-surface/30'
                            : 'border-cryo-border bg-cryo-surface/80'
                        }`}
                      >
                        <div className="flex items-baseline justify-between mb-1">
                          <span className="font-semibold text-slate-200 truncate pr-2" title={f.feature_name}>
                            {f.mathematical_symbol} {f.feature_name}
                          </span>
                          <span className="text-[10px] text-cryo-cyan font-mono flex-shrink-0">
                            {f.physical_units}
                          </span>
                        </div>

                        <input
                          type="number"
                          step="any"
                          disabled={isDummy}
                          value={manualFeatures[key] ?? 0}
                          onChange={(e) => handleManualFeatureChange(key, e.target.value)}
                          className={`w-full bg-cryo-darkest border rounded px-2.5 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-cryo-cyan ${
                            isDummy
                              ? 'border-transparent text-slate-500 cursor-not-allowed'
                              : 'border-cryo-border'
                          }`}
                        />

                        <div className="mt-1 text-[10px] text-cryo-muted truncate" title={f.feature_importance_hypothesis}>
                          Lag: {f.operational_lag} &bull; {f.feature_category}
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="pt-2">
                  <Button
                    type="button"
                    onClick={handleExecuteInference}
                    loading={submitting}
                    icon={<Play className="w-4 h-4" />}
                    className="w-full"
                    size="md"
                  >
                    Evaluate Custom Scenario Vector
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Future Projection Disclosure & Safeguards */}
          <Card className="border-amber-900/40 bg-amber-950/10 text-xs font-mono text-amber-200/90 space-y-2">
            <div className="flex items-center gap-2 text-amber-300 font-semibold">
              <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span>Future Forecasting & Centennial Projection Guardrail</span>
            </div>
            <p className="text-[11px] leading-relaxed text-amber-200/80">
              Observational records terminate in 2024. This model is a 1-year ahead autoregressive statistical benchmark,
              not an integrated climate-forced prognostic ice sheet model. Future years cannot be computed without external
              surface mass balance and grounding-line discharge scenarios. <strong>Projections beyond 2099 are strictly blocked.</strong>
            </p>
          </Card>
        </div>

        {/* Right Output Panel: Results & Scientific Validation */}
        <div className="lg:col-span-5 space-y-5">
          {inferenceError && (
            <ErrorMessage
              title="Execution Safeguard Triggered"
              message={inferenceError}
            />
          )}

          {predictionResult ? (
            <Card glow className="border-emerald-500/40 bg-cryo-dark">
              <CardHeader
                title="Live Model Inference Result"
                subtitle="Evaluated via saved scikit-learn model artifact."
                icon={<CheckCircle className="w-4 h-4 text-emerald-400" />}
                action={
                  <Badge variant="success">
                    {predictionResult.inference_mode === 'historical' ? 'Historical Mode' : 'Manual Mode'}
                  </Badge>
                }
              />

              <div className="space-y-4 font-mono">
                {/* Mass Balance & Volume Change Outputs */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-lg bg-cryo-surface border border-cryo-border">
                    <span className="text-[10px] uppercase text-cryo-muted tracking-wider block">
                      Predicted Mass Balance
                    </span>
                    <div className="text-2xl font-bold text-white mt-1">
                      {predictionResult.predicted_mass_balance_gt_yr > 0 ? '+' : ''}
                      {predictionResult.predicted_mass_balance_gt_yr.toFixed(2)}
                      <span className="text-xs text-cryo-cyan ml-1">Gt/yr</span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-lg bg-cryo-surface border border-cryo-border">
                    <span className="text-[10px] uppercase text-cryo-muted tracking-wider block">
                      Derived Volume Change
                    </span>
                    <div className="text-2xl font-bold text-white mt-1">
                      {predictionResult.predicted_volume_change_km3_yr > 0 ? '+' : ''}
                      {predictionResult.predicted_volume_change_km3_yr.toFixed(2)}
                      <span className="text-xs text-sky-400 ml-1">km³/yr</span>
                    </div>
                  </div>
                </div>

                {/* Ground-Truth Comparison (Historical Mode Only) */}
                {predictionResult.inference_mode === 'historical' && historicalData && (
                  <div className="p-3.5 rounded-lg bg-cryo-surface/90 border border-cryo-border space-y-2 text-xs">
                    <div className="flex items-center justify-between border-b border-cryo-border pb-1.5">
                      <span className="font-semibold text-slate-200">Ground-Truth Benchmark Comparison</span>
                      <Badge variant="cyan" size="sm">Observed {historicalData.year}</Badge>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div>
                        <span className="text-slate-500 block">Actual Observed MB:</span>
                        <span className="text-white font-semibold">
                          {historicalData.observed_mass_balance_gt_yr > 0 ? '+' : ''}
                          {historicalData.observed_mass_balance_gt_yr.toFixed(2)} Gt/yr
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Model Residual (Pred - Obs):</span>
                        {(() => {
                          const res = predictionResult.predicted_mass_balance_gt_yr - historicalData.observed_mass_balance_gt_yr;
                          return (
                            <span className={`font-semibold ${Math.abs(res) < 5 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {res > 0 ? '+' : ''}{res.toFixed(2)} Gt/yr
                            </span>
                          );
                        })()}
                      </div>
                    </div>

                    <div className="pt-1 flex items-center justify-between text-[10px] text-slate-400">
                      <span>Partition: <strong>{historicalData.split_status} FOLD</strong></span>
                      <span>Absolute Error: <strong>{Math.abs(predictionResult.predicted_mass_balance_gt_yr - historicalData.observed_mass_balance_gt_yr).toFixed(2)} Gt/yr</strong></span>
                    </div>
                  </div>
                )}

                {/* Mode & Parameter Details */}
                <div className="p-3 rounded bg-cryo-surface/80 border border-cryo-border text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Model Identifier:</span>
                    <span className="text-white font-semibold">{predictionResult.model_name} ({predictionResult.model_id})</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Evaluated Basin:</span>
                    <span className="text-slate-200">{predictionResult.basin_name} ({predictionResult.basin_id})</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Target Year:</span>
                    <span className="text-cryo-cyan font-semibold">
                      {predictionResult.target_year ? `${predictionResult.target_year} (Historical)` : 'N/A — Manual Scenario'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Inference Mode:</span>
                    <span className="text-slate-300 uppercase text-[11px] font-semibold">{predictionResult.inference_mode}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Density Conversion:</span>
                    <span className="text-slate-300 text-[11px]">ΔV = ΔM / 0.917 Gt/km³</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Trace UUID:</span>
                    <span className="text-slate-500 text-[10px] font-mono">{predictionResult.prediction_id}</span>
                  </div>
                </div>

                {/* Evaluated 14 Features Disclosure Accordion */}
                <div className="rounded border border-cryo-border bg-cryo-surface/50 overflow-hidden text-xs">
                  <button
                    type="button"
                    onClick={() => setShowFeatureVector(!showFeatureVector)}
                    className="w-full px-3 py-2 flex items-center justify-between text-slate-300 hover:text-white transition-colors"
                  >
                    <span className="font-semibold text-[11px]">Evaluated 14-Feature Input Vector</span>
                    {showFeatureVector ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-500" />}
                  </button>

                  {showFeatureVector && (
                    <div className="p-2.5 border-t border-cryo-border grid grid-cols-2 gap-1.5 text-[10px]">
                      {Object.entries(predictionResult.input_features).map(([fKey, fVal]) => (
                        <div key={fKey} className="p-1 rounded bg-cryo-dark flex justify-between">
                          <span className="text-slate-400 truncate pr-1" title={fKey}>{fKey}</span>
                          <span className="text-white font-mono">{fVal.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Uncertainty Disclosure */}
                <div className="p-2.5 rounded border border-slate-800 bg-slate-900/40 text-slate-400 text-[10px] leading-relaxed">
                  <em>Notice on Uncertainty:</em> Formal predictive uncertainty intervals are withheld from live point-inference display pending empirical calibration of the residual error distributions across regional validation folds.
                </div>

                {/* Mandated Scientific Disclosure */}
                <div className="p-3 rounded border border-amber-900/40 bg-amber-950/20 text-amber-200/90 text-xs">
                  <div className="flex items-center gap-1.5 font-semibold text-amber-300 mb-1">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                    <span>Scientific Notice</span>
                  </div>
                  <p className="text-[11px] leading-relaxed text-amber-200/80">
                    {predictionResult.scientific_disclosure}
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <Card className="border-dashed border-cryo-border flex flex-col items-center justify-center p-8 text-center h-80">
              <Activity className="w-10 h-10 text-slate-700 mb-3" />
              <h4 className="text-sm font-semibold font-mono text-slate-300">Awaiting Inference Request</h4>
              <p className="text-xs text-cryo-muted font-mono max-w-xs mt-1 leading-relaxed">
                {activeMode === 'historical'
                  ? `Select a historical year (1979–2024) and model, then click "Run Model on Year ${historicalYear} Telemetry".`
                  : 'Configure the 14 physical predictors or populate from template, then click "Evaluate Custom Scenario Vector".'}
              </p>
            </Card>
          )}

          {/* Glaciological Density Note */}
          <Card className="text-xs font-mono text-slate-400 space-y-2">
            <div className="flex items-center gap-1.5 text-cryo-cyan font-semibold">
              <Info className="w-4 h-4" />
              <span>Governing Physical Conversion</span>
            </div>
            <p className="text-[11px] leading-relaxed">
              Solid-ice volume change (&Delta;V) is derived from mass balance (&Delta;M) assuming a constant solid-ice density of &rho;<sub>ice</sub> = 917 kg/m&sup3; (0.917 Gt/km&sup3;).
              Altimetry compaction effects (firn air content) are not mixed into satellite gravimetry flux gates.
            </p>
          </Card>
        </div>
      </div>

      <ScientificDisclaimer compact />
    </div>
  );
};
