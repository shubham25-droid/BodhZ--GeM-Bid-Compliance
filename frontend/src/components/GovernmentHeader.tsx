import React from 'react';
import { ShieldCheck, Lock, UserCheck, Award } from 'lucide-react';

export const GovernmentHeader: React.FC = () => {
  return (
    <header className="bg-gov-navy text-white shadow-md border-b-2 border-gov-saffron">
      {/* Top Government Portal Utility Bar */}
      <div className="bg-[#041329] px-6 py-1 text-xs flex justify-between items-center text-slate-300 border-b border-slate-800">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            GOVERNMENT E-MARKETPLACE (GeM) INTEGRATED PORTAL
          </span>
          <span className="text-slate-500">|</span>
          <span>SIH26100 OFFICIAL COMPLIANCE ENGINE</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 text-emerald-300 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60 text-[11px]">
            <Lock className="w-3 h-3" /> SECURE GOV SSL
          </span>
          <span>Helpdesk: 1800-419-3436</span>
        </div>
      </div>

      {/* Main Header Banner */}
      <div className="px-6 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
          {/* Emblem of India / Ashoka Chakra Stylized Emblem Motif */}
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-500 via-amber-600 to-amber-700 p-0.5 shadow-lg flex items-center justify-center shrink-0 border border-amber-300/40">
            <div className="w-full h-full rounded-full bg-gov-navy flex items-center justify-center relative overflow-hidden">
              {/* Ashoka Chakra 24 Spokes Geometric Wheel Icon */}
              <div className="w-9 h-9 rounded-full border-2 border-amber-400/90 flex items-center justify-center relative">
                <Award className="w-5 h-5 text-amber-400" />
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">BodhZ — GeM Bid Compliance Platform</h1>
              <span className="bg-gov-saffron text-white text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded shadow-sm">
                OFFICIAL VERIFICATION ENGINE
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              AI-Powered Decision Support System for Government Procurement Officers • SIH26100
            </p>
          </div>
        </div>

        {/* Officer Active Badge */}
        <div className="flex items-center gap-3 bg-gov-navyLight px-3.5 py-2 rounded-lg border border-slate-700 shadow-inner">
          <div className="w-8 h-8 rounded-full bg-gov-saffron/20 border border-gov-saffron/40 flex items-center justify-center text-gov-saffron">
            <UserCheck className="w-4 h-4" />
          </div>
          <div className="text-right">
            <div className="text-xs font-semibold text-white">Rajesh Kumar</div>
            <div className="text-[10px] text-emerald-400 font-medium">Senior Procurement Officer</div>
          </div>
        </div>
      </div>
    </header>
  );
};
