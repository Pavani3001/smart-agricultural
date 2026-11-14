'use client';

import { useState, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import { CROP_TYPES, SOIL_TYPES } from '@/lib/constants';

const emptyForm = {
  field_name: '',
  farmer_id: '',
  latitude: '',
  longitude: '',
  area_hectares: '',
  crop_type: '',
  soil_type: '',
};

export default function FieldForm({ initialData, farmers = [], onSubmit, onCancel, loading = false }) {
  const [form, setForm] = useState(emptyForm);
  const [errors, setErrors] = useState({});
  const isEdit = !!initialData;

  useEffect(() => {
    if (initialData) {
      setForm({
        field_name: initialData.field_name || '',
        farmer_id: initialData.farmer_id?.toString() || '',
        latitude: initialData.latitude?.toString() || '',
        longitude: initialData.longitude?.toString() || '',
        area_hectares: initialData.area_hectares?.toString() || '',
        crop_type: initialData.crop_type || '',
        soil_type: initialData.soil_type || '',
      });
    } else {
      setForm(emptyForm);
    }
    setErrors({});
  }, [initialData]);

  const validate = () => {
    const errs = {};
    if (!form.field_name.trim()) errs.field_name = 'Field name is required';
    if (!form.farmer_id) errs.farmer_id = 'Select a farmer';
    if (!form.latitude) {
      errs.latitude = 'Latitude is required';
    } else if (isNaN(form.latitude) || form.latitude < -90 || form.latitude > 90) {
      errs.latitude = 'Latitude must be between -90 and 90';
    }
    if (!form.longitude) {
      errs.longitude = 'Longitude is required';
    } else if (isNaN(form.longitude) || form.longitude < -180 || form.longitude > 180) {
      errs.longitude = 'Longitude must be between -180 and 180';
    }
    if (form.area_hectares && (isNaN(form.area_hectares) || parseFloat(form.area_hectares) <= 0)) {
      errs.area_hectares = 'Area must be a positive number';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        ...form,
        farmer_id: parseInt(form.farmer_id),
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        area_hectares: form.area_hectares ? parseFloat(form.area_hectares) : null,
      });
    }
  };

  const farmerOptions = farmers.map((f) => ({
    value: f.id.toString(),
    label: f.name,
  }));

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Field Name"
          name="field_name"
          value={form.field_name}
          onChange={handleChange}
          placeholder="e.g. North Paddy Field"
          error={errors.field_name}
          required
        />
        <Select
          label="Farmer"
          name="farmer_id"
          value={form.farmer_id}
          onChange={handleChange}
          options={farmerOptions}
          placeholder="Select farmer..."
          error={errors.farmer_id}
          required
        />
        <Input
          label="Latitude"
          name="latitude"
          type="number"
          step="any"
          value={form.latitude}
          onChange={handleChange}
          placeholder="e.g. 26.8467"
          error={errors.latitude}
          required
        />
        <Input
          label="Longitude"
          name="longitude"
          type="number"
          step="any"
          value={form.longitude}
          onChange={handleChange}
          placeholder="e.g. 80.9462"
          error={errors.longitude}
          required
        />
        <Input
          label="Area (Hectares)"
          name="area_hectares"
          type="number"
          step="0.01"
          value={form.area_hectares}
          onChange={handleChange}
          placeholder="e.g. 2.5"
          error={errors.area_hectares}
        />
        <Select
          label="Crop Type"
          name="crop_type"
          value={form.crop_type}
          onChange={handleChange}
          options={CROP_TYPES}
          placeholder="Select crop..."
        />
        <Select
          label="Soil Type"
          name="soil_type"
          value={form.soil_type}
          onChange={handleChange}
          options={SOIL_TYPES}
          placeholder="Select soil type..."
        />
      </div>
      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" loading={loading}>
          {isEdit ? '💾 Update Field' : '➕ Add Field'}
        </Button>
        {onCancel && (
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
