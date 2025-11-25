import { useState } from 'react';
import type { FeatureCollection, Geometry } from 'geojson';
import './SummaryPanel.css';

interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  total_population: number;
  area_sqm: number;
  num_parts: number;
  total_area_all_sqm: number;
}

interface SummaryPanelProps {
  data: FeatureCollection<Geometry, HalfAmericaProperties> | undefined;
  lambda: number;
}

export function SummaryPanel({ data, lambda }: SummaryPanelProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  if (!data || data.features.length === 0) {
    return null;
  }

  // Get properties from first feature (all features share the same aggregate properties)
  const props = data.features[0].properties;

  // Hero stats
  const populationPercent = ((props.population_selected / props.total_population) * 100).toFixed(1);
  const landAreaPercent = ((props.area_sqm / props.total_area_all_sqm) * 100).toFixed(1);

  // Supporting stats
  const areaSqMiles = (props.area_sqm / 2_589_988).toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div className="summary-panel">
      <h2 className="summary-title">Half of America</h2>

      {/* Hero stats section */}
      <div className="hero-stats">
        <div className="hero-stat">
          <span className="hero-value">{populationPercent}%</span>
          <span className="hero-label">of Total Population</span>
        </div>
        <div className="hero-stat">
          <span className="hero-value">{landAreaPercent}%</span>
          <span className="hero-label">of Total Land Area</span>
        </div>
      </div>

      {/* Supporting stats */}
      <dl className="summary-stats">
        <div className="stat">
          <dt>Area</dt>
          <dd>{areaSqMiles} mi²</dd>
        </div>
        <div className="stat">
          <dt>Regions</dt>
          <dd>{props.num_parts.toLocaleString()}</dd>
        </div>
      </dl>

      {/* Technical stats (de-emphasized) */}
      <div className="technical-stats">
        <span className="technical-stat">λ = {lambda.toFixed(2)}</span>
        <button
          type="button"
          className="info-icon"
          aria-label="Geographic scope information"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          onClick={() => setShowTooltip(!showTooltip)}
          onFocus={() => setShowTooltip(true)}
          onBlur={() => setShowTooltip(false)}
        >
          <span className="icon" aria-hidden="true">ⓘ</span>
        </button>
      </div>

      {showTooltip && (
        <div className="scope-tooltip" role="tooltip">
          <div className="tooltip-section">
            <strong>Geographic Scope</strong>
            <p>
              This visualization covers the conterminous United States only
              (48 states + DC).
            </p>
            <p>
              Alaska, Hawaii, Puerto Rico, and other U.S. territories are
              excluded due to map projection constraints.
            </p>
          </div>
          <p className="tooltip-suggestion">
            See the Method tab for details.
          </p>
        </div>
      )}
    </div>
  );
}
