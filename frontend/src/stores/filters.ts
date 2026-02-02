import { create } from 'zustand';
import type { ProjectFilters } from '@/types';

interface FilterState extends ProjectFilters {
  setFilter: <K extends keyof ProjectFilters>(key: K, value: ProjectFilters[K]) => void;
  setFilters: (filters: Partial<ProjectFilters>) => void;
  resetFilters: () => void;
}

const initialFilters: ProjectFilters = {
  search: '',
  status: '',
  project_type: undefined,
  province: undefined,
  district: undefined,
  municipality: undefined,
  barangay: undefined,
  date_from: '',
  date_to: '',
};

export const useFilterStore = create<FilterState>((set) => ({
  ...initialFilters,
  setFilter: (key, value) => set((state) => ({ ...state, [key]: value })),
  setFilters: (filters) => set((state) => ({ ...state, ...filters })),
  resetFilters: () => set(initialFilters),
}));
