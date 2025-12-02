import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Warehouse {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  capacity: number;
  country?: string;
}

interface Customer {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  demand: number;
  country?: string;
}

interface Assignment {
  customerId: string;
  warehouseId: string;
  cost: number;
  co2: number;
  distanceKm: number;
}

interface RoutesMapProps {
  warehouses: Warehouse[];
  customers: Customer[];
  assignments?: Assignment[];
  showAnimation?: boolean;
  highlightRoute?: string;
}

const RoutesMap: React.FC<RoutesMapProps> = ({
  warehouses,
  customers,
  assignments = [],
  showAnimation = false,
  highlightRoute,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;
    if (!mapboxToken) {
      console.warn('Mapbox token not configured');
      return;
    }

    mapboxgl.accessToken = mapboxToken;

    const bounds = new mapboxgl.LngLatBounds();
    [...warehouses, ...customers].forEach(point => {
      bounds.extend([point.longitude, point.latitude]);
    });

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      bounds: bounds.isEmpty() ? undefined : bounds,
      fitBoundsOptions: { padding: 50 },
    });

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Add warehouse markers
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    warehouses.forEach(warehouse => {
      const el = document.createElement('div');
      el.className = 'warehouse-marker';
      el.style.cssText = `
        width: 24px;
        height: 24px;
        background-color: #3b82f6;
        border: 2px solid #1e40af;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      `;

      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="color: #000; padding: 8px;">
          <strong style="color: #3b82f6;">${warehouse.name}</strong><br/>
          <span>Capacity: ${warehouse.capacity}</span><br/>
          <span>${warehouse.country || ''}</span>
        </div>
      `);

      new mapboxgl.Marker(el)
        .setLngLat([warehouse.longitude, warehouse.latitude])
        .setPopup(popup)
        .addTo(map.current!);
    });
  }, [warehouses, mapLoaded]);

  // Add customer markers
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    customers.forEach(customer => {
      const el = document.createElement('div');
      el.className = 'customer-marker';
      el.style.cssText = `
        width: 16px;
        height: 16px;
        background-color: #ef4444;
        border: 2px solid #dc2626;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      `;

      const popup = new mapboxgl.Popup({ offset: 15 }).setHTML(`
        <div style="color: #000; padding: 8px;">
          <strong style="color: #ef4444;">${customer.name}</strong><br/>
          <span>Demand: ${customer.demand}</span><br/>
          <span>${customer.country || ''}</span>
        </div>
      `);

      new mapboxgl.Marker(el)
        .setLngLat([customer.longitude, customer.latitude])
        .setPopup(popup)
        .addTo(map.current!);
    });
  }, [customers, mapLoaded]);

  // Add route lines
  useEffect(() => {
    if (!map.current || !mapLoaded || assignments.length === 0) return;

    const routeFeatures = assignments.map((assignment, index) => {
      const warehouse = warehouses.find(w => w.id === assignment.warehouseId);
      const customer = customers.find(c => c.id === assignment.customerId);

      if (!warehouse || !customer) return null;

      return {
        type: 'Feature' as const,
        properties: {
          id: `route-${index}`,
          cost: assignment.cost,
          co2: assignment.co2,
          distance: assignment.distanceKm,
          warehouseName: warehouse.name,
          customerName: customer.name,
          highlight: highlightRoute === `route-${index}`,
        },
        geometry: {
          type: 'LineString' as const,
          coordinates: [
            [warehouse.longitude, warehouse.latitude],
            [customer.longitude, customer.latitude],
          ],
        },
      };
    }).filter(Boolean);

    const source = map.current.getSource('routes');
    if (source) {
      (source as mapboxgl.GeoJSONSource).setData({
        type: 'FeatureCollection',
        features: routeFeatures as any[],
      });
    } else {
      map.current.addSource('routes', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: routeFeatures as any[],
        },
      });

      map.current.addLayer({
        id: 'routes-layer',
        type: 'line',
        source: 'routes',
        paint: {
          'line-color': [
            'case',
            ['get', 'highlight'],
            '#fbbf24',
            '#10b981'
          ],
          'line-width': [
            'case',
            ['get', 'highlight'],
            4,
            2
          ],
          'line-opacity': 0.7,
        },
      });

      // Add animation if enabled
      if (showAnimation) {
        let animationCounter = 0;
        const animate = () => {
          animationCounter = (animationCounter + 1) % 100;
          if (map.current?.getLayer('routes-layer')) {
            map.current.setPaintProperty(
              'routes-layer',
              'line-dasharray',
              [animationCounter / 20, (100 - animationCounter) / 20]
            );
          }
          requestAnimationFrame(animate);
        };
        animate();
      }

      // Add click handler
      map.current.on('click', 'routes-layer', (e) => {
        if (!e.features || e.features.length === 0) return;
        
        const feature = e.features[0];
        const props = feature.properties;

        new mapboxgl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="color: #000; padding: 8px;">
              <strong style="color: #10b981;">Route</strong><br/>
              <span>${props?.warehouseName} → ${props?.customerName}</span><br/>
              <span>Distance: ${props?.distance?.toFixed(1)} km</span><br/>
              <span>Cost: $${props?.cost?.toFixed(2)}</span><br/>
              <span>CO₂: ${props?.co2?.toFixed(2)} kg</span>
            </div>
          `)
          .addTo(map.current!);
      });

      map.current.on('mouseenter', 'routes-layer', () => {
        map.current!.getCanvas().style.cursor = 'pointer';
      });

      map.current.on('mouseleave', 'routes-layer', () => {
        map.current!.getCanvas().style.cursor = '';
      });
    }
  }, [assignments, mapLoaded, warehouses, customers, highlightRoute, showAnimation]);

  if (!import.meta.env.VITE_MAPBOX_TOKEN) {
    return (
      <div className="w-full h-full bg-slate-800 rounded-lg flex items-center justify-center border border-slate-700">
        <div className="text-center p-8">
          <div className="text-yellow-500 mb-3 text-4xl">⚠️</div>
          <p className="text-slate-300 mb-2">Mapbox token not configured</p>
          <p className="text-slate-500 text-sm">
            Set VITE_MAPBOX_TOKEN in your environment
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full rounded-lg" />
      
      {assignments.length > 0 && (
        <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
          <div className="text-sm text-slate-300 space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span>Warehouses ({warehouses.length})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500"></div>
              <span>Customers ({customers.length})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 bg-green-500"></div>
              <span>Routes ({assignments.length})</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoutesMap;
