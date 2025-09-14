import React, { useCallback, useState } from 'react'
import { Wrapper, Status } from '@googlemaps/react-wrapper'

interface Warehouse {
  id: string
  name: string
  latitude: number
  longitude: number
  capacity: number
  country: string
}

interface Customer {
  id: string
  name: string
  latitude: number
  longitude: number
  demand: number
  country: string
}

interface Route {
  id: string
  warehouseId: string
  customerId: string
  distanceKm: number
  cost: number
}

interface Props {
  warehouses?: Warehouse[]
  customers?: Customer[]
  routes?: Route[]
  highlightOptimal?: boolean
}

const GoogleMap: React.FC<{
  warehouses: Warehouse[]
  customers: Customer[]
  routes: Route[]
}> = ({ warehouses, customers, routes }) => {
  const [map, setMap] = useState<google.maps.Map>()

  const ref = useCallback((node: HTMLDivElement | null) => {
    if (node && !map) {
      // Default center (USA)
      const center = { lat: 39.8283, lng: -98.5795 }
      
      // Calculate bounds if we have data
      const mapId = import.meta.env.VITE_GOOGLE_MAP_ID as string | undefined
      if (warehouses.length > 0 || customers.length > 0) {
        const bounds = new google.maps.LatLngBounds()
        warehouses.forEach(w => bounds.extend({ lat: w.latitude, lng: w.longitude }))
        customers.forEach(c => bounds.extend({ lat: c.latitude, lng: c.longitude }))
        
        const newMap = new google.maps.Map(node, {
          zoom: 6,
          center,
          mapTypeId: 'roadmap',
          ...(mapId ? { mapId } : {})
        })
        
        // Add warehouse markers (blue) using AdvancedMarkerElement
        warehouses.forEach(warehouse => {
          const pin = new (google as any).maps.marker.PinElement({
            background: '#3b82f6',
            borderColor: '#1e40af',
            glyphColor: '#ffffff'
          })
          const marker = new (google as any).maps.marker.AdvancedMarkerElement({
            position: { lat: warehouse.latitude, lng: warehouse.longitude },
            map: newMap,
            title: `${warehouse.name} (Capacity: ${warehouse.capacity})`,
            content: pin.element
          })

          const infoWindow = new google.maps.InfoWindow({
            content: `
              <div class="p-2">
                <h3 class="font-bold text-blue-600">${warehouse.name}</h3>
                <p>Capacity: ${warehouse.capacity}</p>
                <p>Location: ${warehouse.country}</p>
              </div>
            `
          })

          marker.addListener('click', () => {
            infoWindow.open({ map: newMap, anchor: marker })
          })
        })

        // Add customer markers (red) using AdvancedMarkerElement
        customers.forEach(customer => {
          const pin = new (google as any).maps.marker.PinElement({
            background: '#ef4444',
            borderColor: '#dc2626',
            glyphColor: '#ffffff'
          })
          const marker = new (google as any).maps.marker.AdvancedMarkerElement({
            position: { lat: customer.latitude, lng: customer.longitude },
            map: newMap,
            title: `${customer.name} (Demand: ${customer.demand})`,
            content: pin.element
          })

          const infoWindow = new google.maps.InfoWindow({
            content: `
              <div class="p-2">
                <h3 class="font-bold text-red-600">${customer.name}</h3>
                <p>Demand: ${customer.demand}</p>
                <p>Location: ${customer.country}</p>
              </div>
            `
          })

          marker.addListener('click', () => {
            infoWindow.open({ map: newMap, anchor: marker })
          })
        })

        // Add route lines
        routes.forEach(route => {
          const warehouse = warehouses.find(w => w.id === route.warehouseId)
          const customer = customers.find(c => c.id === route.customerId)
          
          if (warehouse && customer) {
            const routeLine = new google.maps.Polyline({
              path: [
                { lat: warehouse.latitude, lng: warehouse.longitude },
                { lat: customer.latitude, lng: customer.longitude }
              ],
              geodesic: true,
              strokeColor: '#10b981',
              strokeOpacity: 0.6,
              strokeWeight: 2,
            })
            
            routeLine.setMap(newMap)
          }
        })

        // Fit map to bounds
        if (warehouses.length > 0 || customers.length > 0) {
          newMap.fitBounds(bounds)
          
          // Add padding to the bounds
          const listener = google.maps.event.addListener(newMap, 'bounds_changed', () => {
            const zoom = newMap.getZoom()
            if (zoom && zoom > 10) {
              newMap.setZoom(10)
            }
            google.maps.event.removeListener(listener)
          })
        }
        
        setMap(newMap)
      } else {
        // No data - show default map
        const newMap = new google.maps.Map(node, {
          zoom: 4,
          center,
          mapTypeId: 'roadmap',
          ...(mapId ? { mapId } : {})
        })
        setMap(newMap)
      }
    }
  }, [warehouses, customers, routes, map])

  return <div ref={ref} className="w-full h-full rounded-lg" />
}

const MapLoadingComponent: React.FC = () => (
  <div className="w-full h-full bg-slate-700 rounded-lg flex items-center justify-center">
    <div className="text-center">
      <div className="spinner mb-2" />
      <span className="text-slate-300">Loading map...</span>
    </div>
  </div>
)

const MapErrorComponent: React.FC<{ status: Status }> = ({ status }) => (
  <div className="w-full h-full bg-red-900/20 border border-red-600 rounded-lg flex items-center justify-center">
    <div className="text-center">
      <div className="text-red-400 mb-2">⚠️</div>
      <span className="text-red-300">Failed to load map: {status}</span>
    </div>
  </div>
)

const MapVisualization: React.FC<Props> = ({ 
  warehouses = [], 
  customers = [], 
  routes = []
}) => {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

  if (!apiKey) {
    return (
      <div className="w-full h-full bg-yellow-900/20 border border-yellow-600 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="text-yellow-400 mb-2">⚠️</div>
          <span className="text-yellow-300">Google Maps API key not configured</span>
        </div>
      </div>
    )
  }

  const render = (status: Status): React.ReactElement => {
    if (status === Status.LOADING) return <MapLoadingComponent />
    if (status === Status.FAILURE) return <MapErrorComponent status={status} />
    return (
      <GoogleMap 
        warehouses={warehouses} 
        customers={customers} 
        routes={routes} 
      />
    )
  }

  return (
    <div className="w-full h-full">
  <Wrapper apiKey={apiKey} render={render} libraries={["marker"]} />
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 border border-slate-600">
        <h4 className="text-sm font-medium text-slate-200 mb-2">Legend</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span className="text-slate-300">Warehouses</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <span className="text-slate-300">Customers</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-0.5 bg-green-500 mr-2"></div>
            <span className="text-slate-300">Routes</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapVisualization
