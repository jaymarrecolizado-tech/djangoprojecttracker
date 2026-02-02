import { useState, useCallback, useEffect } from 'react';
import { toast } from 'sonner';
import { Upload, FileSpreadsheet, RefreshCw, Trash2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { importService } from '@/services/import';
import { useRealTimeNotifications } from '@/hooks/useNotifications';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { ImportJob, ImportProgress } from '@/types/api';

export function ImportPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [imports, setImports] = useState<ImportJob[]>([]);
  const [currentImport, setCurrentImport] = useState<ImportJob | null>(null);
  const { isConnected } = useRealTimeNotifications();

  // Fetch import history
  const fetchImports = async () => {
    try {
      const response = await importService.getImports(1, 20);
      setImports(response.results);
    } catch (error) {
      console.error('Failed to fetch imports:', error);
    }
  };

  useEffect(() => {
    fetchImports();
  }, []);

  // Listen for import progress updates
  useEffect(() => {
    if (!currentImport) return;

    const pollProgress = async () => {
      try {
        const importJob = await importService.getProgress(currentImport.id);
        setCurrentImport(importJob);

        if (importJob.status === 'completed' || importJob.status === 'failed') {
          setIsUploading(false);
          toast.success(
            importJob.status === 'completed' 
              ? `Import completed: ${importJob.success_count} successful, ${importJob.error_count} failed`
              : 'Import failed'
          );
          fetchImports();
        }
      } catch (error) {
        console.error('Failed to poll progress:', error);
      }
    };

    const interval = setInterval(pollProgress, 2000);
    return () => clearInterval(interval);
  }, [currentImport]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, []);

  const handleFileSelect = (file: File) => {
    const validation = importService.validateCSVFile(file);
    if (!validation.valid) {
      toast.error(validation.error);
      return;
    }
    setSelectedFile(file);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(10);

    try {
      const importJob = await importService.uploadCSV(selectedFile);
      setCurrentImport(importJob);
      setUploadProgress(50);
      toast.info('Import started. This may take a few minutes...');
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Failed to start import');
      setIsUploading(false);
    }
  };

  const handleCancelImport = async () => {
    if (!currentImport) return;

    try {
      await importService.cancelImport(currentImport.id);
      toast.info('Import cancelled');
      setCurrentImport(null);
      setIsUploading(false);
      setUploadProgress(0);
    } catch (error) {
      console.error('Failed to cancel import:', error);
      toast.error('Failed to cancel import');
    }
  };

  const handleDeleteImport = async (importId: number) => {
    try {
      await importService.deleteImport(importId);
      toast.success('Import deleted');
      fetchImports();
    } catch (error) {
      console.error('Failed to delete import:', error);
      toast.error('Failed to delete import');
    }
  };

  const handleRetryImport = async (importId: number) => {
    try {
      const importJob = await importService.retryImport(importId);
      setCurrentImport(importJob);
      toast.info('Retrying import...');
    } catch (error) {
      console.error('Failed to retry import:', error);
      toast.error('Failed to retry import');
    }
  };

  const getStatusIcon = (status: ImportJob['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-4 w-4 text-amber-500" />;
    }
  };

  const getStatusBadge = (status: ImportJob['status']) => {
    const variants: Record<ImportJob['status'], 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      processing: 'default',
      completed: 'default',
      failed: 'destructive',
    };
    
    return (
      <Badge variant={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Import Projects</h1>
        <p className="text-muted-foreground">
          Import projects from CSV file
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload CSV File</CardTitle>
          <CardDescription>
            Drag and drop your CSV file here, or click to browse
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center ${
              isDragging ? 'border-primary bg-primary/5' : 'border-border'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".csv"
              className="hidden"
              id="file-upload"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  handleFileSelect(e.target.files[0]);
                }
              }}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-4 text-sm text-muted-foreground">
                {selectedFile ? selectedFile.name : 'Supported format: .csv'}
              </p>
              {!selectedFile && (
                <Button variant="outline" className="mt-4">
                  Browse Files
                </Button>
              )}
            </label>
          </div>

          {selectedFile && (
            <div className="mt-4 flex items-center justify-between p-3 bg-accent rounded-lg">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">{selectedFile.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isUploading ? (
                  <>
                    <span className="text-sm text-muted-foreground">
                      {currentImport?.status === 'processing' ? 'Processing...' : 'Uploading...'}
                    </span>
                    <Button variant="outline" size="sm" onClick={handleCancelImport}>
                      Cancel
                    </Button>
                  </>
                ) : (
                  <Button onClick={handleUpload}>
                    <Upload className="mr-2 h-4 w-4" />
                    Import
                  </Button>
                )}
              </div>
            </div>
          )}

          {isUploading && currentImport && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Progress</span>
                <span>
                  {currentImport.processed_rows}/{currentImport.total_rows} rows
                </span>
              </div>
              <Progress 
                value={importService.calculateProgress(currentImport)} 
                className="h-2"
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{currentImport.success_count} successful</span>
                <span>{currentImport.error_count} errors</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Import History</CardTitle>
            <Button variant="outline" size="sm" onClick={fetchImports}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {imports.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No imports yet
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Rows</TableHead>
                  <TableHead>Success</TableHead>
                  <TableHead>Errors</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {imports.map((importJob) => (
                  <TableRow key={importJob.id}>
                    <TableCell className="font-medium">{importJob.file_name}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(importJob.status)}
                        {getStatusBadge(importJob.status)}
                      </div>
                    </TableCell>
                    <TableCell>{importJob.total_rows}</TableCell>
                    <TableCell>
                      <span className="text-green-600">{importJob.success_count}</span>
                    </TableCell>
                    <TableCell>
                      <span className={importJob.error_count > 0 ? 'text-red-600' : ''}>
                        {importJob.error_count}
                      </span>
                    </TableCell>
                    <TableCell>
                      {new Date(importJob.uploaded_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        {importJob.status === 'failed' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleRetryImport(importJob.id)}
                          >
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteImport(importJob.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
