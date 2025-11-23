import { useState, useMemo, useRef, useEffect } from 'react';
import { Map } from 'react-map-gl/maplibre';
import type { MapRef } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './DeckGLOverlay';
import { LambdaSlider } from './LambdaSlider';
import { SummaryPanel } from './SummaryPanel';
import { useKeepMounted } from '../hooks/useKeepMounted';
import { LAMBDA_VALUES } from '../types/lambda';
import type { LambdaValue } from '../types/lambda';
import type { LoaderState } from '../hooks/useTopoJsonLoader';
import './MapTab.css';

const CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};

// Okabe-Ito Blue at 60% opacity
const FILL_COLOR: [number, number, number, number] = [0, 114, 178, 153];
const HIGHLIGHT_COLOR: [number, number, number, number] = [255, 255, 255, 100];

interface MapTabProps {
  isActive: boolean;
  loaderState: LoaderState;
}

export function MapTab({ isActive, loaderState }: MapTabProps) {
  const { shouldRender, isVisible } = useKeepMounted(isActive);
  const mapRef = useRef<MapRef>(null);
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(0.5);

  // Trigger map resize when becoming visible
  useEffect(() => {
    if (isVisible && mapRef.current) {
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        mapRef.current?.resize();
      });
    }
  }, [isVisible]);

  const layers = useMemo(() => {
    if (loaderState.status !== 'success') return [];

    return LAMBDA_VALUES.map((lambda) => {
      const data = loaderState.data.get(lambda);
      return new GeoJsonLayer({
        id: `layer-${lambda.toFixed(2)}`,
        data,
        visible: lambda === currentLambda,
        filled: true,
        stroked: false,
        getFillColor: FILL_COLOR,
        pickable: true,
        autoHighlight: true,
        highlightColor: HIGHLIGHT_COLOR,
      });
    });
  }, [loaderState, currentLambda]);

  if (!shouldRender) {
    return null;
  }

  const showMap = loaderState.status === 'success';

  return (
    <div
      className="map-tab"
      role="tabpanel"
      id="map-tab"
      aria-labelledby="map"
      style={{ visibility: isVisible ? 'visible' : 'collapse' }}
    >
      {showMap && (
        <>
          <Map
            ref={mapRef}
            initialViewState={INITIAL_VIEW_STATE}
            style={{ width: '100%', height: '100vh' }}
            mapStyle={CARTO_DARK_MATTER}
          >
            <DeckGLOverlay layers={layers} interleaved />
          </Map>
          <LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
          <SummaryPanel data={loaderState.data.get(currentLambda)} lambda={currentLambda} />
        </>
      )}
    </div>
  );
}
