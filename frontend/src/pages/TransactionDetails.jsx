import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api"; // Assuming a configured axios instance
import { ArrowLeft, Clock, DollarSign, Server, AlertTriangle, FileJson, CheckCircle } from "lucide-react";

/**
 * TransactionDetails Page
 * Shows comprehensive details for a single transaction, including timeline and mismatches.
 */
const TransactionDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [transaction, setTransaction] = useState(null);
    const [mismatches, setMismatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState("timeline");

    useEffect(() => {
        fetchDetails();
    }, [id]);

    const fetchDetails = async () => {
        try {
            setLoading(true);
            // Calls the new backend endpoint: GET /transactions/{id}/details
            const response = await api.get(`/transactions/${id}/details`);
            setTransaction(response.data.data.transaction);
            setMismatches(response.data.data.mismatches);
        } catch (err) {
            console.error("Failed to fetch transaction details:", err);
            setError("Failed to load transaction details. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error || !transaction) {
        return (
            <div className="p-8 bg-gray-900 min-h-screen text-white">
                <div className="max-w-4xl mx-auto text-center">
                    <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">Error Loading Transaction</h2>
                    <p className="text-gray-400 mb-6">{error || "Transaction not found"}</p>
                    <button
                        onClick={() => navigate("/transactions")}
                        className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition"
                    >
                        Back to Transactions
                    </button>
                </div>
            </div>
        );
    }

    const getStatusColor = (status) => {
        switch (status) {
            case "SUCCESS": return "text-green-500 bg-green-900/20 border-green-900/50";
            case "FAILED": return "text-red-500 bg-red-900/20 border-red-900/50";
            case "PENDING": return "text-yellow-500 bg-yellow-900/20 border-yellow-900/50";
            default: return "text-gray-400 bg-gray-800 border-gray-700";
        }
    };

    return (
        <div className="p-6 bg-gray-900 min-h-screen text-white">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex items-center space-x-4 mb-6">
                    <button
                        onClick={() => navigate(-1)}
                        className="p-2 hover:bg-gray-800 rounded-full transition"
                    >
                        <ArrowLeft className="h-6 w-6 text-gray-400" />
                    </button>
                    <div>
                        <h1 className="text-2xl font-bold flex items-center">
                            Transaction Details
                            <span className={`ml-4 px-3 py-1 rounded-full text-xs border ${getStatusColor(transaction.status)}`}>
                                {transaction.status}
                            </span>
                        </h1>
                        <p className="text-gray-400 text-sm">ID: {transaction.txn_id}</p>
                    </div>
                </div>

                {/* Top KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center space-x-3 text-gray-400 mb-2">
                            <DollarSign className="h-5 w-5" />
                            <span>Amount</span>
                        </div>
                        <div className="text-2xl font-bold text-white">
                            {transaction.currency} {transaction.amount?.toFixed(2)}
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center space-x-3 text-gray-400 mb-2">
                            <Server className="h-5 w-5" />
                            <span>Source System</span>
                        </div>
                        <div className="text-2xl font-bold text-white capitalize">
                            {transaction.source || "Unknown"}
                        </div>
                    </div>

                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center space-x-3 text-gray-400 mb-2">
                            <Clock className="h-5 w-5" />
                            <span>Timestamp</span>
                        </div>
                        <div className="text-lg font-bold text-white">
                            {new Date(transaction.timestamp).toLocaleString()}
                        </div>
                    </div>
                </div>

                {/* Main Content Tabs */}
                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                    <div className="flex border-b border-gray-700">
                        <button
                            onClick={() => setActiveTab("timeline")}
                            className={`flex-1 py-4 text-center font-medium transition ${activeTab === "timeline"
                                    ? "text-blue-500 border-b-2 border-blue-500 bg-gray-800/50"
                                    : "text-gray-400 hover:text-white hover:bg-gray-700"
                                }`}
                        >
                            Execution Timeline
                        </button>
                        <button
                            onClick={() => setActiveTab("mismatches")}
                            className={`flex-1 py-4 text-center font-medium transition ${activeTab === "mismatches"
                                    ? "text-blue-500 border-b-2 border-blue-500 bg-gray-800/50"
                                    : "text-gray-400 hover:text-white hover:bg-gray-700"
                                }`}
                        >
                            Mismatches ({mismatches.length})
                        </button>
                        <button
                            onClick={() => setActiveTab("raw")}
                            className={`flex-1 py-4 text-center font-medium transition ${activeTab === "raw"
                                    ? "text-blue-500 border-b-2 border-blue-500 bg-gray-800/50"
                                    : "text-gray-400 hover:text-white hover:bg-gray-700"
                                }`}
                        >
                            Raw Data (JSON)
                        </button>
                    </div>

                    <div className="p-6">
                        {activeTab === "timeline" && (
                            <div className="space-y-8 pl-4 border-l-2 border-gray-700 relative">
                                <div className="relative pl-8">
                                    <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-blue-500 ring-4 ring-gray-900"></div>
                                    <h3 className="text-lg font-semibold text-white">Transaction Created</h3>
                                    <p className="text-gray-400 text-sm">{new Date(transaction.timestamp).toLocaleString()}</p>
                                    <p className="text-gray-400 mt-1">Initiated by {transaction.source} system.</p>
                                </div>

                                {/* Mismatches in timeline */}
                                {mismatches.map((m) => (
                                    <div key={m.id} className="relative pl-8">
                                        <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-red-500 ring-4 ring-gray-900"></div>
                                        <h3 className="text-lg font-semibold text-red-400">Mismatch Detected: {m.mismatch_type}</h3>
                                        <p className="text-gray-400 text-sm">{new Date(m.detected_at).toLocaleString()}</p>
                                        <p className="text-gray-300 mt-1">{m.details}</p>
                                    </div>
                                ))}

                                {/* Completion Node */}
                                <div className="relative pl-8">
                                    <div className={`absolute -left-[9px] top-1 h-4 w-4 rounded-full ring-4 ring-gray-900 ${transaction.status === "SUCCESS" ? "bg-green-500" :
                                            transaction.status === "FAILED" ? "bg-red-500" : "bg-yellow-500"
                                        }`}></div>
                                    <h3 className="text-lg font-semibold text-white">Final Status: {transaction.status}</h3>
                                    <p className="text-gray-400 text-sm">Latest update recorded.</p>
                                </div>
                            </div>
                        )}

                        {activeTab === "mismatches" && (
                            <div className="space-y-4">
                                {mismatches.length === 0 ? (
                                    <div className="text-center py-10">
                                        <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
                                        <p className="text-gray-300 text-lg">No mismatches found for this transaction.</p>
                                        <p className="text-gray-500">Everything looks good!</p>
                                    </div>
                                ) : (
                                    mismatches.map((m) => (
                                        <div key={m.id} className="bg-red-900/10 border border-red-900/30 p-4 rounded-lg flex justify-between items-center">
                                            <div>
                                                <h4 className="font-bold text-red-400 text-lg">{m.mismatch_type}</h4>
                                                <p className="text-gray-400 text-sm">Detected: {new Date(m.detected_at).toLocaleString()}</p>
                                                <p className="text-gray-300 mt-1">{m.details}</p>
                                            </div>
                                            <div className="text-right">
                                                <span className={`px-2 py-1 rounded text-xs font-bold ${m.status === 'RESOLVED' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'
                                                    }`}>
                                                    {m.status}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}

                        {activeTab === "raw" && (
                            <div className="bg-black p-4 rounded-lg overflow-x-auto">
                                <pre className="text-green-400 text-sm font-mono">
                                    {JSON.stringify(transaction, null, 2)}
                                </pre>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TransactionDetails;
