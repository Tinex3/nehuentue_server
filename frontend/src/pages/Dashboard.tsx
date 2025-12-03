import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Loading } from '../components/ui/Loading';
import { zonesService } from '../services/zonesService';
import { eventsService } from '../services/eventsService';
import { devicesService } from '../services/devicesService';
import { Link } from 'react-router-dom';
import type { Zone, Device, Event } from '../types';

export const Dashboard = () => {
  const { data: zones = [], isLoading: zonesLoading } = useQuery({
    queryKey: ['zones'],
    queryFn: () => zonesService.getAll(),
  });

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['events', { limit: 10 }],
    queryFn: () => eventsService.getAll({ limit: 10 }),
  });

  const { data: devices = [], isLoading: devicesLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesService.getAll(),
  });

  const { data: statsData } = useQuery({
    queryKey: ['events', 'stats'],
    queryFn: () => eventsService.getStats(),
  });

  if (zonesLoading || eventsLoading || devicesLoading) {
    return (
      <Layout>
        <Loading message="Cargando dashboard..." />
      </Layout>
    );
  }

  const totalDevices = devices.length;
  const activeDevices = devices.filter((d: Device) => d.status).length;
  const totalZones = zones.length;
  const recentEvents: Event[] = eventsData?.events || [];
  const stats = statsData?.stats || {};

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'motion':
        return '🚶';
      case 'relay_on':
        return '💡';
      case 'relay_off':
        return '🌑';
      case 'capture':
        return '📸';
      default:
        return '⚡';
    }
  };

  const getEventColor = (type: string): 'warning' | 'success' | 'gray' | 'info' => {
    switch (type) {
      case 'motion':
        return 'warning';
      case 'relay_on':
        return 'success';
      case 'relay_off':
        return 'gray';
      case 'capture':
        return 'info';
      default:
        return 'gray';
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Zonas</p>
                <h3 className="text-3xl font-bold mt-2">{totalZones}</h3>
              </div>
              <div className="text-5xl opacity-50">🏠</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Dispositivos Activos</p>
                <h3 className="text-3xl font-bold mt-2">
                  {activeDevices} / {totalDevices}
                </h3>
              </div>
              <div className="text-5xl opacity-50">📱</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100 text-sm">Eventos Hoy</p>
                <h3 className="text-3xl font-bold mt-2">{stats['motion'] || 0}</h3>
              </div>
              <div className="text-5xl opacity-50">⚡</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Eventos Totales</p>
                <h3 className="text-3xl font-bold mt-2">{eventsData?.total || 0}</h3>
              </div>
              <div className="text-5xl opacity-50">📊</div>
            </div>
          </Card>
        </div>

        {/* Recent Events */}
        <Card title="Eventos Recientes">
          <div className="space-y-3">
            {recentEvents.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay eventos recientes</p>
            ) : (
              recentEvents.map((event: Event) => (
                <div
                  key={event.event_id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="text-3xl">{getEventIcon(event.event_type)}</div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-800">
                          {event.device_name || `Dispositivo #${event.device_id}`}
                        </p>
                        <Badge variant={getEventColor(event.event_type)}>
                          {event.event_type}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">
                        {new Date(event.created_at).toLocaleString('es-CL')}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="mt-4 text-center">
            <Link
              to="/events"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Ver todos los eventos →
            </Link>
          </div>
        </Card>

        {/* Zones Status */}
        <Card title="Estado de Zonas">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {zones.map((zone: Zone) => {
              const zoneDevices = devices.filter((d: Device) => d.zone_id === zone.zone_id);
              const activeInZone = zoneDevices.filter((d: Device) => d.status).length;

              return (
                <div
                  key={zone.zone_id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-800">{zone.name}</h4>
                    <Badge variant={activeInZone > 0 ? 'success' : 'gray'}>
                      {activeInZone} activos
                    </Badge>
                  </div>
                  {zone.description && (
                    <p className="text-sm text-gray-600 mb-3">{zone.description}</p>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">
                      {zoneDevices.length} dispositivos
                    </span>
                    <Link
                      to="/zones"
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Ver detalles →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </Layout>
  );
};
