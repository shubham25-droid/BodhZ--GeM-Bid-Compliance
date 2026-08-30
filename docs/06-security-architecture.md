# BodhZ Security & Anti-Scraping Architecture Specifications

## 1. Security Overview
BodhZ is engineered specifically for government procurement officers. Security and data protection are integrated directly into the baseline architecture.

---

## 2. Security Controls & Protections

### A. Authentication & Role-Based Access Control (RBAC)
- **Password Protection**: Passwords hashed using `bcrypt` (work factor 12).
- **JWT Authorization**: Cryptographically signed JSON Web Tokens (HS256) with strict 8-hour expiration.
- **Roles**:
  - `PROCUREMENT_OFFICER`: Full evaluation, review, and qualification decision rights.
  - `AUDITOR`: Read-only access to audit logs, evidence, and decision history.
  - `ADMIN`: User management and connector configuration.

### B. Anti-Scraping & Bot Mitigation Architecture
- **Zero Unauthenticated Access**: 100% of business endpoints (`/api/v1/tenders`, `/api/v1/bids`, `/api/v1/verify`, `/api/v1/audit`) mandate a valid Bearer token. Public bots or unauthenticated requests are blocked at the middleware gateway layer.
- **Rate Limiting**: `SlowAPI` middleware limits request frequency by IP and user identity:
  - Standard API endpoints: 10 requests / second.
  - Document Upload / Processing: 5 requests / minute.
  - Auth Endpoints: 5 attempts / minute (preventing brute-force attacks).
- **Strict CORS Lock**: CORS middleware permits requests strictly from configured, trusted frontend domains (`http://localhost:3000` or government domain).

### C. Defense-in-Depth HTTP Security Headers
All API responses return mandatory security headers:
- `X-Frame-Options: DENY` (Prevents clickjacking attacks).
- `X-Content-Type-Options: nosniff` (Blocks MIME-type sniffing).
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Enforces HTTPS).
- `Content-Security-Policy: default-src 'self'` (Prevents unauthorized script injection).
- `X-XSS-Protection: 1; mode=block` (Mitigates Cross-Site Scripting).

### D. File Upload & Storage Security
- **Magic-Byte MIME Verification**: File uploads are inspected at the binary header level (`python-magic` / magic bytes check) to ensure actual PDF (`%PDF-`) or JPEG (`\xFF\xD8\xFF`) format, preventing file extension spoofing.
- **Path Traversal Shield**: File paths are sanitized using `os.path.basename` and assigned randomized UUID filenames stored outside the web root.
- **File Size Caps**: Upload size hard-capped at 25MB per document.

### E. Database Injection Protection
- All database queries executed exclusively via SQLAlchemy 2.0 ORM parameterized statements. Raw concatenated SQL strings are strictly prohibited.
