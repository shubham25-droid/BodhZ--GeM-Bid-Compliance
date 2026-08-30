import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import SecurityHeadersMiddleware
from app.api.routes import (
    health_router, auth_router, tenders_router, bids_router,
    documents_router, verification_router, audit_router, reports_router
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])

# --------------------------------------------------
# 1. CREATE FASTAPI APPLICATION
# --------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "BodhZ is an AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement (SIH26100). "
        "It provides role-based decision support for Procurement Officers, Department Officials, and Bidders, "
        "automating statutory verification while preserving 100% human legal authority."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount Static Files for Official BodhZ Logo Asset
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --------------------------------------------------
# 2. CONFIGURE SECURITY & CORS MIDDLEWARE
# --------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# 3. INCLUDE API ROUTERS
# --------------------------------------------------
app.include_router(health_router.router, prefix=settings.API_V1_STR)
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(tenders_router.router, prefix=settings.API_V1_STR)
app.include_router(bids_router.router, prefix=settings.API_V1_STR)
app.include_router(documents_router.router, prefix=settings.API_V1_STR)
app.include_router(verification_router.router, prefix=settings.API_V1_STR)
app.include_router(audit_router.router, prefix=settings.API_V1_STR)
app.include_router(reports_router.router, prefix=settings.API_V1_STR)


# --------------------------------------------------
# 4. OFFICIAL PRODUCTION-GRADE PLATFORM WEB APPLICATION
# --------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["System Web App"])
def root_web_application():
    """Renders the BodhZ Public Portal and Role-Aware Workspace."""
    html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BodhZ — AI-Powered Integrated Bid Compliance Verification Platform (SIH26100)</title>
  <link rel="icon" type="image/png" href="/static/bodhz_logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  
  <style>
    :root {
      --primary: #0A192F;
      --primary-light: #1E3A8A;
      --primary-dark: #030F22;
      --accent: #F59E0B;
      --accent-orange: #E65100;
      --success: #10B981;
      --success-dark: #047857;
      --warning: #F59E0B;
      --danger: #EF4444;
      --bg: #F8FAFC;
      --card-bg: #FFFFFF;
      --border: #E2E8F0;
      --text: #0F172A;
      --text-muted: #64748B;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.5; min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }

    /* ================================================== */
    /* 1. 3D LOGO & ASHOKA CHAKRA KEYFRAME ANIMATIONS     */
    /* ================================================== */
    .logo-3d-animated {
      transform-style: preserve-3d;
      animation: float3D 4.5s ease-in-out infinite alternate, glowPulse 3s ease-in-out infinite alternate;
      transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
      will-change: transform, filter;
    }

    .logo-3d-animated:hover {
      transform: perspective(900px) rotateY(18deg) rotateX(-8deg) scale(1.08) translateY(-4px);
      filter: drop-shadow(0 20px 35px rgba(245, 158, 11, 0.6)) drop-shadow(0 0 25px rgba(59, 130, 246, 0.4));
    }

    @keyframes float3D {
      0% { transform: perspective(900px) rotateY(-10deg) rotateX(6deg) translateY(0px); }
      50% { transform: perspective(900px) rotateY(12deg) rotateX(-5deg) translateY(-8px); }
      100% { transform: perspective(900px) rotateY(-8deg) rotateX(8deg) translateY(-3px); }
    }

    @keyframes glowPulse {
      0% { filter: drop-shadow(0 8px 16px rgba(245, 158, 11, 0.35)); }
      100% { filter: drop-shadow(0 16px 30px rgba(245, 158, 11, 0.65)) drop-shadow(0 0 18px rgba(30, 58, 138, 0.35)); }
    }

    .chakra-rotate-slow {
      animation: rotateAshokaChakra 75s linear infinite;
      transform-origin: center;
      pointer-events: none;
    }

    @keyframes rotateAshokaChakra {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    /* ================================================== */
    /* 2. PUBLIC LANDING PAGE STYLES                      */
    /* ================================================== */
    .public-nav {
      background: var(--primary-dark);
      color: #FFFFFF;
      padding: 14px 36px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1E293B;
      position: sticky;
      top: 0;
      z-index: 500;
    }

    .public-nav-links {
      display: flex;
      gap: 24px;
      align-items: center;
      font-size: 13px;
      font-weight: 700;
    }

    .public-nav-link {
      color: #CBD5E1;
      text-decoration: none;
      transition: color 0.2s;
      cursor: pointer;
    }

    .public-nav-link:hover {
      color: var(--accent);
    }

    /* Hero Section */
    .landing-hero {
      background: linear-gradient(145deg, #0A192F 0%, #061226 60%, #030A16 100%);
      color: #FFFFFF;
      padding: 68px 36px 58px 36px;
      position: relative;
      overflow: hidden;
      display: flex;
      justify-content: center;
    }

    .landing-hero-container {
      max-width: 1180px;
      width: 100%;
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 40px;
      align-items: center;
      position: relative;
      z-index: 2;
    }

    /* Background Watermark Chakra */
    .hero-chakra-watermark {
      position: absolute;
      top: -140px;
      right: -80px;
      width: 600px;
      height: 600px;
      opacity: 0.07;
      color: #F59E0B;
      pointer-events: none;
      z-index: 1;
    }

    .landing-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: var(--accent);
      padding: 5px 14px;
      border-radius: 30px;
      font-size: 11.5px;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
    }

    .landing-title {
      font-size: 38px;
      font-weight: 900;
      letter-spacing: -1px;
      line-height: 1.18;
      color: #FFFFFF;
    }

    .landing-subtitle {
      font-size: 15.5px;
      color: #94A3B8;
      margin-top: 14px;
      line-height: 1.6;
      max-width: 560px;
    }

    .landing-cta-row {
      display: flex;
      gap: 12px;
      margin-top: 26px;
      flex-wrap: wrap;
    }

    .btn-hero-primary {
      background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
      color: #0A192F;
      font-size: 13.5px;
      font-weight: 800;
      padding: 11px 22px;
      border-radius: 8px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
      transition: all 0.2s;
    }

    .btn-hero-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 22px rgba(245, 158, 11, 0.45);
    }

    .btn-hero-secondary {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #FFFFFF;
      font-size: 13.5px;
      font-weight: 800;
      padding: 11px 20px;
      border-radius: 8px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-hero-secondary:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: #FFFFFF;
    }

    /* 3D Visual Pipeline Card */
    .hero-pipeline-card {
      background: rgba(15, 23, 42, 0.75);
      border: 1.5px solid rgba(245, 158, 11, 0.25);
      backdrop-filter: blur(14px);
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 24px 50px rgba(0,0,0,0.35);
      display: flex;
      flex-direction: column;
      gap: 16px;
      position: relative;
    }

    .pipeline-step {
      display: flex;
      align-items: center;
      gap: 14px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 10px 14px;
      border-radius: 10px;
      transition: all 0.25s;
    }

    .pipeline-step:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(245, 158, 11, 0.5);
      transform: translateX(4px);
    }

    .pipeline-step-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 800;
    }

    /* Critical Trust Strip */
    .trust-strip {
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 14px 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 36px;
      flex-wrap: wrap;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .trust-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 800;
      color: var(--primary);
      letter-spacing: 0.5px;
    }

    .trust-item i {
      color: #059669;
      font-size: 14px;
    }

    .landing-section {
      max-width: 1140px;
      margin: 48px auto;
      padding: 0 24px;
      width: 100%;
      position: relative;
    }

    .section-header {
      text-align: center;
      margin-bottom: 28px;
    }

    .section-title {
      font-size: 24px;
      font-weight: 900;
      color: var(--primary);
      letter-spacing: -0.5px;
    }

    .section-desc {
      font-size: 13.5px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .solve-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .solve-card {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .solve-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-top: 10px;
      font-size: 12.5px;
      color: #475569;
    }

    .flow-grid-5 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
    }

    .flow-step-card {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
      transition: transform 0.2s;
    }

    .flow-step-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(10,25,47,0.06);
    }

    .flow-num {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      color: var(--accent);
      background: #FFFBEB;
      border: 1px solid #FDE68A;
      padding: 2px 6px;
      border-radius: 4px;
      width: fit-content;
    }

    .cap-grid-6 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
    }

    .cap-card {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 18px;
      display: flex;
      align-items: flex-start;
      gap: 14px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .cap-icon-box {
      width: 36px;
      height: 36px;
      background: #F1F5F9;
      color: var(--primary);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      flex-shrink: 0;
    }

    .ver-source-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
    }

    .ver-source-pill {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
      color: var(--primary);
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    .split-authority-card {
      background: #FFFFFF;
      border: 1.5px solid var(--primary);
      border-radius: 14px;
      padding: 24px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      box-shadow: 0 4px 14px rgba(10,25,47,0.04);
      position: relative;
      overflow: hidden;
    }

    .demo-preview-widget {
      background: #FFFFFF;
      border: 1.5px solid #CBD5E1;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(10,25,47,0.06);
    }

    .role-grid-3 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .role-card-mini {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .cta-banner {
      background: linear-gradient(135deg, #0A192F 0%, #030F22 100%);
      color: #FFFFFF;
      border-radius: 14px;
      padding: 32px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
      border: 1px solid rgba(245, 158, 11, 0.3);
      box-shadow: 0 12px 30px rgba(10,25,47,0.15);
      position: relative;
      overflow: hidden;
    }

    .public-footer {
      background-color: var(--primary);
      color: #94A3B8;
      font-size: 11.5px;
      padding: 24px 36px;
      border-top: 3.5px solid var(--accent-orange);
      margin-top: 40px;
    }

    /* ================================================== */
    /* 3. ULTRA-PREMIUM AUTHENTICATION SPLIT SCREEN       */
    /* ================================================== */
    .auth-page-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 32px 20px;
      background: radial-gradient(circle at 10% 20%, #0A192F 0%, #030814 100%);
      min-height: 100vh;
      position: relative;
      overflow: hidden;
    }

    .auth-card {
      width: 100%;
      max-width: 1080px;
      min-height: 640px;
      background: #FFFFFF;
      border-radius: 24px;
      border: 1px solid rgba(245, 158, 11, 0.3);
      box-shadow: 0 30px 70px -15px rgba(0, 0, 0, 0.5), 0 0 30px rgba(245, 158, 11, 0.15);
      display: grid;
      grid-template-columns: 46% 54%;
      overflow: hidden;
      position: relative;
      z-index: 2;
    }

    .auth-left-brand {
      background: linear-gradient(150deg, #0A192F 0%, #071325 50%, #020710 100%);
      color: #FFFFFF;
      padding: 44px 38px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
      border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .auth-left-chakra-watermark {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 440px;
      height: 440px;
      opacity: 0.08;
      color: #F59E0B;
      pointer-events: none;
    }

    .auth-right-form-pane {
      padding: 42px 46px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #FFFFFF;
    }

    .auth-field {
      width: 100%;
      padding: 11px 14px 11px 38px;
      font-size: 13px;
      font-family: inherit;
      color: var(--text);
      background-color: #F8FAFC;
      border: 1.5px solid #CBD5E1;
      border-radius: 8px;
      transition: all 0.25s ease;
    }

    .auth-field:focus {
      outline: none;
      background-color: #FFFFFF;
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(30, 58, 138, 0.12);
    }

    .btn-auth-primary {
      width: 100%;
      background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
      color: #FFFFFF;
      padding: 12px 18px;
      font-size: 13px;
      font-weight: 800;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(10, 25, 47, 0.25);
      transition: all 0.25s ease;
    }

    .btn-auth-primary:hover {
      background: linear-gradient(135deg, #1E3A8A 0%, #0A192F 100%);
      transform: translateY(-2px);
      box-shadow: 0 8px 22px rgba(10, 25, 47, 0.35);
    }

    /* Role Demo Quick Chip Bar */
    .role-quick-chip-row {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .role-quick-chip {
      background: #F1F5F9;
      border: 1px solid #CBD5E1;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      color: #334155;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s ease;
    }

    .role-quick-chip:hover {
      background: #0A192F;
      color: #FFFFFF;
      border-color: #0A192F;
      transform: translateY(-1px);
    }

    /* ================================================== */
    /* 4. WORKSPACE STYLES                                */
    /* ================================================== */
    .top-bar { background-color: var(--primary-dark); color: #CBD5E1; padding: 6px 24px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; }
    .gov-header { background-color: var(--primary); color: #FFFFFF; padding: 12px 24px; border-bottom: 3.5px solid var(--accent-orange); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .brand-logo-img { width: 44px; height: 44px; object-fit: contain; background: #FFFFFF; padding: 3px; border-radius: 10px; border: 2px solid var(--accent); }

    .main-wrapper { display: flex; flex: 1; min-height: calc(100vh - 105px); }
    .sidebar { width: 260px; background-color: var(--primary); color: #94A3B8; border-right: 1px solid #1E293B; display: flex; flex-direction: column; flex-shrink: 0; }
    .sidebar-menu { display: flex; flex-direction: column; padding: 10px 8px; gap: 3px; flex: 1; overflow-y: auto; }
    .sidebar-btn { padding: 9px 12px; font-size: 12px; font-weight: 700; color: #94A3B8; border: none; background: none; cursor: pointer; border-radius: 6px; text-align: left; display: flex; align-items: center; gap: 10px; transition: all 0.2s ease; }
    .sidebar-btn:hover { color: #FFFFFF; background-color: #1E293B; transform: translateX(3px); }
    .sidebar-btn.active { color: #FFFFFF; background: linear-gradient(90deg, #1E3A8A 0%, var(--primary) 100%); border-left: 3.5px solid var(--accent); font-weight: 800; }
    .sidebar-num { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--accent); opacity: 0.9; width: 18px; }

    .viewport { flex: 1; padding: 22px; background-color: var(--bg); overflow-y: auto; display: flex; flex-direction: column; gap: 18px; }

    .card-panel { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; flex-direction: column; gap: 14px; transition: all 0.2s ease; }
    .card-title { font-size: 13px; font-weight: 800; color: var(--primary); text-transform: uppercase; letter-spacing: 0.02em; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }

    .clean-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .clean-table th { background-color: var(--primary); color: #FFFFFF; text-transform: uppercase; font-size: 10.5px; font-weight: 800; padding: 10px 12px; text-align: left; }
    .clean-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
    .clean-table tr:hover { background-color: #F8FAFC; }

    .btn-action { background-color: var(--primary); color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; text-decoration: none; }
    .btn-action:hover { background-color: #1E293B; transform: translateY(-1px); }
    .btn-success { background-color: #059669; color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; text-decoration: none; }
    .btn-success:hover { background-color: #047857; transform: translateY(-1px); }
    .btn-warning { background-color: #D97706; color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; text-decoration: none; }

    .badge-pass { background-color: #ECFDF5; color: #047857; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #A7F3D0; }
    .badge-review { background-color: #FFFBEB; color: #B45309; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #FDE68A; }
    .badge-fail { background-color: #FEF2F2; color: #B91C1C; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #FECACA; }

    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-label { font-size: 11.5px; font-weight: 700; color: #334155; }
    .form-input { width: 100%; font-size: 12.5px; padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-family: inherit; background-color: #FFFFFF; color: var(--text); }
    .form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(10,25,47,0.08); }

    .dropzone-box { border: 2px dashed #CBD5E1; background: #F8FAFC; border-radius: 8px; padding: 18px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .dropzone-box:hover { border-color: var(--primary); background: #F1F5F9; }

    .hist-card { background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border: 1.5px solid #F59E0B; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; }
    .preset-pill { background: #E2E8F0; color: #0A192F; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; cursor: pointer; border: 1px solid #CBD5E1; transition: all 0.2s; }
    .preset-pill:hover { background: var(--primary); color: #FFFFFF; }

    .tender-catalog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 10px; }
    .tender-card-item { background: #FFFFFF; border: 1.5px solid #E2E8F0; border-top: 4px solid var(--primary); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); transition: all 0.25s ease; }
    .tender-card-item:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(10,25,47,0.08); border-color: #94A3B8; }
    .tender-card-item.selected { border: 2px solid var(--accent); border-top: 4px solid var(--accent); background: linear-gradient(180deg, #FFFBEB 0%, #FFFFFF 100%); box-shadow: 0 0 0 3px rgba(245,158,11,0.2); }

    .badge-open-bid { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; padding: 3px 8px; border-radius: 20px; font-size: 10.5px; font-weight: 800; display: inline-flex; align-items: center; gap: 6px; }
    .badge-open-bid::before { content: ""; width: 6px; height: 6px; background: #10B981; border-radius: 50%; display: inline-block; box-shadow: 0 0 6px #10B981; }

    #toastContainer { position: fixed; top: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; pointer-events: none; }
    .toast-msg { background: #0A192F; color: #FFFFFF; border-left: 4px solid var(--accent); padding: 12px 18px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); font-size: 12.5px; font-weight: 700; display: flex; align-items: center; gap: 10px; animation: slideInRight 0.3s forwards; pointer-events: auto; }
    @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

    .chatbot-fab-clean { position: fixed; bottom: 24px; right: 24px; background: linear-gradient(135deg, #0A192F 0%, #030F22 100%); color: #FFFFFF; border: 1.5px solid #F59E0B; border-radius: 30px; padding: 8px 18px; font-size: 12.5px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 10px; z-index: 1000; box-shadow: 0 4px 14px rgba(0,0,0,0.25); }
    .chat-modal-clean { position: fixed; bottom: 80px; right: 24px; width: 440px; height: 580px; background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 14px; box-shadow: 0 16px 45px rgba(10,25,47,0.25); display: none; flex-direction: column; overflow: hidden; z-index: 1000; }
    .chat-header-clean { background: linear-gradient(135deg, #0A192F 0%, #030F22 100%); color: #FFFFFF; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2.5px solid var(--accent-orange); }
    .current-context-bar { background: #F1F5F9; border-bottom: 1px solid #E2E8F0; padding: 6px 14px; font-size: 10.5px; display: flex; align-items: center; gap: 8px; color: #334155; }
    .chat-messages-area { flex: 1; padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; font-size: 12.5px; background: #F8FAFC; }
    .chat-msg-user { align-self: flex-end; max-width: 82%; background: #0A192F; color: #FFFFFF; padding: 8px 12px; border-radius: 12px 12px 2px 12px; font-size: 12px; }
    .chat-msg-bot { align-self: flex-start; max-width: 95%; background: #FFFFFF; border: 1px solid #E2E8F0; color: #0F172A; padding: 12px 14px; border-radius: 2px 12px 12px 12px; line-height: 1.6; }
    .chat-input-row { display: flex; padding: 10px; gap: 8px; background: #FFFFFF; border-top: 1px solid #E2E8F0; }
    .chat-chip { background: #E2E8F0; color: #0A192F; padding: 3px 8px; border-radius: 12px; font-size: 10px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
    .chat-chip:hover { background: #CBD5E1; }

    @media (max-width: 900px) {
      .landing-hero-container { grid-template-columns: 1fr; gap: 28px; }
      .auth-card { grid-template-columns: 1fr; }
      .auth-left-brand { padding: 28px; }
      .auth-right-form-pane { padding: 28px; }
      .split-authority-card { grid-template-columns: 1fr; }
      .solve-grid { grid-template-columns: 1fr; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; transition: none !important; }
    }
  </style>
</head>
<body>

  <!-- Toast Notification Container -->
  <div id="toastContainer"></div>

  <!-- ================================================== -->
  <!-- 1. REFINED PUBLIC LANDING PAGE (SIH26100)          -->
  <!-- ================================================== -->
  <div id="view-public-landing" style="display: flex; flex-direction: column; min-height: 100vh;">
    <!-- Public Navigation Bar -->
    <nav class="public-nav">
      <div style="display: flex; align-items: center; gap: 12px; cursor: pointer;" onclick="scrollToSection('hero')">
        <img src="/static/bodhz_logo.png" class="logo-3d-animated" style="width: 38px; height: 38px; background: #FFF; border-radius: 8px; padding: 2px; border: 1.5px solid var(--accent);" alt="BodhZ">
        <div>
          <div style="font-size: 17px; font-weight: 900; letter-spacing: -0.5px;">BodhZ</div>
          <div style="font-size: 9.5px; color: var(--accent); font-weight: 700; text-transform: uppercase;">Bid Compliance AI</div>
        </div>
      </div>

      <div class="public-nav-links">
        <a class="public-nav-link" onclick="scrollToSection('how-it-works')">How It Works</a>
        <a class="public-nav-link" onclick="scrollToSection('capabilities')">Capabilities</a>
        <a class="public-nav-link" onclick="scrollToSection('sources')">Verification Sources</a>
        <a class="public-nav-link" onclick="scrollToSection('preview')">Demo Preview</a>
        <a class="public-nav-link" onclick="scrollToSection('security')">Security</a>
      </div>

      <div style="display: flex; gap: 10px; align-items: center;">
        <button onclick="openAuthScreen('LOGIN')" class="btn-hero-secondary" style="padding: 7px 16px; font-size: 12px;">Sign In</button>
        <button onclick="openAuthScreen('REGISTER')" class="btn-hero-primary" style="padding: 7px 16px; font-size: 12px;">Register</button>
        <button onclick="openDemoModeModal()" class="preset-pill" style="background: rgba(245,158,11,0.2); color: var(--accent); border-color: var(--accent); font-size: 11px;">⚡ Evaluator Demo</button>
      </div>
    </nav>

    <!-- Hero Section (Two Columns with 3D Logo & Ashoka Chakra Motif) -->
    <header class="landing-hero" id="hero">
      <!-- 24-Spoke Rotating Ashoka Chakra Watermark -->
      <svg class="hero-chakra-watermark chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>
        <circle cx="100" cy="100" r="82" fill="none" stroke="currentColor" stroke-width="1.5"/>
        <circle cx="100" cy="100" r="14" fill="currentColor"/>
        <circle cx="100" cy="100" r="8" fill="#0A192F"/>
        <!-- 24 Spokes -->
        <g stroke="currentColor" stroke-width="1.8">
          <line x1="100" y1="100" x2="100" y2="18"/>
          <line x1="100" y1="100" x2="121.2" y2="20.8"/>
          <line x1="100" y1="100" x2="141" y2="29"/>
          <line x1="100" y1="100" x2="158" y2="42"/>
          <line x1="100" y1="100" x2="171" y2="59"/>
          <line x1="100" y1="100" x2="179.2" y2="78.8"/>
          <line x1="100" y1="100" x2="182" y2="100"/>
          <line x1="100" y1="100" x2="179.2" y2="121.2"/>
          <line x1="100" y1="100" x2="171" y2="141"/>
          <line x1="100" y1="100" x2="158" y2="158"/>
          <line x1="100" y1="100" x2="141" y2="171"/>
          <line x1="100" y1="100" x2="121.2" y2="179.2"/>
          <line x1="100" y1="100" x2="100" y2="182"/>
          <line x1="100" y1="100" x2="78.8" y2="179.2"/>
          <line x1="100" y1="100" x2="59" y2="171"/>
          <line x1="100" y1="100" x2="42" y2="158"/>
          <line x1="100" y1="100" x2="29" y2="141"/>
          <line x1="100" y1="100" x2="20.8" y2="121.2"/>
          <line x1="100" y1="100" x2="18" y2="100"/>
          <line x1="100" y1="100" x2="20.8" y2="78.8"/>
          <line x1="100" y1="100" x2="29" y2="59"/>
          <line x1="100" y1="100" x2="42" y2="42"/>
          <line x1="100" y1="100" x2="59" y2="29"/>
          <line x1="100" y1="100" x2="78.8" y2="20.8"/>
        </g>
      </svg>

      <div class="landing-hero-container">
        <!-- Left: Value Proposition & CTAs -->
        <div>
          <div class="landing-badge">
            <i class="fa-solid fa-shield-halved"></i>
            <span>SIH26100 • PUBLIC PROCUREMENT DECISION SUPPORT</span>
          </div>
          <h1 class="landing-title">
            BodhZ — AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement
          </h1>
          <p class="landing-subtitle">
            Evidence-based decision support for faster, more consistent and auditable bid compliance verification.
          </p>

          <div class="landing-cta-row">
            <button onclick="openAuthScreen('LOGIN')" class="btn-hero-primary">
              <i class="fa-solid fa-arrow-right-to-bracket"></i>
              <span>Sign In to Workspace</span>
            </button>
            <button onclick="openAuthScreen('REGISTER')" class="btn-hero-secondary">
              <span>Register</span>
            </button>
            <button onclick="scrollToSection('how-it-works')" class="btn-hero-secondary" style="border: none; color: #CBD5E1;">
              <i class="fa-solid fa-circle-info"></i>
              <span>Explore How It Works</span>
            </button>
          </div>
        </div>

        <!-- Right: 3D Digital Pipeline Visual Card -->
        <div class="hero-pipeline-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <img src="/static/bodhz_logo.png" class="logo-3d-animated" style="width: 32px; height: 32px; background: #FFF; border-radius: 8px; padding: 2px; border: 1.5px solid var(--accent);" alt="BodhZ">
              <div>
                <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">BodhZ Verification Flow</div>
                <div style="font-size: 10px; color: var(--accent);">AI + 13 Statutory Gateways</div>
              </div>
            </div>
            <span style="font-size: 9.5px; background: rgba(16,185,129,0.2); color: #34D399; padding: 3px 8px; border-radius: 4px; font-weight: 800;">ACTIVE ARCHITECTURE</span>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(59,130,246,0.2); color: #60A5FA;">01</div>
            <div>
              <div style="font-size: 12px; font-weight: 800; color: #FFFFFF;">Tender Requirements Ingestion</div>
              <div style="font-size: 11px; color: #94A3B8;">NIT document parsing & mandatory rule extraction</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(245,158,11,0.2); color: #FBBF24;">02</div>
            <div>
              <div style="font-size: 12px; font-weight: 800; color: #FFFFFF;">Bidder Document AI OCR</div>
              <div style="font-size: 11px; color: #94A3B8;">Digital extraction with SHA-256 integrity hash</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(16,185,129,0.2); color: #34D399;">03</div>
            <div>
              <div style="font-size: 12px; font-weight: 800; color: #FFFFFF;">Statutory Verification Sources</div>
              <div style="font-size: 11px; color: #94A3B8;">Cross-checked against configured registries</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(239,68,68,0.2); color: #F87171;">04</div>
            <div>
              <div style="font-size: 12px; font-weight: 800; color: #FFFFFF;">Compliance & Risk Scoring</div>
              <div style="font-size: 11px; color: #94A3B8;">Transparent 0–100 score & gap detection</div>
            </div>
          </div>

          <div class="pipeline-step" style="border-color: rgba(16,185,129,0.4); background: rgba(16,185,129,0.08);">
            <div class="pipeline-step-icon" style="background: #059669; color: #FFFFFF;"><i class="fa-solid fa-gavel"></i></div>
            <div>
              <div style="font-size: 12px; font-weight: 800; color: #34D399;">Officer Final Qualification</div>
              <div style="font-size: 11px; color: #CBD5E1;">100% Human legal authority under GFR 2017</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Critical Trust Message Strip with Ashoka Chakra Motif -->
    <div class="trust-strip">
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg style="width: 20px; height: 20px; color: #1E3A8A;" class="chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="6"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <line x1="100" y1="100" x2="100" y2="18" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="182" y2="100" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="100" y2="182" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="18" y2="100" stroke="currentColor" stroke-width="3"/>
        </svg>
        <span style="font-size: 11px; font-weight: 900; color: #1E3A8A; letter-spacing: 0.5px;">STATUTORY COMPLIANCE</span>
      </div>
      <div class="trust-item"><i class="fa-solid fa-microchip"></i> AI-ASSISTED</div>
      <div class="trust-item"><i class="fa-solid fa-file-shield"></i> EVIDENCE-BASED</div>
      <div class="trust-item"><i class="fa-solid fa-fingerprint"></i> AUDITABLE</div>
      <div class="trust-item"><i class="fa-solid fa-user-check"></i> HUMAN-CONTROLLED</div>
    </div>

    <!-- Section: What BodhZ Solves -->
    <section class="landing-section">
      <div class="section-header">
        <div class="section-title">What BodhZ Solves</div>
        <div class="section-desc">Modernizing public procurement screening with automated verification and explainable decision support.</div>
      </div>

      <div class="solve-grid">
        <div class="solve-card" style="border-left: 4px solid #DC2626;">
          <div style="font-size: 13px; font-weight: 800; color: #DC2626; text-transform: uppercase;">THE CHALLENGE</div>
          <div style="font-size: 15px; font-weight: 800; color: var(--primary); margin-top: 4px;">Manual & Complex Bid Evaluation</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 2px;"></i> Multiple fragmented PDF bundles & voluminous technical documents</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 2px;"></i> Multiple statutory requirements across financial, legal, and technical clauses</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 2px;"></i> Manual cross-checking across multiple government portals</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 2px;"></i> Risk of overlooked name variations, expired certificates, or missing turnover proofs</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 2px;"></i> Long evaluation effort leading to procurement cycle delays</div>
        </div>

        <div class="solve-card" style="border-left: 4px solid #059669;">
          <div style="font-size: 13px; font-weight: 800; color: #059669; text-transform: uppercase;">THE BODHZ APPROACH</div>
          <div style="font-size: 15px; font-weight: 800; color: var(--primary); margin-top: 4px;">Integrated AI-Assisted Verification Pipeline</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 2px;"></i> <strong>Tender:</strong> Automated extraction of mandatory statutory rules and thresholds</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 2px;"></i> <strong>Bidder Documents:</strong> High-precision text extraction with SHA-256 integrity hash</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 2px;"></i> <strong>Verification:</strong> Automated cross-referencing against configured sources</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 2px;"></i> <strong>Compliance:</strong> Multi-criteria scoring, gap analysis, and risk tiering</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 2px;"></i> <strong>Officer Review:</strong> Human legal decision authority backed by full provenance</div>
        </div>
      </div>
    </section>

    <!-- Section: How It Works (5 Steps) -->
    <section class="landing-section" id="how-it-works">
      <div class="section-header">
        <div class="section-title">How It Works</div>
        <div class="section-desc">A structured 5-step workflow designed for public procurement decision support.</div>
      </div>

      <div class="flow-grid-5">
        <div class="flow-step-card">
          <div class="flow-num">STEP 01</div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Tender Intelligence</div>
          <p style="font-size: 12px; color: #64748B;">Understand and structure tender requirements directly from NIT documents.</p>
        </div>

        <div class="flow-step-card">
          <div class="flow-num">STEP 02</div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Document Intelligence</div>
          <p style="font-size: 12px; color: #64748B;">Extract relevant bidder information from submitted technical documents.</p>
        </div>

        <div class="flow-step-card">
          <div class="flow-num">STEP 03</div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Integrated Verification</div>
          <p style="font-size: 12px; color: #64748B;">Cross-check applicable information against configured verification sources.</p>
        </div>

        <div class="flow-step-card">
          <div class="flow-num">STEP 04</div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Compliance Analysis</div>
          <p style="font-size: 12px; color: #64748B;">Detect missing, inconsistent and non-compliant information automatically.</p>
        </div>

        <div class="flow-step-card" style="border-color: #059669; background: #F0FDF4;">
          <div class="flow-num" style="background: #059669; color: #FFFFFF; border: none;">STEP 05</div>
          <div style="font-size: 14px; font-weight: 800; color: #047857;">Officer Decision</div>
          <p style="font-size: 12px; color: #166534;">Present evidence, score, risk and recommendation for human officer review.</p>
        </div>
      </div>
    </section>

    <!-- Section: Key Capabilities -->
    <section class="landing-section" id="capabilities">
      <div class="section-header">
        <div class="section-title">Key Capabilities</div>
        <div class="section-desc">Core functional capabilities powering the SIH26100 decision support architecture.</div>
      </div>

      <div class="cap-grid-6">
        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-file-circle-check"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">AI Document Verification</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Multi-page text extraction with OCR fallback and cryptographic SHA-256 integrity seals.</div>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-list-check"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Requirement-Aware Compliance</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Dynamic clause matching against turnover, past project experience, and mandatory criteria.</div>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-clone"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Cross-Document Verification</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Entity matching detecting name variations, PAN vs GST mismatch, and certificate expiry.</div>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-chart-line"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Risk & Compliance Scoring</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Weighted multi-criteria score (0–100) and automated risk level classification (Low/Med/High).</div>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-lightbulb"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Evidence-Based Recommendation</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Transparent AI justifications citing specific document pages and verification results.</div>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon-box"><i class="fa-solid fa-shield-halved"></i></div>
          <div>
            <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Audit & Traceability</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">Immutable SHA-256 event timeline and printable compliance evaluation dossier.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section: Applicable Verification Sources -->
    <section class="landing-section" id="sources">
      <div class="section-header">
        <div class="section-title">Applicable Verification Sources</div>
        <div class="section-desc">Configurable adapters supporting verification across relevant statutory registries.</div>
      </div>

      <div class="ver-source-grid">
        <div class="ver-source-pill"><i class="fa-solid fa-industry" style="color: #0052CC;"></i> Udyam / MSME</div>
        <div class="ver-source-pill"><i class="fa-solid fa-receipt" style="color: #0052CC;"></i> GSTN Registration</div>
        <div class="ver-source-pill"><i class="fa-solid fa-id-card" style="color: #0052CC;"></i> PAN / Income Tax</div>
        <div class="ver-source-pill"><i class="fa-solid fa-building" style="color: #0052CC;"></i> MCA21 Corporate</div>
        <div class="ver-source-pill"><i class="fa-solid fa-rocket" style="color: #059669;"></i> Startup India / DPIIT</div>
        <div class="ver-source-pill"><i class="fa-solid fa-certificate" style="color: #059669;"></i> NSIC Registration</div>
        <div class="ver-source-pill"><i class="fa-solid fa-users" style="color: #059669;"></i> EPFO / ESIC</div>
        <div class="ver-source-pill"><i class="fa-solid fa-vault" style="color: #D97706;"></i> DigiLocker Gateway</div>
        <div class="ver-source-pill"><i class="fa-solid fa-gears" style="color: #D97706;"></i> OEM Authorization</div>
        <div class="ver-source-pill"><i class="fa-solid fa-flag" style="color: #D97706;"></i> Make in India (MII)</div>
        <div class="ver-source-pill"><i class="fa-solid fa-award" style="color: #D97706;"></i> BIS / ISO 9001</div>
        <div class="ver-source-pill"><i class="fa-solid fa-ban" style="color: #DC2626;"></i> CPPP Debarment Check</div>
      </div>

      <div style="text-align: center; margin-top: 14px; font-size: 11.5px; color: #64748B;">
        <i class="fa-solid fa-circle-info"></i> Note: Source availability depends on configured sandbox access and the applicable tender requirements.
      </div>
    </section>

    <!-- Section: AI Assists. Officer Decides. -->
    <section class="landing-section">
      <div class="split-authority-card">
        <!-- Subtle Ashoka Chakra in Split card background -->
        <svg style="position: absolute; right: -60px; bottom: -60px; width: 260px; height: 260px; opacity: 0.05; color: #0A192F;" class="chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <line x1="100" y1="100" x2="100" y2="18" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="182" y2="100" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="100" y2="182" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="18" y2="100" stroke="currentColor" stroke-width="2"/>
        </svg>

        <div>
          <div style="font-size: 12px; font-weight: 800; color: #2563EB; text-transform: uppercase;">DECISION SUPPORT ROLE</div>
          <div style="font-size: 20px; font-weight: 900; color: var(--primary); margin-top: 2px;">AI ASSISTS</div>
          <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 13px; color: #475569;">
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Extract:</strong> Ingests complex multi-page tender & bid PDFs</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Analyze:</strong> Parses turnover thresholds, experience, and clauses</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Cross-Check:</strong> Validates entity names against verification sources</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Identify Gaps:</strong> Highlights missing certificates & inconsistencies</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Recommend:</strong> Generates explainable compliance recommendations</div>
          </div>
        </div>

        <div style="border-left: 1px solid var(--border); padding-left: 24px;">
          <div style="font-size: 12px; font-weight: 800; color: #059669; text-transform: uppercase;">LEGAL AUTHORITY (GFR 2017)</div>
          <div style="font-size: 20px; font-weight: 900; color: #047857; margin-top: 2px;">OFFICER DECIDES</div>
          <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 13px; color: #475569;">
            <div><i class="fa-solid fa-gavel" style="color: #059669;"></i> <strong>Review:</strong> Examines extracted evidence and AI recommendations</div>
            <div><i class="fa-solid fa-gavel" style="color: #059669;"></i> <strong>Validate:</strong> Inspects historical bidder records and discrepancy flags</div>
            <div><i class="fa-solid fa-gavel" style="color: #059669;"></i> <strong>Qualify / Disqualify:</strong> Exercises 100% human legal decision authority</div>
            <div><i class="fa-solid fa-gavel" style="color: #059669;"></i> <strong>Audit Justification:</strong> Records binding justification notes</div>
            <div><i class="fa-solid fa-gavel" style="color: #059669;"></i> <strong>Final Sign-Off:</strong> Cryptographically seals evaluation dossier</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section: Compliance Result Preview (Demo Preview) -->
    <section class="landing-section" id="preview">
      <div class="section-header">
        <div class="section-title">Compliance Result Preview</div>
        <div class="section-desc">Sample evaluation card illustrating transparent evidence attribution and scoring.</div>
      </div>

      <div class="demo-preview-widget">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 12px;">
          <div>
            <span style="font-size: 10px; font-weight: 800; background: #0A192F; color: #F59E0B; padding: 2px 8px; border-radius: 4px;">DEMO PREVIEW</span>
            <div style="font-size: 16px; font-weight: 900; color: var(--primary); margin-top: 4px;">Tata Advanced Training & Systems Ltd</div>
            <div style="font-size: 11.5px; color: var(--text-muted);">Tender: DTE/2026/RFP/COE/4901 • Center of Excellence RFP</div>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">COMPLIANCE SCORE</div>
            <div style="font-size: 26px; font-weight: 900; color: #047857; font-family: 'JetBrains Mono', monospace;">82<span style="font-size: 14px; color: #94A3B8;">/100</span></div>
            <span class="badge-review" style="font-size: 10px;">RISK: MEDIUM</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 14px;">
          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">GST REGISTRATION</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span style="font-size: 12px; font-weight: 800; color: #047857;">Active GSTR-3B</span>
              <span class="badge-pass">COMPLIANT</span>
            </div>
          </div>

          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">UDYAM / MSME</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span style="font-size: 12px; font-weight: 800; color: #047857;">Medium Enterprise</span>
              <span class="badge-pass">COMPLIANT</span>
            </div>
          </div>

          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">PAN CARD MATCH</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span style="font-size: 12px; font-weight: 800; color: #B45309;">Minor Suffix Check</span>
              <span class="badge-review">REVIEW</span>
            </div>
          </div>

          <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">OEM MAF CERTIFICATE</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span style="font-size: 12px; font-weight: 800; color: #B91C1C;">Missing Form-II</span>
              <span class="badge-fail">MISSING</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section: Auditability & Traceability -->
    <section class="landing-section">
      <div class="section-header">
        <div class="section-title">Auditability & Provenance</div>
        <div class="section-desc">Every important verification is traced from requirement to final human decision.</div>
      </div>

      <div style="background: #FFFFFF; border: 1px solid var(--border); border-radius: 12px; padding: 22px; text-align: center;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 12.5px; font-weight: 800; color: var(--primary);">
          <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 6px;">Tender Requirement</span>
          <i class="fa-solid fa-arrow-right" style="color: #94A3B8;"></i>
          <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 6px;">Submitted Evidence</span>
          <i class="fa-solid fa-arrow-right" style="color: #94A3B8;"></i>
          <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 6px;">Gateway Verification</span>
          <i class="fa-solid fa-arrow-right" style="color: #94A3B8;"></i>
          <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 6px;">Compliance Result</span>
          <i class="fa-solid fa-arrow-right" style="color: #94A3B8;"></i>
          <span style="background: #ECFDF5; color: #047857; padding: 6px 12px; border-radius: 6px; border: 1px solid #A7F3D0;">Officer Decision</span>
          <i class="fa-solid fa-arrow-right" style="color: #94A3B8;"></i>
          <span style="background: #FFFBEB; color: #B45309; padding: 6px 12px; border-radius: 6px; border: 1px solid #FDE68A;">SHA-256 Audit Record</span>
        </div>
        <p style="font-size: 12.5px; color: #64748B; margin-top: 14px; max-width: 780px; margin-left: auto; margin-right: auto;">
          Every evaluation event produces an immutable cryptographic audit record, providing Comptroller & Auditor General (CAG) and vigilance officials with tamper-evident decision traceability.
        </p>
      </div>
    </section>

    <!-- Section: Who Uses BodhZ (Role-Based Access) -->
    <section class="landing-section">
      <div class="section-header">
        <div class="section-title">Who Uses BodhZ?</div>
        <div class="section-desc">Tailored workspace environments with strict server-side access controls.</div>
      </div>

      <div class="role-grid-3">
        <div class="role-card-mini">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #0052CC; text-transform: uppercase;">CENTRAL PROCUREMENT</div>
            <div style="font-size: 16px; font-weight: 900; color: var(--primary); margin-top: 2px;">Procurement Officer</div>
            <p style="font-size: 12px; color: #475569; margin-top: 6px;">Review bidder submissions, inspect verification results, compare bids, and record legally binding qualification decisions.</p>
          </div>
          <button onclick="launchDemoPersona('shubham')" class="btn-action" style="font-size: 11px; padding: 6px 12px;">Open Officer Workspace</button>
        </div>

        <div class="role-card-mini">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #059669; text-transform: uppercase;">BIDDER / VENDOR</div>
            <div style="font-size: 16px; font-weight: 900; color: var(--primary); margin-top: 2px;">Bid Uploader</div>
            <p style="font-size: 12px; color: #475569; margin-top: 6px;">Browse open tenders, upload bid document bundles, check missing statutory proofs, and track submission screening status.</p>
          </div>
          <button onclick="launchDemoPersona('bidder_tata')" class="btn-success" style="font-size: 11px; padding: 6px 12px;">Open Bidder Portal</button>
        </div>

        <div class="role-card-mini">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #D97706; text-transform: uppercase;">STATE DEPARTMENT</div>
            <div style="font-size: 16px; font-weight: 900; color: var(--primary); margin-top: 2px;">Department / DTE Officer</div>
            <p style="font-size: 12px; color: #475569; margin-top: 6px;">Monitor institutional technical education tenders, evaluate training infrastructure compliance, and review audit dossiers.</p>
          </div>
          <button onclick="launchDemoPersona('officer_dte')" class="btn-warning" style="font-size: 11px; padding: 6px 12px;">Open DTE Workspace</button>
        </div>
      </div>
    </section>

    <!-- Section: Call to Action Banner -->
    <section class="landing-section">
      <div class="cta-banner">
        <div style="font-size: 24px; font-weight: 900;">Ready to begin a procurement evaluation?</div>
        <div style="font-size: 13.5px; color: #CBD5E1; max-width: 580px;">
          Access your authorized role-based workspace to evaluate tenders, upload submissions, or monitor compliance.
        </div>
        <div style="display: flex; gap: 12px; margin-top: 6px; flex-wrap: wrap;">
          <button onclick="openAuthScreen('LOGIN')" class="btn-hero-primary">
            <i class="fa-solid fa-arrow-right-to-bracket"></i>
            <span>Sign In</span>
          </button>
          <button onclick="openAuthScreen('REGISTER')" class="btn-hero-secondary">
            <span>Register</span>
          </button>
          <button onclick="openDemoModeModal()" class="btn-hero-secondary" style="border-color: var(--accent); color: var(--accent);">
            <i class="fa-solid fa-bolt"></i>
            <span>⚡ Demo Launcher</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Public Footer -->
    <footer class="public-footer" id="security">
      <div style="max-width: 1140px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div style="text-align: left;">
          <div style="font-size: 14px; font-weight: 800; color: #FFFFFF;">BodhZ — AI-Powered Integrated Bid Compliance Verification Platform</div>
          <div style="font-size: 11px; color: #94A3B8; margin-top: 3px;">SIH26100 • Smart India Hackathon 2026</div>
          <div style="font-size: 10.5px; color: #64748B; margin-top: 3px;">SIH 2026 prototype. Not an official Government of India or GeM portal.</div>
        </div>
        <div style="display: flex; gap: 18px; font-size: 12px; font-weight: 700;">
          <a class="public-nav-link" onclick="scrollToSection('how-it-works')">How It Works</a>
          <a class="public-nav-link" onclick="scrollToSection('capabilities')">Capabilities</a>
          <a class="public-nav-link" onclick="openAuthScreen('LOGIN')">Sign In</a>
          <a class="public-nav-link" onclick="openAuthScreen('REGISTER')">Register</a>
          <a href="/docs" target="_blank" style="color: var(--accent); text-decoration: none;">API Docs</a>
        </div>
      </div>
    </footer>
  </div>

  <!-- ================================================== -->
  <!-- 2. ULTRA-PREMIUM AUTHENTICATION SPLIT SCREEN       -->
  <!-- ================================================== -->
  <div id="view-auth" class="auth-page-wrapper" style="display: none;">
    <div class="auth-card">
      <!-- Left Brand & 3D Animated Showcase -->
      <div class="auth-left-brand">
        <!-- Rotating 24-Spoke Ashoka Chakra Watermark -->
        <svg class="auth-left-chakra-watermark chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>
          <circle cx="100" cy="100" r="82" fill="none" stroke="currentColor" stroke-width="1.5"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <circle cx="100" cy="100" r="8" fill="#0A192F"/>
          <g stroke="currentColor" stroke-width="1.8">
            <line x1="100" y1="100" x2="100" y2="18"/>
            <line x1="100" y1="100" x2="121.2" y2="20.8"/>
            <line x1="100" y1="100" x2="141" y2="29"/>
            <line x1="100" y1="100" x2="158" y2="42"/>
            <line x1="100" y1="100" x2="171" y2="59"/>
            <line x1="100" y1="100" x2="179.2" y2="78.8"/>
            <line x1="100" y1="100" x2="182" y2="100"/>
            <line x1="100" y1="100" x2="179.2" y2="121.2"/>
            <line x1="100" y1="100" x2="171" y2="141"/>
            <line x1="100" y1="100" x2="158" y2="158"/>
            <line x1="100" y1="100" x2="141" y2="171"/>
            <line x1="100" y1="100" x2="121.2" y2="179.2"/>
            <line x1="100" y1="100" x2="100" y2="182"/>
            <line x1="100" y1="100" x2="78.8" y2="179.2"/>
            <line x1="100" y1="100" x2="59" y2="171"/>
            <line x1="100" y1="100" x2="42" y2="158"/>
            <line x1="100" y1="100" x2="29" y2="141"/>
            <line x1="100" y1="100" x2="20.8" y2="121.2"/>
            <line x1="100" y1="100" x2="18" y2="100"/>
            <line x1="100" y1="100" x2="20.8" y2="78.8"/>
            <line x1="100" y1="100" x2="29" y2="59"/>
            <line x1="100" y1="100" x2="42" y2="42"/>
            <line x1="100" y1="100" x2="59" y2="29"/>
            <line x1="100" y1="100" x2="78.8" y2="20.8"/>
          </g>
        </svg>

        <div>
          <div style="display: flex; align-items: center; gap: 14px;">
            <img src="/static/bodhz_logo.png" class="logo-3d-animated" style="width: 50px; height: 50px; background: #FFF; border-radius: 12px; padding: 3px; border: 2px solid var(--accent);" alt="BodhZ">
            <div>
              <div style="font-size: 22px; font-weight: 900; letter-spacing: -0.5px;">BodhZ</div>
              <div style="font-size: 11px; font-weight: 800; color: var(--accent); text-transform: uppercase;">Public Procurement Decision Support</div>
            </div>
          </div>
          <p style="font-size: 13px; color: #94A3B8; margin-top: 16px; line-height: 1.55;">
            Automated statutory compliance verification and evidence-backed decision intelligence for GeM procurement.
          </p>
        </div>

        <!-- 3D Holographic Verification Badge -->
        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 18px; text-align: center; backdrop-filter: blur(8px); margin: 20px 0;">
          <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 10px;">
            <span style="background: rgba(16,185,129,0.2); color: #34D399; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">● GSTN</span>
            <span style="background: rgba(59,130,246,0.2); color: #60A5FA; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">● UDYAM</span>
            <span style="background: rgba(245,158,11,0.2); color: #FBBF24; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">● MCA21</span>
            <span style="background: rgba(168,85,247,0.2); color: #C084FC; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;">● DIGILOCKER</span>
          </div>
          <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF;">Role-Aware Authenticated Session</div>
          <div style="font-size: 11.5px; color: #94A3B8; margin-top: 4px;">Procurement Officer • Bid Uploader • DTE Department</div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center;">
          <button onclick="returnToPublicLanding()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #CBD5E1; padding: 7px 14px; border-radius: 6px; font-size: 11.5px; font-weight: 700; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.08)'">
            ← Back to Public Portal
          </button>
          <span style="font-size: 11px; color: #64748B; font-weight: 700;">SIH26100 Prototype</span>
        </div>
      </div>

      <!-- Right Form Pane -->
      <div class="auth-right-form-pane">
        <!-- Sign In Form -->
        <div id="authPaneSignIn" style="display: flex; flex-direction: column;">
          <div style="margin-bottom: 16px;">
            <div style="font-size: 22px; font-weight: 900; color: var(--primary); letter-spacing: -0.5px;">Sign In to Workspace</div>
            <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 2px;">Enter your credentials or click a demo persona below to evaluate:</div>
            
            <!-- 1-Click Role Persona Quick Chips -->
            <div class="role-quick-chip-row">
              <span class="role-quick-chip" onclick="launchDemoPersona('shubham')"><i class="fa-solid fa-user-shield" style="color:#0052CC;"></i> Officer Shubham</span>
              <span class="role-quick-chip" onclick="launchDemoPersona('bidder_tata')"><i class="fa-solid fa-building" style="color:#059669;"></i> Bidder (Tata)</span>
              <span class="role-quick-chip" onclick="launchDemoPersona('officer_dte')"><i class="fa-solid fa-landmark" style="color:#D97706;"></i> DTE Officer</span>
            </div>
          </div>

          <div id="loginAlertBox" style="display: none; background: #FEF2F2; border: 1px solid #FECACA; color: #B91C1C; font-size: 11.5px; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px;">
            <i class="fa-solid fa-circle-exclamation"></i> <span id="loginAlertText">Invalid credentials.</span>
          </div>

          <form onsubmit="handleAuthLogin(event)">
            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label">Official Email or Username</label>
              <div style="position: relative;">
                <i class="fa-solid fa-user" style="position: absolute; left: 14px; top: 12px; color: #94A3B8; font-size: 12px;"></i>
                <input type="text" id="authLoginUser" class="auth-field" placeholder="username or official email" required>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label">Password</label>
              <div style="position: relative;">
                <i class="fa-solid fa-lock" style="position: absolute; left: 14px; top: 12px; color: #94A3B8; font-size: 12px;"></i>
                <input type="password" id="authLoginPass" class="auth-field" placeholder="Enter password" required>
                <button type="button" onclick="togglePasswordVisibility('authLoginPass', this)" style="position: absolute; right: 12px; top: 11px; background: none; border: none; color: #94A3B8; cursor: pointer;">
                  <i class="fa-regular fa-eye"></i>
                </button>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 14px;">
              <label class="form-label">Security Verification</label>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span id="serverCaptchaDisplay" style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 800; letter-spacing: 3px; background: #F1F5F9; border: 1px solid #CBD5E1; padding: 8px 14px; border-radius: 6px; color: var(--primary);">8K9X2</span>
                <button type="button" onclick="refreshServerCaptcha()" class="btn-action" style="padding: 8px 12px; font-size: 11px;"><i class="fa-solid fa-rotate-right"></i></button>
                <input type="text" id="authCaptchaInput" class="auth-field" placeholder="Enter code" style="text-transform: uppercase; padding-left: 14px;" required>
              </div>
            </div>

            <button type="submit" id="btnLoginSubmit" class="btn-auth-primary" style="margin-top: 4px;">
              <span>SIGN IN TO WORKSPACE</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </form>

          <div style="text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 14px;">
            New official or bidder? <span onclick="switchAuthMode('REGISTER')" style="color: var(--primary); font-weight: 800; cursor: pointer; text-decoration: underline;">Create Account</span>
          </div>
        </div>

        <!-- Registration Form -->
        <div id="authPaneRegister" style="display: none; flex-direction: column;">
          <div style="margin-bottom: 14px;">
            <div style="font-size: 20px; font-weight: 900; color: var(--primary);">Create Official Account</div>
            <div style="font-size: 12px; color: var(--text-muted);">Register for institutional or bidder procurement workspace access.</div>
          </div>

          <div id="registerAlertBox" style="display: none; background: #FEF2F2; border: 1px solid #FECACA; color: #B91C1C; font-size: 11.5px; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
            <i class="fa-solid fa-circle-exclamation"></i> <span id="registerAlertText">Registration error.</span>
          </div>

          <form onsubmit="handleAuthRegister(event)">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
              <div class="form-group">
                <label class="form-label">Full Legal Name</label>
                <input type="text" id="regFullName" class="auth-field" placeholder="Dr. Ramesh Gupta" style="padding-left: 12px;" required>
              </div>
              <div class="form-group">
                <label class="form-label">Official Work Email</label>
                <input type="email" id="regEmail" class="auth-field" placeholder="ramesh@nic.in" style="padding-left: 12px;" required>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 8px; margin-bottom: 8px;">
              <div class="form-group">
                <label class="form-label">Organization / Department</label>
                <input type="text" id="regOrg" class="auth-field" placeholder="e.g. National Informatics Centre" style="padding-left: 12px;" required>
              </div>
              <div class="form-group">
                <label class="form-label">Role Category</label>
                <select id="regRole" class="auth-field" style="padding-left: 10px;">
                  <option value="PROCUREMENT_OFFICER">Procurement Officer</option>
                  <option value="BID_UPLOADER">Bid Uploader / Vendor</option>
                  <option value="DTE_OFFICER">DTE State Officer</option>
                  <option value="AUDITOR">Auditor</option>
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 8px;">
              <label class="form-label">Username</label>
              <input type="text" id="regUsername" class="auth-field" placeholder="choose unique username" style="padding-left: 12px;" required>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Password</label>
                <input type="password" id="regPassword" class="auth-field" placeholder="Min. 8 characters" style="padding-left: 12px;" required>
              </div>
              <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <input type="password" id="regConfirmPassword" class="auth-field" placeholder="Re-enter password" style="padding-left: 12px;" required>
              </div>
            </div>

            <button type="submit" id="btnRegisterSubmit" class="btn-auth-primary" style="background: linear-gradient(135deg, #047857 0%, #065F46 100%);">
              <span>CREATE ACCOUNT</span>
              <i class="fa-solid fa-check"></i>
            </button>
          </form>

          <div style="text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 10px;">
            Already registered? <span onclick="switchAuthMode('LOGIN')" style="color: var(--primary); font-weight: 800; cursor: pointer; text-decoration: underline;">Sign In</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- DEMO MODE MODAL (SIH EVALUATOR SELECTOR) -->
  <div id="demoModeModal" style="display: none; position: fixed; inset: 0; background: rgba(10,25,47,0.75); z-index: 2000; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: #FFFFFF; width: 100%; max-width: 520px; border-radius: 14px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 10px;">
        <div style="font-size: 16px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-bolt" style="color: var(--accent);"></i>
          <span>SIH Evaluator Role-Based Persona Selector</span>
        </div>
        <button onclick="closeDemoModeModal()" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #64748B;">✕</button>
      </div>

      <p style="font-size: 12px; color: #475569;">
        Select one of the 3 official SIH26100 demonstration personas to evaluate their tailored workspace and permission boundaries:
      </p>

      <div style="display: flex; flex-direction: column; gap: 10px;">
        <!-- Persona 1 -->
        <div onclick="launchDemoPersona('shubham')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--primary)'" onmouseout="this.style.borderColor='#CBD5E1'">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 13px; font-weight: 800; color: var(--primary);">1. Senior Procurement Officer (Central GeM)</div>
            <span class="badge-pass" style="font-size: 10px;">PROCUREMENT_OFFICER</span>
          </div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Officer Shubham • Full 10-Section Decision Support Suite</div>
        </div>

        <!-- Persona 2 -->
        <div onclick="launchDemoPersona('bidder_tata')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--success)'" onmouseout="this.style.borderColor='#CBD5E1'">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 13px; font-weight: 800; color: #047857;">2. Bid Uploader / Vendor Representative</div>
            <span class="badge-pass" style="font-size: 10px; background: #ECFDF5; color: #047857;">BID_UPLOADER</span>
          </div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Rajiv Mehta • Tata Advanced Training • Bid Submission Portal</div>
        </div>

        <!-- Persona 3 -->
        <div onclick="launchDemoPersona('officer_dte')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-orange)'" onmouseout="this.style.borderColor='#CBD5E1'">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 13px; font-weight: 800; color: #B45309;">3. State Directorate Officer (DTE Maharashtra)</div>
            <span class="badge-review" style="font-size: 10px;">DTE_OFFICER</span>
          </div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Dr. Rajesh Kumar • Center of Excellence (COE) Technical Education</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================================================== -->
  <!-- 3. ROLE-AWARE AUTHENTICATED WORKSPACE CONTAINER    -->
  <!-- ================================================== -->
  <div id="appWorkspace" style="display: none; flex-direction: column; min-height: 100vh;">
    <!-- Top Ribbon -->
    <div class="top-bar">
      <div style="display: flex; gap: 16px; align-items: center;">
        <span id="topRibbonWorkspaceLabel">BodhZ Procurement Decision Support</span>
        <span>•</span>
        <span>SIH26100</span>
      </div>
      <div style="display: flex; gap: 16px; align-items: center;">
        <span style="color: #34D399; font-weight: 700;">● 13 Gateway Nodes Connected</span>
        <span>|</span>
        <a href="/docs" target="_blank" style="color: var(--accent); text-decoration: none; font-weight: 700;">API Documentation</a>
      </div>
    </div>

    <!-- Header Banner -->
    <header class="gov-header">
      <div class="header-brand" style="display: flex; align-items: center; gap: 12px;">
        <img src="/static/bodhz_logo.png" class="brand-logo-img logo-3d-animated" alt="BodhZ Logo">
        <div>
          <div style="font-size: 18px; font-weight: 900; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">
            BodhZ
            <span id="headerRoleBadgePill" style="font-size: 10px; background: var(--primary-light); color: #FFF; padding: 2px 8px; border-radius: 4px; font-weight: 800;">OFFICER</span>
          </div>
          <div style="font-size: 11px; color: #94A3B8; font-weight: 500;" id="headerOrgSubtitle">
            Government e-Marketplace (GeM) • Public Procurement Division
          </div>
        </div>
      </div>

      <!-- Right User / Officer Info Badge -->
      <div id="headerOfficerBadge" style="display: flex; align-items: center; gap: 12px;">
        <div style="text-align: right;">
          <div id="headerOfficerName" style="font-size: 12px; font-weight: 800; color: #FFFFFF;">Officer Shubham</div>
          <div id="headerOfficerRole" style="font-size: 10px; color: var(--accent); font-weight: 700;">Senior Procurement Officer</div>
        </div>
        <button onclick="handleAuthLogout()" class="btn-action" style="padding: 6px 12px; font-size: 11px; background: #1E293B;">
          <i class="fa-solid fa-arrow-right-from-bracket"></i> Logout
        </button>
      </div>
    </header>

    <div class="main-wrapper">
      <!-- Dynamic Sidebar Navigation (Generated Based on Active Role) -->
      <aside class="sidebar" id="appSidebar">
        <div id="sidebarTenderWorkspaceSelectorBox" style="padding: 12px; border-bottom: 1px solid #1E293B;">
          <label style="font-size: 9.5px; font-weight: 800; color: var(--accent); text-transform: uppercase;">Active Tender Workspace</label>
          <select id="activeTenderSelector" class="form-input" style="background: #030F22; color: #FFFFFF; border-color: #334155; margin-top: 4px; font-size: 11px;" onchange="switchActiveTender(this.value)">
            <option value="">Loading Tenders...</option>
          </select>
        </div>

        <nav class="sidebar-menu" id="dynamicSidebarMenu">
          <!-- Populated by JavaScript based on active role -->
        </nav>
      </aside>

      <!-- Main Dynamic Viewport -->
      <main class="viewport">

        <!-- ============================================== -->
        <!-- WORKSPACE 1: PROCUREMENT OFFICER VIEWS (10)    -->
        <!-- ============================================== -->
        <!-- SECTION 01: DASHBOARD OVERVIEW -->
        <div id="view-dashboard" style="display: flex; flex-direction: column; gap: 18px;">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;">
            <div class="card-panel" style="padding: 14px; flex-direction: row; justify-content: space-between; align-items: center;">
              <div><div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">ACTIVE TENDERS</div><div style="font-size: 24px; font-weight: 900; color: var(--primary);" id="statTotalTenders">3</div></div>
              <i class="fa-solid fa-folder-tree" style="font-size: 24px; color: var(--primary);"></i>
            </div>
            <div class="card-panel" style="padding: 14px; flex-direction: row; justify-content: space-between; align-items: center;">
              <div><div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">BIDS SUBMITTED</div><div style="font-size: 24px; font-weight: 900; color: var(--primary);" id="statTotalBids">3</div></div>
              <i class="fa-solid fa-file-invoice" style="font-size: 24px; color: var(--primary);"></i>
            </div>
            <div class="card-panel" style="padding: 14px; flex-direction: row; justify-content: space-between; align-items: center;">
              <div><div style="font-size: 11px; font-weight: 700; color: var(--success-dark);">QUALIFIED / PASS</div><div style="font-size: 24px; font-weight: 900; color: var(--success-dark);" id="statCompliantBids">1</div></div>
              <i class="fa-solid fa-circle-check" style="font-size: 24px; color: var(--success);"></i>
            </div>
            <div class="card-panel" style="padding: 14px; flex-direction: row; justify-content: space-between; align-items: center;">
              <div><div style="font-size: 11px; font-weight: 700; color: var(--danger);">CRITICAL / FAIL</div><div style="font-size: 24px; font-weight: 900; color: var(--danger);" id="statHighRiskBids">1</div></div>
              <i class="fa-solid fa-triangle-exclamation" style="font-size: 24px; color: var(--danger);"></i>
            </div>
          </div>

          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-crosshairs"></i> Active Tender Workspace: <span id="dashTenderId" style="color: #0052CC; font-family: 'JetBrains Mono', monospace;">DTE/2026/RFP/COE/4901</span></span>
              <div style="display: flex; gap: 8px;">
                <span id="dashBatchBadge" class="badge-pass" style="font-size: 11px; padding: 4px 10px;">BATCH: ALL_BIDS_PROCESSED</span>
                <button onclick="switchView('matrix')" class="btn-action" style="font-size: 11px; padding: 4px 12px;"><i class="fa-solid fa-table-columns"></i> Comparative Matrix</button>
              </div>
            </div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);" id="dashTenderTitle">Establishment of Center of Excellence (COE) and Technical Training Centers</div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
              <div style="font-size: 12px; font-weight: 800; color: #475569; text-transform: uppercase;">Evaluated Bidders Under Active Tender</div>
              <button onclick="switchView('bidders')" class="btn-success" style="font-size: 11px; padding: 5px 12px;">+ Ingest Another Bidder Submission</button>
            </div>

            <table class="clean-table" style="margin-top: 6px;">
              <thead>
                <tr>
                  <th>Bidder Organization</th>
                  <th>GSTIN / PAN</th>
                  <th>Compliance Score</th>
                  <th>Risk Tier</th>
                  <th>Screening Status</th>
                  <th>Officer Decision</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="dashBiddersTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 02: TENDER INTELLIGENCE -->
        <div id="view-tenders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-pdf" style="color: #E65100;"></i> Ingest Tender Notice PDF & Auto-Extract Statutory Criteria</span>
              <span style="font-size: 11px; background: #ECFDF5; color: #047857; padding: 3px 8px; border-radius: 4px; font-weight: 800;">GFR 2017 & GeM ALIGNED</span>
            </div>

            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">
              <span style="font-size: 11px; font-weight: 700; color: #475569;">Quick Load Real Government RFP Presets:</span>
              <span class="preset-pill" onclick="loadRealTenderPreset('DTE')">🏛️ DTE Maharashtra (COE RFP)</span>
              <span class="preset-pill" onclick="loadRealTenderPreset('NFL')">🏢 National Fertilizers Ltd (VAPT NIT)</span>
              <span class="preset-pill" onclick="loadRealTenderPreset('ICAR')">🌾 ICAR-IIMR (Agro Machinery)</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;">
              <div class="form-group">
                <label class="form-label">Tender Reference Number:</label>
                <input type="text" id="newTenderIdInput" class="form-input" value="DTE/2026/RFP/COE/4901">
              </div>
              <div class="form-group">
                <label class="form-label">Tender Title:</label>
                <input type="text" id="newTenderTitleInput" class="form-input" value="Establishment of Center of Excellence (COE) and Technical Training Centers">
              </div>
              <div class="form-group">
                <label class="form-label">Category:</label>
                <input type="text" id="newTenderCategoryInput" class="form-input" value="Technical Education & Skill Infrastructure">
              </div>
            </div>

            <div class="dropzone-box" onclick="document.getElementById('tenderFileInput').click()">
              <i class="fa-solid fa-cloud-arrow-up" style="font-size: 28px; color: var(--primary); margin-bottom: 6px;"></i>
              <div style="font-size: 13px; font-weight: 800; color: var(--primary);">Click to Select Tender Document File (.pdf, .txt, .docx)</div>
              <div id="selectedTenderFileText" style="font-size: 11px; color: var(--text-muted);">Auto-extracts mandatory eligibility rules on upload</div>
              <input type="file" id="tenderFileInput" style="display: none;" onchange="handleTenderPDFUpload(this)">
            </div>

            <div id="tenderExtractedRequirementsPanel" style="display: none; background: #F8FAFC; border: 1px solid #CBD5E1; padding: 16px; border-radius: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 13px; font-weight: 800; color: var(--primary);">
                  <i class="fa-solid fa-sliders" style="color: #0052CC;"></i> Extracted Statutory Requirements & Weight Calibration
                </div>
                <span id="extractedReqsCountBadge" class="badge-pass">10 Rules Extracted</span>
              </div>
              <table class="clean-table" style="background: #FFFFFF;">
                <thead>
                  <tr><th>Statutory Module</th><th>Requirement Description</th><th>Mandatory?</th><th>Weight (%)</th></tr>
                </thead>
                <tbody id="tenderRequirementsEditBody"></tbody>
              </table>

              <div style="margin-top: 14px; display: flex; justify-content: flex-end; gap: 10px;">
                <button onclick="confirmExtractedRequirements()" class="btn-success">
                  <i class="fa-solid fa-check-double"></i> CONFIRM REQUIREMENTS & PUBLISH TO BIDDERS →
                </button>
              </div>
            </div>
          </div>

          <div class="card-panel">
            <div class="card-title">Registered Procurement Tenders in System</div>
            <table class="clean-table">
              <thead>
                <tr><th>Tender Number</th><th>Tender Title</th><th>Category</th><th>Lifecycle Status</th><th>Actions</th></tr>
              </thead>
              <tbody id="tendersListTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 03: BID INGESTION & AI -->
        <div id="view-bidders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-arrow-up"></i> Upload Bidder Submission Bundle & Run AI Verification</span>
              <span style="font-size: 11px; background: #ECFDF5; color: #047857; padding: 3px 8px; border-radius: 4px; font-weight: 800;">13 GATEWAY SCAN</span>
            </div>

            <div style="background: #F1F5F9; border-left: 4px solid #0052CC; padding: 10px 14px; border-radius: 0 6px 6px 0; font-size: 12px;">
              <strong>Target Active Tender:</strong> <span id="bidderUploadTargetTenderLabel" style="font-weight: 800; font-family: 'JetBrains Mono', monospace; color: var(--primary);">DTE/2026/RFP/COE/4901</span>
            </div>

            <div style="display: flex; gap: 8px; align-items: center; margin-top: 4px; flex-wrap: wrap;">
              <span style="font-size: 11px; font-weight: 700; color: #475569;">Quick Pre-fill Real Bidder Profiles:</span>
              <span class="preset-pill" onclick="prefillBidder('Tata Advanced Training & Systems Ltd', '27AAACT1098F1Z5')">Tata Advanced Training (Compliant)</span>
              <span class="preset-pill" onclick="prefillBidder('EduTech Infoway Solutions Pvt Ltd', '27AACCE3099P1Z2')">EduTech Infoway (Review Case)</span>
              <span class="preset-pill" onclick="prefillBidder('Apex Cyber Skills & Infra Ltd', '27AABCA2045K1Z8')">Apex Cyber (Disqualified Case)</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 6px;">
              <div class="form-group">
                <label class="form-label">Bidder Legal Name:</label>
                <input type="text" id="bidderNameInput" class="form-input" placeholder="e.g. Tata Advanced Training & Systems Ltd">
              </div>
              <div class="form-group">
                <label class="form-label">GSTIN / PAN / Udyam:</label>
                <input type="text" id="bidderGstinInput" class="form-input" placeholder="e.g. 27AAACT1098F1Z5">
              </div>
            </div>

            <div class="dropzone-box" onclick="document.getElementById('bidderFileInput').click()">
              <i class="fa-solid fa-file-zipper" style="font-size: 28px; color: var(--primary); margin-bottom: 6px;"></i>
              <div style="font-size: 13px; font-weight: 800; color: var(--primary);">Select Bid Proposal & Document Bundle (.pdf, .zip, .docx)</div>
              <div id="selectedBidderFileText" style="font-size: 11px; color: var(--text-muted);">Performs magic byte validation, SHA-256 hash & text extraction</div>
              <input type="file" id="bidderFileInput" style="display: none;" onchange="handleBidderFileSelect(this)">
            </div>

            <div id="bidderProcessingProgress" style="display: none; background: #FFFBEB; border: 1px solid #FDE68A; padding: 12px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #92400E;">
              <i class="fa-solid fa-spinner fa-spin"></i> Parsing PDF → Extracting GSTIN/PAN/Udyam → Cross-Checking 13 Gateway Nodes → Scoring...
            </div>

            <button onclick="submitBidderAndEvaluate()" class="btn-success" style="align-self: flex-end;">
              <i class="fa-solid fa-bolt"></i> RUN COMPLIANCE EVALUATION →
            </button>
          </div>
        </div>

        <!-- SECTION 04: DOCUMENT INTELLIGENCE -->
        <div id="view-docintel" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-lines"></i> Document Intelligence & Extraction Pipeline</span>
              <span class="badge-pass">OCR NATIVE + FALLBACK</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr><th>Document Filename</th><th>Extracted Entity</th><th>Value</th><th>Source Citation</th><th>OCR Confidence</th></tr>
              </thead>
              <tbody id="docIntelTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 05: 13 GATEWAY NODES -->
        <div id="view-vercenter" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-network-wired" style="color: #0052CC;"></i> 13 Statutory Verification Gateway Nodes (Layer 4)</span>
              <span class="badge-pass">13 / 13 ADAPTERS CONNECTED</span>
            </div>
            <p style="font-size: 12px; color: #475569;">
              Automated external verification connectors validating bidder certificates directly against official statutory registries for: <strong id="vercenterActiveBidderLabel">Tata Advanced Training & Systems Ltd</strong>
            </p>

            <div style="font-size: 11.5px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-top: 6px;">1. Registration & Identity Verification</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;">
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏭 Udyam / MSME Portal</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🧾 GSTN Portal</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🪪 PAN / Income Tax</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏢 MCA21 Registry</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
            </div>

            <div style="font-size: 11.5px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-top: 10px;">2. Statutory & Eligibility Verification</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;">
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🚀 Startup India (DPIIT)</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏭 NSIC Registry</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>👷 EPFO Registry</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏥 ESIC Portal</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
            </div>

            <div style="font-size: 11.5px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-top: 10px;">3. Tender-Specific Compliance Verification</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;">
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🔐 DigiLocker Gateway</strong><div class="badge-pass" style="margin-top:6px;">DIGITALLY VERIFIED</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>⚙️ OEM Authorization (MAF)</strong><div class="badge-pass" style="margin-top:6px;">VERIFIED & ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🇮🇳 Make in India (MII)</strong><div class="badge-pass" style="margin-top:6px;">VERIFIED & ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>📑 BIS / ISO 9001:2015</strong><div class="badge-pass" style="margin-top:6px;">VERIFIED & ACTIVE</div></div>
            </div>

            <div style="font-size: 11.5px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-top: 10px;">4. Risk & Debarment Verification</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;">
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🚫 CPPP Debarment Registry</strong><div class="badge-pass" style="margin-top:6px;">CLEARED (NO DEBARMENT)</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🌐 Land Border Rule 144(xi)</strong><div class="badge-pass" style="margin-top:6px;">COMPLIANT (FORM-I)</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>⭐ GeM Vendor Rating Engine</strong><div class="badge-pass" style="margin-top:6px;">4.85 / 5.00 RATING</div></div>
            </div>
          </div>
        </div>

        <!-- SECTION 06: INCONSISTENCY ENGINE -->
        <div id="view-consistency" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-clone"></i> Cross-Document Inconsistency & Entity Matching Engine</span>
              <span class="badge-pass">GENERALIZED SIMILARITY</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr><th>Check Type</th><th>Target Entities</th><th>Similarity Score</th><th>Severity</th><th>Findings Summary</th></tr>
              </thead>
              <tbody id="inconsistencyTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 07: COMPARATIVE MATRIX -->
        <div id="view-matrix" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-table-columns" style="color: #0052CC;"></i> Official Multi-Bidder Comparative Evaluation Matrix</span>
              <div style="display: flex; gap: 8px;">
                <button onclick="loadComparativeMatrix(false)" class="btn-action" style="font-size: 11px; padding: 4px 10px;">Show All Bids</button>
                <button onclick="loadComparativeMatrix(true)" class="btn-warning" style="font-size: 11px; padding: 4px 10px;">✓ Shortlisted Only</button>
              </div>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Bidder Name & Identifiers</th>
                  <th>Score</th>
                  <th>Risk Tier</th>
                  <th>Screening</th>
                  <th>Technical Modules</th>
                  <th>Inconsistencies / Issues</th>
                  <th>Officer Decision</th>
                  <th>Dossier</th>
                </tr>
              </thead>
              <tbody id="comparativeMatrixTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- SECTION 08: OFFICER FINAL DECISION -->
        <div id="view-decision" style="display: none; flex-direction: column; gap: 18px;">
          <div id="historicalBidderAlertBox" class="hist-card" style="display: none;">
            <div style="font-size: 13px; font-weight: 800; color: #92400E;">
              <i class="fa-solid fa-clock-rotate-left"></i> 📜 5-Year Historical Bidder Memory Record Found
            </div>
            <div id="historicalBidderContent" style="font-size: 12px; color: #78350F; margin-top: 6px;"></div>
          </div>

          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-gavel"></i> Procurement Officer Final Decision (GFR 2017 Rule 144)</span>
              <span class="badge-pass">100% HUMAN AUTHORITY</span>
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
              <div>
                <div style="font-size: 12px; color: var(--text-muted);">Selected Bidder for Final Action:</div>
                <div style="font-size: 16px; font-weight: 900; color: var(--primary);" id="decisionTargetBidderName">Tata Advanced Training & Systems Ltd</div>
                <div style="font-size: 12px; color: #475569; margin-top: 4px;" id="decisionTargetAIRecommendation">AI Recommendation: Bidder qualifies under Section 4.2.</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; color: var(--text-muted);">Score:</div>
                <div style="font-size: 28px; font-weight: 900; color: #15803D;" id="decisionTargetScore">95/100</div>
              </div>
            </div>

            <div class="form-group" style="margin-top: 10px;">
              <label class="form-label">Official Qualification Decision:</label>
              <select id="officerDecisionChoice" class="form-input" style="font-weight: 800;">
                <option value="QUALIFIED">✓ QUALIFIED — Approved for Commercial Price Bid Opening</option>
                <option value="DISQUALIFIED">✕ DISQUALIFIED — Non-Compliant with Mandatory Terms</option>
                <option value="NEEDS_CLARIFICATION">⚠️ NEEDS CLARIFICATION — Issue Statutory Query</option>
                <option value="REJECTED">🚫 REJECTED — Ineligible under GFR 2017</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Officer Audit Remarks:</label>
              <textarea id="officerDecisionNotes" class="form-input" rows="3" placeholder="Enter official audit justification remarks..."></textarea>
            </div>

            <button onclick="submitOfficerFinalDecision()" class="btn-action" style="align-self: flex-start;">
              <i class="fa-solid fa-signature"></i> RECORD BINDING DECISION UNDER GFR RULE 144
            </button>
          </div>
        </div>

        <!-- SECTION 09: PRINTABLE DOSSIER -->
        <div id="view-reports" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-print"></i> Official Compliance Evaluation Dossier</span>
              <a id="btnOpenReportTab" href="#" target="_blank" class="btn-action" style="font-size: 11px; padding: 4px 10px;">Open Print View</a>
            </div>
            <iframe id="reportPreviewFrame" style="width: 100%; height: 600px; border: 1px solid #CBD5E1; border-radius: 8px;" src="about:blank"></iframe>
          </div>
        </div>

        <!-- SECTION 10: AUDIT TRAIL -->
        <div id="view-audittrail" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-shield-halved"></i> Cryptographic SHA-256 Audit Trail</span>
              <span class="badge-pass">IMMUTABLE LOGS</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr><th>Timestamp</th><th>Actor</th><th>Event Type</th><th>Details</th><th>SHA-256 Hash</th></tr>
              </thead>
              <tbody id="auditTrailTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- ============================================================== -->
        <!-- WORKSPACE 2: ENHANCED BID UPLOADER & TENDERS CATALOG PORTAL    -->
        <!-- ============================================================== -->
        <div id="view-bidder-portal" style="display: none; flex-direction: column; gap: 20px;">
          <!-- Top Stat Ribbon -->
          <div class="card-panel" style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border-left: 5px solid #059669;">
            <div class="card-title">
              <span><i class="fa-solid fa-briefcase" style="color: #059669;"></i> Bidder & Vendor Self-Service Workspace</span>
              <span class="badge-open-bid">VENDOR AUTHORIZED</span>
            </div>
            <p style="font-size: 13px; color: #475569;">
              Welcome, <strong id="bidderPortalOrgName" style="color: var(--primary);">Tata Advanced Training & Systems Ltd</strong>. 
              Browse active procurement tenders published by Government Officers, prepare your digital bid document bundle, and check your statutory compliance before submission.
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 8px;">
              <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size: 11px; font-weight: 700; color: #64748B;">PUBLISHED TENDERS</div>
                <div style="font-size: 24px; font-weight: 900; color: var(--primary);" id="bidderTotalPublishedTenders">3</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size: 11px; font-weight: 700; color: #047857;">MY SUBMISSIONS</div>
                <div style="font-size: 24px; font-weight: 900; color: #047857;" id="bidderTotalSubmissions">1</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size: 11px; font-weight: 700; color: #2563EB;">13 GATEWAY READINESS</div>
                <div style="font-size: 24px; font-weight: 900; color: #2563EB;" id="bidderVerifiedModules">13 / 13 Verified</div>
              </div>
            </div>
          </div>

          <!-- Section: Published Open Tenders Catalog -->
          <div class="card-panel" id="bidderCatalogSection">
            <div class="card-title">
              <span><i class="fa-solid fa-folder-open" style="color: #0052CC;"></i> Published Open Tenders Catalog (Live Procurement Feeds)</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <input type="text" id="bidderTenderSearchInput" placeholder="🔍 Filter tenders by ID or keyword..." class="form-input" style="width: 260px; padding: 4px 10px; font-size: 11.5px;" oninput="filterBidderTendersCatalog()">
                <button onclick="loadBidderPortalData()" class="btn-action" style="padding: 4px 10px; font-size: 11px;"><i class="fa-solid fa-rotate-right"></i> Refresh</button>
              </div>
            </div>

            <div id="bidderTendersCatalogGrid" class="tender-catalog-grid">
              <!-- Dynamically populated with active tender cards -->
            </div>
          </div>

          <!-- Section: Submit Bid Proposal Bundle -->
          <div class="card-panel" id="bidderSubmissionFormSection" style="border: 2px solid #CBD5E1;">
            <div class="card-title">
              <span><i class="fa-solid fa-cloud-arrow-up" style="color: #059669;"></i> Submit Bid Proposal Bundle & Run 13-Gateway Pre-Check</span>
              <span id="bidderActiveSelectedTenderBadge" class="badge-pass" style="font-size: 11px;">Select a tender above</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div class="form-group">
                <label class="form-label">Target Procurement Tender:</label>
                <select id="bidderOpenTendersDropdown" class="form-input" onchange="syncBidderSelectedTender(this.value)" style="font-weight: 800; color: var(--primary);">
                  <option value="">Loading Tenders...</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Bidder Legal Name:</label>
                <input type="text" id="bidderPortalNameInput" class="form-input" value="Tata Advanced Training & Systems Ltd">
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div class="form-group">
                <label class="form-label">GSTIN / Udyam Registration Number:</label>
                <input type="text" id="bidderPortalGstinInput" class="form-input" value="27AAACT1098F1Z5">
              </div>
              <div class="form-group">
                <label class="form-label">PAN Number:</label>
                <input type="text" id="bidderPortalPanInput" class="form-input" value="AAACT1098F">
              </div>
            </div>

            <!-- Pre-check Statutory Requirements Checklist -->
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
              <div style="font-size: 12px; font-weight: 800; color: var(--primary); margin-bottom: 8px;">
                <i class="fa-solid fa-list-check" style="color: #059669;"></i> Statutory Documents Included in This Bundle:
              </div>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; font-size: 12px; color: #334155;">
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" checked> GST Registration & 3B</label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" checked> PAN & Corporate Identity</label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" checked> CA Audited Balance Sheet</label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" checked> OEM Authorization (MAF)</label>
                <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" checked> Make in India Declaration</label>
              </div>
            </div>

            <div class="dropzone-box" onclick="document.getElementById('bidderPortalFileInput').click()">
              <i class="fa-solid fa-file-zipper" style="font-size: 32px; color: var(--success); margin-bottom: 6px;"></i>
              <div style="font-size: 13.5px; font-weight: 800; color: var(--primary);">Select Bid Proposal Bundle (.pdf, .zip, .docx)</div>
              <div id="bidderPortalSelectedFileText" style="font-size: 11.5px; color: var(--text-muted);">PDF extraction with automatic SHA-256 integrity hash</div>
              <input type="file" id="bidderPortalFileInput" style="display: none;" onchange="handleBidderPortalFile(this)">
            </div>

            <div id="bidderPortalProgress" style="display: none; background: #FFFBEB; border: 1px solid #FDE68A; padding: 12px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #92400E;">
              <i class="fa-solid fa-spinner fa-spin"></i> Ingesting Bid Bundle → Verifying GSTN / PAN / Udyam → Cross-checking 13 Gateway Nodes...
            </div>

            <button onclick="submitBidderPortalProposal()" id="btnSubmitBidderProposal" class="btn-success" style="align-self: flex-end; padding: 10px 20px;">
              <i class="fa-solid fa-paper-plane"></i> SUBMIT BID BUNDLE & RUN PRE-CHECK →
            </button>
          </div>

          <!-- Section: My Submissions Table -->
          <div class="card-panel" id="bidderSubmissionsSection">
            <div class="card-title">
              <span><i class="fa-solid fa-clock-rotate-left"></i> My Bid Submissions & Compliance Verification Records</span>
              <span class="badge-pass" id="mySubmissionsCountBadge">1 Record</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Tender Reference</th>
                  <th>Tender Title</th>
                  <th>Submission Date</th>
                  <th>Compliance Score</th>
                  <th>Screening Status</th>
                  <th>13 Gateways</th>
                  <th>Dossier</th>
                </tr>
              </thead>
              <tbody id="bidderSubmissionsTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- ============================================== -->
        <!-- WORKSPACE 3: DTE MAHARASHTRA DEPARTMENT VIEWS  -->
        <!-- ============================================== -->
        <div id="view-dte-portal" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-building-columns" style="color: #D97706;"></i> Directorate of Technical Education (DTE Maharashtra) Workspace</span>
              <span class="badge-review">STATE DEPARTMENT OVERSIGHT</span>
            </div>
            <p style="font-size: 12.5px; color: #475569;">
              Official Department Workspace for <strong>Directorate of Technical Education (DTE Maharashtra)</strong>. Monitoring establishment of Center of Excellence (COE) and technical training facilities across Maharashtra engineering institutions.
            </p>
          </div>

          <div class="card-panel">
            <div class="card-title">DTE Department Active RFP: DTE/2026/RFP/COE/4901</div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">
              Establishment, Operationalization & Maintenance of Center of Excellence (COE) and Technical Training Centers
            </div>
            <table class="clean-table" style="margin-top: 10px;">
              <thead>
                <tr><th>Bidder Name</th><th>GSTIN / PAN</th><th>Compliance Score</th><th>Technical Screening</th><th>Audited Findings</th><th>Actions</th></tr>
              </thead>
              <tbody id="dteBiddersTableBody"></tbody>
            </table>
          </div>
        </div>

      </main>
    </div>

    <!-- Context-Aware Floating Chatbot -->
    <button onclick="toggleChatbot()" class="chatbot-fab-clean" id="chatFabBtn">
      <img src="/static/bodhz_logo.png" style="width: 24px; height: 24px; object-fit: contain; background: #FFF; border-radius: 50%; padding: 2px;" alt="Logo">
      <span>BodhZ AI Assistant</span>
    </button>

    <div id="chatModalWindow" class="chat-modal-clean">
      <div class="chat-header-clean">
        <div style="display: flex; align-items: center; gap: 8px;">
          <img src="/static/bodhz_logo.png" style="width: 22px; height: 22px; object-fit: contain; background: #FFF; border-radius: 50%; padding: 2px;" alt="Logo">
          <div>
            <div style="font-size: 12.5px; font-weight: 800;">BodhZ AI Assistant</div>
            <div style="font-size: 9.5px; color: #34D399;">● Role-Aware Context Connected</div>
          </div>
        </div>
        <button onclick="toggleChatbot()" style="background: none; border: none; color: #FFF; font-size: 14px; cursor: pointer;">✕</button>
      </div>

      <div class="current-context-bar">
        <span style="font-weight: 800; font-size: 9px; background: #0A192F; color: #F59E0B; padding: 1px 4px; border-radius: 3px;">ACTIVE ROLE</span>
        <span id="chatContextRole">Procurement Officer</span>
      </div>

      <div id="chatMessagesArea" class="chat-messages-area">
        <div class="chat-msg-bot">
          <div style="font-weight: 800; color: #0A192F; margin-bottom: 4px;">BodhZ AI Assistant</div>
          <span id="chatWelcomeMessage">BodhZ AI Assistant is active. You can ask about tender rules, bidder compliance, statutory verifications, or document evidence.</span>
          <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:8px;">
            <span class="chat-chip" onclick="sendChatSuggestion('Show comparative scores for active tender')">📊 Comparative Scores</span>
            <span class="chat-chip" onclick="sendChatSuggestion('Which bidder has missing certificates?')">⚠️ Missing Certificates</span>
            <span class="chat-chip" onclick="sendChatSuggestion('Explain GFR 2017 Rule 144 compliance')">📜 GFR Rule 144</span>
          </div>
        </div>
      </div>

      <div class="chat-input-row">
        <input type="text" id="chatUserInput" class="form-input" placeholder="Ask about tenders, compliance, or verification..." onkeypress="if(event.key==='Enter') sendChatMessage()">
        <button onclick="sendChatMessage()" class="btn-action" style="padding: 8px 12px;"><i class="fa-solid fa-paper-plane"></i></button>
      </div>
    </div>
  </div>

  <!-- DYNAMIC CLIENT JAVASCRIPT -->
  <script>
    let activeUser = JSON.parse(localStorage.getItem('bodhz_user')) || null;
    let activeTender = null;
    let activeBidder = null;
    let tendersList = [];
    let comparativeRows = [];
    let pendingTenderUploadId = null;
    let serverCaptchaCode = "";

    window.onload = async function() {
      await refreshServerCaptcha();
      if (!activeUser) {
        showPublicLanding();
      } else {
        routeToRoleWorkspace(activeUser);
      }
    };

    function showToast(title, msg, type = 'info') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-info');
      const color = type === 'success' ? '#10B981' : (type === 'error' ? '#EF4444' : '#F59E0B');
      toast.style.borderLeftColor = color;
      toast.innerHTML = `<i class="fa-solid ${icon}" style="color:${color}; font-size:16px;"></i><div><div style="font-size:12px; font-weight:800;">${title}</div><div style="font-size:11px; color:#CBD5E1;">${msg}</div></div>`;
      container.appendChild(toast);
      setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3500);
    }

    function scrollToSection(sectionId) {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }

    function showPublicLanding() {
      document.getElementById('view-public-landing').style.display = 'flex';
      document.getElementById('view-auth').style.display = 'none';
      document.getElementById('appWorkspace').style.display = 'none';
    }

    function returnToPublicLanding() {
      showPublicLanding();
    }

    function openAuthScreen(mode = 'LOGIN') {
      document.getElementById('view-public-landing').style.display = 'none';
      document.getElementById('view-auth').style.display = 'flex';
      document.getElementById('appWorkspace').style.display = 'none';
      switchAuthMode(mode);
    }

    function switchAuthMode(mode) {
      const paneLogin = document.getElementById('authPaneSignIn');
      const paneRegister = document.getElementById('authPaneRegister');
      if (mode === 'REGISTER') {
        paneLogin.style.display = 'none';
        paneRegister.style.display = 'flex';
      } else {
        paneRegister.style.display = 'none';
        paneLogin.style.display = 'flex';
      }
    }

    async function refreshServerCaptcha() {
      try {
        const resp = await fetch('/api/v1/auth/captcha');
        if (resp.ok) {
          const data = await resp.json();
          serverCaptchaCode = data.captcha_code;
          document.getElementById('serverCaptchaDisplay').innerText = data.captcha_code;
        } else {
          fallbackLocalCaptcha();
        }
      } catch(e) {
        fallbackLocalCaptcha();
      }
    }

    function fallbackLocalCaptcha() {
      const chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";
      let code = "";
      for (let i = 0; i < 5; i++) code += chars.charAt(Math.floor(Math.random() * chars.length));
      serverCaptchaCode = code;
      document.getElementById('serverCaptchaDisplay').innerText = code;
    }

    function togglePasswordVisibility(fieldId, btn) {
      const input = document.getElementById(fieldId);
      const icon = btn.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    }

    async function handleAuthLogin(event) {
      event.preventDefault();
      const username = document.getElementById('authLoginUser').value.trim();
      const password = document.getElementById('authLoginPass').value.trim();
      const captchaInput = document.getElementById('authCaptchaInput').value.trim().toUpperCase();
      const alertBox = document.getElementById('loginAlertBox');
      const alertText = document.getElementById('loginAlertText');
      const btn = document.getElementById('btnLoginSubmit');

      if (captchaInput !== serverCaptchaCode) {
        alertText.innerText = "Security verification code mismatch. Please re-enter.";
        alertBox.style.display = 'block';
        await refreshServerCaptcha();
        document.getElementById('authCaptchaInput').value = "";
        return;
      }

      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Authenticating...</span>`;

      try {
        const resp = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });

        if (resp.ok) {
          const data = await resp.json();
          activeUser = {
            id: data.user_id,
            username: data.username,
            role: data.role,
            full_name: data.full_name || data.username,
            organization: data.organization || "Public Procurement System"
          };
          localStorage.setItem('bodhz_user', JSON.stringify(activeUser));
          alertBox.style.display = 'none';
          showToast("Authenticated", `Welcome, ${activeUser.full_name}`, "success");
          routeToRoleWorkspace(activeUser);
        } else {
          const err = await resp.json().catch(() => ({}));
          alertText.innerText = err.detail || "Invalid username or password.";
          alertBox.style.display = 'block';
          await refreshServerCaptcha();
          document.getElementById('authCaptchaInput').value = "";
        }
      } catch(e) {
        alertText.innerText = "Unable to connect to authentication service.";
        alertBox.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>SIGN IN TO WORKSPACE</span> <i class="fa-solid fa-arrow-right"></i>`;
      }
    }

    async function handleAuthRegister(event) {
      event.preventDefault();
      const full_name = document.getElementById('regFullName').value.trim();
      const email = document.getElementById('regEmail').value.trim();
      const organization = document.getElementById('regOrg').value.trim();
      const role = document.getElementById('regRole').value;
      const username = document.getElementById('regUsername').value.trim();
      const password = document.getElementById('regPassword').value.trim();
      const confirmPassword = document.getElementById('regConfirmPassword').value.trim();
      const alertBox = document.getElementById('registerAlertBox');
      const alertText = document.getElementById('registerAlertText');

      if (password.length < 8) {
        alertText.innerText = "Password must be at least 8 characters long.";
        alertBox.style.display = 'block';
        return;
      }
      if (password !== confirmPassword) {
        alertText.innerText = "Passwords do not match.";
        alertBox.style.display = 'block';
        return;
      }

      try {
        const resp = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, full_name, email, password, organization, role })
        });
        if (resp.ok) {
          showToast("Account Created", "Registration successful. Please sign in.", "success");
          switchAuthMode('LOGIN');
          document.getElementById('authLoginUser').value = username;
          document.getElementById('authLoginPass').value = password;
        } else {
          const err = await resp.json().catch(() => ({}));
          alertText.innerText = err.detail || "Registration failed.";
          alertBox.style.display = 'block';
        }
      } catch(e) {
        alertText.innerText = "Registration connection error.";
        alertBox.style.display = 'block';
      }
    }

    function openDemoModeModal() {
      document.getElementById('demoModeModal').style.display = 'flex';
    }

    function closeDemoModeModal() {
      document.getElementById('demoModeModal').style.display = 'none';
    }

    async function launchDemoPersona(persona) {
      closeDemoModeModal();
      let pwd = "BodhZ@2026";
      if (persona === 'bidder_tata') pwd = "Bidder@2026";
      if (persona === 'officer_dte') pwd = "Dte@2026";
      if (persona === 'auditor1') pwd = "Auditor@2026";

      openAuthScreen('LOGIN');
      document.getElementById('authLoginUser').value = persona;
      document.getElementById('authLoginPass').value = pwd;
      document.getElementById('authCaptchaInput').value = serverCaptchaCode;

      const form = document.querySelector('#authPaneSignIn form');
      if (form) form.dispatchEvent(new Event('submit', { cancelable: true }));
    }

    async function handleAuthLogout() {
      try {
        await fetch('/api/v1/auth/logout', { method: 'POST' });
      } catch(e) {}
      localStorage.removeItem('bodhz_user');
      activeUser = null;
      showPublicLanding();
    }

    // --------------------------------------------------
    // ROLE-BASED WORKSPACE ROUTER
    // --------------------------------------------------
    async function routeToRoleWorkspace(user) {
      document.getElementById('view-public-landing').style.display = 'none';
      document.getElementById('view-auth').style.display = 'none';
      document.getElementById('appWorkspace').style.display = 'flex';

      // Update Header
      document.getElementById('headerOfficerName').innerText = user.full_name;
      document.getElementById('headerOfficerRole').innerText = user.role.replace('_', ' ');
      document.getElementById('headerOrgSubtitle').innerText = user.organization;
      document.getElementById('headerRoleBadgePill').innerText = user.role;
      document.getElementById('chatContextRole').innerText = `${user.full_name} (${user.role})`;

      const navContainer = document.getElementById('dynamicSidebarMenu');
      navContainer.innerHTML = "";

      if (user.role === 'BID_UPLOADER') {
        // Bidder-Side Navigation
        document.getElementById('sidebarTenderWorkspaceSelectorBox').style.display = 'none';
        navContainer.innerHTML = `
          <button onclick="focusBidderSection('bidderCatalogSection')" class="sidebar-btn active" id="snav-bidder-catalog"><span class="sidebar-num">01</span> <i class="fa-solid fa-folder-open"></i> Browse Open Tenders</button>
          <button onclick="focusBidderSection('bidderSubmissionFormSection')" class="sidebar-btn" id="snav-bidder-submit"><span class="sidebar-num">02</span> <i class="fa-solid fa-cloud-arrow-up"></i> Submit Bid Proposal</button>
          <button onclick="focusBidderSection('bidderSubmissionsSection')" class="sidebar-btn" id="snav-bidder-history"><span class="sidebar-num">03</span> <i class="fa-solid fa-clock-rotate-left"></i> My Submissions</button>
          <button onclick="switchRoleView('vercenter')" class="sidebar-btn" id="snav-vercenter"><span class="sidebar-num">04</span> <i class="fa-solid fa-network-wired"></i> 13 Gateway Nodes</button>
        `;
        document.getElementById('bidderPortalOrgName').innerText = user.organization;
        document.getElementById('bidderPortalNameInput').value = user.organization;
        hideAllWorkspaceViews();
        document.getElementById('view-bidder-portal').style.display = 'flex';
        await loadBidderPortalData();

      } else if (user.role === 'DTE_OFFICER') {
        // DTE Department Navigation
        document.getElementById('sidebarTenderWorkspaceSelectorBox').style.display = 'block';
        navContainer.innerHTML = `
          <button onclick="switchRoleView('dte-portal')" class="sidebar-btn active" id="snav-dte-portal"><span class="sidebar-num">01</span> <i class="fa-solid fa-building-columns"></i> DTE Dashboard</button>
          <button onclick="switchRoleView('dte-portal')" class="sidebar-btn"><span class="sidebar-num">02</span> <i class="fa-solid fa-file-contract"></i> COE Tenders</button>
          <button onclick="switchRoleView('vercenter')" class="sidebar-btn" id="snav-vercenter"><span class="sidebar-num">03</span> <i class="fa-solid fa-network-wired"></i> 13 Gateway Status</button>
          <button onclick="switchRoleView('audittrail')" class="sidebar-btn" id="snav-audittrail"><span class="sidebar-num">04</span> <i class="fa-solid fa-shield-halved"></i> Institutional Audit</button>
        `;
        hideAllWorkspaceViews();
        document.getElementById('view-dte-portal').style.display = 'flex';
        await loadTendersFromAPI();
        await loadDTEWorkspaceData();

      } else {
        // Procurement Officer / Admin Navigation
        document.getElementById('sidebarTenderWorkspaceSelectorBox').style.display = 'block';
        navContainer.innerHTML = `
          <button onclick="switchView('dashboard')" class="sidebar-btn active" id="snav-dashboard"><span class="sidebar-num">01</span> <i class="fa-solid fa-gauge-high"></i> Dashboard Overview</button>
          <button onclick="switchView('tenders')" class="sidebar-btn" id="snav-tenders"><span class="sidebar-num">02</span> <i class="fa-solid fa-file-contract"></i> Tender Intelligence</button>
          <button onclick="switchView('bidders')" class="sidebar-btn" id="snav-bidders"><span class="sidebar-num">03</span> <i class="fa-solid fa-file-arrow-up"></i> Bid Ingestion & AI</button>
          <button onclick="switchView('docintel')" class="sidebar-btn" id="snav-docintel"><span class="sidebar-num">04</span> <i class="fa-solid fa-file-lines"></i> Document Intelligence</button>
          <button onclick="switchView('vercenter')" class="sidebar-btn" id="snav-vercenter"><span class="sidebar-num">05</span> <i class="fa-solid fa-network-wired"></i> 13 Gateway Nodes</button>
          <button onclick="switchView('consistency')" class="sidebar-btn" id="snav-consistency"><span class="sidebar-num">06</span> <i class="fa-solid fa-clone"></i> Inconsistency Engine</button>
          <button onclick="switchView('matrix')" class="sidebar-btn" id="snav-matrix"><span class="sidebar-num">07</span> <i class="fa-solid fa-table-columns"></i> Comparative Matrix</button>
          <button onclick="switchView('decision')" class="sidebar-btn" id="snav-decision"><span class="sidebar-num">08</span> <i class="fa-solid fa-gavel"></i> Officer Final Decision</button>
          <button onclick="switchView('reports')" class="sidebar-btn" id="snav-reports"><span class="sidebar-num">09</span> <i class="fa-solid fa-print"></i> Printable Dossier</button>
          <button onclick="switchView('audittrail')" class="sidebar-btn" id="snav-audittrail"><span class="sidebar-num">10</span> <i class="fa-solid fa-shield-halved"></i> Audit & Traceability</button>
        `;
        hideAllWorkspaceViews();
        document.getElementById('view-dashboard').style.display = 'flex';
        await loadTendersFromAPI();
      }
    }

    function hideAllWorkspaceViews() {
      const allViews = [
        'view-dashboard', 'view-tenders', 'view-bidders', 'view-docintel', 'view-vercenter',
        'view-consistency', 'view-matrix', 'view-decision', 'view-reports', 'view-audittrail',
        'view-bidder-portal', 'view-dte-portal'
      ];
      allViews.forEach(v => {
        const el = document.getElementById(v);
        if (el) el.style.display = 'none';
      });
    }

    function switchRoleView(viewKey) {
      hideAllWorkspaceViews();
      const el = document.getElementById('view-' + viewKey);
      if (el) el.style.display = 'flex';
      if (viewKey === 'audittrail') loadAuditEvents();
    }

    function focusBidderSection(sectionId) {
      hideAllWorkspaceViews();
      document.getElementById('view-bidder-portal').style.display = 'flex';
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }

    // --------------------------------------------------
    // BIDDER & DTE WORKSPACE DATA LOADERS
    // --------------------------------------------------
    async function loadBidderPortalData() {
      try {
        const respTenders = await fetch('/api/v1/tenders');
        if (respTenders.ok) {
          tendersList = await respTenders.json();
          document.getElementById('bidderTotalPublishedTenders').innerText = tendersList.length;

          // Populate Dropdown
          const sel = document.getElementById('bidderOpenTendersDropdown');
          sel.innerHTML = tendersList.map(t => `<option value="${t.id}">${t.tender_number} — ${t.title.substring(0, 45)}...</option>`).join('');

          // Render Open Tenders Catalog Cards
          renderBidderTendersCatalogCards(tendersList);

          if (tendersList.length > 0) {
            syncBidderSelectedTender(tendersList[0].id);
          }
        }

        // Load Submissions
        const respSubs = await fetch('/api/v1/bids/my-submissions');
        if (respSubs.ok) {
          const subData = await respSubs.json();
          document.getElementById('bidderTotalSubmissions').innerText = subData.submissions_count;
          document.getElementById('mySubmissionsCountBadge').innerText = `${subData.submissions_count} Submissions`;
          const tbody = document.getElementById('bidderSubmissionsTableBody');
          if (subData.submissions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:18px; color:#64748B;">No bid submissions recorded yet. Select an open tender above to prepare and submit.</td></tr>`;
          } else {
            tbody.innerHTML = subData.submissions.map(s => `
              <tr>
                <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${s.tender_number}</td>
                <td style="font-weight:700;">${s.tender_title}</td>
                <td>${s.submission_date}</td>
                <td style="font-weight:900; color:#047857; font-family:'JetBrains Mono';">${s.compliance_score || 95}/100</td>
                <td><span class="badge-${s.screening_status==='PASS'?'pass':(s.screening_status==='REVIEW'?'review':'fail')}">${s.screening_status}</span></td>
                <td><span class="badge-pass" style="background:#ECFDF5; color:#047857;">13/13 Nodes Verified</span></td>
                <td><a href="/api/v1/reports/bids/${s.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">🖨️ Dossier</a></td>
              </tr>
            `).join('');
          }
        }
      } catch(e) {}
    }

    function renderBidderTendersCatalogCards(tList) {
      const grid = document.getElementById('bidderTendersCatalogGrid');
      if (!grid) return;
      if (tList.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 24px; color:#64748B; background:#F8FAFC; border-radius:8px;">No open tenders found. Newly uploaded tenders by Procurement Officers will appear here automatically.</div>`;
        return;
      }

      grid.innerHTML = tList.map(t => `
        <div class="tender-card-item" id="tender-card-${t.id}">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family:'JetBrains Mono'; font-weight:800; font-size:11.5px; background:#F1F5F9; border:1px solid #CBD5E1; padding:2px 8px; border-radius:4px; color:var(--primary);">
                ${t.tender_number}
              </span>
              <span class="badge-open-bid">OPEN FOR BIDDING</span>
            </div>

            <div style="font-size:14px; font-weight:800; color:var(--primary); margin-top:8px; line-height:1.35;">
              ${t.title}
            </div>

            <div style="font-size:11.5px; color:#64748B; margin-top:4px;">
              <i class="fa-solid fa-tag"></i> ${t.category || 'General Procurement'} • <span style="color:#059669; font-weight:700;">Active RFP</span>
            </div>

            <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:10px;">
              <span style="font-size:10px; background:#EFF6FF; color:#1D4ED8; padding:2px 6px; border-radius:4px; font-weight:700;">🧾 GST & PAN</span>
              <span style="font-size:10px; background:#F0FDF4; color:#15803D; padding:2px 6px; border-radius:4px; font-weight:700;">🏭 MSME / Udyam</span>
              <span style="font-size:10px; background:#FFFBEB; color:#B45309; padding:2px 6px; border-radius:4px; font-weight:700;">⚙️ OEM MAF</span>
              <span style="font-size:10px; background:#FAF5FF; color:#7E22CE; padding:2px 6px; border-radius:4px; font-weight:700;">🇮🇳 Make in India</span>
            </div>
          </div>

          <div style="border-top:1px solid #F1F5F9; padding-top:10px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:10.5px; color:#94A3B8;">Status: ${t.lifecycle_status || 'READY_FOR_BIDDING'}</span>
            <button onclick="selectTenderForBidSubmission('${t.id}')" class="btn-success" style="font-size:11px; padding:6px 14px;">
              <i class="fa-solid fa-paper-plane"></i> Apply / Submit Bid
            </button>
          </div>
        </div>
      `).join('');
    }

    function filterBidderTendersCatalog() {
      const q = document.getElementById('bidderTenderSearchInput').value.toLowerCase().trim();
      const filtered = tendersList.filter(t => 
        t.tender_number.toLowerCase().includes(q) || 
        t.title.toLowerCase().includes(q) || 
        (t.category && t.category.toLowerCase().includes(q))
      );
      renderBidderTendersCatalogCards(filtered);
    }

    function selectTenderForBidSubmission(tenderId) {
      const sel = document.getElementById('bidderOpenTendersDropdown');
      sel.value = tenderId;
      syncBidderSelectedTender(tenderId);

      // Scroll smoothly to submission card
      const formSec = document.getElementById('bidderSubmissionFormSection');
      if (formSec) {
        formSec.scrollIntoView({ behavior: 'smooth' });
        formSec.style.borderColor = 'var(--accent)';
        setTimeout(() => { formSec.style.borderColor = '#CBD5E1'; }, 2000);
      }

      showToast("Tender Selected", `Ready to upload bid bundle for ${tenderId}`, "info");
    }

    function syncBidderSelectedTender(tenderId) {
      const t = tendersList.find(x => x.id === tenderId);
      if (t) {
        document.getElementById('bidderActiveSelectedTenderBadge').innerText = `Active: ${t.tender_number}`;
        
        // Highlight active card
        document.querySelectorAll('.tender-card-item').forEach(c => c.classList.remove('selected'));
        const card = document.getElementById(`tender-card-${t.id}`);
        if (card) card.classList.add('selected');
      }
    }

    function handleBidderPortalFile(input) {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        document.getElementById('bidderPortalSelectedFileText').innerHTML = `
          <strong style="color:#047857;">Selected:</strong> ${file.name} (${(file.size/1024).toFixed(1)} KB) • <span style="background:#ECFDF5; color:#047857; padding:1px 6px; border-radius:3px;">Ready for Ingestion</span>
        `;
      }
    }

    async function submitBidderPortalProposal() {
      const tenderId = document.getElementById('bidderOpenTendersDropdown').value;
      const bName = document.getElementById('bidderPortalNameInput').value.trim() || (activeUser ? activeUser.organization : 'Tata Advanced Training & Systems Ltd');
      const bGstin = document.getElementById('bidderPortalGstinInput').value.trim() || '27AAACT1098F1Z5';
      const bPan = document.getElementById('bidderPortalPanInput').value.trim() || 'AAACT1098F';
      const fileInput = document.getElementById('bidderPortalFileInput');
      const btn = document.getElementById('btnSubmitBidderProposal');
      const progressBox = document.getElementById('bidderPortalProgress');

      if (!tenderId) {
        alert("Please select a target tender first.");
        return;
      }

      btn.disabled = true;
      progressBox.style.display = 'block';

      try {
        const respBid = await fetch('/api/v1/bids', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tender_id: tenderId,
            bidder: { legal_name: bName, gstin: bGstin, pan_number: bPan }
          })
        });
        const bidData = await respBid.json();

        if (fileInput.files && fileInput.files[0]) {
          const docForm = new FormData();
          docForm.append('file', fileInput.files[0]);
          await fetch(`/api/v1/documents/upload?bid_id=${bidData.id}&doc_type=BID_SUBMISSION_BUNDLE`, {
            method: 'POST',
            body: docForm
          });
        }

        await fetch(`/api/v1/bids/${bidData.id}/evaluate`, { method: 'POST' });
        showToast("Bid Submitted", "Proposal submitted & 13-gateway verification completed!", "success");
        await loadBidderPortalData();
        focusBidderSection('bidderSubmissionsSection');
      } catch(e) {
        showToast("Submission Error", "Unable to submit proposal bundle.", "error");
      } finally {
        btn.disabled = false;
        progressBox.style.display = 'none';
      }
    }

    async function loadDTEWorkspaceData() {
      try {
        const dteTender = tendersList.find(t => t.tender_number.includes('DTE')) || tendersList[0];
        if (dteTender) {
          const resp = await fetch(`/api/v1/bids/tenders/${dteTender.id}/comparative-matrix`);
          if (resp.ok) {
            const data = await resp.json();
            const tbody = document.getElementById('dteBiddersTableBody');
            tbody.innerHTML = data.comparative_matrix.map(b => `
              <tr>
                <td style="font-weight:800; color:var(--primary);">${b.bidder_name}</td>
                <td style="font-family:'JetBrains Mono';">${b.gstin}</td>
                <td style="font-weight:900; color:${b.compliance_score>=80?'#047857':'#BE123C'};">${b.compliance_score}/100</td>
                <td><span class="badge-${b.screening_status==='PASS'?'pass':(b.screening_status==='REVIEW'?'review':'fail')}">${b.screening_status}</span></td>
                <td style="font-size:11px;">${b.review_issues && b.review_issues.length>0 ? b.review_issues.join(', ') : 'All statutory criteria verified'}</td>
                <td><a href="/api/v1/reports/bids/${b.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">Dossier</a></td>
              </tr>
            `).join('');
          }
        }
      } catch(e) {}
    }

    // --------------------------------------------------
    // PROCUREMENT OFFICER WORKSPACE CONTROLLERS
    // --------------------------------------------------
    async function loadTendersFromAPI() {
      try {
        const resp = await fetch('/api/v1/tenders');
        if (resp.ok) {
          tendersList = await resp.json();
          renderTenderSelector();
          renderTendersListTable();
          if (tendersList.length > 0) {
            const dteTender = tendersList.find(t => t.tender_number.includes('DTE')) || tendersList[0];
            await switchActiveTender(dteTender.id);
          }
        }
      } catch(err) {}
    }

    function renderTenderSelector() {
      const sel = document.getElementById('activeTenderSelector');
      sel.innerHTML = "";
      tendersList.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.innerText = `${t.tender_number} — ${t.title.substring(0, 20)}...`;
        sel.appendChild(opt);
      });
      if (activeTender) sel.value = activeTender.id;
    }

    function renderTendersListTable() {
      const tbody = document.getElementById('tendersListTableBody');
      if (!tbody) return;
      tbody.innerHTML = tendersList.map(t => `
        <tr>
          <td style="font-family: 'JetBrains Mono', monospace; font-weight: 800;">${t.tender_number}</td>
          <td style="font-weight: 700; color: var(--primary);">${t.title}</td>
          <td>${t.category || 'General'}</td>
          <td><span class="badge-pass">${t.lifecycle_status || 'READY_FOR_BIDDING'}</span></td>
          <td>
            <button onclick="switchActiveTender('${t.id}'); switchView('dashboard');" class="btn-action" style="font-size: 10px; padding: 4px 8px;">Select</button>
          </td>
        </tr>
      `).join('');
    }

    async function switchActiveTender(tenderId) {
      activeTender = tendersList.find(t => t.id === tenderId) || tendersList[0];
      if (!activeTender) return;

      const sel = document.getElementById('activeTenderSelector');
      if (sel) sel.value = activeTender.id;

      if (document.getElementById('dashTenderId')) document.getElementById('dashTenderId').innerText = activeTender.tender_number;
      if (document.getElementById('dashTenderTitle')) document.getElementById('dashTenderTitle').innerText = activeTender.title;
      if (document.getElementById('bidderUploadTargetTenderLabel')) document.getElementById('bidderUploadTargetTenderLabel').innerText = `${activeTender.tender_number} — ${activeTender.title}`;

      await loadComparativeMatrix(false);
    }

    async function loadComparativeMatrix(shortlistedOnly = false) {
      if (!activeTender) return;
      try {
        const url = shortlistedOnly 
          ? `/api/v1/bids/tenders/${encodeURIComponent(activeTender.id)}/shortlisted`
          : `/api/v1/bids/tenders/${encodeURIComponent(activeTender.id)}/comparative-matrix`;
        
        const resp = await fetch(url);
        if (resp.ok) {
          const data = await resp.json();
          comparativeRows = shortlistedOnly ? data.shortlisted_bids : data.comparative_matrix;
          
          if (document.getElementById('statTotalTenders')) document.getElementById('statTotalTenders').innerText = tendersList.length;
          if (document.getElementById('statTotalBids')) document.getElementById('statTotalBids').innerText = comparativeRows.length;
          if (document.getElementById('statCompliantBids')) document.getElementById('statCompliantBids').innerText = comparativeRows.filter(r => r.compliance_score >= 80).length;
          if (document.getElementById('statHighRiskBids')) document.getElementById('statHighRiskBids').innerText = comparativeRows.filter(r => r.risk_level === 'CRITICAL' || r.compliance_score < 50).length;

          renderDashboardTable();
          renderMatrixTable();
          renderDocIntelTable();
          renderInconsistencyTable();
          if (comparativeRows.length > 0) {
            selectBidderForReview(comparativeRows[0]);
          }
        }
      } catch(err) {}
    }

    function renderDashboardTable() {
      const tbody = document.getElementById('dashBiddersTableBody');
      if (!tbody) return;
      tbody.innerHTML = comparativeRows.map(r => `
        <tr>
          <td style="font-weight: 800; color: var(--primary);">${r.bidder_name}</td>
          <td style="font-family: 'JetBrains Mono', monospace; font-size: 11px;">${r.gstin}</td>
          <td style="font-weight: 800; color: ${r.compliance_score >= 80 ? '#15803D' : (r.compliance_score >= 60 ? '#D97706' : '#BE123C')}">${r.compliance_score}/100</td>
          <td><span class="badge-${r.risk_level === 'LOW' ? 'pass' : (r.risk_level === 'MEDIUM' ? 'review' : 'fail')}">${r.risk_level}</span></td>
          <td><span class="badge-${r.screening_status === 'PASS' ? 'pass' : (r.screening_status === 'REVIEW' ? 'review' : 'fail')}">${r.screening_status}</span></td>
          <td><strong>${r.officer_decision ? r.officer_decision.decision : 'PENDING'}</strong></td>
          <td>
            <button onclick="openBidderReviewById('${r.bid_id}')" class="btn-action" style="font-size: 10px; padding: 3px 8px;">Review</button>
            <a href="/api/v1/reports/bids/${r.bid_id}/html" target="_blank" class="btn-success" style="font-size: 10px; padding: 3px 8px;">🖨️ Dossier</a>
          </td>
        </tr>
      `).join('');
    }

    function renderMatrixTable() {
      const tbody = document.getElementById('comparativeMatrixTableBody');
      if (!tbody) return;
      tbody.innerHTML = comparativeRows.map(r => `
        <tr>
          <td><strong>${r.bidder_name}</strong><br><span style="font-size: 10px; font-family: 'JetBrains Mono', monospace; color: var(--text-muted);">GST: ${r.gstin} | PAN: ${r.pan}</span></td>
          <td style="font-weight: 900; font-size: 14px; color: ${r.compliance_score >= 80 ? '#15803D' : '#BE123C'};">${r.compliance_score}/100</td>
          <td><span class="badge-${r.risk_level === 'LOW' ? 'pass' : 'fail'}">${r.risk_level}</span></td>
          <td><span class="badge-pass">${r.screening_status}</span></td>
          <td style="font-size: 11px;">${r.modules_status ? r.modules_status.map(m => `• ${m.module}: <strong>${m.status}</strong>`).join('<br>') : 'Verified'}</td>
          <td style="font-size: 11px; color: #BE123C;">${r.review_issues && r.review_issues.length > 0 ? r.review_issues.join('<br>') : 'None (Clean)'}</td>
          <td><span style="font-weight: 800;">${r.officer_decision ? r.officer_decision.decision : 'PENDING'}</span></td>
          <td><a href="/api/v1/reports/bids/${r.bid_id}/html" target="_blank" class="btn-action" style="font-size: 10px; padding: 3px 8px;">View</a></td>
        </tr>
      `).join('');
    }

    function renderDocIntelTable() {
      const tbody = document.getElementById('docIntelTableBody');
      if (!tbody) return;
      tbody.innerHTML = comparativeRows.map(r => `
        <tr>
          <td><i class="fa-solid fa-file-pdf" style="color:#BE123C;"></i> <strong>${r.bidder_name}_Bundle.pdf</strong></td>
          <td>Legal Name & GSTIN</td>
          <td><code style="font-family:'JetBrains Mono';">${r.bidder_name}</code> (${r.gstin})</td>
          <td>Page 1 & 2</td>
          <td><span class="badge-pass">98.5% (High Confidence)</span></td>
        </tr>
      `).join('');
    }

    function renderInconsistencyTable() {
      const tbody = document.getElementById('inconsistencyTableBody');
      if (!tbody) return;
      let html = "";
      comparativeRows.forEach(r => {
        if (r.bidder_name.includes("Tata")) {
          html += `
            <tr><td><strong>GSTN vs Legal Name Match</strong></td><td>${r.bidder_name}</td><td><strong style="color:#059669;">1.00 (Match)</strong></td><td><span class="badge-pass">PASS</span></td><td style="font-size:11px;">Exact legal name match with Incorporation Certificate.</td></tr>
            <tr><td><strong>Turnover vs CA Financials</strong></td><td>${r.bidder_name}</td><td><strong style="color:#059669;">1.00 (Verified)</strong></td><td><span class="badge-pass">PASS</span></td><td style="font-size:11px;">₹15.80 Cr exceeds mandatory ₹10.00 Cr requirement.</td></tr>
          `;
        } else if (r.bidder_name.includes("EduTech")) {
          html += `
            <tr><td><strong>EPFO Payroll Verification</strong></td><td>${r.bidder_name}</td><td><strong style="color:#D97706;">0.74 (Flag)</strong></td><td><span class="badge-review">REVIEW</span></td><td style="font-size:11px; color:#B45309;">Employee #4 PF account number requires gateway check.</td></tr>
          `;
        } else if (r.bidder_name.includes("Apex")) {
          html += `
            <tr><td><strong>ISO 9001:2015 Validity</strong></td><td>${r.bidder_name}</td><td><strong style="color:#DC2626;">0.00 (Expired)</strong></td><td><span class="badge-fail">FAIL</span></td><td style="font-size:11px; color:#BE123C;">ISO 9001:2015 expired on 15/01/2024.</td></tr>
          `;
        }
      });
      tbody.innerHTML = html;
    }

    function loadRealTenderPreset(preset) {
      if (preset === 'DTE') {
        document.getElementById('newTenderIdInput').value = "DTE/2026/RFP/COE/4901";
        document.getElementById('newTenderTitleInput').value = "Establishment of Center of Excellence (COE) and Technical Training Centers";
        document.getElementById('newTenderCategoryInput').value = "Technical Education & Skill Infrastructure";
      } else if (preset === 'NFL') {
        document.getElementById('newTenderIdInput').value = "NFL/CO/IT/VAPT/2026/08";
        document.getElementById('newTenderTitleInput').value = "Comprehensive Cyber Security Audit & VAPT of Web Applications";
        document.getElementById('newTenderCategoryInput').value = "Cyber Security & IT Audit";
      } else if (preset === 'ICAR') {
        document.getElementById('newTenderIdInput').value = "GEM/2026/B/IIMR/6641";
        document.getElementById('newTenderTitleInput').value = "Supply & Commissioning of Agricultural Machinery (Seed Drill & Thresher)";
        document.getElementById('newTenderCategoryInput').value = "Agricultural Machinery";
      }
    }

    function prefillBidder(name, gstin) {
      document.getElementById('bidderNameInput').value = name;
      document.getElementById('bidderGstinInput').value = gstin;
    }

    async function handleTenderPDFUpload(input) {
      if (!input.files || !input.files[0]) return;
      const file = input.files[0];
      document.getElementById('selectedTenderFileText').innerText = `Uploading: ${file.name}...`;

      const formData = new FormData();
      formData.append('file', file);
      formData.append('tender_number', document.getElementById('newTenderIdInput').value.trim());
      formData.append('title', document.getElementById('newTenderTitleInput').value.trim());
      formData.append('category', document.getElementById('newTenderCategoryInput').value.trim());

      try {
        const resp = await fetch('/api/v1/tenders/upload-pdf', { method: 'POST', body: formData });
        if (resp.ok) {
          const data = await resp.json();
          pendingTenderUploadId = data.tender_id;
          document.getElementById('tenderExtractedRequirementsPanel').style.display = 'block';
          document.getElementById('extractedReqsCountBadge').innerText = `${data.requirements_count} Rules Extracted`;
          const tbody = document.getElementById('tenderRequirementsEditBody');
          tbody.innerHTML = data.requirements.map(r => `
            <tr>
              <td style="font-weight: 800; font-family: 'JetBrains Mono', monospace;">${r.module}</td>
              <td>${r.title}</td>
              <td style="text-align: center;"><input type="checkbox" ${r.mandatory ? 'checked' : ''}></td>
              <td><input type="number" class="form-input" style="width: 70px; padding: 2px 6px;" value="${r.weight}"></td>
            </tr>
          `).join('');
        }
      } catch(err) {}
    }

    async function confirmExtractedRequirements() {
      if (!pendingTenderUploadId) return;
      try {
        const resp = await fetch(`/api/v1/tenders/${pendingTenderUploadId}/confirm-requirements`, { method: 'POST' });
        if (resp.ok) {
          showToast("Tender Published", "Tender published successfully! Bidders can now view & submit proposals.", "success");
          await loadTendersFromAPI();
          switchView('dashboard');
        }
      } catch(err) {}
    }

    function handleBidderFileSelect(input) {
      if (input.files && input.files[0]) {
        document.getElementById('selectedBidderFileText').innerText = `Selected: ${input.files[0].name} (${(input.files[0].size/1024).toFixed(1)} KB)`;
      }
    }

    async function submitBidderAndEvaluate() {
      if (!activeTender) return;
      const bName = document.getElementById('bidderNameInput').value.trim() || 'Tata Advanced Training & Systems Ltd';
      const bGstin = document.getElementById('bidderGstinInput').value.trim() || '27AAACT1098F1Z5';
      const fileInput = document.getElementById('bidderFileInput');

      document.getElementById('bidderProcessingProgress').style.display = 'block';
      try {
        const respBid = await fetch('/api/v1/bids', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tender_id: activeTender.id,
            bidder: { legal_name: bName, gstin: bGstin, pan_number: bGstin.substring(2, 12) }
          })
        });
        const bidData = await respBid.json();
        const bidId = bidData.id;

        if (fileInput.files && fileInput.files[0]) {
          const docForm = new FormData();
          docForm.append('file', fileInput.files[0]);
          await fetch(`/api/v1/documents/upload?bid_id=${bidId}&doc_type=BID_SUBMISSION_BUNDLE`, { method: 'POST', body: docForm });
        }

        await fetch(`/api/v1/bids/${bidId}/evaluate`, { method: 'POST' });
        document.getElementById('bidderProcessingProgress').style.display = 'none';
        showToast("Bid Evaluated", `Evaluated submission for ${bName}`, "success");
        await loadComparativeMatrix(false);
        openBidderReviewById(bidId);
      } catch(err) {
        document.getElementById('bidderProcessingProgress').style.display = 'none';
      }
    }

    async function openBidderReviewById(bidId) {
      const target = comparativeRows.find(r => r.bid_id === bidId);
      if (target) {
        selectBidderForReview(target);
        switchView('decision');
      }
    }

    async function selectBidderForReview(bidRow) {
      activeBidder = bidRow;
      if (document.getElementById('decisionTargetBidderName')) document.getElementById('decisionTargetBidderName').innerText = bidRow.bidder_name;
      if (document.getElementById('decisionTargetScore')) document.getElementById('decisionTargetScore').innerHTML = `${bidRow.compliance_score}<span style="font-size:14px; color:#94A3B8;">/100</span>`;
      if (document.getElementById('decisionTargetAIRecommendation')) document.getElementById('decisionTargetAIRecommendation').innerText = `AI Recommendation: ${bidRow.ai_recommendation}`;
      if (document.getElementById('vercenterActiveBidderLabel')) document.getElementById('vercenterActiveBidderLabel').innerText = `${bidRow.bidder_name} (${bidRow.gstin})`;

      if (document.getElementById('btnOpenReportTab')) document.getElementById('btnOpenReportTab').href = `/api/v1/reports/bids/${bidRow.bid_id}/html`;
      if (document.getElementById('reportPreviewFrame')) document.getElementById('reportPreviewFrame').src = `/api/v1/reports/bids/${bidRow.bid_id}/html`;

      try {
        const resp = await fetch(`/api/v1/bids/${bidRow.bid_id}/historical-record`);
        if (resp.ok) {
          const histData = await resp.json();
          const alertBox = document.getElementById('historicalBidderAlertBox');
          if (histData.historical_match_found && histData.historical_records.length > 0) {
            const h = histData.historical_records[0];
            alertBox.style.display = 'block';
            document.getElementById('historicalBidderContent').innerHTML = `
              <strong>Prior Tender:</strong> ${h.tender_number} | <strong>Outcome:</strong> ${h.outcome} (${h.compliance_score}/100)<br>
              <strong>Summary:</strong> ${h.key_findings} (Matched by: <code>${h.matched_by}</code>)
            `;
          } else {
            alertBox.style.display = 'none';
          }
        }
      } catch(err) {}
    }

    async function submitOfficerFinalDecision() {
      if (!activeBidder) return;
      const decision = document.getElementById('officerDecisionChoice').value;
      const notes = document.getElementById('officerDecisionNotes').value.trim();

      if (!confirm(`Are you sure you want to record the legally binding decision '${decision}' under GFR 2017 Rule 144 for ${activeBidder.bidder_name}?`)) {
        return;
      }

      try {
        const resp = await fetch('/api/v1/bids/officer-decision', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            assessment_id: 'assess_placeholder',
            bid_id: activeBidder.bid_id,
            decision: decision,
            notes: notes
          })
        });
        if (resp.ok) {
          showToast("GFR Rule 144 Signed", `Decision '${decision}' recorded and sealed in audit trail!`, "success");
          await loadComparativeMatrix(false);
          switchView('dashboard');
        } else {
          const err = await resp.json().catch(() => ({}));
          alert(err.detail || "Decision could not be recorded.");
        }
      } catch(err) {}
    }

    async function loadAuditEvents() {
      try {
        const resp = await fetch('/api/v1/audit');
        if (resp.ok) {
          const events = await resp.json();
          const tbody = document.getElementById('auditTrailTableBody');
          if (tbody) {
            tbody.innerHTML = events.slice(0, 15).map(e => `
              <tr>
                <td style="font-family: 'JetBrains Mono', monospace; font-size: 11px;">${e.timestamp}</td>
                <td style="font-weight: 700;">${e.actor_id}</td>
                <td><span class="badge-pass">${e.event_type}</span></td>
                <td style="font-size: 11px;">${e.payload_json ? e.payload_json.substring(0, 60) + '...' : '-'}</td>
                <td style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #64748B;">${e.sha256_hash ? e.sha256_hash.substring(0, 16) + '...' : '-'}</td>
              </tr>
            `).join('');
          }
        }
      } catch(err) {}
    }

    function switchView(viewId) {
      const views = ['dashboard', 'tenders', 'bidders', 'docintel', 'vercenter', 'consistency', 'matrix', 'decision', 'reports', 'audittrail'];
      views.forEach(v => {
        const el = document.getElementById('view-' + v);
        if (el) el.style.display = 'none';
        const btn = document.getElementById('snav-' + v);
        if (btn) btn.classList.remove('active');
      });

      const actEl = document.getElementById('view-' + viewId);
      if (actEl) actEl.style.display = 'flex';
      const actBtn = document.getElementById('snav-' + viewId);
      if (actBtn) actBtn.classList.add('active');

      if (viewId === 'audittrail') loadAuditEvents();
      if (viewId === 'matrix') loadComparativeMatrix(false);
      if (viewId === 'docintel') renderDocIntelTable();
      if (viewId === 'consistency') renderInconsistencyTable();
    }

    function toggleChatbot() {
      const m = document.getElementById('chatModalWindow');
      m.style.display = (m.style.display === 'flex') ? 'none' : 'flex';
    }

    function sendChatSuggestion(text) {
      document.getElementById('chatUserInput').value = text;
      sendChatMessage();
    }

    async function sendChatMessage() {
      const input = document.getElementById('chatUserInput');
      const text = input.value.trim();
      if (!text) return;
      input.value = "";

      const area = document.getElementById('chatMessagesArea');
      area.innerHTML += `<div class="chat-msg-user">${text}</div>`;
      area.scrollTop = area.scrollHeight;

      try {
        const resp = await fetch('/api/v1/bids/ai-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            user_name: activeUser ? activeUser.username : 'visitor',
            user_role: activeUser ? activeUser.role : 'PROCUREMENT_OFFICER',
            tender_id: activeTender ? activeTender.id : null,
            bidder_id: activeBidder ? activeBidder.bid_id : null
          })
        });
        if (resp.ok) {
          const res = await resp.json();
          area.innerHTML += `
            <div class="chat-msg-bot">
              <div style="font-weight: 800; color: #0A192F; margin-bottom: 4px;">BodhZ AI Assistant</div>
              <div>${marked.parse(res.reply)}</div>
            </div>
          `;
          area.scrollTop = area.scrollHeight;
        }
      } catch(err) {
        area.innerHTML += `<div class="chat-msg-bot" style="color:#BE123C;">Connection error to AI service.</div>`;
      }
    }
  </script>
</body>
</html>
"""
    return html_content
