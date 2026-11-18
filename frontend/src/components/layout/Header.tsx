import React, { useEffect, useState } from 'react';
import { Menu, Terminal, ExternalLink, Activity } from 'lucide-react';
import { Badge } from '../common/Badge';
import { CryoApi } from '../../api/client';
import { HealthResponse } from '../../api/types';

interface HeaderProps {
  onMenuToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchHealth = async () => {
      try {
        const data = await CryoApi.getHealth();
        if (isMounted) setHealth(data);
      } catch (err) {
        if (isMounted) {
          setHealth({
            status: 'degraded',
            version: '1.0.0',
            timestamp: new Date().toISOString(),
            environment: 'offline',
            models_loaded: false,
            loaded_models_count: 0,
            primary_model_status: 'UNAVAILABLE',
          });
        }
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const isHealthy = health?.status === 'healthy';

  return (
    <header className="h-16 bg-cryo-darkest/90 backdrop-blur border-b border-cryo-border flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="p-1.5 rounded border border-cryo-border text-slate-300 hover:text-white lg:hidden"
          aria-label="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-cryo-muted">
          <span className="text-slate-400">Antarctic Peninsula Domain</span>
          <span className="text-slate-600">/</span>
          <span className="text-cryo-cyan">Domain A (866,358 Grounded Cells)</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Backend status pill */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded border border-cryo-border bg-cryo-dark text-xs font-mono">
          <div className="relative flex items-center justify-center">
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy ? 'bg-emerald-400' : 'bg-amber-400'
              }`}
            />
            {isHealthy && (
              <span className="absolute w-3.5 h-3.5 rounded-full bg-emerald-400/30 animate-ping" />
            )}
          </div>
          <span className="text-slate-300 text-[11px] uppercase tracking-wider">
            {isHealthy ? 'Backend Active' : 'API Connecting...'}
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-[10px] text-cryo-muted">
            {health?.loaded_models_count ?? 4} Models Loaded
          </span>
        </div>

        {/* API Docs Link */}
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded border border-cryo-border hover:border-cryo-cyan/40 bg-cryo-surface/60 text-slate-300 hover:text-white text-xs font-mono transition-colors"
        >
          <Terminal className="w-3.5 h-3.5 text-cryo-cyan" />
          <span>FastAPI Docs</span>
          <ExternalLink className="w-3 h-3 text-slate-500" />
        </a>
      </div>
    </header>
  );
};
