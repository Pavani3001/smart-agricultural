'use client';

import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Toast from '@/components/ui/Toast';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { getFields, getWeather, fetchWeather } from '@/lib/api';
import { WEATHER_EMOJIS } from '@/lib/constants';

export default function WeatherPage() {
  const [fields, setFields] = useState([]);
  const [selectedField, setSelectedField] = useState(null);
  const [weatherHistory, setWeatherHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const loadFields = async () => {
    setLoading(true);
    const { data } = await getFields();
    const fieldList = data || [];
    setFields(fieldList);
    if (fieldList.length > 0 && !selectedField) {
      selectField(fieldList[0]);
    }
    setLoading(false);
  };

  const selectField = async (field) => {
    setSelectedField(field);
    const { data } = await getWeather(field.id, { limit: 30 });
    setWeatherHistory(data || []);
  };

  useEffect(() => {
    loadFields();
  }, []);

  const handleFetchWeather = async (fieldId) => {
    setFetching(true);
    const { data, error } = await fetchWeather(fieldId);
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      const msg = data?.is_stale
        ? 'OpenWeatherMap API unavailable; returning cached data.'
        : 'Live weather observation fetched from OpenWeatherMap!';
      setToast({ show: true, message: msg, type: data?.is_stale ? 'warning' : 'success' });
      if (selectedField?.id === fieldId) {
        selectField(selectedField);
      }
    }
    setFetching(false);
  };

  const latestObservation = weatherHistory[0] || null;
  const emoji = latestObservation
    ? WEATHER_EMOJIS[latestObservation.weather_condition] || WEATHER_EMOJIS.default
    : '🌤️';

  const chartData = weatherHistory.map((w) => ({
    time: new Date(w.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    temp: Math.round(w.temperature_celsius || 0),
    humidity: Math.round(w.humidity_percent || 0),
    rainfall: w.rainfall_mm || 0,
  })).reverse();

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
          <h2 className="text-2xl font-bold text-slate-800">Weather API Integration</h2>
          <p className="text-sm text-slate-500">
            Real-time observations from OpenWeatherMap with auto-retry and cache fallback.
          </p>
        </div>
        {selectedField && (
          <Button
            variant="primary"
            onClick={() => handleFetchWeather(selectedField.id)}
            loading={fetching}
          >
            🔄 Fetch Live Weather
          </Button>
        )}
      </div>

      {/* Field Selector Pill Tabs */}
      {fields.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {fields.map((f) => {
            const active = selectedField?.id === f.id;
            return (
              <button
                key={f.id}
                onClick={() => selectField(f)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  active
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                🗺️ {f.field_name} ({f.latitude?.toFixed(2)}, {f.longitude?.toFixed(2)})
              </button>
            );
          })}
        </div>
      )}

      {selectedField ? (
        <>
          {/* Current Observation Summary Card */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="flex items-center gap-4">
              <span className="text-4xl">{emoji}</span>
              <div>
                <p className="text-xs font-medium text-slate-400">Temperature</p>
                <p className="text-2xl font-bold text-slate-800">
                  {latestObservation?.temperature_celsius != null
                    ? `${latestObservation.temperature_celsius.toFixed(1)}°C`
                    : '—'}
                </p>
                <p className="text-xs text-slate-500 capitalize">
                  {latestObservation?.weather_condition || 'No Data'}
                </p>
              </div>
            </Card>

            <Card className="flex items-center gap-4">
              <span className="text-4xl">💧</span>
              <div>
                <p className="text-xs font-medium text-slate-400">Relative Humidity</p>
                <p className="text-2xl font-bold text-slate-800">
                  {latestObservation?.humidity_percent != null
                    ? `${latestObservation.humidity_percent}%`
                    : '—'}
                </p>
                <p className="text-xs text-slate-500">Atmospheric moisture</p>
              </div>
            </Card>

            <Card className="flex items-center gap-4">
              <span className="text-4xl">🌧️</span>
              <div>
                <p className="text-xs font-medium text-slate-400">Precipitation</p>
                <p className="text-2xl font-bold text-slate-800">
                  {latestObservation?.rainfall_mm != null
                    ? `${latestObservation.rainfall_mm} mm`
                    : '0.0 mm'}
                </p>
                <p className="text-xs text-slate-500">Last 1 hour</p>
              </div>
            </Card>

            <Card className="flex items-center gap-4">
              <span className="text-4xl">💨</span>
              <div>
                <p className="text-xs font-medium text-slate-400">Wind Speed</p>
                <p className="text-2xl font-bold text-slate-800">
                  {latestObservation?.wind_speed_ms != null
                    ? `${latestObservation.wind_speed_ms} m/s`
                    : '—'}
                </p>
                <p className="text-xs text-slate-500">Surface velocity</p>
              </div>
            </Card>
          </div>

          {/* Historical Trends Chart */}
          <Card>
            <h3 className="text-base font-bold text-slate-800 mb-4">
              📈 Weather History &amp; Trends for {selectedField.field_name}
            </h3>

            {chartData.length === 0 ? (
              <div className="h-64 flex flex-col items-center justify-center text-slate-400 border border-dashed rounded-lg">
                <p className="text-2xl mb-1">🌦️</p>
                <p className="text-sm">No historical weather observations recorded yet.</p>
                <p className="text-xs mt-1">Click &quot;Fetch Live Weather&quot; above to pull from OpenWeatherMap.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#64748b' }} label={{ value: '°C / mm', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#94a3b8' } }} />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} label={{ value: '% Humidity', angle: 90, position: 'insideRight', style: { fontSize: 10, fill: '#94a3b8' } }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line yAxisId="left" type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={2} name="Temp (°C)" />
                  <Line yAxisId="right" type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={2} name="Humidity (%)" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </>
      ) : (
        <Card>
          <div className="text-center py-12 text-slate-500">
            <span className="text-4xl block mb-2">🗺️</span>
            <p className="font-semibold text-slate-700">No fields registered yet.</p>
            <p className="text-xs text-slate-400 mt-1">Register a field to monitor location-based OpenWeatherMap feeds.</p>
          </div>
        </Card>
      )}
    </div>
  );
}

