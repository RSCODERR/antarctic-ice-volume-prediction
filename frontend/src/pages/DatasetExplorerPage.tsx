import React, { useEffect, useState } from 'react';
import {
  Database,
  Layers,
  FileSpreadsheet,
  Calendar,
  CheckCircle,
  Search,
  Filter,
  Info,
  Sliders
} from 'lucide-react';
import { CryoApi } from '../api/client';
import { DatasetItem, FeatureItem } from '../api/types';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

export const DatasetExplorerPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [features, setFeatures] = useState<FeatureItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'datasets' | 'features'>('datasets');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        const [dList, fList] = await Promise.all([
          CryoApi.getDatasets(),
          CryoApi.getFeatures(),
        ]);
        if (isMounted) {
          setDatasets(dList);
          setFeatures(fList);
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to load dataset inventory and feature dictionary from backend.');
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
    return <LoadingSpinner message="Querying dataset catalog & feature dictionary..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Dataset Explorer Error"
        message={error}
        onRetry={() => window.location.reload()}
      />
    );
  }

  // Filter datasets
  const filteredDatasets = datasets.filter((d) => {
    const matchesSearch =
      d.dataset_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.inventory_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.provenance_and_role.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  // Filter features
  const categories = Array.from(new Set(features.map((f) => f.feature_category)));
  const filteredFeatures = features.filter((f) => {
    const matchesSearch =
      f.feature_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.feature_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.mathematical_symbol.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = categoryFilter === 'ALL' || f.feature_category === categoryFilter;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Research Provenance</Badge>
            <Badge variant="neutral">14 Inventory Items &bull; 14 Frozen Features</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Dataset & Feature Catalog
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Exhaustive inventory of remote sensing observations, atmospheric reanalysis, physical model diagnostics,
            and the frozen 14-feature machine-learning dictionary.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="success" className="px-3 py-1">Frozen Schema</Badge>
        </div>
      </div>

      {/* View Switcher Tabs & Search Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2 p-1 rounded-lg border border-cryo-border bg-cryo-dark">
          <button
            onClick={() => setActiveTab('datasets')}
            className={`flex items-center gap-2 px-4 py-2 rounded text-xs font-mono font-medium transition-colors ${
              activeTab === 'datasets'
                ? 'bg-cryo-surface text-cryo-cyan border border-cryo-cyan/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Dataset Inventory ({datasets.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('features')}
            className={`flex items-center gap-2 px-4 py-2 rounded text-xs font-mono font-medium transition-colors ${
              activeTab === 'features'
                ? 'bg-cryo-surface text-cryo-cyan border border-cryo-cyan/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Feature Dictionary ({features.length})</span>
          </button>
        </div>

        {/* Search Input */}
        <div className="flex items-center gap-2 max-w-xs w-full">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-cryo-dark border border-cryo-border rounded pl-8 pr-3 py-1.5 text-xs text-white font-mono placeholder:text-slate-600 focus:outline-none focus:border-cryo-cyan"
            />
          </div>
        </div>
      </div>

      {/* Tab 1: Dataset Inventory */}
      {activeTab === 'datasets' && (
        <Card>
          <CardHeader
            title="Stage 6.0 Verified Dataset Inventory"
            subtitle="Provenance, coverage, physical units, and ML readiness status."
            icon={<Database className="w-4 h-4" />}
          />

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-cryo-surface text-slate-400 border-b border-cryo-border uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Inventory ID</th>
                  <th className="py-2.5 px-3">Dataset Name</th>
                  <th className="py-2.5 px-3">Temporal Coverage</th>
                  <th className="py-2.5 px-3">Spatial Coverage</th>
                  <th className="py-2.5 px-3">Physical Quantity & Units</th>
                  <th className="py-2.5 px-3">Samples</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Provenance & Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cryo-border/60 text-slate-200">
                {filteredDatasets.map((d) => (
                  <tr key={d.inventory_id} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 font-semibold text-cryo-cyan">{d.inventory_id}</td>
                    <td className="py-2.5 px-3 font-semibold text-white whitespace-nowrap">{d.dataset_name}</td>
                    <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">{d.temporal_coverage}</td>
                    <td className="py-2.5 px-3 text-slate-400">{d.spatial_coverage}</td>
                    <td className="py-2.5 px-3 text-cryo-ice">{d.physical_quantity_and_units}</td>
                    <td className="py-2.5 px-3 text-slate-300">{d.sample_count}</td>
                    <td className="py-2.5 px-3">
                      <Badge
                        variant={
                          d.ml_readiness_status === 'ML_READY'
                            ? 'success'
                            : d.ml_readiness_status === 'STATIC_METRIC'
                            ? 'neutral'
                            : 'warning'
                        }
                      >
                        {d.ml_readiness_status}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 max-w-xs truncate" title={d.provenance_and_role}>
                      {d.provenance_and_role}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tab 2: Feature Dictionary */}
      {activeTab === 'features' && (
        <Card>
          <CardHeader
            title="Stage 6.0 Frozen 14-Feature Dictionary (FEAT-01 to FEAT-14)"
            subtitle="Mathematical symbols, physical units, operational lags, imputation strategies, and ElasticNet sparsity weights."
            icon={<Sliders className="w-4 h-4" />}
            action={
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-cryo-muted">Category:</span>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="bg-cryo-surface border border-cryo-border rounded px-2 py-1 text-xs text-white font-mono focus:outline-none"
                >
                  <option value="ALL">All Categories</option>
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            }
          />

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-cryo-surface text-slate-400 border-b border-cryo-border uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3">Feature Name</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Units</th>
                  <th className="py-2.5 px-3">Lag</th>
                  <th className="py-2.5 px-3">Imputation</th>
                  <th className="py-2.5 px-3">ElasticNet Coef</th>
                  <th className="py-2.5 px-3">Sparsity Status</th>
                  <th className="py-2.5 px-3">Physical Hypothesis</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cryo-border/60 text-slate-200">
                {filteredFeatures.map((f) => (
                  <tr key={f.feature_id} className="hover:bg-slate-900/40">
                    <td className="py-2.5 px-3 font-semibold text-cryo-cyan">{f.feature_id}</td>
                    <td className="py-2.5 px-3 text-sky-300 font-semibold">{f.mathematical_symbol}</td>
                    <td className="py-2.5 px-3 font-semibold text-white whitespace-nowrap">{f.feature_name}</td>
                    <td className="py-2.5 px-3">
                      <Badge variant="neutral">{f.feature_category}</Badge>
                    </td>
                    <td className="py-2.5 px-3 text-cryo-ice">{f.physical_units}</td>
                    <td className="py-2.5 px-3 text-slate-400">{f.operational_lag}</td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px]">{f.imputation_method}</td>
                    <td className="py-2.5 px-3 font-semibold">
                      {f.elasticnet_coefficient !== null ? (
                        <span className={f.elasticnet_coefficient !== 0 ? 'text-emerald-400' : 'text-slate-500'}>
                          {f.elasticnet_coefficient.toFixed(6)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge
                        variant={
                          f.elasticnet_status === 'ACTIVE_SELECTED'
                            ? 'success'
                            : 'neutral'
                        }
                      >
                        {f.elasticnet_status || 'PRUNED_ZERO'}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 max-w-sm truncate" title={f.feature_importance_hypothesis}>
                      {f.feature_importance_hypothesis}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Scientific Disclaimer */}
      <ScientificDisclaimer compact />
    </div>
  );
};
