'use client';

import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Toast from '@/components/ui/Toast';
import FarmerForm from '@/components/forms/FarmerForm';
import { getFarmers, createFarmer, updateFarmer, deleteFarmer } from '@/lib/api';

export default function FarmersPage() {
  const [farmers, setFarmers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingFarmer, setEditingFarmer] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const fetchFarmerList = async () => {
    setLoading(true);
    const { data, error } = await getFarmers();
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setFarmers(data || []);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchFarmerList();
  }, []);

  const handleCreateOrUpdate = async (formData) => {
    setSubmitting(true);
    if (editingFarmer) {
      const { data, error } = await updateFarmer(editingFarmer.id, formData);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'Farmer updated successfully!', type: 'success' });
        setFormOpen(false);
        setEditingFarmer(null);
        fetchFarmerList();
      }
    } else {
      const { data, error } = await createFarmer(formData);
      if (error) {
        setToast({ show: true, message: error, type: 'error' });
      } else {
        setToast({ show: true, message: 'Farmer registered successfully!', type: 'success' });
        setFormOpen(false);
        fetchFarmerList();
      }
    }
    setSubmitting(false);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this farmer? All linked fields and sensors will be removed.')) return;
    const { error } = await deleteFarmer(id);
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setToast({ show: true, message: 'Farmer deleted successfully.', type: 'success' });
      fetchFarmerList();
    }
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
          <h2 className="text-2xl font-bold text-slate-800">Farmer Profiles</h2>
          <p className="text-sm text-slate-500">Register and manage smallholder and commercial farmer profiles.</p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            setEditingFarmer(null);
            setFormOpen(true);
          }}
        >
          ➕ Register New Farmer
        </Button>
      </div>

      <Card>
        {loading ? (
          <div className="space-y-3 py-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : farmers.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <span className="text-4xl block mb-2">👨‍🌾</span>
            <p className="font-semibold text-slate-700">No farmers registered yet.</p>
            <p className="text-xs text-slate-400 mt-1">Click &quot;Register New Farmer&quot; to add your first farmer profile.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase text-slate-400 border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Phone</th>
                  <th className="py-3 px-4">Address / Village</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {farmers.map((farmer) => (
                  <tr key={farmer.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-800">{farmer.name}</td>
                    <td className="py-3 px-4">{farmer.email}</td>
                    <td className="py-3 px-4">{farmer.phone || '—'}</td>
                    <td className="py-3 px-4">{farmer.address || '—'}</td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => {
                          setEditingFarmer(farmer);
                          setFormOpen(true);
                        }}
                        className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(farmer.id)}
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
          title={editingFarmer ? 'Edit Farmer Profile' : 'Register New Farmer'}
        >
          <FarmerForm
            initialData={editingFarmer}
            onSubmit={handleCreateOrUpdate}
            onCancel={() => setFormOpen(false)}
            loading={submitting}
          />
        </Modal>
      )}
    </div>
  );
}

