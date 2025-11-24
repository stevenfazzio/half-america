import { useCallback, useSyncExternalStore } from 'react';
import * as topojson from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import type { FeatureCollection, Feature, Geometry, MultiPolygon, Position } from 'geojson';
import { LAMBDA_VALUES, getTopoJsonPath } from '../types/lambda';
import type { LambdaValue } from '../types/lambda';

interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  total_population: number;
  area_sqm: number;
  num_parts: number;
}

type HalfAmericaTopology = Topology<{
  selected_region: GeometryCollection<HalfAmericaProperties>;
}>;

export type LoaderState =
  | { status: 'idle' }
  | { status: 'loading'; loaded: number; total: number }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>> };

/**
 * Split MultiPolygon features into individual Polygon features.
 * This enables deck.gl's autoHighlight to work on individual polygons.
 */
function explodeMultiPolygons(
  fc: FeatureCollection<Geometry, HalfAmericaProperties>
): FeatureCollection<Geometry, HalfAmericaProperties> {
  const features: Feature<Geometry, HalfAmericaProperties>[] = [];
  for (const feature of fc.features) {
    if (feature.geometry.type === 'MultiPolygon') {
      const multiPoly = feature.geometry as MultiPolygon;
      for (const coordinates of multiPoly.coordinates) {
        features.push({
          type: 'Feature',
          properties: feature.properties,
          geometry: { type: 'Polygon', coordinates: coordinates as Position[][] },
        });
      }
    } else {
      features.push(feature as Feature<Geometry, HalfAmericaProperties>);
    }
  }
  return { type: 'FeatureCollection', features };
}

async function loadSingleTopoJSON(lambda: LambdaValue): Promise<FeatureCollection<Geometry, HalfAmericaProperties>> {
  const response = await fetch(getTopoJsonPath(lambda));
  if (!response.ok) {
    throw new Error(`Failed to load lambda_${lambda.toFixed(2)}.json: ${response.status}`);
  }
  const topology = await response.json() as HalfAmericaTopology;
  const geojson = topojson.feature(topology, topology.objects.selected_region) as FeatureCollection<Geometry, HalfAmericaProperties>;
  return explodeMultiPolygons(geojson);
}

// Module-level cache for loaded data
let cachedState: LoaderState = { status: 'idle' };
let loadPromise: Promise<void> | null = null;
const listeners = new Set<() => void>();

function subscribe(callback: () => void) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

function getSnapshot() {
  return cachedState;
}

function notifyListeners() {
  for (const listener of listeners) {
    listener();
  }
}

async function performLoad() {
  cachedState = { status: 'loading', loaded: 0, total: LAMBDA_VALUES.length };
  notifyListeners();

  const dataMap = new Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>>();

  try {
    // Load all files in parallel with batching to avoid overwhelming the browser
    const BATCH_SIZE = 10; // 10 concurrent requests at a time
    const batches: LambdaValue[][] = [];

    for (let i = 0; i < LAMBDA_VALUES.length; i += BATCH_SIZE) {
      batches.push(LAMBDA_VALUES.slice(i, i + BATCH_SIZE) as LambdaValue[]);
    }

    let loadedCount = 0;
    for (const batch of batches) {
      const results = await Promise.all(
        batch.map(async (lambda) => {
          const geojson = await loadSingleTopoJSON(lambda);
          return { lambda, geojson };
        })
      );

      for (const { lambda, geojson } of results) {
        dataMap.set(lambda, geojson);
      }

      loadedCount += batch.length;
      cachedState = { status: 'loading', loaded: loadedCount, total: LAMBDA_VALUES.length };
      notifyListeners();
    }

    cachedState = { status: 'success', data: dataMap };
  } catch (err) {
    cachedState = { status: 'error', error: err instanceof Error ? err : new Error(String(err)) };
  }

  loadPromise = null;
  notifyListeners();
}

function startLoading() {
  if (loadPromise === null && cachedState.status !== 'success') {
    loadPromise = performLoad();
  }
}

// Start loading immediately when module is imported
startLoading();

export function useTopoJsonLoader() {
  const state = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  const retry = useCallback(() => {
    loadPromise = null;
    cachedState = { status: 'idle' };
    startLoading();
  }, []);

  return { state, retry };
}
