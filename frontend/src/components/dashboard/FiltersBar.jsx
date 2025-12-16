export default function FiltersBar({ filters, setFilters }) {
  return (
    <div className="glass-card p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Date filter */}
        <input
          type="date"
          value={filters.date}
          onChange={(e) => setFilters({ ...filters, date: e.target.value })}
          className="input-field"
        />

        {/* Source filter */}
        <select
          value={filters.source}
          onChange={(e) => setFilters({ ...filters, source: e.target.value })}
          className="input-field"
        >
          <option value="">All Sources</option>
          <option value="core">Core Banking</option>
          <option value="gateway">Payment Gateway</option>
          <option value="mobile">Mobile App</option>
        </select>

        {/* Status filter */}
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="input-field"
        >
          <option value="">All Status</option>
          <option value="success">Success</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>
    </div>
  );
}
