export default function TransactionsTable({ transactions }) {
  return (
    <div className="glass-card overflow-hidden">
      <div className="overflow-x-auto custom-scrollbar">
        <table className="min-w-full text-sm">
          <thead className="bg-white/5 border-b border-white/10">
            <tr>
              <th className="p-3 text-left text-dark-300 font-semibold">ID</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Amount</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Source</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Status</th>
              <th className="p-3 text-left text-dark-300 font-semibold">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {transactions.map((t) => (
              <tr key={t.txn_id} className="hover:bg-white/5 transition-colors">
                <td className="p-3 text-primary-400 font-mono">{t.txn_id}</td>
                <td className="p-3 text-dark-100 font-semibold">${t.amount?.toFixed(2)}</td>
                <td className="p-3 text-dark-200 capitalize">{t.source}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    t.status === 'success' ? 'bg-success-light/20 text-success-light' :
                    t.status === 'pending' ? 'bg-warning-light/20 text-warning-light' :
                    'bg-danger-light/20 text-danger-light'
                  }`}>
                    {t.status}
                  </span>
                </td>
                <td className="p-3 text-dark-400 text-xs">{new Date(t.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
