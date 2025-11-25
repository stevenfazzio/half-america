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
            <strong>What it does:</strong>
            <p>
              Surface Tension (λ) controls the tradeoff between compact boundaries
              and precise area selection. Lower values create scattered regions
              that minimize land area. Higher values create smooth, organic shapes.
            </p>
            <p className="tooltip-suggestion">Visit the Story tab to learn more.</p>
          </div>
          <div className="tooltip-section">
            <strong>How it works:</strong>
            <p>
              Uses max-flow min-cut graph optimization with a perimeter
              minimization term. λ weights the boundary smoothness penalty
              in the energy function.
            </p>
            <p className="tooltip-suggestion">See the Method tab for full methodology.</p>
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
