import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Loading } from '../components/ui/Loading';
import { Badge } from '../components/ui/Badge';
import { Table } from '../components/ui/Table';
import { devicesService } from '../services/devicesService';
import { zonesService } from '../services/zonesService';
import { Device } from '../types';
import toast from 'react-hot-toast';

export const Devices = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [formData, setFormData] = useState({
    zone_id: '',
    device_type_id: '',
    name: '',
    description: '',
    params: {} as Record<string, unknown>,
  });

  const queryClient = useQueryClient();

  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesService.getAll(),
  });

  const { data: zones } = useQuery({
    queryKey: ['zones'],
    queryFn: () => zonesService.getAll(),
  });

  const { data: deviceTypes } = useQuery({
    queryKey: ['deviceTypes'],
    queryFn: () => devicesService.getTypes(),
  });

  const createMutation = useMutation({
    mutationFn: devicesService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      toast.success('Dispositivo creado exitosamente');
      closeModal();
    },
    onError: () => {
      toast.error('Error al crear dispositivo');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      devicesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      toast.success('Dispositivo actualizado exitosamente');
      closeModal();
    },
    onError: () => {
      toast.error('Error al actualizar dispositivo');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: devicesService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      toast.success('Dispositivo eliminado exitosamente');
    },
    onError: () => {
      toast.error('Error al eliminar dispositivo');
    },
  });

  const commandMutation = useMutation({
    mutationFn: ({ id, command, payload }: any) =>
      devicesService.sendCommand(id, command, payload),
    onSuccess: () => {
      toast.success('Comando enviado exitosamente');
    },
    onError: () => {
      toast.error('Error al enviar comando');
    },
  });

  const openCreateModal = () => {
    setEditingDevice(null);
    setFormData({
      zone_id: '',
      device_type_id: '',
      name: '',
      description: '',
      params: {},
    });
    setIsModalOpen(true);
  };

  const openEditModal = (device: Device) => {
    setEditingDevice(device);
    setFormData({
      zone_id: device.zone_id?.toString() || '',
      device_type_id: device.device_type_id.toString(),
      name: device.name,
      description: device.description || '',
      params: device.params || {},
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingDevice(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name: formData.name,
      description: formData.description || undefined,
      zone_id: formData.zone_id ? parseInt(formData.zone_id) : undefined,
      device_type_id: parseInt(formData.device_type_id),
      params: formData.params,
    };

    if (editingDevice) {
      updateMutation.mutate({ id: editingDevice.device_id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar este dispositivo?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleCommand = (deviceId: number, command: string) => {
    const payload = command === 'on' || command === 'off' ? { state: command } : {};
    commandMutation.mutate({ id: deviceId, command, payload });
  };

  const getStatusBadge = (status: boolean) => {
    return status ? (
      <Badge variant="success">Activo</Badge>
    ) : (
      <Badge variant="gray">Inactivo</Badge>
    );
  };

  const getZoneName = (zoneId: number | null) => {
    if (!zoneId) return 'Sin zona';
    return zones?.find((z) => z.zone_id === zoneId)?.name || `Zona ${zoneId}`;
  };

  const getDeviceTypeName = (typeId: number) => {
    return deviceTypes?.find((t) => t.device_type_id === typeId)?.type_name || `Tipo ${typeId}`;
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'device_id' as keyof Device,
    },
    {
      header: 'Nombre',
      accessor: 'name' as keyof Device,
    },
    {
      header: 'Zona',
      accessor: (row: Device) => getZoneName(row.zone_id),
    },
    {
      header: 'Tipo',
      accessor: (row: Device) => getDeviceTypeName(row.device_type_id),
    },
    {
      header: 'Estado',
      accessor: (row: Device) => getStatusBadge(row.status),
    },
    {
      header: 'Acciones',
      accessor: (row: Device) => (
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={() => openEditModal(row)}>
            ✏️
          </Button>
          <Button size="sm" variant="success" onClick={() => handleCommand(row.device_id, 'on')}>
            ON
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleCommand(row.device_id, 'off')}>
            OFF
          </Button>
          <Button size="sm" variant="danger" onClick={() => handleDelete(row.device_id)}>
            🗑️
          </Button>
        </div>
      ),
    },
  ];

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Cargando dispositivos..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              Gestión de Dispositivos
            </h2>
            <p className="text-gray-600 mt-1">
              Controla y administra tus dispositivos IoT
            </p>
          </div>
          <Button onClick={openCreateModal}>+ Nuevo Dispositivo</Button>
        </div>

        {/* Devices Table */}
        <Card>
          <Table data={devices || []} columns={columns} />
        </Card>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingDevice ? 'Editar Dispositivo' : 'Nuevo Dispositivo'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Zona
            </label>
            <select
              value={formData.zone_id}
              onChange={(e) => setFormData({ ...formData, zone_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Selecciona una zona</option>
              {zones?.map((zone) => (
                <option key={zone.zone_id} value={zone.zone_id}>
                  {zone.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Dispositivo
            </label>
            <select
              value={formData.device_type_id}
              onChange={(e) =>
                setFormData({ ...formData, device_type_id: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Selecciona un tipo</option>
              {deviceTypes?.map((type) => (
                <option key={type.device_type_id} value={type.device_type_id}>
                  {type.type_name}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Nombre del Dispositivo"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Ej: Sensor de Movimiento Principal"
            required
          />

          <Input
            label="Descripción"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Descripción del dispositivo"
          />

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              {editingDevice ? 'Actualizar' : 'Crear'}
            </Button>
            <Button type="button" variant="ghost" onClick={closeModal}>
              Cancelar
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
};
