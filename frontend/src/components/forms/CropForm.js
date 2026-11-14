'use client';

import { useState, useEffect } from 'react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import { GROWTH_STAGES, SEASONS } from '@/lib/constants';

const emptyForm = {
  crop_name: '',
  optimal_moisture_min: '',
  optimal_moisture_max: '',
  growth_stage: '',
  water_requirement_mm: '',
  season: '',
  description: '',
};

export default function CropForm({ initialData, onSubmit, onCancel, loading = false }) {
  const [form, setForm] = useState(emptyForm);
  const [errors, setErrors] = useState({});
  const isEdit = !!initialData;

  useEffect(() => {
    if (initialData) {
      setForm({
        crop_name: initialData.crop_name || '',
        optimal_moisture_min: initialData.optimal_moisture_min?.toString() || '',
        optimal_moisture_max: initialData.optimal_moisture_max?.toString() || '',
        growth_stage: initialData.growth_stage || '',
        water_requirement_mm: initialData.water_requirement_mm?.toString() || '',
        season: initialData.season || '',
        description: initialData.description || '',
      });
    } else {
      setForm(emptyForm);
    }
    setErrors({});
  }, [initialData]);

  const validate = () => {
    const errs = {};
    if (!form.crop_name.trim()) errs.crop_name = 'Crop name is required';
    if (form.optimal_moisture_min && (isNaN(form.optimal_moisture_min) || form.optimal_moisture_min < 0 || form.optimal_moisture_min > 100)) {
      errs.optimal_moisture_min = 'Must be 0-100';
    }
    if (form.optimal_moisture_max && (isNaN(form.optimal_moisture_max) || form.optimal_moisture_max < 0 || form.optimal_moisture_max > 100)) {
      errs.optimal_moisture_max = 'Must be 0-100';
    }
    if (form.optimal_moisture_min && form.optimal_moisture_max &&
        parseFloat(form.optimal_moisture_min) > parseFloat(form.optimal_moisture_max)) {
      errs.optimal_moisture_max = 'Max must be greater than min';
    }
    if (form.water_requirement_mm && (isNaN(form.water_requirement_mm) || form.water_requirement_mm < 0)) {
      errs.water_requirement_mm = 'Must be a positive number';
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
        optimal_moisture_min: form.optimal_moisture_min ? parseFloat(form.optimal_moisture_min) : null,
        optimal_moisture_max: form.optimal_moisture_max ? parseFloat(form.optimal_moisture_max) : null,
        water_requirement_mm: form.water_requirement_mm ? parseFloat(form.water_requirement_mm) : null,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Crop Name"
          name="crop_name"
          value={form.crop_name}
          onChange={handleChange}
          placeholder="e.g. Rice (Basmati)"
          error={errors.crop_name}
          required
        />
        <Select
          label="Growth Stage"
          name="growth_stage"
          value={form.growth_stage}
          onChange={handleChange}
          options={GROWTH_STAGES}
          placeholder="Select stage..."
        />
        <Input
          label="Optimal Moisture Min (%)"
          name="optimal_moisture_min"
          type="number"
          step="0.1"
          value={form.optimal_moisture_min}
          onChange={handleChange}
          placeholder="e.g. 40"
          error={errors.optimal_moisture_min}
        />
        <Input
          label="Optimal Moisture Max (%)"
          name="optimal_moisture_max"
          type="number"
          step="0.1"
          value={form.optimal_moisture_max}
          onChange={handleChange}
          placeholder="e.g. 70"
          error={errors.optimal_moisture_max}
        />
        <Input
          label="Water Requirement (mm/day)"
          name="water_requirement_mm"
          type="number"
          step="0.1"
          value={form.water_requirement_mm}
          onChange={handleChange}
          placeholder="e.g. 5.5"
          error={errors.water_requirement_mm}
        />
        <Select
          label="Season"
          name="season"
          value={form.season}
          onChange={handleChange}
          options={SEASONS}
          placeholder="Select season..."
        />
      </div>
      <Input
        label="Description"
        name="description"
        value={form.description}
        onChange={handleChange}
        placeholder="Brief description of the crop variety..."
      />
      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" loading={loading}>
          {isEdit ? '💾 Update Crop' : '➕ Add Crop'}
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
