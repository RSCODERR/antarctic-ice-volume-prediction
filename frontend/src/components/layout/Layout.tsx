import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-cryo-darkest text-slate-100 flex flex-col">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="lg:pl-64 flex flex-col flex-1">
        <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
          <Outlet />
        </main>

        <footer className="border-t border-cryo-border/60 py-4 px-6 text-center text-xs font-mono text-slate-500 bg-cryo-darkest">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
            <div>CryoPredict Platform &copy; 2026 — Antarctic Peninsula Cryospheric Research Group</div>
            <div className="text-slate-600">
              BedMachine v4.1 &bull; RACMO2.3p2 &bull; 2D SSA Solver &bull; ElasticNet Benchmark
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};
