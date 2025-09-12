import React from 'react'
import { useDispatch } from 'react-redux'
import { setMethod } from '../../store/optimizationSlice'

const MethodSelector: React.FC = () => {
  const dispatch = useDispatch()
  return (
    <div className="space-y-2">
      <h4 className="font-medium text-slate-200">Optimization Method</h4>
      <select
        className="block w-full px-3 py-2 border border-slate-600 rounded-md shadow-sm bg-slate-800 text-slate-200 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        onChange={(e) => dispatch(setMethod(e.target.value))}
        defaultValue="hybrid"
      >
        <option value="hybrid">Hybrid (QAOA + Classical)</option>
        <option value="quantum">Quantum (QAOA)</option>
        <option value="classical">Classical (OR-Tools)</option>
        <option value="vrp">Vehicle Routing Problem (VRP)</option>
        <option value="hybrid_vrp">Hybrid VRP (Classical + Quantum)</option>
      </select>
    </div>
  )
}

export default MethodSelector
