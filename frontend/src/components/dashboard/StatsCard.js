import Card from '@/components/ui/Card';

export default function StatsCard({ icon, title, value, trend, trendColor = 'text-slate-500', loading = false }) {
  return (
    <Card className="flex items-start gap-4">
      <div className="flex-shrink-0 text-3xl">{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-500 truncate">{title}</p>
        {loading ? (
          <div className="h-8 w-16 bg-slate-200 rounded animate-pulse mt-1" />
        ) : (
          <p className="text-2xl font-bold text-slate-800 mt-1">{value ?? '—'}</p>
        )}
        {trend && (
          <p className={`text-xs mt-1 font-medium ${trendColor}`}>{trend}</p>
        )}
      </div>
    </Card>
  );
}
