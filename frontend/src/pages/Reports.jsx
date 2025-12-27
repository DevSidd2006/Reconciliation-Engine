import React, { useState } from 'react';
import { 
    FileText, 
    Download, 
    Calendar, 
    Filter,
    TrendingUp,
    AlertTriangle,
    Clock,
    DollarSign
} from 'lucide-react';

const ReportCard = ({ title, description, icon: Icon, onGenerate, loading }) => (
    <div className="glass-card p-6 hover:scale-105 transition-transform duration-200">
        <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-primary-600 to-primary-500 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h3 className="font-semibold text-dark-100">{title}</h3>
                    <p className="text-sm text-dark-400">{description}</p>
                </div>
            </div>
        </div>
        <button
            onClick={onGenerate}
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
            {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
                <Download className="w-4 h-4" />
            )}
            Generate Report
        </button>
    </div>
);

export const Reports = () => {
    const [dateRange, setDateRange] = useState({
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0]
    });
    const [loadingReports, setLoadingReports] = useState({});

    const handleGenerateReport = async (reportType) => {
        setLoadingReports(prev => ({ ...prev, [reportType]: true }));
        
        // Simulate report generation
        setTimeout(() => {
            setLoadingReports(prev => ({ ...prev, [reportType]: false }));
            
            // Create and download mock report
            const reportData = generateMockReportData(reportType);
            const blob = new Blob([reportData], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${reportType}_${dateRange.startDate}_${dateRange.endDate}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 2000);
    };

    const generateMockReportData = (reportType) => {
        const headers = {
            'daily-summary': 'Date,Total Transactions,Matched,Mismatches,Success Rate\n',
            'amount-mismatches': 'Transaction ID,Source,Expected Amount,Actual Amount,Difference,Status\n',
            'missing-transactions': 'Transaction ID,Source,Expected Time,Missing From,Status\n',
            'delay-analysis': 'Transaction ID,Source,Processing Time,Expected Time,Delay,Impact\n',
            'failure-patterns': 'Pattern,Frequency,Last Occurrence,Severity,Recommendation\n'
        };

        const sampleData = {
            'daily-summary': '2025-12-17,1250,1180,70,94.4%\n2025-12-16,1180,1120,60,94.9%\n',
            'amount-mismatches': 'TXN001,Core Banking,$1000.00,$999.95,$0.05,Resolved\nTXN002,Gateway,$500.00,$505.00,-$5.00,Pending\n',
            'missing-transactions': 'TXN003,Mobile App,14:30:00,Gateway,Investigating\nTXN004,Core Banking,15:45:00,Mobile App,Resolved\n',
            'delay-analysis': 'TXN005,Gateway,2.5s,1.0s,1.5s,Medium\nTXN006,Mobile App,3.2s,1.2s,2.0s,High\n',
            'failure-patterns': 'Timeout Errors,15,2025-12-17 14:30,High,Increase timeout threshold\nAmount Rounding,8,2025-12-17 13:15,Medium,Standardize rounding rules\n'
        };

        return headers[reportType] + sampleData[reportType];
    };

    const reports = [
        {
            id: 'daily-summary',
            title: 'Daily Reconciliation Summary',
            description: 'Complete daily overview with success rates and trends',
            icon: TrendingUp
        },
        {
            id: 'amount-mismatches',
            title: 'Amount Mismatches Report',
            description: 'Detailed analysis of amount discrepancies',
            icon: DollarSign
        },
        {
            id: 'missing-transactions',
            title: 'Missing Transactions Report',
            description: 'Transactions missing from one or more systems',
            icon: AlertTriangle
        },
        {
            id: 'delay-analysis',
            title: 'Processing Delay Analysis',
            description: 'Transaction processing time analysis and bottlenecks',
            icon: Clock
        },
        {
            id: 'failure-patterns',
            title: 'Recurring Failure Patterns',
            description: 'Top recurring issues and recommended fixes',
            icon: FileText
        }
    ];

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-dark-100 mb-2">
                    Reconciliation Reports
                </h1>
                <p className="text-dark-400">Generate comprehensive reports for audit and analysis</p>
            </div>

            {/* Date Range Selector */}
            <div className="glass-card p-6 mb-8">
                <div className="flex items-center gap-4 mb-4">
                    <Calendar className="w-5 h-5 text-primary-400" />
                    <h3 className="text-lg font-semibold text-dark-100">Report Date Range</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">Start Date</label>
                        <input
                            type="date"
                            value={dateRange.startDate}
                            onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-dark-300 mb-2">End Date</label>
                        <input
                            type="date"
                            value={dateRange.endDate}
                            onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
                            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-3 py-2 text-dark-100 focus:border-primary-500 focus:outline-none"
                        />
                    </div>
                </div>
            </div>

            {/* Report Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {reports.map((report) => (
                    <ReportCard
                        key={report.id}
                        title={report.title}
                        description={report.description}
                        icon={report.icon}
                        loading={loadingReports[report.id]}
                        onGenerate={() => handleGenerateReport(report.id)}
                    />
                ))}
            </div>

            {/* Recent Reports */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-dark-100 mb-4">Recent Reports</h3>
                <div className="space-y-3">
                    {[
                        { name: 'Daily Summary - Dec 16, 2025', size: '2.3 MB', date: '2 hours ago' },
                        { name: 'Amount Mismatches - Dec 15, 2025', size: '1.8 MB', date: '1 day ago' },
                        { name: 'Failure Patterns - Week 50', size: '3.1 MB', date: '2 days ago' }
                    ].map((report, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <FileText className="w-5 h-5 text-primary-400" />
                                <div>
                                    <p className="text-dark-100 font-medium">{report.name}</p>
                                    <p className="text-dark-400 text-sm">{report.size} • {report.date}</p>
                                </div>
                            </div>
                            <button className="text-primary-400 hover:text-primary-300 transition-colors">
                                <Download className="w-4 h-4" />
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};