import React, { useState } from 'react';
import {
  Map,
  Layers,
  Compass,
  Eye,
  Info,
  Maximize2,
  ZoomIn,
  CheckCircle,
  FileText
} from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';

interface MapLayer {
  id: string;
  title: string;
  filename: string;
  category: string;
  source: string;
  description: string;
}

const SCIENTIFIC_MAPS: MapLayer[] = [
  {
    id: 'basins-domain',
    title: 'Peninsula Study Basins & Domain Delineation',
    filename: '/figures/map1_peninsula_basins_domain.png',
    category: 'Regional Boundary',
    source: 'IMBIE-3 & BedMachine v4.1 Mask',
    description: 'Delineation of drainage sectors Hp-I, I-Ipp, and Ipp-J across 866,358 grounded cells in Domain A.',
  },
  {
    id: 'bedmap3-thickness',
    title: 'Bedmap3 Ice Thickness Distribution',
    filename: '/figures/map2_bedmap3_thickness.png',
    category: 'Ice Geometry',
    source: 'Bedmap3 Airborne Radar Sounding Compilation',
    description: 'Reconciled solid-ice thickness column (meters) across the alpine spine and marine-terminating outlets.',
  },
  {
    id: 'classification-masks',
    title: 'Bedmap3 Classification & Flotation Masks',
    filename: '/figures/map3_bedmap3_classification_masks.png',
    category: 'Flotation Mask',
    source: 'BedMachine / Bedmap3 Flotation Criterion',
    description: 'Spatial delineation of grounded ice, floating ice shelves (Larsen C, George VI), and ocean embayments.',
  },
  {
    id: 'velocity-field',
    title: 'Satellite Surface Ice Velocity Field',
    filename: '/figures/stage4_6_velocity_field.png',
    category: 'Kinematics',
    source: 'MEaSUREs InSAR & Landsat-8 Feature Tracking',
    description: 'Logarithmic surface ice velocity magnitudes (m/year) showing rapid ice stream corridors.',
  },
  {
    id: 'mass-budget-maps',
    title: 'Physical Mass Budget & Flux Divergence',
    filename: '/figures/stage4_8_mass_budget_maps.png',
    category: 'Conservation',
    source: '2D SSA Physical Model Diagnostic (Stage 4.8)',
    description: 'Spatial divergence of horizontal ice flux reconciled with RACMO surface mass balance accumulation.',
  },
];

export const IceSheetExplorerPage: React.FC = () => {
  const [activeMapId, setActiveMapId] = useState<string>('basins-domain');
  const [selectedBasin, setSelectedBasin] = useState<string>('Hp-I');

  const activeMap = SCIENTIFIC_MAPS.find((m) => m.id === activeMapId) || SCIENTIFIC_MAPS[0];

  const basinMetrics: Record<
    string,
    {
      name: string;
      groundedArea: string;
      percentage: string;
      thickness: string;
      bedElevation: string;
      stress: string;
      regime: string;
      flowFeatures: string;
    }
  > = {
    'Hp-I': {
      name: 'Palmer Land West',
      groundedArea: '108,945.63 km²',
      percentage: '50.4%',
      thickness: '1,482.40 m',
      bedElevation: '-124.20 m at flux gates',
      stress: '105.40 kPa driving stress',
      regime: 'Marine-Terminating Ice Streams',
      flowFeatures: 'Fast-flowing ice streams discharging into Bellingshausen Sea and George VI Sound.',
    },
    'I-Ipp': {
      name: 'Graham Land',
      groundedArea: '38,616.54 km²',
      percentage: '17.9%',
      thickness: '812.30 m',
      bedElevation: '-45.10 m at flux gates',
      stress: '132.80 kPa driving stress',
      regime: 'Alpine Mountain Glaciers',
      flowFeatures: 'Steep alpine tributary glaciers accelerated post-collapse of Larsen A (1995) and Larsen B (2002).',
    },
    'Ipp-J': {
      name: 'Palmer Land East',
      groundedArea: '68,500.00 km²',
      percentage: '31.7%',
      thickness: '1,220.50 m',
      bedElevation: '-88.30 m at flux gates',
      stress: '98.20 kPa driving stress',
      regime: 'Weddell Sea Embayment',
      flowFeatures: 'Broad ice sheet reservoir feeding into Larsen C ice shelf and Weddell Sea grounding lines.',
    },
  };

  const currBasin = basinMetrics[selectedBasin];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cryo-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="cyan">Geospatial Explorer</Badge>
            <Badge variant="neutral">Domain A (BedMachine v4.1)</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
            Ice Sheet Geospatial Explorer
          </h1>
          <p className="text-xs sm:text-sm text-cryo-muted font-mono mt-1 max-w-3xl leading-relaxed">
            Spatial inspection of verified Antarctic Peninsula drainage sectors, Bedmap3 ice thickness,
            grounding-line masks, and observed satellite velocity fields.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="primary" className="px-3 py-1">Authentic Cartography</Badge>
        </div>
      </div>

      {/* Geospatial Layout: Map Controls & High-Res Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Layer Switcher & Basin Telemetry */}
        <div className="lg:col-span-4 space-y-5">
          <Card>
            <CardHeader
              title="Scientific Map Layers"
              subtitle="Select authentic spatial export from research pipeline."
              icon={<Layers className="w-4 h-4" />}
            />

            <div className="space-y-2 font-mono">
              {SCIENTIFIC_MAPS.map((layer) => {
                const isActive = layer.id === activeMapId;
                return (
                  <button
                    key={layer.id}
                    onClick={() => setActiveMapId(layer.id)}
                    className={`w-full text-left p-3 rounded border transition-all text-xs ${
                      isActive
                        ? 'bg-cryo-surface border-cryo-cyan text-white shadow-md'
                        : 'bg-cryo-dark/80 border-cryo-border text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-100">{layer.title}</span>
                      {isActive && <CheckCircle className="w-3.5 h-3.5 text-cryo-cyan" />}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-cryo-muted">
                      <span>{layer.category}</span>
                      <span>&bull;</span>
                      <span className="text-slate-500 truncate">{layer.source}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Basin Telemetry Selector */}
          <Card>
            <CardHeader
              title="IMBIE Basin Telemetry"
              subtitle="Inspect individual physical properties."
              icon={<Compass className="w-4 h-4" />}
            />

            <div className="flex items-center gap-2 mb-3">
              {(['Hp-I', 'I-Ipp', 'Ipp-J'] as const).map((b) => (
                <button
                  key={b}
                  onClick={() => setSelectedBasin(b)}
                  className={`flex-1 py-1.5 rounded text-xs font-mono font-semibold border transition-colors ${
                    selectedBasin === b
                      ? 'bg-cryo-cyan/20 border-cryo-cyan text-cryo-cyan'
                      : 'border-cryo-border bg-cryo-surface text-slate-400 hover:text-white'
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>

            <div className="p-3 rounded bg-cryo-surface border border-cryo-border text-xs font-mono space-y-2">
              <div className="text-sm font-bold text-white border-b border-cryo-border pb-1.5">
                {currBasin.name} ({selectedBasin})
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Grounded Area:</span>
                <span className="text-slate-200">{currBasin.groundedArea} ({currBasin.percentage})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Mean Column Thickness:</span>
                <span className="text-slate-200">{currBasin.thickness}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Bed Elevation:</span>
                <span className="text-slate-200">{currBasin.bedElevation}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Driving Shear Stress:</span>
                <span className="text-slate-200">{currBasin.stress}</span>
              </div>
              <div className="pt-2 border-t border-cryo-border/60 text-[11px] text-cryo-muted leading-relaxed">
                {currBasin.flowFeatures}
              </div>
            </div>
          </Card>

          {/* Geospatial Scope Disclaimer */}
          <Card className="text-xs font-mono text-slate-400 space-y-2">
            <div className="flex items-center gap-1.5 text-cryo-cyan font-semibold">
              <Info className="w-4 h-4" />
              <span>Data Provenance & Spatial Scope</span>
            </div>
            <p className="text-[11px] leading-relaxed">
              Spatial grids originate from BedMachine Antarctica v4.1 (500m polar stereographic EPSG:3031),
              Bedmap3, MEaSUREs InSAR, and REMA v1.1. High-resolution raw NetCDF arrays have been audited for mass
              divergence consistency.
            </p>
          </Card>
        </div>

        {/* Right Authentic Scientific Map Viewer */}
        <div className="lg:col-span-8 space-y-4">
          <Card className="p-4 bg-cryo-darkest border-cryo-border flex flex-col justify-between">
            <div className="flex items-start justify-between border-b border-cryo-border/80 pb-3 mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold font-mono text-white">{activeMap.title}</h3>
                  <Badge variant="cyan">{activeMap.category}</Badge>
                </div>
                <p className="text-xs font-mono text-cryo-muted mt-0.5">{activeMap.description}</p>
              </div>
              <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                <FileText className="w-3 h-3" />
                <span>{activeMap.source}</span>
              </span>
            </div>

            {/* High-Resolution Scientific Image Viewer */}
            <div className="relative rounded-lg overflow-hidden border border-cryo-border/80 bg-slate-950 flex items-center justify-center min-h-[500px]">
              <img
                src={activeMap.filename}
                alt={activeMap.title}
                className="max-h-[620px] w-auto object-contain transition-all"
                loading="lazy"
                onError={(e) => {
                  // Fallback message if image loading encounters path issue
                  (e.target as HTMLElement).style.display = 'none';
                  const fallback = document.getElementById('map-fallback');
                  if (fallback) fallback.style.display = 'flex';
                }}
              />
              <div
                id="map-fallback"
                style={{ display: 'none' }}
                className="flex-col items-center justify-center p-8 text-center text-xs font-mono text-slate-400"
              >
                <Layers className="w-8 h-8 text-slate-600 mb-2" />
                <p>Authentic spatial figure available in reports/figures/{activeMap.filename.replace('/figures/', '')}</p>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-cryo-border/60 flex items-center justify-between text-[11px] font-mono text-cryo-muted">
              <span>Projection: Antarctic Polar Stereographic (EPSG:3031, 71°S standard parallel)</span>
              <span className="text-slate-400">Resolution: 500m &bull; Grounded Cells: 866,358</span>
            </div>
          </Card>
        </div>
      </div>

      <ScientificDisclaimer compact />
    </div>
  );
};
