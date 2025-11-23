import { useState } from 'react';

/**
 * Hook to implement lazy mount + state persistence pattern.
 * Component mounts on first activation and stays mounted thereafter.
 * Use with visibility: collapse (NOT display: none) for deck.gl compatibility.
 */
export function useKeepMounted(isActive: boolean) {
  // Track whether component has ever been activated
  // useState initializer runs once, so we initialize based on initial isActive
  const [hasBeenMounted, setHasBeenMounted] = useState(isActive);

  // If isActive becomes true and we haven't mounted yet, update state
  // This uses the functional form to avoid the effect-based setState warning
  if (isActive && !hasBeenMounted) {
    setHasBeenMounted(true);
  }

  return {
    /** Whether the component should render at all */
    shouldRender: hasBeenMounted,
    /** Whether the component is currently visible */
    isVisible: isActive,
  };
}
