import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsService } from '@/services/projects';
import type { 
  ProjectFilters, 
  CreateProjectData, 
  UpdateProjectData, 
  StatusChangeData 
} from '@/types';

const PROJECTS_QUERY_KEY = 'projects';

export function useProjects(filters?: ProjectFilters & { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, filters],
    queryFn: () => projectsService.getProjects(filters),
    staleTime: 30 * 1000,
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, id],
    queryFn: () => projectsService.getProject(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateProjectData) => projectsService.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateProjectData }) => 
      projectsService.updateProject(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => projectsService.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] });
    },
  });
}

export function useProjectHistory(id: number) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, id, 'history'],
    queryFn: () => projectsService.getProjectHistory(id),
    enabled: !!id,
  });
}

export function useChangeStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: StatusChangeData }) => 
      projectsService.changeStatus(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY, variables.id] });
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY, variables.id, 'history'] });
    },
  });
}
