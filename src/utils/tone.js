// src/utils/tone.js
/**
 * Tone and voice guidelines for UI copy
 * This file provides constants for consistent messaging throughout the application
 */

/**
 * Message tones for different contexts
 */
export const TONES = {
  // Success messages
  success: {
    prefix: 'Success!',
    messages: {
      analysisComplete: 'Analysis completed successfully.',
      saveSuccess: 'Your changes have been saved.',
      exportComplete: 'Export finished.',
    },
  },

  // Error messages
  error: {
    prefix: 'Error',
    messages: {
      networkError: 'Network error. Please check your connection.',
      validationFailed: 'Please check your input and try again.',
      analysisFailed: 'Analysis could not be completed. Please try again.',
      unauthorized: 'You are not authorized to perform this action.',
    },
  },

  // Warning messages
  warning: {
    prefix: 'Warning',
    messages: {
      unsavedChanges: 'You have unsaved changes that will be lost.',
      largeFile: 'The file is large and may take time to process.',
      outdatedBrowser: 'You are using an outdated browser. Some features may not work correctly.',
    },
  },

  // Info messages
  info: {
    prefix: 'Info',
    messages: {
      loading: 'Loading...',
      noData: 'No data available for the selected criteria.',
      featureComingSoon: 'This feature is coming soon!',
    },
  },

  // Placeholder text
  placeholders: {
    search: 'Search locations...',
    enterAddress: 'Enter address or coordinates',
    selectOption: 'Select an option',
    enterEmail: 'Enter your email',
    enterPassword: 'Enter your password',
  },

  // Button labels
  buttons: {
    submit: 'Submit',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    viewDetails: 'View Details',
    runAnalysis: 'Run Analysis',
    exportReport: 'Export Report',
    refresh: 'Refresh',
    tryAgain: 'Try Again',
  },

  // Navigation labels
  navigation: {
    home: 'Home',
    dashboard: 'Dashboard',
    about: 'About',
    projects: 'Projects',
    sites: 'Sites',
    reports: 'Reports',
    settings: 'Settings',
  },
};

/**
 * Get a message by category and key
 * @param {string} category - Message category (success, error, warning, info)
 * @param {string} key - Message key
 * @returns {string} Formatted message
 */
export function getMessage(category, key) {
  const categoryObj = TONES[category];
  if (!categoryObj || !categoryObj.messages) return '';
  return categoryObj.messages[key] || '';
}

/**
 * Get a button label by key
 * @param {string} key - Button key
 * @returns {string} Button label
 */
export function getButtonLabel(key) {
  return TONES.buttons[key] || key;
}

/**
 * Get a placeholder text by key
 * @param {string} key - Placeholder key
 * @returns {string} Placeholder text
 */
export function getPlaceholder(key) {
  return TONES.placeholders[key] || '';
}

export default {
  TONES,
  getMessage,
  getButtonLabel,
  getPlaceholder,
};