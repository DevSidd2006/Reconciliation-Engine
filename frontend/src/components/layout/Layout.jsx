import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const Layout = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen flex">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

            <div className="flex-1 flex flex-col min-h-screen lg:ml-0">
                <Header onMenuClick={() => setSidebarOpen(true)} />

                <main className="flex-1 p-6 overflow-auto custom-scrollbar">
                    {children}
                </main>
            </div>
        </div>
    );
};
