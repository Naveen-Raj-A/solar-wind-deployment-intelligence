// src/utils/leafletIconFix.js
/**
 * Fix for Leaflet icon paths when using bundlers like Vite/Webpack
 * This ensures that Leaflet's default icon images are correctly resolved
 */

import { icon as leafletIcon } from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Delete the default icons to force Leaflet to use our imported ones
delete leafletIcon.Default.prototype._getIconUrl;

// Create new icon options
leafletIcon.Default.mergeOptions({
  iconRetinaUrl: markerIcon,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

/**
 * Returns a Leaflet icon instance with fixed paths
 * @returns {L.Icon} Leaflet icon object
 */
export function getFixedLeafletIcon() {
  return leafletIcon.default();
}

export default {
  getFixedLeafletIcon,
};