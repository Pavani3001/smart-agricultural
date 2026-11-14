'use client';

import { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Toast from '@/components/ui/Toast';
import Select from '@/components/ui/Select';
import Input from '@/components/ui/Input';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { getSensors, getFields, createSensor, getSensorReadings, simulateSensor } from '@/lib/api';
import { SENSOR_STATUS_COLORS } from '@/lib/constants';

export default function SensorsPage() {
  const [sensors, setSensors] = useState([]);
  const [fields, setFields] = useState([]);
  const [selectedSensor, setSelectedSensor] = useState(null);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [newSensor, setNewSensor] = useState({ sensor_id: '', field_id: '', sensor_type: 'soil_moisture' });
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const loadData = async () => {
    setLoading(true);
    const [sensorsRes, fieldsRes] = await Promise.all([getSensors(), getFields()]);
    const sensorList = sensorsRes.data || [];
    setSensors(sensorList);
    setFields(fieldsRes.data || []);

    if (sensorList.length > 0 && !selectedSensor) {
      selectSensor(sensorList[0]);
    }
    setLoading(false);
  };

  const selectSensor = async (sensor) => {
    setSelectedSensor(sensor);
    const { data } = await getSensorReadings(sensor.sensor_id, { limit: 50 });
    setReadings(data || []);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateSensor = async (e) => {
    e.preventDefault();
    if (!newSensor.sensor_id || !newSensor.field_id) {
      setToast({ show: true, message: 'Please provide Sensor ID and select a Field', type: 'error' });
      return;
    }
    const { error } = await createSensor({
      sensor_id: newSensor.sensor_id,
      field_id: parseInt(newSensor.field_id),
      sensor_type: newSensor.sensor_type,
    });
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setToast({ show: true, message: 'Sensor registered successfully!', type: 'success' });
      setFormOpen(false);
      setNewSensor({ sensor_id: '', field_id: '', sensor_type: 'soil_moisture' });
      loadData();
    }
  };

  const handleSimulate = async (sensorId) => {
    setSimulating(true);
    const { error } = await simulateSensor(sensorId);
    if (error) {
      setToast({ show: true, message: error, type: 'error' });
    } else {
      setToast({
        show: true,
        message: `Simulation completed! 7 days of telemetry generated for ${sensorId}.`,
        type: 'success',
      });
      if (selectedSensor?.sensor_id === sensorId) {
        selectSensor(selectedSensor);
      }
    }
    setSimulating(false);
  };

  const chartData = readings.map((r) => ({
    time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    moisture: Math.round(r.soil_moisture_percent || 0),
    temp: Math.round(r.temperature_celsius || 0),
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
          <h2 className="text-2xl font-bold text-slate-800">Sensors & Telemetry Pipeline</h2>
          <p className="text-sm text-slate-500">
            Ingest real IoT telemetry, trigger simulator feeds, and track calibration flags.
          </p>
        </div>
        <Button variant="primary" onClick={() => setFormOpen(true)}>
          ➕ Register Sensor Node
        </Button>
      </div>

      {/* Sensor Selection Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1 space-y-3">
          <Card>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">Sensor Nodes</h3>
            {sensors.length === 0 ? (
              <p className="text-xs text-slate-400">No sensors registered.</p>
            ) : (
              <div className="space-y-2">
                {sensors.map((s) => {
                  const isSelected = selectedSensor?.sensor_id === s.sensor_id;
                  const st = SENSOR_STATUS_COLORS[s.status] || SENSOR_STATUS_COLORS.active;
                  return (
                    <div
                      key={s.sensor_id}
                      onClick={() => selectSensor(s)}
                      className={`p-3 rounded-lg cursor-pointer border transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50/50 shadow-sm'
                          : 'border-slate-100 hover:border-slate-200 bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm text-slate-800">{s.sensor_id}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${st.bg} ${st.text}`}>
                          {st.label}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Field #{s.field_id}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        {/* Telemetry Chart & Readings Feed */}
        <div className="md:col-span-3 space-y-6">
          {selectedSensor ? (
            <>
              <Card>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                  <div>
                    <h3 className="text-base font-bold text-slate-800">
                      🌊 Telemetry History — {selectedSensor.sensor_id}
                    </h3>
                    <p className="text-xs text-slate-500">
                      Soil moisture (%) &amp; Ambient temperature (°C) timeline
                    </p>
                  </div>
                  <Button
                    variant="secondary"
                    onClick={() => handleSimulate(selectedSensor.sensor_id)}
                    loading={simulating}
                    className="text-xs"
                  >
                    ⚡ Simulate 7-Day IoT Data
                  </Button>
                </div>

                {chartData.length === 0 ? (
                  <div className="h-64 flex flex-col items-center justify-center text-slate-400 border border-dashed rounded-lg">
                    <p className="text-2xl mb-1">📉</p>
                    <p className="text-sm">No telemetry records found for this node.</p>
                    <p className="text-xs mt-1">Click &quot;Simulate 7-Day IoT Data&quot; or POST to /api/v1/sensor-data</p>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="moistGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#16a34a" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <Tooltip />
                      <Area type="monotone" dataKey="moisture" stroke="#16a34a" strokeWidth={2} fillOpacity={1} fill="url(#moistGrad)" name="Moisture %" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </Card>

              {/* Detailed Readings Table */}
              <Card>
                <h3 className="text-sm font-bold text-slate-800 mb-3">Logged Readings ({readings.length})</h3>
                <div className="overflow-x-auto max-h-80 overflow-y-auto">
                  <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-50 text-xs uppercase text-slate-400 sticky top-0">
                      <tr>
                        <th className="py-2.5 px-3">Timestamp (UTC)</th>
                        <th className="py-2.5 px-3">Moisture</th>
                        <th className="py-2.5 px-3">Temperature</th>
                        <th className="py-2.5 px-3">Source Flag</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {readings.map((r) => (
                        <tr key={r.id} className="hover:bg-slate-50/70">
                          <td className="py-2 px-3 text-xs font-mono">{new Date(r.timestamp).toLocaleString()}</td>
                          <td className="py-2 px-3 font-semibold text-primary-700">{r.soil_moisture_percent?.toFixed(1)}%</td>
                          <td className="py-2 px-3">{r.temperature_celsius?.toFixed(1)}°C</td>
                          <td className="py-2 px-3">
                            <span
                              className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                                r.is_simulated
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-emerald-100 text-emerald-800'
                              }`}
                            >
                              {r.quality_flag || (r.is_simulated ? 'SIMULATED' : 'VALID')}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          ) : (
            <Card>
              <div className="text-center py-12 text-slate-400">
                <p className="text-3xl mb-2">📡</p>
                <p className="text-sm font-medium">Select a sensor to view telemetry graphs and logs.</p>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Modal for Registering a Sensor */}
      {formOpen && (
        <Modal isOpen={formOpen} onClose={() => setFormOpen(false)} title="Register IoT Sensor">
          <form onSubmit={handleCreateSensor} className="space-y-4">
            <Input
              label="Sensor Identifier"
              placeholder="e.g. SN-MOIST-204"
              value={newSensor.sensor_id}
              onChange={(e) => setNewSensor({ ...newSensor, sensor_id: e.target.value })}
              required
            />
            <Select
              label="Assigned Field"
              value={newSensor.field_id}
              onChange={(e) => setNewSensor({ ...newSensor, field_id: e.target.value })}
              options={fields.map((f) => ({ value: f.id, label: `${f.field_name} (#${f.id})` }))}
              placeholder="Select field"
              required
            />
            <Input
              label="Sensor Hardware Type"
              value={newSensor.sensor_type}
              onChange={(e) => setNewSensor({ ...newSensor, sensor_type: e.target.value })}
            />
            <div className="flex justify-end gap-3 pt-3">
              <Button variant="secondary" onClick={() => setFormOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                Register Sensor
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}

