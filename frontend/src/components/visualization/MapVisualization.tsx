import React from 'react'

interface Props {
  warehouses?: any[]
  customers?: any[]
  routes?: any[]
  highlightOptimal?: boolean
}

const MapVisualization: React.FC<Props> = () => {
  return (
    <div className="w-full h-full bg-slate-800 rounded-lg flex items-center justify-center text-slate-400 border border-slate-700">
      Map Visualization Placeholder
    </div>
  )
}

export default MapVisualization
