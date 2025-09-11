import React from 'react'

const DataExport: React.FC<{ data: { warehouses: any[]; customers: any[]; routes: any[] } }> = ({ data }) => {
  const handleExport = (format: 'csv' | 'json') => {
    // placeholder
    alert(`Exporting ${format}...`)
  }
  return (
    <div className="space-x-3">
      <button className="btn-secondary" onClick={() => handleExport('csv')}>Export CSV</button>
      <button className="btn-secondary" onClick={() => handleExport('json')}>Export JSON</button>
    </div>
  )
}

export default DataExport
