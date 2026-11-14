'use client';

import { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Card from '@/components/ui/Card';

// Generate stable demo data for the last 24 hours if no real data provided
function generateDemoData() {
  const data = [];
  const now = new Date();
  for (let i = 24; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    data.push({
      time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      moisture: Math.round(45 + Math.sin(i / 3) * 15),
    });
  }
  return data;
}

export default function MoistureChart({ data, loading = false }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDemo = !data || data.length === 0;
  const chartData = data && data.length > 0 ? data : (mounted ? generateDemoData() : []);

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-slate-700">🌊 Soil Moisture Trend</h3>
        {isDemo && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full font-medium">
            Demo Data
          </span>
        )}
      </div>
      {loading || !mounted ? (
        <div className="h-64 bg-slate-100 rounded animate-pulse flex items-center justify-center text-slate-400 text-sm">
          Loading soil moisture charts...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              label={{ value: 'Moisture %', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#94a3b8' } }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
              }}
              formatter={(value) => [`${value}%`, 'Moisture']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="moisture"
              stroke="#16a34a"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#16a34a' }}
              name="Soil Moisture"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
