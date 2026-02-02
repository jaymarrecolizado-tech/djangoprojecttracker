import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2 } from 'lucide-react'
import { projectSchema, type ProjectFormData } from '@/lib/validators'
import { useProvinces, useMunicipalities, useBarangays, useProjectTypes } from '@/hooks/useLocations'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ProjectSite } from '@/types'

interface ProjectFormProps {
  project?: ProjectSite
  onSubmit: (data: ProjectFormData) => void
  isLoading?: boolean
}

const statusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'on_hold', label: 'On Hold' },
]

export function ProjectForm({ project, onSubmit, isLoading }: ProjectFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: project
      ? {
          site_code: project.site_code,
          site_name: project.site_name,
          latitude: project.latitude,
          longitude: project.longitude,
          status: project.status,
          project_type: project.project_type.id,
          province: project.province.id,
          district: project.district?.id || null,
          municipality: project.municipality.id,
          barangay: project.barangay.id,
          remarks: project.remarks,
          activation_date: project.activation_date,
        }
      : undefined,
  })

  const provinceId = watch('province')
  const municipalityId = watch('municipality')

  const { data: provinces } = useProvinces()
  const { data: municipalities } = useMunicipalities({ province: provinceId })
  const { data: barangays } = useBarangays(municipalityId)
  const { data: projectTypes } = useProjectTypes()

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="site_code">Site Code</Label>
          <Input id="site_code" {...register('site_code')} disabled={!!project} />
          {errors.site_code && <p className="text-sm text-destructive">{errors.site_code.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="site_name">Site Name</Label>
          <Input id="site_name" {...register('site_name')} />
          {errors.site_name && <p className="text-sm text-destructive">{errors.site_name.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select onValueChange={(v) => setValue('status', v as ProjectFormData['status'])} defaultValue={project?.status}>
            <SelectTrigger>
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((s) => (
                <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.status && <p className="text-sm text-destructive">{errors.status.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="project_type">Project Type</Label>
          <Select onValueChange={(v) => setValue('project_type', parseInt(v))} defaultValue={project?.project_type.id.toString()}>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              {projectTypes?.map((t) => (
                <SelectItem key={t.id} value={t.id.toString()}>{t.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.project_type && <p className="text-sm text-destructive">{errors.project_type.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="province">Province</Label>
          <Select onValueChange={(v) => setValue('province', parseInt(v))} defaultValue={project?.province.id.toString()}>
            <SelectTrigger>
              <SelectValue placeholder="Select province" />
            </SelectTrigger>
            <SelectContent>
              {provinces?.map((p) => (
                <SelectItem key={p.id} value={p.id.toString()}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.province && <p className="text-sm text-destructive">{errors.province.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="municipality">Municipality</Label>
          <Select onValueChange={(v) => setValue('municipality', parseInt(v))} defaultValue={project?.municipality.id.toString()} disabled={!provinceId}>
            <SelectTrigger>
              <SelectValue placeholder="Select municipality" />
            </SelectTrigger>
            <SelectContent>
              {municipalities?.map((m) => (
                <SelectItem key={m.id} value={m.id.toString()}>{m.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.municipality && <p className="text-sm text-destructive">{errors.municipality.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="barangay">Barangay</Label>
          <Select onValueChange={(v) => setValue('barangay', parseInt(v))} defaultValue={project?.barangay.id.toString()} disabled={!municipalityId}>
            <SelectTrigger>
              <SelectValue placeholder="Select barangay" />
            </SelectTrigger>
            <SelectContent>
              {barangays?.map((b) => (
                <SelectItem key={b.id} value={b.id.toString()}>{b.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.barangay && <p className="text-sm text-destructive">{errors.barangay.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="latitude">Latitude</Label>
          <Input id="latitude" type="number" step="any" {...register('latitude', { valueAsNumber: true })} />
          {errors.latitude && <p className="text-sm text-destructive">{errors.latitude.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="longitude">Longitude</Label>
          <Input id="longitude" type="number" step="any" {...register('longitude', { valueAsNumber: true })} />
          {errors.longitude && <p className="text-sm text-destructive">{errors.longitude.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="activation_date">Activation Date</Label>
          <Input id="activation_date" type="date" {...register('activation_date')} />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="remarks">Remarks</Label>
        <Textarea id="remarks" rows={4} {...register('remarks')} />
        {errors.remarks && <p className="text-sm text-destructive">{errors.remarks.message}</p>}
      </div>

      <div className="flex justify-end gap-4">
        <Button type="submit" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {project ? 'Update Project' : 'Create Project'}
        </Button>
      </div>
    </form>
  )
}
