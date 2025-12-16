import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useSocket } from '../../hooks/useSocket';
import { CHART_DATA_POINTS } from '../../utils/constants';

const RealtimeChart = () => {
    const { subscribe, unsubscribe } = useSocket();
    const [data, setData] = useState([]);

    useEffect(() => {
        // Initialize with empty data points
        const initialData = Array.from({ length: CHART_DATA_POINTS }, (_, i) => ({
            time: new Date(Date.now() - (CHART_DATA_POINTS - i) * 5000).toLocaleTimeString(),
            core: 0,
            gateway: 0,
            mobile: 0,
        }));
        setData(initialData);

        // Subscribe to real-time transaction events
        const handleTransaction = (transaction) => {
            setData((prevData) => {
                const newData = [...prevData];
                const lastPoint = newData[newData.length - 1];

                // Update the last data point
                const updated = { ...lastPoint };
                if (transaction.source === 'core') updated.core += 1;
                if (transaction.source === 'gateway') updated.gateway += 1;
                if (transaction.source === 'mobile') updated.mobile += 1;

                newData[newData.length - 1] = updated;

                // Shift data if we have too many points
                if (newData.length >= CHART_DATA_POINTS) {
                    newData.shift();
                }

                return newData;
            });
        };

        subscribe('new_transaction', handleTransaction);

        // Add new data point every 5 seconds
        const interval = setInterval(() => {
            setData((prevData) => {
                const newPoint = {
                    time: new Date().toLocaleTimeString(),
                    core: 0,
                    gateway: 0,
                    mobile: 0,
                };

                const newData = [...prevData, newPoint];

                if (newData.length > CHART_DATA_POINTS) {
                    newData.shift();
                }

                return newData;
            });
        }, 5000);

        return () => {
            unsubscribe('new_transaction', handleTransaction);
            clearInterval(interval);
        };
    }, [subscribe, unsubscribe]);

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-dark-100 mb-4">Real-Time Transaction Flow</h3>

            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey="time"
                        stroke="#94a3b8"
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis
                        stroke="#94a3b8"
                        style={{ fontSize: '12px' }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            backdropFilter: 'blur(10px)',
                        }}
                        labelStyle={{ color: '#e2e8f0' }}
                    />
                    <Legend
                        wrapperStyle={{ fontSize: '14px' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="core"
                        stroke="#0ea5e9"
                        strokeWidth={2}
                        dot={false}
                        name="Core Banking"
                    />
                    <Line
                        type="monotone"
                        dataKey="gateway"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                        name="Payment Gateway"
                    />
                    <Line
                        type="monotone"
                        dataKey="mobile"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        dot={false}
                        name="Mobile App"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RealtimeChart;
