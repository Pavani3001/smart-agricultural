'use client';

import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Toast from '@/components/ui/Toast';
import CropForm from '@/components/forms/CropForm';
import { getCrops, createCrop, updateCrop } from '@/lib/api';

export default function CropsPage() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingCrop, setEditingCrop] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const loadCrops = async () => {
    setLoading(true);
    const { data, error } = await getCrops();
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setCrops(data || []);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCrops();
  }, []);

  const handleCreateOrUpdate = async (formData) => {
    setSubmitting(true);
    const payload = {
      ...formData,
      optimal_moisture_min: parseFloat(formData.optimal_moisture_min || 30.0),
      optimal_moisture_max: parseFloat(formData.optimal_moisture_max || 70.0),
      water_requirement_mm: formData.water_requirement_mm ? parseInt(formData.water_requirement_mm) : 500,
    };

    if (editingCrop) {
      const { error } = await updateCrop(editingCrop.id, payload);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'Crop configuration updated!', type: 'success' });
        setFormOpen(false);
        setEditingCrop(null);
        loadCrops();
      }
    } else {
      const { error } = await createCrop(payload);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'New crop configured successfully!', type: 'success' });
        setFormOpen(false);
        loadCrops();
      }
    }
    setSubmitting(false);
  };

  return (
    <div className="space-y-6">
      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Crop Configurations</h2>
          <p className="text-sm text-slate-500">
            Define optimal soil moisture bounds, water requirements (mm), and seasonal cycles.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setEditingCrop(null);
            setFormOpen(true);
          }}
        >
          ➕ Configure New Crop
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : crops.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-slate-500">
            <span className="text-4xl block mb-2">🌾</span>
            <p className="font-semibold text-slate-700">No crop profiles configured yet.</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {crops.map((crop) => (
            <Card key={crop.id} className="relative overflow-hidden flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🌱</span>
                    <h3 className="text-lg font-bold text-slate-800">{crop.crop_name}</h3>
                  </div>
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-primary-100 text-primary-800">
                    {crop.season || 'All Season'}
                  </span>
                </div>

                <p className="text-xs text-slate-500 mb-4 line-clamp-2">
                  {crop.description || 'Configured agricultural crop with standard irrigation limits.'}
                </p>

                <div className="space-y-1.5 mb-4">
                  <div className="flex justify-between text-xs font-semibold text-slate-600">
                    <span>Optimal Moisture</span>
                    <span className="text-primary-700 font-bold">
                      {crop.optimal_moisture_min}% – {crop.optimal_moisture_max}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full relative overflow-hidden">
                    <div
                      className="absolute top-0 bottom-0 bg-primary-500 rounded-full"
                      style={{
                        left: `${crop.optimal_moisture_min}%`,
                        width: `${crop.optimal_moisture_max - crop.optimal_moisture_min}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 pt-3 border-t border-slate-100">
                  <div>
                    <span className="text-slate-400 block">Water Need:</span>
                    <span className="font-semibold text-slate-800">{crop.water_requirement_mm} mm</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Growth Stage:</span>
                    <span className="font-semibold text-slate-800 capitalize">{crop.growth_stage || 'vegetative'}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex justify-end">
                <button
                  onClick={() => {
                    setEditingCrop(crop);
                    setFormOpen(true);
                  }}
                  className="text-xs px-3 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                >
                  Edit Configuration
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {formOpen && (
        <Modal
          isOpen={formOpen}
          onClose={() => setFormOpen(false)}
          title={editingCrop ? 'Edit Crop Configuration' : 'Configure New Crop'}
        >
          <CropForm
            initialData={editingCrop}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => setFormOpen(false)}
            loading={submitting}
          />
        </Modal>
      )}
    </div>
  );
}

