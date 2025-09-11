import React from 'react'

interface Props {
  data: any[]
  dataType: 'warehouses' | 'customers' | 'routes'
  onDelete?: () => void
}

const DataPreview: React.FC<Props> = ({ data = [], dataType, onDelete }) => {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-slate-200 capitalize">{dataType}</h4>
        {onDelete && (
          <button className="btn-secondary" onClick={onDelete}>Clear</button>
        )}
      </div>
      <div className="bg-slate-800 rounded-lg p-4 text-sm text-slate-300 border border-slate-700">
        {data.length === 0 ? 'No data loaded.' : JSON.stringify(data.slice(0, 3), null, 2)}
      </div>
    </div>
  )
}

export default DataPreview
