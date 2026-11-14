import { SENSOR_STATUS_COLORS } from '@/lib/constants';

export default function SensorStatus({ sensors = [], loading = false }) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (sensors.length === 0) {
    return (
      <div className="text-center py-6 text-slate-500">
        <p className="text-2xl mb-2">📡</p>
        <p className="text-sm">No sensors registered yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {sensors.slice(0, 8).map((sensor) => {
        const status = SENSOR_STATUS_COLORS[sensor.status] || SENSOR_STATUS_COLORS.inactive;
        return (
          <div
            key={sensor.sensor_id || sensor.id}
            className="flex items-center justify-between p-3 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={`w-2.5 h-2.5 rounded-full ${status.dot}`} />
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {sensor.sensor_id || sensor.id}
                </p>
                <p className="text-xs text-slate-500">{sensor.sensor_type || 'Unknown'}</p>
              </div>
            </div>
            <div className="text-right">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${status.bg} ${status.text}`}>
                {status.label}
              </span>
              {sensor.last_reading_at && (
                <p className="text-xs text-slate-400 mt-0.5">
                  {new Date(sensor.last_reading_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
