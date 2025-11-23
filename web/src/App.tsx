import { LAMBDA_VALUES, getTopoJsonPath } from './types/lambda';
import './App.css';

function App() {
  return (
    <div className="app">
      <h1>Half of America</h1>
      <p>Project setup complete. Map implementation coming in Sub-Phase 5.2.</p>

      <section>
        <h2>Stack</h2>
        <p>Using MapLibre GL JS with CARTO basemaps (no API key required).</p>
      </section>

      <section>
        <h2>Data Files</h2>
        <p>TopoJSON files available for lambda values:</p>
        <ul>
          {LAMBDA_VALUES.map((lambda) => (
            <li key={lambda}>
              <code>{getTopoJsonPath(lambda)}</code>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
