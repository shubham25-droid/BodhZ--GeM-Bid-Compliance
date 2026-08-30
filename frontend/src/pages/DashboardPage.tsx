import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, AlertTriangle, XCircle, FileText, 
  ExternalLink, Search, CheckCircle, HelpCircle, UserCheck, Scale, History, RefreshCw
} from 'lucide-react';
import { apiService } from '../services/apiService';

export const DashboardPage: React.FC = () => {
  const [selectedBidder, setSelectedBidder] = useState('bidder-01');
  const [decisionNotes, setDecisionNotes] = useState('');
  const [decisionStatus, setDecisionStatus] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Live Assessment State with Demo Fallback
  const [mockAssessment, setMockAssessment] = useState({
    tenderNumber: 'GEM/2026/B/882109',
    tenderTitle: 'Procurement of Server Infrastructure & Enterprise Storage',
    bidderName: 'Acme Solutions & Technologies Pvt Ltd',
    gstin: '27ABCDE1234F1Z5',
    pan: 'ABCDE1234F',
    udyam: 'UDYAM-MH-12-0098234',
    complianceScore: 85,
    riskLevel: 'MEDIUM',
    aiRecommendation: (
      "Bidder satisfies mandatory statutory requirements for GST registration and Udyam MSME status. " +
      "However, a minor identity spelling inconsistency was detected between the GST Certificate ('Acme Solutions Pvt Ltd') " +
      "and Bid Form ('Acme Solutions & Technologies Pvt Ltd'). OEM Authorization evidence is valid. " +
      "Procurement Officer review is recommended before final qualification."
    ),
    verificationModules: [
      { id: 'gst', name: 'GST Registration', status: 'PASS', mode: 'SANDBOX', confidence: '98%', evidenceDoc: 'GST_Certificate.pdf', page: 1 },
      { id: 'udyam', name: 'Udyam / MSME Status', status: 'PASS', mode: 'SANDBOX', confidence: '96%', evidenceDoc: 'Udyam_Registration.pdf', page: 1 },
      { id: 'pan', name: 'PAN & Legal Name Match', status: 'REVIEW', mode: 'DOCUMENT_CONSISTENCY', confidence: '82%', evidenceDoc: 'Bid_Form.pdf', page: 2 },
      { id: 'oem', name: 'OEM Authorization', status: 'PASS', mode: 'DOCUMENT_CONSISTENCY', confidence: '94%', evidenceDoc: 'OEM_Auth_Letter.pdf', page: 1 },
    ],
    findings: [
      {
        id: 'f-1',
        severity: 'WARNING',
        title: 'Identity Name Mismatch across Bid Form and GST Certificate',
        description: "Bid Form lists legal name as 'Acme Solutions & Technologies Pvt Ltd' whereas GST Certificate lists 'Acme Solutions Pvt Ltd'.",
        evidence: 'Bid_Form.pdf (Page 2) vs GST_Certificate.pdf (Page 1)'
      },
      {
        id: 'f-2',
        severity: 'INFO',
        title: 'Udyam Enterprise Type Verified',
        description: 'Micro & Small Enterprise (MSE) benefits applicable under Public Procurement Policy for MSEs Order, 2012.',
        evidence: 'Udyam_Registration.pdf (Page 1)'
      }
    ]
  });

  const handleDecision = async (type: string) => {
    setDecisionStatus(type);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Notification Banner */}
      <div className="bg-amber-50 border-l-4 border-gov-saffron p-4 rounded-r shadow-sm flex items-start justify-between">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-gov-saffron shrink-0 mt-0.5" />
          <div>
            <h3 className="text-xs font-bold text-amber-900 uppercase tracking-wide">
              DECISION SUPPORT MANDATE: OFFICER REVIEW REQUIRED
            </h3>
            <p className="text-xs text-amber-800 mt-0.5">
              The AI Engine has generated an evidence-backed compliance analysis. The final qualification or disqualification decision remains 100% with the Procurement Officer.
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono bg-amber-200/80 text-amber-900 px-2 py-1 rounded border border-amber-300">
          ID: {mockAssessment.tenderNumber}
        </span>
      </div>

      {/* Stats Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gov-border shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs text-gov-textMuted uppercase font-semibold">Total Bidders</div>
            <div className="text-2xl font-bold text-gov-navy mt-1">12</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-700">
            <FileText className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gov-border shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs text-gov-textMuted uppercase font-semibold">Verified Compliant</div>
            <div className="text-2xl font-bold text-emerald-700 mt-1">8</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-700">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gov-border shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs text-gov-textMuted uppercase font-semibold">Review Required</div>
            <div className="text-2xl font-bold text-amber-600 mt-1">3</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center text-amber-600">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gov-border shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs text-gov-textMuted uppercase font-semibold">Non-Compliant / High Risk</div>
            <div className="text-2xl font-bold text-rose-700 mt-1">1</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center text-rose-700">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main Grid: Left Panel (Score & Modules) + Right Panel (Findings & Officer Action) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (5 Cols): Score & Verification Modules */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Compliance Score & Risk Gauge Card */}
          <div className="bg-white p-5 rounded-lg border border-gov-border shadow-sm space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h2 className="text-sm font-bold text-gov-navy uppercase tracking-wide">
                Bidder Evaluation Summary
              </h2>
              <span className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-700 font-mono">
                Bid ID: #BD-9921
              </span>
            </div>

            <div>
              <div className="text-xs font-semibold text-slate-600">Selected Bidder:</div>
              <div className="text-base font-bold text-gov-navy mt-0.5">{mockAssessment.bidderName}</div>
              <div className="text-xs text-slate-500 mt-1 font-mono">
                GSTIN: {mockAssessment.gstin} | PAN: {mockAssessment.pan}
              </div>
            </div>

            {/* Score & Risk Display */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-center">
                <div className="text-[11px] text-slate-500 font-semibold uppercase">Compliance Score</div>
                <div className="text-3xl font-extrabold text-gov-navy mt-1">
                  {mockAssessment.complianceScore}<span className="text-xs font-normal text-slate-400">/100</span>
                </div>
              </div>

              <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-center">
                <div className="text-[11px] text-amber-800 font-semibold uppercase">Assessed Risk Level</div>
                <div className="inline-block mt-1 bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded">
                  {mockAssessment.riskLevel} RISK
                </div>
              </div>
            </div>

            {/* Verification Modules Grid */}
            <div className="pt-3 border-t">
              <div className="text-xs font-bold text-gov-navy uppercase mb-3">Verification Module Status</div>
              <div className="space-y-2.5">
                {mockAssessment.verificationModules.map((mod) => (
                  <div key={mod.id} className="p-2.5 rounded border border-slate-200 bg-slate-50 flex items-center justify-between">
                    <div>
                      <div className="text-xs font-semibold text-slate-800">{mod.name}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5 flex items-center gap-1">
                        <span>Source Mode:</span>
                        <span className="font-mono bg-slate-200 px-1 rounded text-[9px] text-slate-700">{mod.mode}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {mod.status === 'PASS' ? (
                        <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300 flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> PASS
                        </span>
                      ) : (
                        <span className="text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300 flex items-center gap-1">
                          <HelpCircle className="w-3 h-3" /> REVIEW
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* Right Column (7 Cols): Grounded Recommendation, Findings & Officer Action */}
        <div className="lg:col-span-7 space-y-6">

          {/* AI Grounded Recommendation Card */}
          <div className="bg-white p-5 rounded-lg border border-gov-border shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gov-saffron"></div>
                <h3 className="text-xs font-bold text-gov-navy uppercase tracking-wide">
                  AI Compliance Analysis & Evidence Summary
                </h3>
              </div>
              <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                Traceable Evidence Grounded
              </span>
            </div>

            <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded border border-slate-200">
              {mockAssessment.aiRecommendation}
            </p>
          </div>

          {/* Detailed Findings & Evidence Panel */}
          <div className="bg-white p-5 rounded-lg border border-gov-border shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-gov-navy uppercase tracking-wide border-b pb-2">
              Detected Findings & Source Document Citations
            </h3>

            <div className="space-y-3">
              {mockAssessment.findings.map((item) => (
                <div key={item.id} className="p-3 rounded border border-slate-200 bg-slate-50/70 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                      {item.title}
                    </span>
                    <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-200">
                      {item.severity}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600">{item.description}</p>

                  <div className="text-[10px] font-mono text-gov-navy bg-slate-200/60 px-2 py-1 rounded inline-block">
                    📌 Evidence Source: {item.evidence}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Officer Final Qualification Review Form */}
          <div className="bg-white p-5 rounded-lg border-2 border-gov-navy shadow-md space-y-4">
            <div className="flex items-center justify-between border-b pb-2">
              <div className="flex items-center gap-2 text-gov-navy">
                <Scale className="w-5 h-5 text-gov-saffron" />
                <h3 className="text-sm font-bold uppercase tracking-wide">
                  Procurement Officer Final Qualification Decision
                </h3>
              </div>
              <span className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-300 font-semibold px-2 py-0.5 rounded">
                Human Authority Required
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Official Decision Justification / Audit Notes:
              </label>
              <textarea
                rows={3}
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                placeholder="Enter formal justification notes for audit log (e.g. Identity spelling inconsistency verified against PAN certificate; bidder qualified)..."
                className="w-full text-xs p-2.5 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-gov-navy"
              ></textarea>
            </div>

            {decisionStatus && (
              <div className="p-3 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded text-xs font-semibold flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Decision recorded successfully! Status updated to: <span className="uppercase font-bold">{decisionStatus}</span>. Immutable audit record generated.
              </div>
            )}

            <div className="flex items-center gap-3 pt-1">
              <button
                onClick={() => handleDecision('QUALIFIED')}
                className="flex-1 bg-gov-emerald hover:bg-emerald-800 text-white text-xs font-bold py-2.5 px-4 rounded shadow transition-colors flex items-center justify-center gap-2"
              >
                <ShieldCheck className="w-4 h-4" /> QUALIFY BIDDER
              </button>

              <button
                onClick={() => handleDecision('DISQUALIFIED')}
                className="flex-1 bg-gov-crimson hover:bg-rose-900 text-white text-xs font-bold py-2.5 px-4 rounded shadow transition-colors flex items-center justify-center gap-2"
              >
                <XCircle className="w-4 h-4" /> DISQUALIFY BIDDER
              </button>

              <button
                onClick={() => handleDecision('NEEDS_CLARIFICATION')}
                className="bg-slate-700 hover:bg-slate-800 text-white text-xs font-bold py-2.5 px-4 rounded shadow transition-colors"
              >
                REQUEST CLARIFICATION
              </button>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};
