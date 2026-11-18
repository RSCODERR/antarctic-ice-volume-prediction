import axios, { AxiosError } from 'axios';
import {
  HealthResponse,
  OverviewResponse,
  ModelSummary,
  ModelDetailResponse,
  HistoricalPredictionItem,
  HistoricalFeaturesResponse,
  InferenceRequest,
  InferenceResponse,
  DatasetItem,
  FeatureItem,
  ScenarioItem,
  FutureModelInfoResponse,
  AvailabilityResponse,
  ProjectionTrajectoryResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL !== undefined
  ? import.meta.env.VITE_API_BASE_URL
  : (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

/**
 * Parses FastAPI error details into a human-readable string.
 */
export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ detail?: any }>;
    if (axiosErr.response?.data?.detail) {
      const detail = axiosErr.response.data.detail;
      if (typeof detail === 'string') {
        return detail;
      }
      if (Array.isArray(detail)) {
        return detail.map((d: any) => `${d.loc ? d.loc.join('.') : 'field'}: ${d.msg}`).join(', ');
      }
      return JSON.stringify(detail);
    }
    if (axiosErr.message) {
      return axiosErr.message;
    }
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred.';
}

export const CryoApi = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get<HealthResponse>('/api/health');
    return res.data;
  },

  // Overview
  getOverview: async (): Promise<OverviewResponse> => {
    const res = await apiClient.get<OverviewResponse>('/api/overview');
    return res.data;
  },

  // Models
  getModels: async (): Promise<ModelSummary[]> => {
    const res = await apiClient.get<ModelSummary[]>('/api/models');
    return res.data;
  },

  getModelComparison: async (): Promise<any[]> => {
    const res = await apiClient.get<any[]>('/api/models/comparison');
    return res.data;
  },

  getModelDetail: async (modelId: string): Promise<ModelDetailResponse> => {
    const res = await apiClient.get<ModelDetailResponse>(`/api/models/${encodeURIComponent(modelId)}`);
    return res.data;
  },

  // Predictions
  getHistoricalPredictions: async (params?: {
    basin_id?: string;
    year?: number;
    split_status?: string;
  }): Promise<HistoricalPredictionItem[]> => {
    const res = await apiClient.get<HistoricalPredictionItem[]>('/api/predictions/historical', {
      params,
    });
    return res.data;
  },

  getHistoricalFeatures: async (basin_id: string, year: number): Promise<HistoricalFeaturesResponse> => {
    const res = await apiClient.get<HistoricalFeaturesResponse>('/api/predictions/historical-features', {
      params: { basin_id, year },
    });
    return res.data;
  },

  runInference: async (payload: InferenceRequest): Promise<InferenceResponse> => {
    const res = await apiClient.post<InferenceResponse>('/api/predictions/run', payload);
    return res.data;
  },

  // Datasets
  getDatasets: async (): Promise<DatasetItem[]> => {
    const res = await apiClient.get<DatasetItem[]>('/api/datasets');
    return res.data;
  },

  // Features
  getFeatures: async (): Promise<FeatureItem[]> => {
    const res = await apiClient.get<FeatureItem[]>('/api/features');
    return res.data;
  },

  // Future Projections (Stage 7.1/7.2)
  getProjectionScenarios: async (): Promise<ScenarioItem[]> => {
    const res = await apiClient.get<ScenarioItem[]>('/api/projections/scenarios');
    return res.data;
  },

  getProjectionModelInfo: async (): Promise<FutureModelInfoResponse> => {
    const res = await apiClient.get<FutureModelInfoResponse>('/api/projections/models');
    return res.data;
  },

  getProjectionAvailability: async (): Promise<AvailabilityResponse> => {
    const res = await apiClient.get<AvailabilityResponse>('/api/projections/availability');
    return res.data;
  },

  getProjectionTrajectory: async (params: {
    scenario: string;
    spatial_unit?: string;
    start_year?: number;
    end_year?: number;
  }): Promise<ProjectionTrajectoryResponse> => {
    const res = await apiClient.get<ProjectionTrajectoryResponse>('/api/projections/trajectory', {
      params,
    });
    return res.data;
  },
};
