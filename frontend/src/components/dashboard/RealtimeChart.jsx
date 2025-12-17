import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useSocket } from '../../hooks/useSocket';

export const RealTimeChart = () => {
    const [chartData, setChartData] = useState([]);
    const { socket } = useSocket();

    // Initialize with sample data
    useEffect(() => {
        const initialData = Array.from({ length: 20 }, (_, i) => ({
            time: new Date(Date.now() - (19 - i) * 30000).toLocaleTimeString(),
            coreBanking: Math.floor(Math.random() * 100) + 50,
            mobileApp: Math.floor(Math.random() * 80) + 30,
            paymentGateway: Math.floor(Math.random() * 90) + 40,
            totalEvents: Math.floor(Math.random() * 200) + 100
        }));
        setChartData(initialData);
    }, []);

    // Update chart data every 30 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            setChartData(prevData => {
                const newData = [...prevData.slice(1)];
                newData.push({
                    time: new Date().toLocaleTimeString(),
                    coreBanking: Math.floor(Math.random() * 100) + 50,
                    mobileApp: Math.floor(Math.random() * 80) + 30,
                    paymentGateway: Math.floor(Math.random() * 90) + 40,
                    totalEvents: Math.floor(Math.random() * 200) + 100
                });
                return newData;
            });
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    // Listen for real-time updates via socket
    useEffect(() => {
        if (socket) {
            socket.on('transaction_flow_update', (data) => {
                setChartData(prevData => {
                    const newData = [...prevData.slice(1)];
                    newData.push({
                        time: new Date().toLocaleTimeString(),
                        coreBanking: data.coreBanking || Math.floor(Math.random() * 100) + 50,
                        mobileApp: data.mobileApp || Math.floor(Math.random() * 80) + 30,
                        paymentGateway: data.paymentGateway || Math.floor(Math.random() * 90) + 40,
                        totalEvents: data.totalEvents || Math.floor(Math.random() * 200) + 100
                    });
                    return newData;
                });
            });

            return () => {
                socket.off('transaction_flow_update');
            };
        }
    }, [socket]);

    return (
        <div className="glass-card p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-xl font-semibold text-dark-100">Real-Time Transaction Flow</h3>
                    <p className="text-dark-400 text-sm">Events per minute from all sources</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-success-light rounded-full animate-pulse"></div>
                    <span className="text-sm text-success-light">Live</span>
                </div>
            </div>

            <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis 
                            dataKey="time" 
                            stroke="#9CA3AF"
                            fontSize={12}
                        />
                        <YAxis 
                            stroke="#9CA3AF"
                            fontSize={12}
                        />
                        <Tooltip 
                            contentStyle={{
                                backgroundColor: '#1F2937',
                                border: '1px solid #374151',
                                borderRadius: '8px',
                                color: '#F9FAFB'
                            }}
                        />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey="coreBanking" 
                            stroke="#3B82F6" 
                            strokeWidth={2}
                            name="Core Banking"
                            dot={false}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="mobileApp" 
                            stroke="#10B981" 
                            strokeWidth={2}
                            name="Mobile App"
                            dot={false}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="paymentGateway" 
                            stroke="#F59E0B" 
                            strokeWidth={2}
                            name="Payment Gateway"
                            dot={false}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="totalEvents" 
                            stroke="#EF4444" 
                            strokeWidth={2}
                            name="Total Events"
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};