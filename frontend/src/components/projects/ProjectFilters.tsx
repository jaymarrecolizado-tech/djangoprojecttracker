import { Search, X } from 'lucide-react'
import { useFilterStore } from '@/stores/filters'
import { useProvinces, useMunicipalities, useBarangays, useProjectTypes } from '@/hooks/useLocations'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'

const statusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'on_hold', label: 'On Hold' },
]

export function ProjectFilters() {
  const filters = useFilterStore()
  const { data: provinces } = useProvinces()
  const { data: municipalities } = useMunicipalities({ province: filters.province })
  const { data: barangays } = useBarangays(filters.municipality)
  const { data: projectTypes } = useProjectTypes()

  const hasFilters = filters.search || filters.status || filters.project_type || 
                     filters.province || filters.municipality || filters.barangay ||
                     filters.date_from || filters.date_to

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search projects..."
              value={filters.search}
              onChange={(e) => filters.setFilter('search', e.target.value)}
              className="pl-9"
            />
          </div>

          <Select
            value={filters.status || ''}
            onValueChange={(v) => filters.setFilter('status', v || '')}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              {statusOptions.map((s) => (
                <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.project_type?.toString() || ''}
            onValueChange={(v) => filters.setFilter('project_type', v ? parseInt(v) : undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Types</SelectItem>
              {projectTypes?.map((t) => (
                <SelectItem key={t.id} value={t.id.toString()}>{t.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.province?.toString() || ''}
            onValueChange={(v) => {
              filters.setFilters({ 
                province: v ? parseInt(v) : undefined,
                municipality: undefined,
                barangay: undefined
              })
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by province" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Provinces</SelectItem>
              {provinces?.map((p) => (
                <SelectItem key={p.id} value={p.id.toString()}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.municipality?.toString() || ''}
            onValueChange={(v) => {
              filters.setFilters({
                municipality: v ? parseInt(v) : undefined,
                barangay: undefined
              })
            }}
            disabled={!filters.province}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by municipality" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Municipalities</SelectItem>
              {municipalities?.map((m) => (
                <SelectItem key={m.id} value={m.id.toString()}>{m.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={filters.barangay?.toString() || ''}
            onValueChange={(v) => filters.setFilter('barangay', v ? parseInt(v) : undefined)}
            disabled={!filters.municipality}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by barangay" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Barangays</SelectItem>
              {barangays?.map((b) => (
                <SelectItem key={b.id} value={b.id.toString()}>{b.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            type="date"
            placeholder="From date"
            value={filters.date_from || ''}
            onChange={(e) => filters.setFilter('date_from', e.target.value)}
          />

          <Input
            type="date"
            placeholder="To date"
            value={filters.date_to || ''}
            onChange={(e) => filters.setFilter('date_to', e.target.value)}
          />
        </div>

        {hasFilters && (
          <div className="mt-4 flex justify-end">
            <Button variant="outline" size="sm" onClick={() => filters.resetFilters()}>
              <X className="mr-2 h-4 w-4" />
              Clear Filters
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
