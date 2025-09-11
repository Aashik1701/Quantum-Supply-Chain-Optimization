import React from 'react'

interface Props { activities?: Array<{ title: string; time: string; status: string }> }

const RecentActivity: React.FC<Props> = ({ activities = [] }) => {
  const items = activities.length ? activities : [
    { title: 'QAOA Optimization Completed', time: '2h ago', status: 'Success' },
    { title: 'Data Upload: routes.csv', time: '4h ago', status: 'Processed' },
  ]
  return (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg border border-slate-700">
          <div>
            <h4 className="font-medium text-slate-200">{item.title}</h4>
            <p className="text-sm text-slate-400">{item.time}</p>
          </div>
          <span className="px-2 py-1 bg-green-900/50 text-green-400 rounded-full text-sm border border-green-600">
            {item.status}
          </span>
        </div>
      ))}
    </div>
  )
}

export default RecentActivity
