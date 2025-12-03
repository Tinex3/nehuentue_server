import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import { Loading } from '../components/ui/Loading';
import { Badge } from '../components/ui/Badge';
import { zonesService } from '../services/zonesService';
import { devicesService } from '../services/devicesService';
import type { Zone } from '../types';
import toast from 'react-hot-toast';

export const Zones = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<Zone | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  const queryClient = useQueryClient();

  const { data: zones = [], isLoading } = useQuery({
    queryKey: ['zones'],
    queryFn: () => zonesService.getAll(),
  });

  const { data: devices = [] } = useQuery({
    queryKey: ['devices'],
    queryFn: () => devicesService.getAll(),
  });

  const createMutation = useMutation({
    mutationFn: zonesService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones'] });
      toast.success('Zona creada exitosamente');
      closeModal();
    },
    onError: () => {
      toast.error('Error al crear zona');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      zonesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones'] });
      toast.success('Zona actualizada exitosamente');
      closeModal();
    },
    onError: () => {
      toast.error('Error al actualizar zona');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: zonesService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones'] });
      toast.success('Zona eliminada exitosamente');
    },
    onError: () => {
      toast.error('Error al eliminar zona');
    },
  });

  const openCreateModal = () => {
    setEditingZone(null);
    setFormData({ name: '', description: '' });
    setIsModalOpen(true);
  };

  const openEditModal = (zone: Zone) => {
    setEditingZone(zone);
    setFormData({
      name: zone.name,
      description: zone.description || '',
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingZone(null);
    setFormData({ name: '', description: '' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingZone) {
      updateMutation.mutate({ id: editingZone.zone_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar esta zona?')) {
      deleteMutation.mutate(id);
    }
  };

  const getZoneDeviceCount = (zoneId: number) => {
    return devices?.filter((d) => d.zone_id === zoneId).length || 0;
  };

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Cargando zonas..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Gestión de Zonas</h2>
            <p className="text-gray-600 mt-1">
              Administra las zonas de tu sistema de seguridad
            </p>
          </div>
          <Button onClick={openCreateModal}>+ Nueva Zona</Button>
        </div>

        {/* Zones Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {zones.map((zone: Zone) => (
            <Card key={zone.zone_id} className="hover:shadow-lg transition-shadow">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800">
                      {zone.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">ID: {zone.zone_id}</p>
                  </div>
                  <Badge variant="info">{getZoneDeviceCount(zone.zone_id)} dispositivos</Badge>
                </div>

                {zone.description && (
                  <p className="text-gray-600">{zone.description}</p>
                )}

                <div className="flex gap-2 pt-4 border-t border-gray-200">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => openEditModal(zone)}
                    className="flex-1"
                  >
                    ✏️ Editar
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(zone.zone_id)}
                    className="flex-1"
                  >
                    🗑️ Eliminar
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {zones?.length === 0 && (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏠</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                No hay zonas creadas
              </h3>
              <p className="text-gray-600 mb-6">
                Comienza creando tu primera zona de seguridad
              </p>
              <Button onClick={openCreateModal}>+ Crear Primera Zona</Button>
            </div>
          </Card>
        )}
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingZone ? 'Editar Zona' : 'Nueva Zona'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nombre de la Zona"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Ej: Sala Principal"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Describe esta zona..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              {editingZone ? 'Actualizar' : 'Crear'}
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
