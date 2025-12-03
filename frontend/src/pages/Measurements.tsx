import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Loading } from '../components/ui/Loading';
import { measurementsService } from '../services/measurementsService';
import { devicesService } from '../services/devicesService';
import { Measurement } from '../types';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const Measurements = () => {
  const [selectedDevice, setSelectedDevice] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState('24');

  const { data: devices } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesService.getAll(),
  });

  const { data: measurementsResponse, isLoading } = useQuery({
    queryKey: ['measurements', selectedDevice, timeRange],
    queryFn: async () => {
      const result = await measurementsService.getAll({ 
        device_id: selectedDevice || undefined,
        hours: parseInt(timeRange),
        limit: 100 
      });
      return result;
    },
  });

  const { data: summaryData } = useQuery({
    queryKey: ['measurements', 'summary'],
    queryFn: () => measurementsService.getSummary(),
  });

  // Extraer measurements del response
  const measurements: Measurement[] = measurementsResponse?.measurements || [];

  // Preparar datos para gráficos
  const chartData = measurements.map((m) => {
    const data = m.data as Record<string, number | string>;
    return {
      timestamp: new Date(m.created_at).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
      }),
      temperature: typeof data.temperature === 'number' ? data.temperature : 0,
      humidity: typeof data.humidity === 'number' ? data.humidity : 0,
      pressure: typeof data.pressure === 'number' ? data.pressure : 0,
      device_id: m.device_id,
    };
  });

  // Calcular promedios del summary
  const summaryStats = {
    avgTemperature: 0,
    avgHumidity: 0,
    totalMeasurements: 0,
  };
  
  if (summaryData?.summary) {
    const temps: number[] = [];
    const hums: number[] = [];
    summaryData.summary.forEach((s) => {
      summaryStats.totalMeasurements += s.measurement_count;
      if (s.latest_data) {
        const temp = s.latest_data.temperature;
        const hum = s.latest_data.humidity;
        if (typeof temp === 'number') temps.push(temp);
        if (typeof hum === 'number') hums.push(hum);
      }
    });
    if (temps.length > 0) summaryStats.avgTemperature = temps.reduce((a: number, b: number) => a + b, 0) / temps.length;
    if (hums.length > 0) summaryStats.avgHumidity = hums.reduce((a: number, b: number) => a + b, 0) / hums.length;
  }

  // Agrupar datos por dispositivo para estadísticas
  const deviceStats = (devices || []).map((device) => {
    const deviceMeasurements = measurements.filter((m) => m.device_id === device.device_id);
    const temps = deviceMeasurements
      .map((m) => (m.data as Record<string, number>).temperature)
      .filter((t): t is number => typeof t === 'number');
    const hums = deviceMeasurements
      .map((m) => (m.data as Record<string, number>).humidity)
      .filter((h): h is number => typeof h === 'number');

    return {
      device: device.name,
      avgTemp: temps.length > 0 ? (temps.reduce((a: number, b: number) => a + b, 0) / temps.length).toFixed(1) : '0',
      avgHum: hums.length > 0 ? (hums.reduce((a: number, b: number) => a + b, 0) / hums.length).toFixed(1) : '0',
      count: deviceMeasurements.length,
    };
  }).filter((stat) => stat.count > 0);

  const getDeviceName = (deviceId: number) => {
    return devices?.find((d) => d.device_id === deviceId)?.name || `Dispositivo #${deviceId}`;
  };

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Cargando telemetría..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            Telemetría y Mediciones
          </h2>
          <p className="text-gray-600 mt-1">
            Monitorea los datos de sensores en tiempo real
          </p>
        </div>

        {/* Filters */}
        <Card title="Filtros">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dispositivo
              </label>
              <select
                value={selectedDevice || ''}
                onChange={(e) =>
                  setSelectedDevice(e.target.value ? parseInt(e.target.value) : null)
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
                Rango de Tiempo
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1">Última hora</option>
                <option value="6">Últimas 6 horas</option>
                <option value="24">Últimas 24 horas</option>
                <option value="168">Última semana</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-red-500 to-orange-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm">Temperatura Promedio</p>
                <h3 className="text-3xl font-bold mt-2">
                  {summaryStats.avgTemperature.toFixed(1)}°C
                </h3>
              </div>
              <div className="text-5xl opacity-50">🌡️</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Humedad Promedio</p>
                <h3 className="text-3xl font-bold mt-2">
                  {summaryStats.avgHumidity.toFixed(1)}%
                </h3>
              </div>
              <div className="text-5xl opacity-50">💧</div>
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-pink-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Total Mediciones</p>
                <h3 className="text-3xl font-bold mt-2">
                  {summaryStats.totalMeasurements}
                </h3>
              </div>
              <div className="text-5xl opacity-50">📊</div>
            </div>
          </Card>
        </div>

        {/* Temperature Chart */}
        <Card title="Temperatura en el Tiempo">
          <div className="h-80">
            {chartData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                No hay datos de temperatura disponibles
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="temperature"
                    stroke="#ef4444"
                    name="Temperatura (°C)"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Humidity Chart */}
        <Card title="Humedad en el Tiempo">
          <div className="h-80">
            {chartData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                No hay datos de humedad disponibles
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="humidity"
                    stroke="#3b82f6"
                    name="Humedad (%)"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Device Comparison */}
        {deviceStats.length > 0 && (
          <Card title="Comparación por Dispositivo">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deviceStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="device" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="avgTemp" fill="#ef4444" name="Temp. Promedio (°C)" />
                  <Bar dataKey="avgHum" fill="#3b82f6" name="Hum. Promedio (%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        )}

        {/* Latest Measurements Table */}
        <Card title="Últimas Mediciones">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Dispositivo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Temperatura
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Humedad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Presión
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {measurements.slice(0, 10).map((measurement) => {
                  const data = measurement.data as Record<string, number | string>;
                  return (
                    <tr key={measurement.measurement_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getDeviceName(measurement.device_id)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {typeof data.temperature === 'number' ? `${data.temperature}°C` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {typeof data.humidity === 'number' ? `${data.humidity}%` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {typeof data.pressure === 'number' ? `${data.pressure} hPa` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(measurement.created_at).toLocaleString('es-ES')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {measurements.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No hay mediciones disponibles
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
};
