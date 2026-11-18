import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { OverviewPage } from './pages/OverviewPage';
import { ModelLabPage } from './pages/ModelLabPage';
import { PredictionLabPage } from './pages/PredictionLabPage';
import { FutureProjectionsPage } from './pages/FutureProjectionsPage';
import { IceSheetExplorerPage } from './pages/IceSheetExplorerPage';
import { DatasetExplorerPage } from './pages/DatasetExplorerPage';
import { PhysicalModelPage } from './pages/PhysicalModelPage';
import { ValidationPage } from './pages/ValidationPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<OverviewPage />} />
          <Route path="models" element={<ModelLabPage />} />
          <Route path="predictions" element={<PredictionLabPage />} />
          <Route path="projections" element={<FutureProjectionsPage />} />
          <Route path="explorer" element={<IceSheetExplorerPage />} />
          <Route path="datasets" element={<DatasetExplorerPage />} />
          <Route path="physical-model" element={<PhysicalModelPage />} />
          <Route path="validation" element={<ValidationPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
