import React, { useState, useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { uploadData } from '../../store/dataSlice'
import { AppDispatch } from '../../store'

interface DataUploadProps {
  onUploadComplete?: () => void
}

const DataUpload: React.FC<DataUploadProps> = ({ onUploadComplete }) => {
  const dispatch = useDispatch<AppDispatch>()
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
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
      alert('Please upload a CSV file')
      return
    }

    setUploading(true)
    try {
      await dispatch(uploadData({ file, dataType: selectedDataType })).unwrap()
      alert('File uploaded successfully!')
      if (onUploadComplete) {
        onUploadComplete()
      }
    } catch (error) {
      alert('Upload failed: ' + error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-md p-6 border border-slate-700">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Upload Data</h3>
      
      {/* Data Type Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data Type
        </label>
        <select
          value={selectedDataType}
          onChange={(e) => setSelectedDataType(e.target.value)}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="warehouses">Warehouses</option>
          <option value="customers">Customers</option>
          <option value="routes">Routes</option>
        </select>
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
          {selectedDataType === 'routes' && 'id,warehouse_id,customer_id,transport_mode,cost_per_km,co2_per_km,speed_kmh'}
        </div>
      </div>
    </div>
  )
}

export default DataUpload