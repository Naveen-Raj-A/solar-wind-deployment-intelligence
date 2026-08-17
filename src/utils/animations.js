// src/utils/animations.js
/**
 * Animation utilities for the application
 */

/**
 * CSS keyframes for common animations
 * These can be injected into a style tag or used with styled-components
 */
export const keyframes = {
  fadeIn: `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  `,
  fadeOut: `
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
  `,
  slideUp: `
    @keyframes slideUp {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `,
  slideDown: `
    @keyframes slideDown {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `,
  scaleIn: `
    @keyframes scaleIn {
      from { transform: scale(0.9); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `,
  pulse: `
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
  `,
  shake: `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
      20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
  `,
};

/**
 * Animation classes that can be applied directly to elements
 */
export const animationClasses = {
  fadeIn: 'animate-fadeIn',
  fadeOut: 'animate-fadeOut',
  slideUp: 'animate-slideUp',
  slideDown: 'animate-slideDown',
  scaleIn: 'animate-scaleIn',
  pulse: 'animate-pulse',
  infiniteSpin: 'animate-spin',
  bounce: 'animate-bounce',
};

/**
 * Transition classes for smooth state changes
 */
export const transitionClasses = {
  fast: 'transition duration-150 ease-in-out',
  normal: 'transition duration-300 ease-in-out',
  slow: 'transition duration-500 ease-in-out',
  none: 'transition-none',
};

/**
 * Get animation style object for inline styles
 * @param {string} type - Animation type (fadeIn, slideUp, etc.)
 * @param {number} duration - Duration in seconds (default: 0.5)
 * @param {string} timing - Timing function (default: 'ease')
 * @returns {Object} Style object
 */
export function getAnimationStyle(type, duration = 0.5, timing = 'ease') {
  const animations = {
    fadeIn: { animation: `fadeIn ${duration}s ${timing} forwards` },
    fadeOut: { animation: `fadeOut ${duration}s ${timing} forwards` },
    slideUp: { animation: `slideUp ${duration}s ${timing} forwards` },
    slideDown: { animation: `slideDown ${duration}s ${timing} forwards` },
    scaleIn: { animation: `scaleIn ${duration}s ${timing} forwards` },
    pulse: { animation: `pulse ${duration}s ${timing} infinite` },
  };

  return animations[type] || {};
}

/**
 * Get keyframes string for injection into CSS
 * @returns {string} CSS keyframes definitions
 */
export function getKeyframesCss() {
  return Object.values(keyframes).join('\n');
}

/**
 * Stagger children animation delay
 * @param {number} index - Index of the child
 * @param {number} baseDelay - Base delay in seconds (default: 0.1)
 * @param {number} multiplier - Multiplier for delay (default: 0.1)
 * @returns {string} CSS delay value
 */
export function getStaggerDelay(index, baseDelay = 0.1, multiplier = 0.1) {
  return `${baseDelay + index * multiplier}s`;
}

export default {
  keyframes,
  animationClasses,
  transitionClasses,
  getAnimationStyle,
  getKeyframesCss,
  getStaggerDelay,
};