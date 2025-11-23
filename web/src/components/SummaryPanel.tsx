import type { FeatureCollection, Geometry } from 'geojson';
import './SummaryPanel.css';

interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  area_sqm: number;
  num_parts: number;
}

interface SummaryPanelProps {
  data: FeatureCollection<Geometry, HalfAmericaProperties> | undefined;
  lambda: number;
}

// US population from 2022 ACS (same year as our data)
const US_TOTAL_POPULATION = 331_893_745;

export function SummaryPanel({ data, lambda }: SummaryPanelProps) {
  if (!data || data.features.length === 0) {
    return null;
  }

  // Get properties from first feature (all features share the same aggregate properties)
  const props = data.features[0].properties;
  const populationPercent = ((props.population_selected / US_TOTAL_POPULATION) * 100).toFixed(1);
  // Convert area from square meters to square miles (1 sq mi = 2,589,988 sq m)
  const areaSqMiles = (props.area_sqm / 2_589_988).toLocaleString(undefined, { maximumFractionDigits: 0 });
  // Calculate area per region
  const areaPerRegion = (props.area_sqm / 2_589_988 / props.num_parts).toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div className="summary-panel">
      <h2 className="summary-title">Half of America</h2>
      <dl className="summary-stats">
        <div className="stat">
          <dt>Population</dt>
          <dd>{populationPercent}%</dd>
        </div>
        <div className="stat">
          <dt>Area</dt>
          <dd>{areaSqMiles} mi²</dd>
        </div>
        <div className="stat">
          <dt>Regions</dt>
          <dd>{props.num_parts.toLocaleString()}</dd>
        </div>
        <div className="stat">
          <dt>Area/Region</dt>
          <dd>{areaPerRegion} mi²</dd>
        </div>
        <div className="stat">
          <dt>Lambda (λ)</dt>
          <dd>{lambda.toFixed(1)}</dd>
        </div>
      </dl>
    </div>
  );
}
