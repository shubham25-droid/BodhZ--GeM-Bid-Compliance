const API_BASE_URL = '/api/v1';

// --------------------------------------------------
// API CLIENT SERVICE FOR BODHZ PLATFORM
# --------------------------------------------------
export const apiService = {
  // Fetch platform health status
  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  // Fetch all active tenders
  async getTenders() {
    const res = await fetch(`${API_BASE_URL}/tenders`);
    if (!res.ok) throw new Error('Failed to fetch tenders');
    return res.json();
  },

  // Fetch submitted bids
  async getBids(tenderId?: string) {
    const url = tenderId ? `${API_BASE_URL}/bids?tender_id=${tenderId}` : `${API_BASE_URL}/bids`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch bids');
    return res.json();
  },

  // Run full evaluation on a bid
  async evaluateBid(bidId: string) {
    const res = await fetch(`${API_BASE_URL}/bids/${bidId}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error('Failed to run compliance evaluation');
    return res.json();
  },

  // Fetch dashboard assessment details
  async getAssessment(bidId: string) {
    const res = await fetch(`${API_BASE_URL}/bids/${bidId}/assessment`);
    if (!res.ok) throw new Error('Failed to fetch assessment');
    return res.json();
  },

  // Record Procurement Officer Decision
  async recordOfficerDecision(assessmentId: string, bidId: string, decision: string, notes: string) {
    const res = await fetch(`${API_BASE_URL}/bids/officer-decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        assessment_id: assessmentId,
        bid_id: bidId,
        decision,
        notes,
      }),
    });
    if (!res.ok) throw new Error('Failed to record officer decision');
    return res.json();
  },

  // Fetch audit trail timeline
  async getAuditTrail(bidId: string) {
    const res = await fetch(`${API_BASE_URL}/audit/${bidId}`);
    if (!res.ok) throw new Error('Failed to fetch audit trail');
    return res.json();
  },
};
