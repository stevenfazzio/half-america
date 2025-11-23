/**
 * Lambda parameter values for surface tension control.
 * λ≈0 minimizes area (dusty map), λ≈0.9 minimizes perimeter (smooth blobs).
 */
export const LAMBDA_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] as const;

export type LambdaValue = (typeof LAMBDA_VALUES)[number];

/**
 * Get the path to a TopoJSON file for a given lambda value.
 * Files are served from /half-america/data/ in production.
 */
export const getTopoJsonPath = (lambda: LambdaValue): string =>
  `${import.meta.env.BASE_URL}data/lambda_${lambda.toFixed(1)}.json`;

/**
 * Get the path to the combined TopoJSON file (all lambda values).
 */
export const getCombinedTopoJsonPath = (): string =>
  `${import.meta.env.BASE_URL}data/combined.json`;
