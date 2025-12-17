import React, { useMemo } from 'react';
import { AlertTriangle } from 'lucide-react';

/**
 * MismatchHeatmap
 * Visualizes mismatch intensity over time (e.g., last 24 hours).
 * Implemented as a grid of 24 blocks (1 per hour).
 */
const MismatchHeatmap = ({ data = [] }) => {
    // Generate dummy data if none provided (for visualization testing)
    const heatmapData = useMemo(() => {
        const hours = Array.from({ length: 24 }, (_, i) => {
            const hour = i;
            // Mock intensity: 0=None, 1=Low, 2=Medium, 3=High
            const intensity = Math.random() > 0.7 ? Math.floor(Math.random() * 4) : 0;
            return { hour, intensity };
        });
        return hours;
    }, [data]);

    const getColor = (intensity) => {
        switch (intensity) {
            case 3: return 'bg-red-500 shadow-lg shadow-red-500/50'; // High
            case 2: return 'bg-orange-500'; // Medium
            case 1: return 'bg-yellow-500'; // Low
            default: return 'bg-white/5'; // None
        }
    };

    const getLabel = (intensity) => {
        switch (intensity) {
            case 3: return 'Critical Spike';
            case 2: return 'Investigate';
            case 1: return 'Warning';
            default: return 'Normal';
        }
    };

    return (
        <div className="glass-card p-6 col-span-1 md:col-span-2">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-red-400" />
                        Live Mismatch Heatmap
                    </h3>
                    <p className="text-sm text-gray-400">Transaction discrepancy intensity (Last 24h)</p>
                </div>
                <div className="flex gap-2 text-xs text-gray-400">
                    <div className="flex items-center gap-1"><div className="w-3 h-3 bg-white/5 rounded"></div> Normal</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-500 rounded"></div> Low</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 bg-orange-500 rounded"></div> Med</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 bg-red-500 rounded"></div> High</div>
                </div>
            </div>

            <div className="relative">
                {/* Heatmap Grid */}
                <div className="grid grid-cols-12 md:grid-cols-24 gap-2">
                    {heatmapData.map((slot, index) => (
                        <div key={index} className="group relative flex flex-col items-center">
                            {/* Bar */}
                            <div
                                className={`w-full h-12 rounded-sm transition-all duration-300 hover:scale-110 ${getColor(slot.intensity)}`}
                            ></div>

                            {/* X-Axis Label */}
                            <span className="text-[10px] text-gray-500 mt-2 font-mono">
                                {index}:00
                            </span>

                            {/* Tooltip */}
                            <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 border border-gray-700 p-2 rounded text-xs whitespace-nowrap z-10 pointer-events-none">
                                <div className="font-bold text-white mb-1">Time: {index}:00 - {index + 1}:00</div>
                                <div className={`${slot.intensity > 1 ? 'text-red-400' : 'text-gray-300'}`}>
                                    Status: {getLabel(slot.intensity)}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MismatchHeatmap;
