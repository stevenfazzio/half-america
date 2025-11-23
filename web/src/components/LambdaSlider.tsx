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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value, 10);
    onChange(LAMBDA_VALUES[index]);
  };

  return (
    <div className="lambda-slider">
      <label htmlFor="lambda-slider" className="lambda-label">
        Surface Tension (λ)
      </label>
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
          aria-valuemax={0.9}
          aria-valuenow={value}
          aria-valuetext={`Lambda ${value.toFixed(1)}`}
        />
        <span className="lambda-value">{value.toFixed(1)}</span>
      </div>
      <p className="lambda-hint">
        {value < 0.3 ? 'Minimizes area (more fragmented)' :
         value > 0.7 ? 'Minimizes perimeter (smoother shapes)' :
         'Balanced optimization'}
      </p>
    </div>
  );
}
