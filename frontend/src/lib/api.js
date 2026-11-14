const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic API fetch wrapper with error handling.
 * Returns { data, error } pattern.
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutId = controller ? setTimeout(() => controller.abort(), 6000) : null;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    signal: controller ? controller.signal : undefined,
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (timeoutId) clearTimeout(timeoutId);

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      const message = errorBody?.detail || errorBody?.message || `Request failed with status ${response.status}`;
      return { data: null, error: message };
    }

    const data = await response.json();
    return { data, error: null };
  } catch (err) {
    if (timeoutId) clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      return { data: null, error: 'Connection timed out. Backend is taking too long to respond.' };
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      return { data: null, error: 'Unable to connect to server. Please check if the backend is running on http://127.0.0.1:8000.' };
    }
    return { data: null, error: err.message || 'An unexpected error occurred.' };
  }
}

// ─── Farmers ──────────────────────────────────────────────

export async function getFarmers() {
  return fetchAPI('/farmers/');
}

export async function getFarmer(id) {
  return fetchAPI(`/farmers/${id}`);
}

export async function createFarmer(data) {
  return fetchAPI('/farmers/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateFarmer(id, data) {
  return fetchAPI(`/farmers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteFarmer(id) {
  return fetchAPI(`/farmers/${id}`, { method: 'DELETE' });
}

// ─── Fields ───────────────────────────────────────────────

export async function getFields(farmerId) {
  const query = farmerId ? `?farmer_id=${farmerId}` : '';
  return fetchAPI(`/fields/${query}`);
}

export async function getField(id) {
  return fetchAPI(`/fields/${id}`);
}

export async function createField(data) {
  return fetchAPI('/fields/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateField(id, data) {
  return fetchAPI(`/fields/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteField(id) {
  return fetchAPI(`/fields/${id}`, { method: 'DELETE' });
}

// ─── Crops ────────────────────────────────────────────────

export async function getCrops() {
  return fetchAPI('/crops/');
}

export async function getCrop(id) {
  return fetchAPI(`/crops/${id}`);
}

export async function createCrop(data) {
  return fetchAPI('/crops/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCrop(id, data) {
  return fetchAPI(`/crops/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ─── Sensors ──────────────────────────────────────────────

export async function getSensors(fieldId) {
  const query = fieldId ? `?field_id=${fieldId}` : '';
  return fetchAPI(`/sensors/${query}`);
}

export async function getSensor(sensorId) {
  return fetchAPI(`/sensors/${sensorId}`);
}

export async function createSensor(data) {
  return fetchAPI('/sensors/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateSensor(sensorId, data) {
  return fetchAPI(`/sensors/${sensorId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteSensor(sensorId) {
  return fetchAPI(`/sensors/${sensorId}`, { method: 'DELETE' });
}

// ─── Sensor Readings ──────────────────────────────────────

export async function getSensorReadings(sensorId, params = {}) {
  const query = new URLSearchParams();
  if (params.start_time) query.set('start_time', params.start_time);
  if (params.end_time) query.set('end_time', params.end_time);
  if (params.limit) query.set('limit', params.limit);
  const qs = query.toString() ? `?${query.toString()}` : '';
  return fetchAPI(`/sensor-data/${sensorId}${qs}`);
}

export async function getFieldReadings(fieldId, params = {}) {
  const query = new URLSearchParams();
  if (params.start_time) query.set('start_time', params.start_time);
  if (params.end_time) query.set('end_time', params.end_time);
  const qs = query.toString() ? `?${query.toString()}` : '';
  return fetchAPI(`/sensor-data/field/${fieldId}${qs}`);
}

export async function ingestReading(data) {
  return fetchAPI('/sensor-data/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function ingestBatchReadings(data) {
  return fetchAPI('/sensor-data/batch', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function simulateSensor(sensorId) {
  return fetchAPI(`/sensor-data/simulate/${sensorId}`, { method: 'POST' });
}

// ─── Weather ──────────────────────────────────────────────

export async function getWeather(fieldId, params = {}) {
  const query = new URLSearchParams();
  if (params.start_time) query.set('start_time', params.start_time);
  if (params.end_time) query.set('end_time', params.end_time);
  const qs = query.toString() ? `?${query.toString()}` : '';
  return fetchAPI(`/weather/${fieldId}${qs}`);
}

export async function fetchWeather(fieldId) {
  return fetchAPI(`/weather/fetch/${fieldId}`, { method: 'POST' });
}
