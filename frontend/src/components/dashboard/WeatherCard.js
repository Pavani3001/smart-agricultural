import Card from '@/components/ui/Card';
import { WEATHER_EMOJIS } from '@/lib/constants';

export default function WeatherCard({ weather, loading = false }) {
  if (loading) {
    return (
      <Card>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-slate-200 rounded w-1/2" />
          <div className="h-8 bg-slate-200 rounded w-1/3" />
          <div className="h-4 bg-slate-200 rounded w-2/3" />
        </div>
      </Card>
    );
  }

  if (!weather) {
    return (
      <Card>
        <div className="text-center py-4 text-slate-500">
          <p className="text-3xl mb-2">🌤️</p>
          <p className="text-sm">No weather data available</p>
          <p className="text-xs text-slate-400 mt-1">Fetch weather to see conditions</p>
        </div>
      </Card>
    );
  }

  const emoji = WEATHER_EMOJIS[weather.condition] || WEATHER_EMOJIS.default;

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-medium text-slate-500 mb-1">Current Weather</h3>
          <div className="flex items-center gap-2">
            <span className="text-4xl">{emoji}</span>
            <div>
              <p className="text-2xl font-bold text-slate-800">
                {weather.temperature_celsius != null ? `${Math.round(weather.temperature_celsius)}°C` : '—'}
              </p>
              <p className="text-sm text-slate-500">{weather.condition || 'Unknown'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-slate-100">
        <div>
          <p className="text-xs text-slate-500">Humidity</p>
          <p className="text-sm font-semibold text-slate-700">
            {weather.humidity_percent != null ? `${weather.humidity_percent}%` : '—'}
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Rainfall</p>
          <p className="text-sm font-semibold text-slate-700">
            {weather.rainfall_mm != null ? `${weather.rainfall_mm} mm` : '—'}
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Wind Speed</p>
          <p className="text-sm font-semibold text-slate-700">
            {weather.wind_speed_ms != null ? `${weather.wind_speed_ms} m/s` : '—'}
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Fetched</p>
          <p className="text-sm font-semibold text-slate-700">
            {weather.fetched_at
              ? new Date(weather.fetched_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : '—'}
          </p>
        </div>
      </div>
    </Card>
  );
}
