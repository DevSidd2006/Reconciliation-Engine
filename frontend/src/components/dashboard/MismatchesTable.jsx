export default function MismatchesTable({ mismatches }) {
  return (
    <div className="glass-card overflow-hidden">
      <div className="overflow-x-auto custom-scrollbar">
        <table className="min-w-full text-sm">
          <thead className="bg-danger-light/10 border-b border-danger-light/20">
            <tr>
              <th className="p-3 text-left text-dark-300 font-semibold">Transaction ID</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Type</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Detected</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {mismatches.map((m) => (
              <tr key={m.id} className="hover:bg-white/5 transition-colors">
                <td className="p-3 text-primary-400 font-mono">{m.txn_id}</td>
                <td className="p-3">
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-danger-light/20 text-danger-light">
                    {m.mismatch_type?.replace('_', ' ')}
                  </span>
                </td>
                <td className="p-3 text-dark-400 text-xs">{new Date(m.detected_at).toLocaleString()}</td>
                <td className="p-3 text-dark-200 text-xs">{m.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
