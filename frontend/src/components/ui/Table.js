export default function Table({ columns, data, onEdit, onDelete, emptyMessage = 'No data available.' }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 bg-white rounded-xl border border-slate-200">
        <p className="text-lg">📭</p>
        <p className="mt-2">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded-xl border border-slate-200 shadow-sm">
      <table className="w-full text-sm text-left">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="px-4 py-3 font-semibold text-slate-600 whitespace-nowrap">
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete) && (
              <th className="px-4 py-3 font-semibold text-slate-600 text-right">Actions</th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {data.map((row, rowIdx) => (
            <tr key={row.id || rowIdx} className="hover:bg-slate-50 transition-colors">
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-slate-700 whitespace-nowrap">
                  {col.render ? col.render(row[col.key], row) : row[col.key] ?? '—'}
                </td>
              ))}
              {(onEdit || onDelete) && (
                <td className="px-4 py-3 text-right space-x-2">
                  {onEdit && (
                    <button
                      onClick={() => onEdit(row)}
                      className="text-primary-600 hover:text-primary-800 font-medium text-sm"
                    >
                      ✏️ Edit
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(row)}
                      className="text-red-600 hover:text-red-800 font-medium text-sm"
                    >
                      🗑️ Delete
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
