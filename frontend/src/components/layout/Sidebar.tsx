import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity,
  Layers,
  Database,
  Compass,
  Cpu,
  Map,
  CheckCircle2,
  Snowflake,
  ShieldAlert,
  GitBranch,
  TrendingUp
} from 'lucide-react';
import { Badge } from '../common/Badge';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { to: '/', label: 'Overview', icon: <Compass className="w-4 h-4" /> },
    { to: '/models', label: 'Model Laboratory', icon: <Cpu className="w-4 h-4" /> },
    { to: '/predictions', label: 'Prediction Laboratory', icon: <Activity className="w-4 h-4" /> },
    { to: '/projections', label: 'Future Projections', icon: <TrendingUp className="w-4 h-4" />, highlight: true },
    { to: '/explorer', label: 'Ice Sheet Explorer', icon: <Map className="w-4 h-4" /> },
    { to: '/datasets', label: 'Dataset Explorer', icon: <Database className="w-4 h-4" /> },
    { to: '/physical-model', label: 'Physical Model (SSA)', icon: <Layers className="w-4 h-4" /> },
    { to: '/validation', label: 'Validation & Audit', icon: <CheckCircle2 className="w-4 h-4" /> },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-cryo-darkest border-r border-cryo-border flex flex-col transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand header */}
        <div className="h-16 flex items-center px-5 border-b border-cryo-border/80 gap-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-cryo-cyan to-blue-700 flex items-center justify-center text-cryo-darkest font-bold shadow-md shadow-cryo-cyan/10">
            <Snowflake className="w-5 h-5 text-slate-950" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-base tracking-tight text-white font-mono">CryoPredict</span>
              <Badge variant="cyan" size="sm" className="text-[9px] px-1 py-0">v1.0</Badge>
            </div>
            <p className="text-[10px] uppercase tracking-wider text-cryo-muted font-mono">Antarctic Ice Intelligence</p>
          </div>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-widest text-slate-500 font-semibold">
            Research Modules
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded text-xs font-mono font-medium transition-colors ${
                  isActive
                    ? 'bg-cryo-card text-cryo-cyan border border-cryo-cyan/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                }`
              }
            >
              <span className="flex-shrink-0">{item.icon}</span>
              <span className="truncate">{item.label}</span>
              {item.highlight && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-cryo-cyan animate-pulse" />
              )}
            </NavLink>
          ))}
        </div>

        {/* Research status footer */}
        <div className="p-3 border-t border-cryo-border/80 bg-cryo-dark/40 space-y-2">
          {/* Pillar 1 */}
          <div className="p-2.5 rounded border border-cryo-border/60 bg-cryo-surface/40 text-[10px] font-mono text-slate-400 space-y-1">
            <div className="flex items-center justify-between text-slate-300">
              <span className="flex items-center gap-1">
                <GitBranch className="w-3 h-3 text-cryo-cyan" />
                <span>Pillar 1: Historical</span>
              </span>
              <span className="text-[9px] text-emerald-400 font-semibold">STAGE 6.2</span>
            </div>
            <div className="text-[10px] text-cryo-muted">
              Model: <span className="text-slate-200">ElasticNet (1-yr)</span>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-2.5 rounded border border-cryo-cyan/30 bg-cryo-surface/40 text-[10px] font-mono text-slate-400 space-y-1">
            <div className="flex items-center justify-between text-slate-300">
              <span className="flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-cyan-400" />
                <span>Pillar 2: Projections</span>
              </span>
              <span className="text-[9px] text-cyan-300 font-semibold">STAGE 7.1</span>
            </div>
            <div className="text-[10px] text-cryo-muted">
              Engine: <span className="text-slate-200">QGB (2015–2100)</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
