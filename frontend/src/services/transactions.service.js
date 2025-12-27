import api from "./api";

export async function getTransactions() {
  try {
    const res = await api.get("/transactions");
    return res.data.data;
  } catch (error) {
    console.warn('Backend not available, using mock data:', error.message);
    // Return mock data when backend is not available
    return Array.from({ length: 10 }, (_, i) => ({
      txn_id: `TXN${String(i + 1).padStart(6, '0')}`,
      amount: Math.random() * 10000 + 100,
      status: ['success', 'pending', 'failed'][Math.floor(Math.random() * 3)],
      timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      currency: 'USD',
      account_id: `ACC${Math.floor(Math.random() * 1000)}`,
      source: ['core', 'gateway', 'mobile'][Math.floor(Math.random() * 3)],
    }));
  }
}