// src/utils/formatters.js
/**
 * Formatting utilities for displaying data in UI
 */

/**
 * Format a number to a specific number of decimal places
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted number string
 */
export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  if (isNaN(value)) return '--';
  return value.toFixed(decimals);
}

/**
 * Format a number as a percentage
 * @param {number} value - Value between 0 and 1 or 0 and 100
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage string
 */
export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '--';
  if (isNaN(value)) return '--';
  // Assume value is in 0-1 range if less than 1, otherwise 0-100
  const multiplier = value <= 1 ? 100 : 1;
  return `${(value * multiplier).toFixed(decimals)}%`;
}

/**
 * Format a file size in bytes to human readable format
 * @param {number} bytes - Number of bytes
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted size string
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === null || bytes === undefined) return '--';
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format a distance in meters to appropriate unit
 * @param {number} meters - Distance in meters
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted distance string
 */
export function formatDistance(meters, decimals = 1) {
  if (meters === null || meters === undefined) return '--';
  if (meters === 0) return '0 m';

  if (meters >= 1000) {
    const km = meters / 1000;
    return `${km.toFixed(decimals)} km`;
  }
  return `${meters.toFixed(decimals)} m`;
}

/**
 * Format a number with ordinal suffix (1st, 2nd, 3rd, etc.)
 * @param {number} number - Number to format
 * @returns {string} Ordinal string
 */
export function formatOrdinal(number) {
  if (number === null || number === undefined) return '--';
  if (!Number.isInteger(number)) return String(number);

  const s = ['th', 'st', 'nd', 'rd'];
  const v = number % 100;
  return `${number}${s[(v - 20) % 10] || s[v] || s[0]}`;
}

/**
 * Format a rating as stars (returns array for mapping.
 */

}

/*@param {number} rating - Rating value (0-5)
 * @param {number} max - Maximum rating (default: 5)
 * @returns {Array} Array of objects representing star states
 */
export function formatRatingStars(rating, max = 5) {
  if (rating === null || rating === undefined) return Array(Math.floor(max)).fill({ filled: false, half: false });
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = Math.floor(max - fullStars - (hasHalfStar ? 1 : 0));

  const stars = [];
  for (let i = 0; i < fullStars; i++) stars.push({ filled: true, half: false });
  if (hasHalfStar) stars.push({ filled: true, half: true });
  for (let i = 0; i < emptyStars; i++) stars.push({ filled: false, half: false });

  return stars.map((star, index) => ({ ...star, index }));
}

/**
 * Truncate text to a specified length and add ellipsis
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @param {string} suffix - Suffix to add (default: '...')
 * @returns {string} Truncated string
 */
export function truncateText(text, length, suffix = '...') {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.slice(0, length) + suffix;
}

/**
 * Format a phone number (US format)
 * @param {string} phone - Phone number string
 * @returns {string} Formatted phone number
 */
export function formatPhoneNumber(phone) {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
}

/**
 * Format a currency amount
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: 'USD')
 * @param {string} locale - Locale for formatting (default: 'en-US')
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currency = 'USD', locale = 'en-US') {
  if (amount === null || amount === undefined) return '--';
  if (isNaN(amount)) return '--';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
}

export default {
  formatNumber,
  formatPercentage,
  formatFileSize,
  formatDistance,
  formatOrdinal,
  formatRatingStars,
  truncateText,
  formatPhoneNumber,
  formatCurrency,
};