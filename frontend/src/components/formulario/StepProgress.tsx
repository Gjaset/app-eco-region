import { Check, FileText, MapPinned, Trees } from 'lucide-react';

const steps = [
  { label: 'Titular', icon: FileText },
  { label: 'Predio', icon: MapPinned },
  { label: 'Aprovechamiento', icon: Trees },
];

interface StepProgressProps {
  activeStep: number;
}

export function StepProgress({ activeStep }: StepProgressProps) {
  return (
    <div className="step-progress" aria-label="Progreso del formulario">
      {steps.map((step, index) => {
        const Icon = index < activeStep ? Check : step.icon;
        return (
          <div className={`step ${index <= activeStep ? 'is-active' : ''}`} key={step.label}>
            <span className="step-icon"><Icon size={16} /></span>
            <span>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}
