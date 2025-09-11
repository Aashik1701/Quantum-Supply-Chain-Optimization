import React from 'react'
import { useDispatch } from 'react-redux'
import { updateParameters } from '../../store/optimizationSlice'

const ParameterConfig: React.FC = () => {
  const dispatch = useDispatch()
  return (
    <div className="space-y-4">
      <h4 className="font-medium text-slate-200">Parameters</h4>
      <div className="space-y-3">
        <label className="block">
          <span className="text-sm text-slate-300">Iterations</span>
          <input
            type="number"
            className="block w-full px-3 py-2 mt-1 border rounded-md shadow-sm border-slate-600 bg-slate-800 text-slate-200 focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400"
            defaultValue={50}
            onChange={(e) => dispatch(updateParameters({ iterations: Number(e.target.value) }))}
          />
        </label>
        <label className="block">
          <span className="text-sm text-slate-300">Seed</span>
          <input
            type="number"
            className="block w-full px-3 py-2 mt-1 border rounded-md shadow-sm border-slate-600 bg-slate-800 text-slate-200 focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400"
            defaultValue={42}
            onChange={(e) => dispatch(updateParameters({ seed: Number(e.target.value) }))}
          />
        </label>
      </div>
    </div>
  )
}

export default ParameterConfig
