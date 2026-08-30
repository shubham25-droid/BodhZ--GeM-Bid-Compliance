import React from 'react';
import { ShieldCheck, History, Lock, FileText, CheckCircle2 } from 'lucide-react';

export const AuditPage: React.FC = () => {
  const auditLogs = [
    {
      id: 'AUD-9912',
      timestamp: '2026-08-28 17:45:22 IST',
      actor: 'Rajesh Kumar (Senior Procurement Officer)',
      eventType: 'OFFICER_QUALIFICATION_DECISION',
      details: "Bidder 'Acme Solutions Pvt Ltd' marked as QUALIFIED subject to minor spelling note.",
      sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    },
    {
      id: 'AUD-9911',
      timestamp: '2026-08-28 17:42:10 IST',
      actor: 'SYSTEM (AI Compliance Engine)',
      eventType: 'COMPLIANCE_ASSESSMENT_COMPLETED',
      details: 'Compliance Score computed: 85/100. Risk Level: MEDIUM. 4 modules evaluated.',
      sha256: 'a8f5f167f44f4964e6c998dee827110c deep72120e74f3460835f80b182d3e5a shadow'
    },
    {
      id: 'AUD-9910',
      timestamp: '2026-08-28 17:41:05 IST',
      actor: 'SYSTEM (Verification Gateway)',
      eventType: 'GST_VERIFICATION_CHECK',
      details: 'GSTIN 27ABCDE1234F1Z5 checked against SANDBOX mock connector. Status: VERIFIED ACTIVE.',
      sha256: 'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2'
    }
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header Bar */}
      <div className="flex justify-between items-center bg-white p-4 rounded-lg border border-gov-border shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded bg-gov-navy text-white flex items-center justify-center">
            <History className="w-5 h-5 text-gov-saffron" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gov-navy uppercase tracking-wide">
              Immutable Audit Trail & Traceability Records
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Complete SHA-256 hashed log of automated checks, external portal responses, and officer decisions.
            </p>
          </div>
        </div>

        <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-300 px-3 py-1 rounded flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5" /> TAMPER-EVIDENT LOGGING
        </span>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg border border-gov-border shadow-sm overflow-hidden">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-gov-navy text-white uppercase text-[11px] font-bold">
              <th className="p-3">Event ID</th>
              <th className="p-3">Timestamp</th>
              <th className="p-3">Actor</th>
              <th className="p-3">Event Type</th>
              <th className="p-3">Details & Audit Payload</th>
              <th className="p-3">SHA-256 Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {auditLogs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-50 font-sans">
                <td className="p-3 font-mono font-bold text-gov-navy">{log.id}</td>
                <td className="p-3 text-slate-600 font-mono text-[11px]">{log.timestamp}</td>
                <td className="p-3 font-medium text-slate-800">{log.actor}</td>
                <td className="p-3 font-bold text-slate-700">{log.eventType}</td>
                <td className="p-3 text-slate-600">{log.details}</td>
                <td className="p-3 font-mono text-[10px] text-slate-400 truncate max-w-[150px]" title={log.sha256}>
                  {log.sha256}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
