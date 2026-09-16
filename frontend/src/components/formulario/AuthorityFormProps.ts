import type { ChangeEvent } from 'react';
import type { FormData } from '../../types/formulario';
import type { FormSection } from '../../hooks/useTramiteWizard';

export interface AuthorityFormProps {
  formData: FormData;
  details: Record<string, string | boolean>;
  onSectionChange: (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
    section: FormSection,
  ) => void;
  onSpeciesChange: (index: number, event: ChangeEvent<HTMLInputElement>) => void;
  onAddSpecies: () => void;
  onRemoveSpecies: (index: number) => void;
  onDetailChange: (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => void;
}
