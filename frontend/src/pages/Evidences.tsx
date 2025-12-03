import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Loading } from '../components/ui/Loading';
import { Modal } from '../components/ui/Modal';
import { AuthenticatedImage } from '../components/AuthenticatedImage';
import { evidencesService } from '../services/evidencesService';
import { Evidence } from '../types';

export const Evidences = () => {
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [filters, setFilters] = useState({
    event_id: '',
    limit: 20,
  });

  const { data: evidencesResponse, isLoading } = useQuery({
    queryKey: ['evidences', filters],
    queryFn: () => evidencesService.getAll({
      event_id: filters.event_id ? parseInt(filters.event_id) : undefined,
      limit: filters.limit,
    }),
  });

  // Extraer evidencias del response
  const evidences: Evidence[] = evidencesResponse?.evidences || [];

  const handleViewDetails = (evidence: Evidence) => {
    setSelectedEvidence(evidence);
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-ES');
  };

  if (isLoading) {
    return (
      <Layout>
        <Loading message="Cargando evidencias..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Evidencias de Seguridad</h2>
          <p className="text-gray-600 mt-1">
            Imágenes capturadas con análisis de inteligencia artificial
          </p>
        </div>

        {/* Filters */}
        <Card title="Filtros">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Evento ID
              </label>
              <input
                type="text"
                value={filters.event_id}
                onChange={(e) =>
                  setFilters({ ...filters, event_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Filtrar por ID de evento"
              />
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
                <option value="20">20 evidencias</option>
                <option value="50">50 evidencias</option>
                <option value="100">100 evidencias</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Gallery */}
        <Card title={`Evidencias (${evidences.length})`}>
          {evidences.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📸</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                No hay evidencias
              </h3>
              <p className="text-gray-600">
                No se encontraron evidencias con los filtros seleccionados
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {evidences.map((evidence) => {
                const aiResult = evidence.ai_metadata;
                const hasAI = aiResult && aiResult.persons_detected !== undefined;

                return (
                  <div
                    key={evidence.evidence_id}
                    className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => handleViewDetails(evidence)}
                  >
                    {/* Image */}
                    <div className="relative aspect-video bg-gray-100">
                      <AuthenticatedImage
                        src={evidencesService.getFileUrl(evidence.evidence_id)}
                        alt={`Evidencia ${evidence.evidence_id}`}
                        className="w-full h-full object-cover"
                      />
                      {hasAI && aiResult.persons_detected > 0 && (
                        <div className="absolute top-2 right-2">
                          <Badge variant="danger">
                            👤 {aiResult.persons_detected} persona(s)
                          </Badge>
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          ID: {evidence.evidence_id}
                        </span>
                        <Badge variant={evidence.ai_metadata ? 'success' : 'gray'}>
                          {evidence.ai_metadata ? 'Analizado' : 'Pendiente'}
                        </Badge>
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        Evento: #{evidence.event_id || 'N/A'}
                      </p>

                      <p className="text-xs text-gray-500">
                        {formatDate(evidence.created_at)}
                      </p>

                      {hasAI && aiResult.total_detections > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-600">
                            🤖 {aiResult.total_detections} objetos detectados
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Detail Modal */}
      {selectedEvidence && (
        <Modal
          isOpen={!!selectedEvidence}
          onClose={() => setSelectedEvidence(null)}
          title={`Evidencia #${selectedEvidence.evidence_id}`}
          size="xl"
        >
          <div className="space-y-4">
            {/* Image */}
            <div className="relative">
              <AuthenticatedImage
                src={evidencesService.getFileUrl(selectedEvidence.evidence_id)}
                alt={`Evidencia ${selectedEvidence.evidence_id}`}
                className="w-full rounded-lg"
              />
            </div>

            {/* Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Evento ID</p>
                <p className="text-lg font-semibold text-gray-800">
                  #{selectedEvidence.event_id || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Estado</p>
                <Badge variant={selectedEvidence.ai_metadata ? 'success' : 'gray'}>
                  {selectedEvidence.ai_metadata ? 'Analizado' : 'Pendiente'}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Archivo</p>
                <p className="text-sm text-gray-800 truncate">
                  {selectedEvidence.file_path}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Fecha</p>
                <p className="text-sm text-gray-800">
                  {formatDate(selectedEvidence.created_at)}
                </p>
              </div>
            </div>

            {/* AI Analysis */}
            {selectedEvidence.ai_metadata && (
              <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <h4 className="font-semibold text-gray-800 mb-3">
                  🤖 Análisis de IA
                </h4>
                <pre className="text-sm text-gray-700 overflow-x-auto">
                  {JSON.stringify(selectedEvidence.ai_metadata, null, 2)}
                </pre>
              </div>
            )}

            {/* Download Button */}
            <div className="flex justify-end">
              <button
                onClick={() => evidencesService.downloadFile(
                  selectedEvidence.evidence_id,
                  selectedEvidence.file_path?.split('/').pop()
                )}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                📥 Descargar Imagen
              </button>
            </div>
          </div>
        </Modal>
      )}
    </Layout>
  );
};
