import api from "./api";

export async function getMismatches() {
  try {
    const res = await api.get("/mismatches");
    return res.data.data;
  } catch (error) {
    console.warn('Backend not available, using mock data:', error.message);
    // Return mock data when backend is not available
    return Array.from({ length: 5 }, (_, i) => ({
      id: `MISM${String(i + 1).padStart(6, '0')}`,
      txn_id: `TXN${String(Math.floor(Math.random() * 1000)).padStart(6, '0')}`,
      mismatch_type: ['amount_mismatch', 'status_mismatch', 'timestamp_mismatch', 'missing_transaction'][Math.floor(Math.random() * 4)],
      detected_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      details: 'Core banking shows $1,234.56 but gateway shows $1,234.57. Difference: $0.01',
    }));
  }
}

export async function getMismatchStats() {
  try {
    const res = await api.get("/mismatches/stats");
    return res.data.data;
  } catch (error) {
    console.warn('Backend not available, using mock stats');
    return {
      total: 15,
      by_type: {
        amount_mismatch: 5,
        status_mismatch: 4,
        timestamp_mismatch: 3,
        missing_transaction: 3
      }
    };
  }
}

export async function getMismatchById(id) {
  try {
    const res = await api.get(`/mismatches/${id}`);
    return res.data.data;
  } catch (error) {
    console.warn('Backend not available, using mock data');
    return {
      id,
      txn_id: 'TXN000001',
      mismatch_type: 'amount_mismatch',
      detected_at: new Date().toISOString(),
      details: 'Mock mismatch details'
    };
  }
}