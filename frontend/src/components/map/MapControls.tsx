import { Plus, Minus, Locate, Layers } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface MapControlsProps {
  onZoomIn?: () => void
  onZoomOut?: () => void
  onLocate?: () => void
  onToggleLayer?: () => void
}

export function MapControls({ onZoomIn, onZoomOut, onLocate, onToggleLayer }: MapControlsProps) {
  return (
    <div className="absolute left-4 top-4 z-10 flex flex-col gap-2">
      <Button variant="secondary" size="icon" onClick={onZoomIn}>
        <Plus className="h-4 w-4" />
      </Button>
      <Button variant="secondary" size="icon" onClick={onZoomOut}>
        <Minus className="h-4 w-4" />
      </Button>
      <Button variant="secondary" size="icon" onClick={onLocate}>
        <Locate className="h-4 w-4" />
      </Button>
      <Button variant="secondary" size="icon" onClick={onToggleLayer}>
        <Layers className="h-4 w-4" />
      </Button>
    </div>
  )
}
