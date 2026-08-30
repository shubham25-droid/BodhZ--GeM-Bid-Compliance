import React, { useState } from 'react';
import { GovernmentHeader } from './components/GovernmentHeader';
import { Navigation } from './components/Navigation';
import { DashboardPage } from './pages/DashboardPage';
import { TendersPage } from './pages/TendersPage';
import { AuditPage } from './pages/AuditPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gov-bg flex flex-col font-sans">
      {/* Government Header */}
      <GovernmentHeader />

      {/* Navigation Bar */}
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Body */}
      <main className="flex-1">
        {activeTab === 'dashboard' && <DashboardPage />}
        {activeTab === 'tenders' && <TendersPage />}
        {activeTab === 'verification' && <DashboardPage />}
        {activeTab === 'audit' && <AuditPage />}
      </main>

      {/* Footer */}
      <footer className="bg-gov-navy text-slate-400 text-xs p-4 text-center border-t border-gov-saffron mt-auto">
        <p>BodhZ — GeM Bid Compliance Verification Platform • SIH26100 Official Solution Prototype</p>
        <p className="text-[10px] text-slate-500 mt-1">Designed for Central & State Procurement Officers. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;
