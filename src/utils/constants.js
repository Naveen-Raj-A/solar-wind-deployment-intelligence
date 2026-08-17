// src/utils/constants.js
/**
 * Application constants
 */

export const API_ENDPOINTS = {
  ANALYZE_LOCATION: '/deployment/analyze',
  GET_PROJECTS: '/projects',
  GET_SITES: '/sites',
  GET_PREDICTIONS: '/predictions',
};

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const MAP_CONFIG = {
  DEFAULT_ZOOM: 13,
  MIN_ZOOM: 3,
  MAX_ZOOM: 18,
  TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  ATTRIBUTION:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
};

export const ANALYSIS_STEPS = [
  { id: 1, name: 'NASA POWER', icon: '☀' },
  { id: 2, name: 'Global Wind Atlas', icon: '🌬' },
  { id: 3, name: 'SRTM Terrain', icon: '🏔' },
  { id: 4, name: 'Sentinel-2', icon: '🛰' },
  { id: 5, name: 'OpenStreetMap', icon: '🛣' },
  { id: 6, name: 'Deployment Report', icon: '📊' },
];

export const UNITS = {
  TEMPERATURE: '°C',
  WIND_SPEED: 'm/s',
  SOLAR_IRRADIANCE: 'kWh/m²/day',
  ELEVATION: 'm',
  PERCENTAGE: '%',
};

export const STATUS_COLORS = {
  pending: 'yellow',
  processing: 'blue',
  completed: 'green',
  failed: 'red',
};

export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#10b981',
  accent: '#f59e0b',
  danger: '#ef4444',
  success: '#10b981',
  warning: '#f59e0b',
  info: '#3b82f6',
};

export default {
  API_ENDPOINTS,
  API_BASE_URL,
  MAP_CONFIG,
  ANALYSIS_STEPS,
  UNITS,
  STATUS_COLORS,
  CHART_COLORS,
};