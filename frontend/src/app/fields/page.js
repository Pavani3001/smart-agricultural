'use client';

import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Toast from '@/components/ui/Toast';
import FieldForm from '@/components/forms/FieldForm';
import { getFields, getFarmers, createField, updateField, deleteField } from '@/lib/api';

export default function FieldsPage() {
  const [fields, setFields] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const loadData = async () => {
    setLoading(true);
    const [fieldsRes, farmersRes] = await Promise.all([getFields(), getFarmers()]);
    if (fieldsRes.error) {
      setToast({ show: true, message: fieldsRes.error, type: 'error' });
    } else {
      setFields(fieldsRes.data || []);
    }
    setFarmers(farmersRes.data || []);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOrUpdate = async (formData) => {
    setSubmitting(true);
    const payload = {
      ...formData,
      farmer_id: parseInt(formData.farmer_id),
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude),
      area_hectares: formData.area_hectares ? parseFloat(formData.area_hectares) : 1.0,
    };

    if (editingField) {
      const { error } = await updateField(editingField.id, payload);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'Field updated successfully!', type: 'success' });
        setFormOpen(false);
        setEditingField(null);
        loadData();
      }
    } else {
      const { error } = await createField(payload);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'Field registered successfully!', type: 'success' });
        setFormOpen(false);
        loadData();
      }
    }
    setSubmitting(false);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this field? Associated sensors and telemetry will be deleted.')) return;
    const { error } = await deleteField(id);
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setToast({ show: true, message: 'Field deleted successfully.', type: 'success' });
      loadData();
    }
  };

  const getFarmerName = (farmerId) => {
    const f = farmers.find((item) => item.id === farmerId);
    return f ? f.name : `Farmer #${farmerId}`;
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
          <h2 className="text-2xl font-bold text-slate-800">Agricultural Fields</h2>
          <p className="text-sm text-slate-500">Configure GPS boundaries, soil classifications, and crop associations.</p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setEditingField(null);
            setFormOpen(true);
          }}
        >
          ➕ Register New Field
        </Button>
      </div>

      <Card>
        {loading ? (
          <div className="space-y-3 py-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : fields.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <span className="text-4xl block mb-2">🗺️</span>
            <p className="font-semibold text-slate-700">No fields registered yet.</p>
            <p className="text-xs text-slate-400 mt-1">Register a farmer first, then add their agricultural field here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-400 border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Field Name</th>
                  <th className="py-3 px-4">Farmer</th>
                  <th className="py-3 px-4">GPS Location</th>
                  <th className="py-3 px-4">Area (ha)</th>
                  <th className="py-3 px-4">Crop Type</th>
                  <th className="py-3 px-4">Soil Type</th>
                  <th className="py-3 px-4">Sensors</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {fields.map((field) => (
                  <tr key={field.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-800">{field.field_name}</td>
                    <td className="py-3 px-4 text-slate-600">{getFarmerName(field.farmer_id)}</td>
                    <td className="py-3 px-4 font-mono text-xs text-slate-500">
                      {field.latitude?.toFixed(4)}, {field.longitude?.toFixed(4)}
                    </td>
                    <td className="py-3 px-4">{field.area_hectares} ha</td>
                    <td className="py-3 px-4 font-medium text-primary-700">{field.crop_type || '—'}</td>
                    <td className="py-3 px-4 capitalize">{field.soil_type || 'loamy'}</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {field.sensors?.length || 0} nodes
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        {field.status || 'active'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => {
                          setEditingField(field);
                          setFormOpen(true);
                        }}
                        className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(field.id)}
                        className="text-xs px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-600 font-medium"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {formOpen && (
        <Modal
          isOpen={formOpen}
          onClose={() => setFormOpen(false)}
          title={editingField ? 'Edit Field Configuration' : 'Register Agricultural Field'}
        >
          <FieldForm
            initialData={editingField}
            farmers={farmers}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => setFormOpen(false)}
            loading={submitting}
          />
        </Modal>
      )}
    </div>
  );
}

