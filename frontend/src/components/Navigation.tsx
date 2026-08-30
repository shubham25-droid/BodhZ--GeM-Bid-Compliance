import React from 'react';
import { LayoutDashboard, FileText, CheckCircle2, ShieldAlert } from 'lucide-react';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Procurement Dashboard', icon: LayoutDashboard },
    { id: 'tenders', label: 'Tenders & Requirements', icon: FileText },
    { id: 'verification', label: 'Bidder Compliance Evaluation', icon: CheckCircle2 },
    { id: 'audit', label: 'Audit Trail & Traceability', icon: ShieldAlert },
  ];

  return (
    <nav className="bg-white border-b border-gov-border px-6 shadow-sm">
      <div className="flex space-x-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 py-3 px-4 text-xs font-semibold border-b-2 transition-colors ${
                isActive
                  ? 'border-gov-navy text-gov-navy bg-slate-50'
                  : 'border-transparent text-slate-600 hover:text-gov-navy hover:bg-slate-50/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-gov-saffron' : 'text-slate-400'}`} />
              {item.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
