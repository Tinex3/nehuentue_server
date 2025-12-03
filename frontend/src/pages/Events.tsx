import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Loading } from '../components/ui/Loading';
import { eventsService } from '../services/eventsService';
import { devicesService } from '../services/devicesService';
import { Event } from '../types';

export const Events = () => {
  const [filters, setFilters] = useState({
    device_id: '',
    event_type: '',
    limit: 50,
  });

  const { data: eventsResponse, isLoading } = useQuery({
    queryKey: ['events', filters],
    queryFn: () => eventsService.getAll({
      device_id: filters.device_id ? parseInt(filters.device_id) : undefined,
      event_type: filters.event_type || undefined,
      limit: filters.limit,
    }),
  });

  const { data: devices } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesService.getAll(),
  });

  // Extraer eventos del response
  const events: Event[] = eventsResponse?.events || [];

  const getEventIcon = (type: string) => {
    const icons: Record<string, string> = {
      motion: '🚶',
      relay_on: '💡',
      relay_off: '🌑',
      capture: '📸',
      telemetry: '📊',
    };
    return icons[type] || '⚡';
  };

  const getEventColor = (type: string): any => {
    const colors: Record<string, any> = {
      motion: 'warning',
      relay_on: 'success',
      relay_off: 'gray',
      capture: 'info',
      telemetry: 'info',
    };
    return colors[type] || 'gray';
  };

  const getDeviceName = (deviceId: number) => {
    return devices?.find((d) => d.device_id === deviceId)?.name || `Dispositivo #${deviceId}`;
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Ahora mismo';
    if (minutes < 60) return `Hace ${minutes} minutos`;
    if (hours < 24) return `Hace ${hours} horas`;
    if (days < 7) return `Hace ${days} días`;
    
    return date.toLocaleString('es-ES');
  };

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Cargando eventos..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Historial de Eventos</h2>
          <p className="text-gray-600 mt-1">
            Monitorea todos los eventos del sistema en tiempo real
          </p>
        </div>

        {/* Filters */}
        <Card title="Filtros">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dispositivo
              </label>
              <select
                value={filters.device_id}
                onChange={(e) =>
                  setFilters({ ...filters, device_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos los dispositivos</option>
                {devices?.map((device) => (
                  <option key={device.device_id} value={device.device_id}>
                    {device.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo de Evento
              </label>
              <select
                value={filters.event_type}
                onChange={(e) =>
                  setFilters({ ...filters, event_type: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos los tipos</option>
                <option value="motion">Movimiento</option>
                <option value="relay_on">Relay Encendido</option>
                <option value="relay_off">Relay Apagado</option>
                <option value="capture">Captura</option>
                <option value="telemetry">Telemetría</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Límite
              </label>
              <select
                value={filters.limit}
                onChange={(e) =>
                  setFilters({ ...filters, limit: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="20">20 eventos</option>
                <option value="50">50 eventos</option>
                <option value="100">100 eventos</option>
                <option value="200">200 eventos</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Timeline */}
        <Card title={`Eventos (${events.length})`}>
          <div className="space-y-4">
            {events.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📭</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  No hay eventos
                </h3>
                <p className="text-gray-600">
                  No se encontraron eventos con los filtros seleccionados
                </p>
              </div>
            ) : (
              <div className="relative">
                {/* Timeline Line */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />

                {/* Events */}
                {events.map((event) => (
                  <div key={event.event_id} className="relative flex gap-4 pb-6">
                    {/* Icon */}
                    <div className="relative z-10 flex-shrink-0">
                      <div className="w-16 h-16 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center text-2xl">
                        {getEventIcon(event.event_type)}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-gray-800">
                              {getDeviceName(event.device_id)}
                            </h4>
                            <Badge variant={getEventColor(event.event_type)}>
                              {event.event_type}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600">
                            {formatDate(event.created_at)}
                          </p>
                        </div>
                        <span className="text-sm text-gray-500">ID: {event.event_id}</span>
                      </div>

                      {event.payload && (
                        <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                          <p className="text-xs font-medium text-gray-500 mb-1">
                            Payload
                          </p>
                          <pre className="text-xs text-gray-700 overflow-x-auto">
                            {JSON.stringify(event.payload, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
};
