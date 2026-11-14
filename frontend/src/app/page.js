'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import StatsCard from '@/components/dashboard/StatsCard';
import MoistureChart from '@/components/dashboard/MoistureChart';
import WeatherCard from '@/components/dashboard/WeatherCard';
import SensorStatus from '@/components/dashboard/SensorStatus';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { getFarmers, getFields, getSensors, getFieldReadings, getWeather } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    farmers: 0,
    fields: 0,
    sensors: 0,
    activeSensors: 0,
  });
  const [sensorsList, setSensorsList] = useState([]);
  const [recentReadings, setRecentReadings] = useState([]);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      setLoading(true);
      try {
        const [farmersRes, fieldsRes, sensorsRes] = await Promise.all([
          getFarmers(),
          getFields(),
          getSensors(),
        ]);

        const farmers = farmersRes.data || [];
        const fields = fieldsRes.data || [];
        const sensors = sensorsRes.data || [];

        setSensorsList(sensors);
        setStats({
          farmers: farmers.length,
          fields: fields.length,
          sensors: sensors.length,
          activeSensors: sensors.filter((s) => s.status === 'active').length,
        });

        // Load weather and readings for the first field if available
        if (fields.length > 0) {
          const firstField = fields[0];
          const [weatherRes, readingsRes] = await Promise.all([
            getWeather(firstField.id),
            getFieldReadings(firstField.id, { limit: 15 }),
          ]);

          if (weatherRes.data && weatherRes.data.length > 0) {
            const latestW = weatherRes.data[0];
            setCurrentWeather({
              temperature_celsius: latestW.temperature_celsius,
              humidity_percent: latestW.humidity_percent,
              rainfall_mm: latestW.rainfall_mm,
              condition: latestW.weather_condition,
            });
          }

          if (readingsRes.data && readingsRes.data.length > 0) {
            setRecentReadings(readingsRes.data);
            const formatted = readingsRes.data.map((r) => ({
              time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              moisture: Math.round(r.soil_moisture_percent || 0),
            })).reverse();
            setChartData(formatted);
          }
        }
      } catch (err) {
        console.error('Error loading dashboard:', err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-primary-700 to-primary-900 rounded-2xl p-6 text-white shadow-lg">
        <div>
          <span className="inline-block px-3 py-1 bg-primary-600/60 rounded-full text-xs font-semibold uppercase tracking-wider mb-2">
            🌱 Milestone 1 Live
          </span>
          <h2 className="text-2xl font-bold">Smart Irrigation Dashboard</h2>
          <p className="text-primary-100 text-sm mt-1">
            Real-time soil moisture monitoring, OpenWeatherMap integration, and sensor telemetry.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/sensors">
            <Button variant="secondary" className="bg-white text-primary-800 hover:bg-primary-50">
              📡 Telemetry
            </Button>
          </Link>
          <Link href="/weather">
            <Button variant="primary" className="bg-primary-500 hover:bg-primary-600 border-none">
              🌤️ Weather
            </Button>
          </Link>
        </div>
      </div>

      {/* 4 Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          icon="👨‍🌾"
          title="Registered Farmers"
          value={stats.farmers}
          trend="Profiles in system"
          trendColor="text-primary-600"
          loading={loading}
        />
        <StatsCard
          icon="🗺️"
          title="Monitored Fields"
          value={stats.fields}
          trend="GPS geo-tagged"
          trendColor="text-emerald-600"
          loading={loading}
        />
        <StatsCard
          icon="📡"
          title="IoT Sensors"
          value={stats.sensors}
          trend={`${stats.activeSensors} active`}
          trendColor="text-blue-600"
          loading={loading}
        />
        <StatsCard
          icon="💧"
          title="Ingestion Pipeline"
          value="Online"
          trend="REST & Simulator"
          trendColor="text-primary-700"
          loading={loading}
        />
      </div>

      {/* Moisture Chart and Weather Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MoistureChart data={chartData} loading={loading} />
        </div>
        <div>
          <WeatherCard weather={currentWeather} loading={loading} />
        </div>
      </div>

      {/* Bottom Grid: Recent Readings & Sensor Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Ingested Sensor Data */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-semibold text-slate-800">📊 Recent Sensor Ingestion Feed</h3>
              <Link href="/sensors" className="text-xs font-semibold text-primary-600 hover:text-primary-700">
                View All &rarr;
              </Link>
            </div>

            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-10 bg-slate-100 rounded animate-pulse" />
                ))}
              </div>
            ) : recentReadings.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <p className="text-3xl mb-2">📥</p>
                <p className="text-sm font-medium">No readings recorded yet.</p>
                <p className="text-xs text-slate-400 mt-1">Go to Sensors to simulate or send data via REST API.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 text-xs uppercase text-slate-400 border-b border-slate-100">
                    <tr>
                      <th className="py-2.5 px-3">Sensor ID</th>
                      <th className="py-2.5 px-3">Moisture</th>
                      <th className="py-2.5 px-3">Temp</th>
                      <th className="py-2.5 px-3">Quality</th>
                      <th className="py-2.5 px-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recentReadings.slice(0, 6).map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50/60">
                        <td className="py-2.5 px-3 font-medium text-slate-800">{r.sensor_id}</td>
                        <td className="py-2.5 px-3">
                          <span className="font-semibold text-primary-700">
                            {r.soil_moisture_percent?.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-2.5 px-3">{r.temperature_celsius?.toFixed(1)}°C</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              r.is_simulated
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-emerald-100 text-emerald-800'
                            }`}
                          >
                            {r.quality_flag || 'VALID'}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-xs text-slate-400">
                          {new Date(r.timestamp).toLocaleTimeString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        {/* Sensor Health Status */}
        <div>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-semibold text-slate-800">📡 Sensor Nodes</h3>
              <span className="text-xs text-slate-400">{sensorsList.length} registered</span>
            </div>
            <SensorStatus sensors={sensorsList} loading={loading} />
          </Card>
        </div>
      </div>
    </div>
  );
}

