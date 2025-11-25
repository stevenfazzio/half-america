import { useState } from 'react';
import { LAMBDA_VALUES } from '../types/lambda';
import type { LambdaValue } from '../types/lambda';
import './LambdaSlider.css';

interface LambdaSliderProps {
  value: LambdaValue;
  onChange: (value: LambdaValue) => void;
  disabled?: boolean;
}

export function LambdaSlider({ value, onChange, disabled }: LambdaSliderProps) {
  const stepIndex = LAMBDA_VALUES.indexOf(value);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value, 10);
    onChange(LAMBDA_VALUES[index]);
  };

  return (
    <div className="lambda-slider">
      <label htmlFor="lambda-slider" className="lambda-label">
        Surface Tension (λ)
      </label>

      <button
        type="button"
        className="info-icon"
        aria-label="What is surface tension? Click for details"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
      >
        <span className="icon" aria-hidden="true">ⓘ</span>
      </button>

      {showTooltip && (
        <div className="lambda-tooltip" role="tooltip">
          <div className="tooltip-section">
            <strong>What "Surface Tension" means here:</strong>
            <p>
              In liquids, surface tension causes water to bead into smooth, rounded shapes.
            </p>
            <p>
              Here, increasing λ has a similar effect—pulling the selected regions into
              smoother, more cohesive boundaries.
            </p>
          </div>
          <div className="tooltip-section">
            <strong>Practically:</strong>
            <p>
              Low λ preserves fine detail but creates many tiny fragments.
            </p>
            <p>
              High λ smooths edges and merges nearby areas into clearer shapes.
            </p>
          </div>
          <div className="tooltip-section">
            <strong>Learn more:</strong>
            <p className="tooltip-suggestion">
              See the Story tab for examples and motivation.
            </p>
            <p className="tooltip-suggestion">
              See the Method tab for the full formulation.
            </p>
          </div>
        </div>
      )}

      <div className="slider-container">
        <input
          id="lambda-slider"
          type="range"
          min={0}
          max={LAMBDA_VALUES.length - 1}
          step={1}
          value={stepIndex}
          onChange={handleChange}
          disabled={disabled}
          aria-valuemin={0}
          aria-valuemax={0.98}
          aria-valuenow={value}
          aria-valuetext={`Lambda ${value.toFixed(2)}`}
        />
        <span className="lambda-value">{value.toFixed(2)}</span>
      </div>
      <div className="slider-endpoints">
        <div className="endpoint-left">
          <div className="endpoint-arrow">←</div>
          <div className="endpoint-primary">Minimize Area</div>
          <div className="endpoint-secondary">More Fragmented</div>
        </div>
        <div className="endpoint-right">
          <div className="endpoint-arrow">→</div>
          <div className="endpoint-primary">Minimize Perimeter</div>
          <div className="endpoint-secondary">More Compact</div>
        </div>
      </div>
    </div>
  );
}
