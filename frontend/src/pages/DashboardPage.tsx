import React, { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import { fetchDashboardData } from '../store/dataSlice'
import DashboardStats from '../components/dashboard/DashboardStats'
import QuickActions from '../components/dashboard/QuickActions'
import RecentActivity from '../components/dashboard/RecentActivity'
import PerformanceCharts from '../components/visualization/PerformanceCharts'
import MapVisualization from '../components/visualization/MapVisualization'

const DashboardPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { dashboardData, loading, error } = useSelector((state: RootState) => state.data)
  const { user } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    dispatch(fetchDashboardData())
  }, [dispatch])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner" />
        <span className="ml-2 text-slate-300">Loading dashboard...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/50 border border-red-600 rounded-lg p-4">
        <h3 className="text-lg font-medium text-red-400">Error Loading Dashboard</h3>
        <p className="text-red-300">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800 rounded-lg shadow-sm border border-slate-700 p-6">
        <h1 className="text-2xl font-bold text-slate-200">
          Welcome back, {user?.name || 'User'}!
        </h1>
        <p className="text-slate-300 mt-1">
          Monitor your supply chain optimization performance and insights.
        </p>
      </div>

      {/* Stats Overview */}
      <DashboardStats data={dashboardData?.stats} />

      {/* Quick Actions */}
      <QuickActions />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Charts */}
        <div className="bg-slate-800 rounded-lg shadow-sm border border-slate-700 p-6">
          <h2 className="text-lg font-semibold text-slate-200 mb-4">
            Performance Overview
          </h2>
          <PerformanceCharts data={dashboardData?.performance} />
        </div>

        {/* Recent Activity */}
        <div className="bg-slate-800 rounded-lg shadow-sm border border-slate-700 p-6">
          <h2 className="text-lg font-semibold text-slate-200 mb-4">
            Recent Activity
          </h2>
          <RecentActivity activities={dashboardData?.recentActivity} />
        </div>
      </div>

      {/* Map Visualization */}
      <div className="bg-slate-800 rounded-lg shadow-sm border border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">
          Supply Chain Network
        </h2>
        <div className="h-96">
          <MapVisualization 
            warehouses={dashboardData?.warehouses}
            customers={dashboardData?.customers}
            routes={dashboardData?.routes}
          />
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
