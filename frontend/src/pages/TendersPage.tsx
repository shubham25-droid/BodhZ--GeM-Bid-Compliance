import React from 'react';
import { FileText, CheckCircle2, Shield, Plus, ArrowRight } from 'lucide-react';

export const TendersPage: React.FC = () => {
  const sampleTenders = [
    {
      id: 'TND-001',
      tenderNumber: 'GEM/2026/B/882109',
      title: 'Procurement of Server Infrastructure & Enterprise Storage',
      category: 'IT Hardware & Infrastructure',
      createdDate: '2026-08-20',
      status: 'ACTIVE',
      requirementsCount: 6,
      mandatoryModules: ['GST', 'Udyam/MSME', 'PAN', 'OEM Authorization', 'Financial Turnover']
    },
    {
      id: 'TND-002',
      tenderNumber: 'GEM/2026/B/771042',
      title: 'Supply and Installation of Solar Power Generating Systems',
      category: 'Renewable Energy Systems',
      createdDate: '2026-08-15',
      status: 'ACTIVE',
      requirementsCount: 8,
      mandatoryModules: ['GST', 'Make in India', 'BIS Certification', 'NSIC']
    }
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="flex justify-between items-center bg-white p-4 rounded-lg border border-gov-border shadow-sm">
        <div>
          <h2 className="text-base font-bold text-gov-navy uppercase tracking-wide">
            GeM Procurement Tenders & Structured Requirements
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage active procurement tenders, view extracted rules, and upload bidder submission documents.
          </p>
        </div>

        <button className="bg-gov-navy hover:bg-gov-navyLight text-white text-xs font-bold px-4 py-2 rounded flex items-center gap-2 shadow transition-colors">
          <Plus className="w-4 h-4 text-gov-saffron" /> CREATE NEW TENDER
        </button>
      </div>

      {/* Tender List Grid */}
      <div className="space-y-4">
        {sampleTenders.map((tender) => (
          <div key={tender.id} className="bg-white p-5 rounded-lg border border-gov-border shadow-sm space-y-4 hover:border-gov-navy transition-colors">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold bg-slate-100 text-gov-navy px-2 py-0.5 rounded border border-slate-200">
                    {tender.tenderNumber}
                  </span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded uppercase">
                    {tender.status}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-gov-navy mt-1.5">{tender.title}</h3>
                <p className="text-xs text-slate-500 mt-0.5">Category: {tender.category} | Created: {tender.createdDate}</p>
              </div>

              <button className="bg-slate-100 hover:bg-slate-200 text-gov-navy text-xs font-semibold px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors">
                View Requirements <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Mandatory Modules Chips */}
            <div className="pt-2 border-t flex items-center gap-2 flex-wrap text-xs">
              <span className="text-slate-500 font-semibold">Structured Rules:</span>
              {tender.mandatoryModules.map((mod) => (
                <span key={mod} className="bg-gov-navyLight/10 text-gov-navy font-medium px-2 py-0.5 rounded text-[11px] border border-gov-navy/20 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-gov-saffron" /> {mod}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
