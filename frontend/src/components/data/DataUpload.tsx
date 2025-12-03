import React, { useState, useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { uploadData } from '../../store/dataSlice'
import { AppDispatch } from '../../store'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { useToast } from '../../hooks/useToast'
import { cn } from '@/lib/utils'

interface DataUploadProps {
  onUploadComplete?: () => void
}

const DataUpload: React.FC<DataUploadProps> = ({ onUploadComplete }) => {
  const dispatch = useDispatch<AppDispatch>()
  const toast = useToast()
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [selectedDataType, setSelectedDataType] = useState<string>('warehouses')

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [selectedDataType])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      toast.error({ 
        title: 'Invalid File Type', 
        description: 'Please upload a CSV file.' 
      })
      return
    }

    setUploading(true)
    setUploadSuccess(false)
    
    try {
      await dispatch(uploadData({ file, dataType: selectedDataType })).unwrap()
      setUploadSuccess(true)
      toast.success({ 
        title: 'Upload Successful!', 
        description: `${selectedDataType} data has been uploaded successfully.` 
      })
      
      if (onUploadComplete) {
        onUploadComplete()
      }
      
      // Reset success state after 3 seconds
      setTimeout(() => setUploadSuccess(false), 3000)
    } catch (error: any) {
      toast.error({ 
        title: 'Upload Failed', 
        description: error?.message || 'An error occurred during upload.' 
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-xl font-bold text-slate-200 flex items-center gap-2">
          <Upload className="h-5 w-5 text-blue-400" />
          Upload Data
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Data Type Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">
            Data Type
          </label>
          <Select value={selectedDataType} onValueChange={setSelectedDataType}>
            <SelectTrigger className="w-full bg-slate-700 border-slate-600 text-slate-200">
              <SelectValue placeholder="Select data type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="warehouses">Warehouses</SelectItem>
              <SelectItem value="customers">Customers</SelectItem>
              <SelectItem value="routes">Routes</SelectItem>
            </SelectContent>
          </Select>
        </div>

      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 transition-colors
          ${dragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="text-center">
          {uploading ? (
            <div>
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Uploading...</p>
            </div>
          ) : (
            <>
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-slate-200">
                    Drop CSV files here, or{' '}
                    <span className="text-blue-600 hover:text-blue-500">browse</span>
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".csv"
                    onChange={handleFileInput}
                  />
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  CSV files up to 10MB
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Expected Format Info */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-2">
          Expected CSV Format for {selectedDataType}:
        </h4>
        <div className="text-xs text-gray-600 font-mono">
          {selectedDataType === 'warehouses' && 'id,name,latitude,longitude,capacity,operating_cost,country'}
          {selectedDataType === 'customers' && 'id,name,latitude,longitude,demand,priority,country'}
          {selectedDataType === 'routes' && 'id,warehouse_id,customer_id,distance_km,transport_mode,cost_per_km,co2_per_km,speed_kmh'}
        </div>
      </div>
    </div>
  )
}

export default DataUpload