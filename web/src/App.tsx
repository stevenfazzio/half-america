import { useState, useMemo } from 'react';
import { Map } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './components/DeckGLOverlay';
import { LambdaSlider } from './components/LambdaSlider';
import { SummaryPanel } from './components/SummaryPanel';
import { LoadingOverlay } from './components/LoadingOverlay';
import { ErrorOverlay } from './components/ErrorOverlay';
import { useTopoJsonLoader } from './hooks/useTopoJsonLoader';
import { LAMBDA_VALUES } from './types/lambda';
import type { LambdaValue } from './types/lambda';
import './App.css';

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

function App() {
  const { state, retry } = useTopoJsonLoader();
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(0.5);

  const layers = useMemo(() => {
    if (state.status !== 'success') return [];

    return LAMBDA_VALUES.map((lambda) => {
      const data = state.data.get(lambda);
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
  }, [state, currentLambda]);

  if (state.status === 'loading') {
    return <LoadingOverlay loaded={state.loaded} total={state.total} />;
  }

  if (state.status === 'idle') {
    return <LoadingOverlay loaded={0} total={LAMBDA_VALUES.length} />;
  }

  if (state.status === 'error') {
    return <ErrorOverlay message={state.error.message} onRetry={retry} />;
  }

  return (
    <div className="app">
      <Map
        initialViewState={INITIAL_VIEW_STATE}
        style={{ width: '100%', height: '100vh' }}
        mapStyle={CARTO_DARK_MATTER}
      >
        <DeckGLOverlay layers={layers} interleaved />
      </Map>
      <LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
      <SummaryPanel data={state.data.get(currentLambda)} lambda={currentLambda} />
    </div>
  );
}

export default App;
