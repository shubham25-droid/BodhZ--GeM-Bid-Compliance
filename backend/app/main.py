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
    documents_router, verification_router, audit_router, reports_router,
    dte_router, bidder_router
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
        "It provides role-based decision support for Procurement Officers, Department Officials (DTE Maharashtra), "
        "and Bidders, automating statutory verification while preserving 100% human legal authority."
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
# 3. INCLUDE API ROUTERS (ROLE-SCOPED ARCHITECTURE)
# --------------------------------------------------
app.include_router(health_router.router, prefix=settings.API_V1_STR)
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(tenders_router.router, prefix=settings.API_V1_STR)
app.include_router(bids_router.router, prefix=settings.API_V1_STR)
app.include_router(documents_router.router, prefix=settings.API_V1_STR)
app.include_router(verification_router.router, prefix=settings.API_V1_STR)
app.include_router(audit_router.router, prefix=settings.API_V1_STR)
app.include_router(reports_router.router, prefix=settings.API_V1_STR)
app.include_router(dte_router.router, prefix=settings.API_V1_STR)
app.include_router(bidder_router.router, prefix=settings.API_V1_STR)


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

        /* 3D LOGO & ASHOKA CHAKRA KEYFRAME ANIMATIONS */
    .logo-3d-animated {
      transform-style: preserve-3d;
      animation: float3D 4.5s ease-in-out infinite alternate, glowPulse 3s ease-in-out infinite alternate;
      transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
      will-change: transform, filter;
    }

    .logo-3d-animated:hover {
      transform: perspective(900px) rotateY(18deg) rotateX(-8deg) scale(1.1) translateY(-4px);
      filter: drop-shadow(0 20px 35px rgba(245, 158, 11, 0.7)) drop-shadow(0 0 25px rgba(59, 130, 246, 0.5));
    }

    @keyframes float3D {
      0% { transform: perspective(900px) rotateY(-10deg) rotateX(6deg) translateY(0px); }
      50% { transform: perspective(900px) rotateY(12deg) rotateX(-5deg) translateY(-8px); }
      100% { transform: perspective(900px) rotateY(-8deg) rotateX(8deg) translateY(-3px); }
    }

    @keyframes glowPulse {
      0% { filter: drop-shadow(0 8px 16px rgba(245, 158, 11, 0.35)); }
      100% { filter: drop-shadow(0 18px 32px rgba(245, 158, 11, 0.7)) drop-shadow(0 0 20px rgba(30, 58, 138, 0.4)); }
    }

    .chakra-rotate-slow {
      animation: rotateAshokaChakra 70s linear infinite;
      transform-origin: center;
      pointer-events: none;
    }

    .chakra-rotate-medium {
      animation: rotateAshokaChakra 40s linear infinite;
      transform-origin: center;
      pointer-events: none;
    }

    @keyframes rotateAshokaChakra {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    @keyframes pulseRadarGreen {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    @keyframes pulseRadarSaffron {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }

    @keyframes float3DCard {
      0% { transform: translateY(0px) rotateX(0deg); }
      50% { transform: translateY(-6px) rotateX(2deg); }
      100% { transform: translateY(0px) rotateX(0deg); }
    }

    @keyframes goldShimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }

    /* PUBLIC LANDING PAGE STYLES */
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
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    .public-nav-links { display: flex; gap: 24px; align-items: center; font-size: 13px; font-weight: 700; }
    .public-nav-link { color: #CBD5E1; text-decoration: none; transition: all 0.2s; cursor: pointer; display: flex; align-items: center; gap: 6px; }
    .public-nav-link:hover { color: var(--accent); transform: translateY(-1px); }

    .tricolor-stripe-header {
      height: 3.5px;
      width: 100%;
      background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
      box-shadow: 0 0 10px rgba(255, 153, 51, 0.4);
    }

    .landing-hero {
      background: radial-gradient(circle at 80% 20%, #1E3A8A 0%, #0A192F 45%, #030814 100%);
      color: #FFFFFF;
      padding: 68px 36px 64px 36px;
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

    .hero-chakra-watermark {
      position: absolute;
      top: -140px;
      right: -80px;
      width: 620px;
      height: 620px;
      opacity: 0.08;
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
      padding: 6px 16px;
      border-radius: 30px;
      font-size: 11.5px;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);
    }

    .landing-title { font-size: 38px; font-weight: 900; letter-spacing: -1px; line-height: 1.18; color: #FFFFFF; }
    .landing-subtitle { font-size: 15.5px; color: #94A3B8; margin-top: 14px; line-height: 1.6; max-width: 560px; }
    .landing-cta-row { display: flex; gap: 12px; margin-top: 26px; flex-wrap: wrap; }

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
      transition: all 0.25s;
    }
    .btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(245, 158, 11, 0.5); }

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
      transition: all 0.25s;
    }
    .btn-hero-secondary:hover { background: rgba(255, 255, 255, 0.15); border-color: #FFFFFF; transform: translateY(-2px); }

    .hero-pipeline-card {
      background: rgba(15, 23, 42, 0.85);
      border: 1.5px solid rgba(245, 158, 11, 0.3);
      backdrop-filter: blur(16px);
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 24px 50px rgba(0,0,0,0.45), 0 0 30px rgba(245,158,11,0.12);
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
      transform-style: preserve-3d;
    }

    .pipeline-step {
      display: flex;
      align-items: center;
      gap: 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 10px 14px;
      border-radius: 10px;
      transition: all 0.25s;
    }
    .pipeline-step:hover { background: rgba(255, 255, 255, 0.1); transform: translateX(4px); border-color: var(--accent); }

    .pipeline-step-icon {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13.5px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Trust Strip with Indian Sovereign Micro-Badge */
    .trust-strip {
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 16px 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 36px;
      flex-wrap: wrap;
      box-shadow: 0 4px 14px rgba(0,0,0,0.03);
      position: relative;
    }

    .trust-item { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 800; color: var(--primary); letter-spacing: 0.5px; }
    .trust-item i { color: #059669; font-size: 14px; }

    /* SECTION CONTAINERS & 3D CARDS */
    .landing-section { max-width: 1180px; margin: 60px auto; padding: 0 24px; width: 100%; position: relative; }
    
    .section-header { text-align: center; margin-bottom: 34px; position: relative; }
    .section-header-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(90deg, rgba(255,153,51,0.12) 0%, rgba(255,255,255,0.9) 50%, rgba(19,136,8,0.12) 100%);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #0A192F;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 14px;
      border-radius: 20px;
      margin-bottom: 10px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .section-title { font-size: 28px; font-weight: 900; color: var(--primary); letter-spacing: -0.5px; }
    .section-desc { font-size: 14px; color: var(--text-muted); margin-top: 6px; max-width: 720px; margin-left: auto; margin-right: auto; line-height: 1.55; }

    /* 3D LUXURY CARD STYLE */
    .card-3d-fancy {
      background: #FFFFFF;
      border: 1.5px solid #E2E8F0;
      border-radius: 16px;
      padding: 26px;
      box-shadow: 0 10px 30px -10px rgba(10,25,47,0.06), 0 0 20px rgba(245,158,11,0.03);
      transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
      transform-style: preserve-3d;
    }
    .card-3d-fancy:hover {
      transform: perspective(900px) rotateX(3deg) translateY(-8px) scale(1.015);
      box-shadow: 0 25px 50px -12px rgba(10,25,47,0.18), 0 0 30px rgba(245,158,11,0.15);
      border-color: #CBD5E1;
    }

    /* What BodhZ Solves Battle Cards */
    .solve-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    
    .solve-card-challenge {
      background: linear-gradient(180deg, #FFFFFF 0%, #FFF5F5 100%);
      border: 1.5px solid #FECACA;
      border-top: 5px solid #DC2626;
      border-radius: 16px;
      padding: 26px;
      box-shadow: 0 10px 30px -10px rgba(220, 38, 38, 0.1);
      transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
      transform-style: preserve-3d;
    }
    .solve-card-challenge:hover {
      transform: perspective(900px) rotateX(3deg) translateY(-6px);
      box-shadow: 0 20px 45px -10px rgba(220, 38, 38, 0.2);
    }

    .solve-card-solution {
      background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%);
      border: 1.5px solid #A7F3D0;
      border-top: 5px solid #059669;
      border-radius: 16px;
      padding: 26px;
      box-shadow: 0 10px 30px -10px rgba(5, 150, 105, 0.15), 0 0 25px rgba(245, 158, 11, 0.1);
      transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
      transform-style: preserve-3d;
    }
    .solve-card-solution:hover {
      transform: perspective(900px) rotateX(3deg) translateY(-6px);
      box-shadow: 0 20px 45px -10px rgba(5, 150, 105, 0.25), 0 0 35px rgba(245, 158, 11, 0.2);
    }

    .solve-item { display: flex; align-items: flex-start; gap: 12px; margin-top: 12px; font-size: 13px; color: #334155; line-height: 1.5; }

    /* HOW IT WORKS 3D PIPELINE GRID */
    .flow-grid-5 { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; position: relative; }
    
    .flow-step-3d {
      background: #FFFFFF;
      border: 1.5px solid #E2E8F0;
      border-radius: 14px;
      padding: 20px 18px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      box-shadow: 0 4px 14px rgba(10,25,47,0.03);
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
      transform-style: preserve-3d;
    }
    .flow-step-3d:hover {
      transform: perspective(800px) translateY(-6px) rotateX(4deg);
      box-shadow: 0 16px 36px rgba(10,25,47,0.12), 0 0 20px rgba(245,158,11,0.15);
      border-color: var(--accent);
    }

    .flow-cube-num {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
      color: #F59E0B;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12.5px;
      font-weight: 900;
      box-shadow: 0 4px 12px rgba(10,25,47,0.25);
      border: 1px solid rgba(245,158,11,0.4);
    }

    /* 6 CAPABILITIES HOLOGRAPHIC GRID */
    .cap-grid-6 { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }
    
    .cap-card-3d {
      background: #FFFFFF;
      border: 1.5px solid #E2E8F0;
      border-radius: 14px;
      padding: 22px;
      display: flex;
      align-items: flex-start;
      gap: 16px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.02);
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
    }
    .cap-card-3d:hover {
      transform: translateY(-5px);
      box-shadow: 0 16px 35px rgba(10,25,47,0.1), 0 0 25px rgba(59,130,246,0.12);
      border-color: #94A3B8;
    }

    .cap-icon-box-3d {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
      color: #1D4ED8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
      border: 1px solid #BFDBFE;
      box-shadow: 0 4px 10px rgba(30, 58, 138, 0.08);
      transition: all 0.3s ease;
    }
    .cap-card-3d:hover .cap-icon-box-3d {
      background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%);
      color: #F59E0B;
      transform: scale(1.08) rotate(5deg);
      border-color: #F59E0B;
    }

    /* 13 STATUTORY GATEWAYS 3D GRID */
    .gateway-matrix-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
    
    .gateway-node-3d {
      background: #FFFFFF;
      border: 1.5px solid #E2E8F0;
      border-radius: 12px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
    }
    .gateway-node-3d:hover {
      transform: translateY(-4px);
      box-shadow: 0 14px 30px rgba(10,25,47,0.1), 0 0 20px rgba(16,185,129,0.12);
      border-color: #10B981;
    }

    .radar-beacon {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #10B981;
      animation: pulseRadarGreen 2s infinite;
      display: inline-block;
    }

    /* AI ASSISTS VS OFFICER DECIDES SPLIT EXECUTIVE MONUMENT */
    .split-authority-monument {
      background: #FFFFFF;
      border: 2px solid var(--primary);
      border-radius: 20px;
      padding: 34px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
      box-shadow: 0 16px 45px rgba(10,25,47,0.08), 0 0 35px rgba(245,158,11,0.08);
      position: relative;
      overflow: hidden;
    }

    .monument-chakra-center {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 280px;
      height: 280px;
      opacity: 0.05;
      color: #0A192F;
      pointer-events: none;
    }

    /* LIVE PREVIEW SIMULATOR CARD */
    .live-sim-card {
      background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
      border: 2px solid #CBD5E1;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 14px 38px rgba(10,25,47,0.08);
      position: relative;
      overflow: hidden;
    }

    /* GRAND CTA BANNER WITH TRICOLOR AURA */
    .cta-banner-indian {
      background: radial-gradient(circle at 10% 20%, #0A192F 0%, #061122 50%, #020710 100%);
      color: #FFFFFF;
      border-radius: 20px;
      padding: 44px 36px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      border: 1.5px solid rgba(245, 158, 11, 0.4);
      box-shadow: 0 20px 50px rgba(10,25,47,0.3), 0 0 40px rgba(245,158,11,0.15);
      position: relative;
      overflow: hidden;
    }

    .public-footer-indian {
      background-color: var(--primary-dark);
      color: #94A3B8;
      font-size: 12px;
      padding: 32px 36px 24px 36px;
      border-top: 3.5px solid var(--accent-orange);
      margin-top: 60px;
      position: relative;
    }

    /* AUTHENTICATION STYLES */
    .auth-page-wrapper { flex: 1; display: flex; align-items: center; justify-content: center; padding: 32px 20px; background: radial-gradient(circle at 10% 20%, #0A192F 0%, #030814 100%); min-height: 100vh; position: relative; overflow: hidden; }
    .auth-card { width: 100%; max-width: 1080px; min-height: 640px; background: #FFFFFF; border-radius: 24px; border: 1px solid rgba(245, 158, 11, 0.3); box-shadow: 0 30px 70px -15px rgba(0, 0, 0, 0.5), 0 0 30px rgba(245, 158, 11, 0.15); display: grid; grid-template-columns: 46% 54%; overflow: hidden; position: relative; z-index: 2; }
    .auth-left-brand { background: linear-gradient(150deg, #0A192F 0%, #071325 50%, #020710 100%); color: #FFFFFF; padding: 44px 38px; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    .auth-left-chakra-watermark { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 440px; height: 440px; opacity: 0.08; color: #F59E0B; pointer-events: none; }
    .auth-right-form-pane { padding: 42px 46px; display: flex; flex-direction: column; justify-content: space-between; background: #FFFFFF; }
    .auth-field { width: 100%; padding: 11px 14px 11px 38px; font-size: 13px; font-family: inherit; color: var(--text); background-color: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 8px; transition: all 0.25s ease; }
    .auth-field:focus { outline: none; background-color: #FFFFFF; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(30, 58, 138, 0.12); }
    .btn-auth-primary { width: 100%; background: linear-gradient(135deg, #0A192F 0%, #1E3A8A 100%); color: #FFFFFF; padding: 12px 18px; font-size: 13px; font-weight: 800; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 14px rgba(10, 25, 47, 0.25); transition: all 0.25s ease; }
    .btn-auth-primary:hover { background: linear-gradient(135deg, #1E3A8A 0%, #0A192F 100%); transform: translateY(-2px); box-shadow: 0 8px 22px rgba(10, 25, 47, 0.35); }
    .role-quick-chip-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
    .role-quick-chip { background: #F1F5F9; border: 1px solid #CBD5E1; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; color: #334155; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; transition: all 0.2s ease; }
    .role-quick-chip:hover { background: #0A192F; color: #FFFFFF; border-color: #0A192F; transform: translateY(-1px); }

    /* WORKSPACE UI STYLES */
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
    .card-panel { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; flex-direction: column; gap: 14px; transition: all 0.2s ease; position: relative; }
    .card-title { font-size: 13px; font-weight: 800; color: var(--primary); text-transform: uppercase; letter-spacing: 0.02em; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }

    .clean-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .clean-table th { background-color: var(--primary); color: #FFFFFF; text-transform: uppercase; font-size: 10.5px; font-weight: 800; padding: 10px 12px; text-align: left; }
    .clean-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
    .clean-table tr:hover { background-color: #F8FAFC; }

    .btn-action { background-color: var(--primary); color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 7px 14px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; text-decoration: none; }
    .btn-action:hover { background-color: #1E293B; transform: translateY(-1px); }
    .btn-success { background-color: #059669; color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 7px 14px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; text-decoration: none; }
    .btn-success:hover { background-color: #047857; transform: translateY(-1px); }
    .btn-warning { background-color: #D97706; color: #FFFFFF; font-size: 11.5px; font-weight: 800; border: none; padding: 7px 14px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; text-decoration: none; }
    .btn-warning:hover { background-color: #B45309; transform: translateY(-1px); }

    .badge-pass { background-color: #ECFDF5; color: #047857; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #A7F3D0; }
    .badge-review { background-color: #FFFBEB; color: #B45309; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #FDE68A; }
    .badge-fail { background-color: #FEF2F2; color: #B91C1C; font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 4px; border: 1px solid #FECACA; }

    .form-group { display: flex; flex-direction: column; gap: 5px; }
    .form-label { font-size: 11.5px; font-weight: 700; color: #334155; }
    .form-input { width: 100%; font-size: 12px; padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-family: inherit; background-color: #FFFFFF; color: var(--text); }
    .form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(10,25,47,0.08); }

    .dropzone-box { border: 2px dashed #CBD5E1; background: #F8FAFC; border-radius: 8px; padding: 18px; text-align: center; cursor: pointer; transition: all 0.2s; }
    .dropzone-box:hover { border-color: var(--primary); background: #F1F5F9; }

    .filter-pill { background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
    .filter-pill.active { background: var(--primary); color: #FFFFFF; border-color: var(--primary); }

    .tender-catalog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 10px; }
    .tender-card-item { background: #FFFFFF; border: 1.5px solid #E2E8F0; border-top: 4px solid var(--primary); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); transition: all 0.25s ease; }
    .tender-card-item:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(10,25,47,0.08); border-color: #94A3B8; }

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

    @media (max-width: 900px) {
      .landing-hero-container { grid-template-columns: 1fr; gap: 28px; }
      .auth-card { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <!-- Toast Notification Container -->
  <div id="toastContainer"></div>

    <!-- ================================================== -->
  <!-- 1. SOVEREIGN INDIAN MODERN PUBLIC LANDING PAGE     -->
  <!-- ================================================== -->
  <div id="view-public-landing" style="display: flex; flex-direction: column; min-height: 100vh;">
    <!-- Public Navigation Bar -->
    <nav class="public-nav">
      <div style="display: flex; align-items: center; gap: 12px; cursor: pointer;" onclick="scrollToSection('hero')">
        <img src="/static/bodhz_logo.png" class="logo-3d-animated" style="width: 40px; height: 40px; background: #FFF; border-radius: 10px; padding: 2px; border: 2px solid var(--accent);" alt="BodhZ">
        <div>
          <div style="font-size: 18px; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF;">BodhZ</div>
          <div style="font-size: 9.5px; color: var(--accent); font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Sovereign Bid Compliance AI</div>
        </div>
      </div>

      <div class="public-nav-links">
        <a class="public-nav-link" onclick="scrollToSection('how-it-works')"><i class="fa-solid fa-layer-group" style="color: var(--accent); font-size: 11px;"></i> How It Works</a>
        <a class="public-nav-link" onclick="scrollToSection('capabilities')"><i class="fa-solid fa-microchip" style="color: #60A5FA; font-size: 11px;"></i> Capabilities</a>
        <a class="public-nav-link" onclick="scrollToSection('sources')"><i class="fa-solid fa-network-wired" style="color: #34D399; font-size: 11px;"></i> 13 Gateways</a>
        <a class="public-nav-link" onclick="scrollToSection('authority')"><i class="fa-solid fa-scale-balanced" style="color: #FBBF24; font-size: 11px;"></i> GFR 2017 Mandate</a>
        <a class="public-nav-link" onclick="scrollToSection('preview')"><i class="fa-solid fa-eye" style="color: #C084FC; font-size: 11px;"></i> Live Dossier</a>
      </div>

      <div style="display: flex; gap: 10px; align-items: center;">
        <button onclick="openAuthScreen('LOGIN')" class="btn-hero-secondary" style="padding: 8px 18px; font-size: 12px;">Sign In</button>
        <button onclick="openAuthScreen('REGISTER')" class="btn-hero-primary" style="padding: 8px 18px; font-size: 12px;">Register</button>
        <button onclick="openDemoModeModal()" class="filter-pill" style="background: rgba(245,158,11,0.2); color: var(--accent); border-color: var(--accent); font-size: 11px; font-weight: 800;">⚡ Evaluator Demo</button>
      </div>
    </nav>

    <div class="tricolor-stripe-header"></div>

    <!-- Hero Section -->
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
        <div>
          <div class="landing-badge">
            <i class="fa-solid fa-shield-halved" style="color: #FF9933;"></i>
            <span>🇮🇳 SATYAMEVA JAYATE • SIH26100 GeM DECISION SUPPORT</span>
          </div>
          <h1 class="landing-title">
            BodhZ — AI-Powered Integrated Bid Compliance Verification Platform
          </h1>
          <p class="landing-subtitle">
            Evidence-backed decision support for faster, transparent and CAG-auditable procurement compliance verification across Central GeM and State Departments (DTE Maharashtra).
          </p>

          <div class="landing-cta-row">
            <button onclick="openAuthScreen('LOGIN')" class="btn-hero-primary">
              <i class="fa-solid fa-arrow-right-to-bracket"></i>
              <span>Sign In to Workspace</span>
            </button>
            <button onclick="openDemoModeModal()" class="btn-hero-secondary">
              <i class="fa-solid fa-bolt" style="color: var(--accent);"></i>
              <span>⚡ 1-Click Evaluator Persona</span>
            </button>
            <button onclick="scrollToSection('how-it-works')" class="btn-hero-secondary" style="border: none; color: #CBD5E1;">
              <i class="fa-solid fa-circle-info"></i>
              <span>Explore Pipeline</span>
            </button>
          </div>
        </div>

        <div class="hero-pipeline-card">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <img src="/static/bodhz_logo.png" class="logo-3d-animated" style="width: 34px; height: 34px; background: #FFF; border-radius: 8px; padding: 2px; border: 1.5px solid var(--accent);" alt="BodhZ">
              <div>
                <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF;">BodhZ 5-Step Verification Flow</div>
                <div style="font-size: 10px; color: var(--accent); font-weight: 700;">AI Engine + 13 Statutory Gateways</div>
              </div>
            </div>
            <span style="font-size: 9.5px; background: rgba(16,185,129,0.2); color: #34D399; padding: 3px 8px; border-radius: 4px; font-weight: 800; border: 1px solid rgba(16,185,129,0.3);">ACTIVE SOVEREIGN STACK</span>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(59,130,246,0.2); color: #60A5FA;">01</div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #FFFFFF;">Tender Intelligence (NIT Parsing)</div>
              <div style="font-size: 11px; color: #94A3B8;">Mandatory statutory criteria extraction & weights calibration</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(245,158,11,0.2); color: #FBBF24;">02</div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #FFFFFF;">Bidder Document AI OCR</div>
              <div style="font-size: 11px; color: #94A3B8;">Digital extraction with cryptographic SHA-256 integrity seal</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(16,185,129,0.2); color: #34D399;">03</div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #FFFFFF;">13 Statutory Gateway Verification</div>
              <div style="font-size: 11px; color: #94A3B8;">Parallel cross-check across GSTN, Udyam, MCA21, EPFO, etc.</div>
            </div>
          </div>

          <div class="pipeline-step">
            <div class="pipeline-step-icon" style="background: rgba(168,85,247,0.2); color: #C084FC;">04</div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #FFFFFF;">Compliance & Risk Scoring Engine</div>
              <div style="font-size: 11px; color: #94A3B8;">Multi-criteria 0-100 scoring & entity anomaly detection</div>
            </div>
          </div>

          <div class="pipeline-step" style="border-color: rgba(16,185,129,0.5); background: rgba(16,185,129,0.12);">
            <div class="pipeline-step-icon" style="background: #059669; color: #FFFFFF;"><i class="fa-solid fa-gavel"></i></div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #34D399;">Officer Final Legal Decision</div>
              <div style="font-size: 11px; color: #CBD5E1;">100% Human legal authority under GFR 2017 Rule 144</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Trust Strip with Rotating Ashoka Chakra Emblem -->
    <div class="trust-strip">
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg style="width: 22px; height: 22px; color: #1E3A8A;" class="chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="6"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <line x1="100" y1="100" x2="100" y2="18" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="182" y2="100" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="100" y2="182" stroke="currentColor" stroke-width="3"/>
          <line x1="100" y1="100" x2="18" y2="100" stroke="currentColor" stroke-width="3"/>
        </svg>
        <span style="font-size: 11.5px; font-weight: 900; color: #0A192F; letter-spacing: 0.5px;">SOVEREIGN COMPLIANCE</span>
      </div>
      <div class="trust-item"><i class="fa-solid fa-microchip" style="color: #2563EB;"></i> AI-ASSISTED</div>
      <div class="trust-item"><i class="fa-solid fa-file-shield" style="color: #059669;"></i> EVIDENCE-BASED</div>
      <div class="trust-item"><i class="fa-solid fa-fingerprint" style="color: #D97706;"></i> IMMUTABLE SHA-256</div>
      <div class="trust-item"><i class="fa-solid fa-user-check" style="color: #059669;"></i> HUMAN-CONTROLLED (GFR 2017)</div>
      <div class="trust-item"><i class="fa-solid fa-landmark-flag" style="color: #DC2626;"></i> CAG AUDIT READY</div>
    </div>

    <!-- ================================================== -->
    <!-- SECTION 1: WHAT BODHZ SOLVES (3D BATTLE CARDS)     -->
    <!-- ================================================== -->
    <section class="landing-section" id="solve">
      <div class="section-header">
        <div class="section-header-tag">
          <i class="fa-solid fa-scale-unbalanced" style="color: #FF9933;"></i>
          <span>PARADIGM SHIFT IN PUBLIC PROCUREMENT</span>
        </div>
        <div class="section-title">What BodhZ Solves</div>
        <div class="section-desc">Transforming manual paper-heavy bid evaluation into an integrated, evidence-backed decision support pipeline.</div>
      </div>

      <div class="solve-grid">
        <!-- Challenge Card -->
        <div class="solve-card-challenge">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 11px; font-weight: 900; background: #FEE2E2; color: #B91C1C; padding: 3px 10px; border-radius: 20px; border: 1px solid #FECACA;">THE CHALLENGE</span>
            <i class="fa-solid fa-triangle-exclamation" style="color: #DC2626; font-size: 18px;"></i>
          </div>
          <div style="font-size: 17px; font-weight: 900; color: #991B1B; margin-top: 8px;">Manual & Fragmented Bid Screening</div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 3px;"></i> <div><strong>Fragmented PDF Bundles:</strong> Hundreds of unindexed technical pages per bidder.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 3px;"></i> <div><strong>Multi-Portal Cross Checks:</strong> Manual verification across GSTN, MCA21, EPFO, and CPPP.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 3px;"></i> <div><strong>Overlooked Discrepancies:</strong> Entity name typos, expired ISO/MAF certificates, and false UDINs.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-xmark" style="color: #DC2626; margin-top: 3px;"></i> <div><strong>CAG Audit Vulnerability:</strong> Lack of cryptographic decision provenance during post-procurement vigilance audits.</div></div>
        </div>

        <!-- Solution Card -->
        <div class="solve-card-solution">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 11px; font-weight: 900; background: #D1FAE5; color: #047857; padding: 3px 10px; border-radius: 20px; border: 1px solid #A7F3D0;">THE BODHZ APPROACH</span>
            <i class="fa-solid fa-shield-halved" style="color: #059669; font-size: 18px;"></i>
          </div>
          <div style="font-size: 17px; font-weight: 900; color: #065F46; margin-top: 8px;">Integrated Sovereign AI Verification Pipeline</div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 3px;"></i> <div><strong>Tender Intelligence:</strong> Automated parsing of mandatory rules, turnover thresholds, and eligibility criteria.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 3px;"></i> <div><strong>Document Intelligence:</strong> High-precision OCR with SHA-256 seal and page-level provenance.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 3px;"></i> <div><strong>13 Statutory Gateways:</strong> Real-time cross-referencing against configured sandbox adapters.</div></div>
          <div class="solve-item"><i class="fa-solid fa-circle-check" style="color: #059669; margin-top: 3px;"></i> <div><strong>Officer Legal Decision:</strong> 100% human legal discretion under GFR 2017 Rule 144 backed by printable evaluation dossiers.</div></div>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 2: HOW IT WORKS (3D 5-STEP PIPELINE)       -->
    <!-- ================================================== -->
    <section class="landing-section" id="how-it-works">
      <div class="section-header">
        <div class="section-header-tag">
          <i class="fa-solid fa-arrow-progress" style="color: #2563EB;"></i>
          <span>STRUCTURED WORKFLOW</span>
        </div>
        <div class="section-title">How It Works — 5-Step Procurement Pipeline</div>
        <div class="section-desc">From initial tender ingestion to binding officer qualification under GFR 2017.</div>
      </div>

      <div class="flow-grid-5">
        <div class="flow-step-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flow-cube-num">01</div>
            <i class="fa-solid fa-file-contract" style="color: #0052CC; font-size: 16px;"></i>
          </div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Tender Intelligence</div>
          <p style="font-size: 12px; color: #64748B; line-height: 1.5;">Ingests NIT documents, extracting mandatory eligibility clauses, turnover, and experience thresholds.</p>
          <div style="font-size: 10.5px; font-weight: 700; color: #0052CC; margin-top: auto;">NIT Rule Extraction</div>
        </div>

        <div class="flow-step-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flow-cube-num">02</div>
            <i class="fa-solid fa-brain" style="color: #F59E0B; font-size: 16px;"></i>
          </div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Document Intelligence</div>
          <p style="font-size: 12px; color: #64748B; line-height: 1.5;">High-precision OCR extracts text from submitted technical bundles, sealing each with SHA-256 hashes.</p>
          <div style="font-size: 10.5px; font-weight: 700; color: #D97706; margin-top: auto;">Tamper-Sealed OCR</div>
        </div>

        <div class="flow-step-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flow-cube-num">03</div>
            <i class="fa-solid fa-network-wired" style="color: #059669; font-size: 16px;"></i>
          </div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">13 Gateway Verification</div>
          <p style="font-size: 12px; color: #64748B; line-height: 1.5;">Cross-checks information across 13 statutory registries (GSTN, Udyam, PAN, EPFO, DigiLocker, etc.).</p>
          <div style="font-size: 10.5px; font-weight: 700; color: #059669; margin-top: auto;">Parallel Verification</div>
        </div>

        <div class="flow-step-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flow-cube-num">04</div>
            <i class="fa-solid fa-chart-line" style="color: #7C3AED; font-size: 16px;"></i>
          </div>
          <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Compliance Analysis</div>
          <p style="font-size: 12px; color: #64748B; line-height: 1.5;">Calculates weighted compliance score (0–100), detects missing proofs, and flags inconsistencies.</p>
          <div style="font-size: 10.5px; font-weight: 700; color: #7C3AED; margin-top: auto;">Multi-Criteria Scoring</div>
        </div>

        <div class="flow-step-3d" style="border-color: #10B981; background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="flow-cube-num" style="background: #059669; color: #FFFFFF; border-color: #047857;">05</div>
            <i class="fa-solid fa-gavel" style="color: #047857; font-size: 16px;"></i>
          </div>
          <div style="font-size: 14px; font-weight: 800; color: #047857;">Officer Legal Decision</div>
          <p style="font-size: 12px; color: #166534; line-height: 1.5;">Presents structured evidence and recommendations for human qualification under GFR Rule 144.</p>
          <div style="font-size: 10.5px; font-weight: 800; color: #047857; margin-top: auto;">100% Human Authority</div>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 3: KEY CAPABILITIES (6 3D POWER NODES)     -->
    <!-- ================================================== -->
    <section class="landing-section" id="capabilities">
      <div class="section-header">
        <div class="section-header-tag">
          <i class="fa-solid fa-cubes-stacked" style="color: #059669;"></i>
          <span>CORE FUNCTIONAL SUITE</span>
        </div>
        <div class="section-title">Key Capabilities</div>
        <div class="section-desc">Six high-impact decision support capabilities built specifically for public procurement officers.</div>
      </div>

      <div class="cap-grid-6">
        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-file-circle-check"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">AI Document Intelligence</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Multi-page text extraction with OCR fallback and cryptographic SHA-256 integrity seals.</div>
            <span style="font-size: 10px; background: #EFF6FF; color: #1D4ED8; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">99.8% Precision OCR</span>
          </div>
        </div>

        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-list-check"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Requirement-Aware Matching</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Dynamic clause matching against turnover, past project experience, and mandatory criteria.</div>
            <span style="font-size: 10px; background: #F0FDF4; color: #15803D; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">NIT Clause Mapping</span>
          </div>
        </div>

        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-clone"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Cross-Document Entity Matching</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Entity matching detecting name variations, PAN vs GST mismatch, and certificate expiry.</div>
            <span style="font-size: 10px; background: #FFFBEB; color: #B45309; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">Anomaly Engine</span>
          </div>
        </div>

        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-chart-pie"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Multi-Criteria Scoring Engine</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Weighted scoring (0–100) and automated risk level classification (Low/Medium/High/Critical).</div>
            <span style="font-size: 10px; background: #FDF4FF; color: #86198F; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">Objective Risk Scoring</span>
          </div>
        </div>

        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-lightbulb"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Evidence-Based AI Reasoning</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Transparent justifications citing specific PDF pages, extracted values, and verification results.</div>
            <span style="font-size: 10px; background: #EFF6FF; color: #2563EB; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">Auditable Citations</span>
          </div>
        </div>

        <div class="cap-card-3d">
          <div class="cap-icon-box-3d"><i class="fa-solid fa-shield-halved"></i></div>
          <div>
            <div style="font-size: 14px; font-weight: 800; color: var(--primary);">CAG-Ready Audit Trail</div>
            <div style="font-size: 12px; color: #64748B; margin-top: 3px; line-height: 1.5;">Immutable cryptographic event logs and printable evaluation dossiers for vigilance audits.</div>
            <span style="font-size: 10px; background: #FEF2F2; color: #991B1B; padding: 2px 8px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 6px;">Immutable SHA-256</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 4: 13 STATUTORY VERIFICATION GATEWAYS      -->
    <!-- ================================================== -->
    <section class="landing-section" id="sources">
      <div class="section-header">
        <div class="section-header-tag">
          <i class="fa-solid fa-network-wired" style="color: #059669;"></i>
          <span>13 STATUTORY REGISTRIES & APIS</span>
        </div>
        <div class="section-title">13 Statutory Verification Gateway Sources</div>
        <div class="section-desc">Automated cross-referencing across all 13 government registries to verify bidder authenticity.</div>
      </div>

      <div class="gateway-matrix-grid">
        <!-- 01. GSTN -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-receipt" style="color: #0052CC; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">01. GSTN Tax Portal</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">GSTIN Status, Legal Trade Name & Active GSTR-3B filings.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>Dept. of Revenue</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 02. UDYAM -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-industry" style="color: #0052CC; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">02. Udyam MSME Registry</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Micro / Small / Medium enterprise classification & EMD exemption.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>Ministry of MSME</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 03. PAN / CBDT -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-id-card" style="color: #0052CC; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">03. PAN / Income Tax</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">PAN validity, entity status & Income Tax Return (ITR) filings.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>CBDT / NSDL</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 04. MCA21 -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-building" style="color: #0052CC; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">04. MCA21 Corporate</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">CIN validation, Active company status, DIN director roster.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>Ministry of Corp Affairs</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 05. STARTUP INDIA -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-rocket" style="color: #059669; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">05. Startup India / DPIIT</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">DPIIT recognition certificate & prior turnover/experience waiver.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>DPIIT / Min of Commerce</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 06. NSIC -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-certificate" style="color: #059669; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">06. NSIC SPRS Registry</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Single Point Registration Scheme & monetary capacity limit.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>NSIC Govt of India</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 07. EPFO -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-users" style="color: #059669; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">07. EPFO Provident Fund</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">EPF establishment code & monthly Electronic Challan Return (ECR).</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>Min of Labour & Emp</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 08. ESIC -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-hospital-user" style="color: #059669; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">08. ESIC Social Security</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Employees' State Insurance compliance & contribution verification.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>ESIC India</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 09. DIGILOCKER -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-vault" style="color: #D97706; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">09. DigiLocker Gateway</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Cryptographically verified government documents & certificates.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>MeitY Digital India</span>
            <strong style="color: #059669;">● LIVE API</strong>
          </div>
        </div>

        <!-- 10. OEM MAF -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-gears" style="color: #D97706; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">10. OEM Authorization (MAF)</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Manufacturer Authorization Form validity, tender mapping & warranty.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>OEM Registry / Parser</span>
            <strong style="color: #059669;">● VERIFIED</strong>
          </div>
        </div>

        <!-- 11. MAKE IN INDIA -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-flag" style="color: #D97706; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">11. Make in India (MII)</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">Class-I / Class-II local content certificate & CA self-declaration.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>Public Procurement Order</span>
            <strong style="color: #059669;">● VERIFIED</strong>
          </div>
        </div>

        <!-- 12. ISO / BIS -->
        <div class="gateway-node-3d">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-award" style="color: #D97706; font-size: 16px;"></i>
              <strong style="font-size: 12.5px; color: var(--primary);">12. ISO / BIS Standards</strong>
            </div>
            <span class="radar-beacon"></span>
          </div>
          <div style="font-size: 11.5px; color: #64748B;">ISO 9001:2015, ISO 27001 & BIS certification validity cross-check.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #475569;">
            <span>NABCB / IAF Portal</span>
            <strong style="color: #059669;">● VERIFIED</strong>
          </div>
        </div>

        <!-- 13. CPPP DEBARMENT -->
        <div class="gateway-node-3d" style="grid-column: span 1 / -1; background: linear-gradient(180deg, #FFFFFF 0%, #FEF2F2 100%); border-color: #FECACA;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <i class="fa-solid fa-ban" style="color: #DC2626; font-size: 16px;"></i>
              <strong style="font-size: 13px; color: #991B1B;">13. CPPP / GeM Debarment & Blacklist Registry</strong>
            </div>
            <span style="font-size: 10px; background: #DC2626; color: #FFFFFF; padding: 2px 8px; border-radius: 4px; font-weight: 800;">CRITICAL GATEWAY</span>
          </div>
          <div style="font-size: 11.5px; color: #7F1D1D;">Automated screening against CPPP debarred entities, Land Border Rule 144(xi), and vigilance ban lists.</div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: #991B1B;">
            <span>Central Public Procurement Portal / CAG</span>
            <strong style="color: #059669;">✓ NO DEBARMENT RECORD (CLEARED)</strong>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 5: AI ASSISTS. OFFICER DECIDES (GFR 2017)  -->
    <!-- ================================================== -->
    <section class="landing-section" id="authority">
      <div class="split-authority-monument">
        <!-- 24-Spoke Watermark in background -->
        <svg class="monument-chakra-center chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <line x1="100" y1="100" x2="100" y2="18" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="182" y2="100" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="100" y2="182" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="18" y2="100" stroke="currentColor" stroke-width="2"/>
        </svg>

        <div>
          <div style="font-size: 11px; font-weight: 900; color: #2563EB; letter-spacing: 0.5px; text-transform: uppercase;">MACHINE REASONING & EXTRACTION</div>
          <div style="font-size: 22px; font-weight: 900; color: var(--primary); margin-top: 2px; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-microchip" style="color: #2563EB;"></i>
            <span>AI ASSISTS</span>
          </div>
          <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #475569;">
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Extract:</strong> Ingests complex multi-page tender & bid PDFs with OCR.</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Analyze:</strong> Parses turnover thresholds, experience, and eligibility clauses.</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Cross-Check:</strong> Validates entity names against 13 statutory gateway sources.</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Identify Gaps:</strong> Highlights missing certificates & inconsistency flags.</div>
            <div><i class="fa-solid fa-check" style="color: #2563EB;"></i> <strong>Recommend:</strong> Generates explainable, evidence-cited compliance recommendations.</div>
          </div>
        </div>

        <div style="border-left: 1.5px solid var(--border); padding-left: 32px;">
          <div style="font-size: 11px; font-weight: 900; color: #059669; letter-spacing: 0.5px; text-transform: uppercase;">CONSTITUTIONAL & LEGAL AUTHORITY</div>
          <div style="font-size: 22px; font-weight: 900; color: #047857; margin-top: 2px; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-gavel" style="color: #059669;"></i>
            <span>OFFICER DECIDES</span>
          </div>
          <div style="margin-top: 14px; display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #475569;">
            <div><i class="fa-solid fa-shield-halved" style="color: #059669;"></i> <strong>Review:</strong> Examines extracted evidence, scores, and AI recommendations.</div>
            <div><i class="fa-solid fa-shield-halved" style="color: #059669;"></i> <strong>Validate:</strong> Inspects historical bidder records and discrepancy flags.</div>
            <div><i class="fa-solid fa-shield-halved" style="color: #059669;"></i> <strong>Qualify / Disqualify:</strong> Exercises 100% human legal decision authority under GFR 2017.</div>
            <div><i class="fa-solid fa-shield-halved" style="color: #059669;"></i> <strong>Audit Justification:</strong> Records binding justification notes.</div>
            <div><i class="fa-solid fa-shield-halved" style="color: #059669;"></i> <strong>Final Sign-Off:</strong> Cryptographically signs and seals evaluation dossier.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 6: LIVE EVALUATION DOSSIER PREVIEW         -->
    <!-- ================================================== -->
    <section class="landing-section" id="preview">
      <div class="section-header">
        <div class="section-header-tag">
          <i class="fa-solid fa-magnifying-glass-chart" style="color: #7C3AED;"></i>
          <span>TRANSPARENT EVIDENCE DISPLAY</span>
        </div>
        <div class="section-title">Compliance Evaluation Preview</div>
        <div class="section-desc">Sample live dossier illustrating transparent evidence attribution, gateway indicators, and GFR scoring.</div>
      </div>

      <div class="live-sim-card">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 14px; flex-wrap: wrap; gap: 10px;">
          <div>
            <span style="font-size: 10.5px; font-weight: 800; background: #0A192F; color: #F59E0B; padding: 2px 10px; border-radius: 4px; letter-spacing: 0.5px;">EVALUATED DOSSIER</span>
            <div style="font-size: 18px; font-weight: 900; color: var(--primary); margin-top: 4px;">Tata Advanced Training & Systems Ltd</div>
            <div style="font-size: 12px; color: var(--text-muted);">Tender: DTE/2026/RFP/COE/4901 • Center of Excellence RFP • GST: 27AAACT1098F1Z5</div>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">COMPLIANCE SCORE</div>
            <div style="font-size: 28px; font-weight: 900; color: #047857; font-family: 'JetBrains Mono', monospace;">95<span style="font-size: 15px; color: #94A3B8;">/100</span></div>
            <span class="badge-pass" style="font-size: 10.5px;">✓ QUALIFIED FOR COMMERCIAL BID</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 16px;">
          <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">GST REGISTRATION</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
              <span style="font-size: 12.5px; font-weight: 800; color: #047857;">Active GSTR-3B</span>
              <span class="badge-pass">COMPLIANT</span>
            </div>
          </div>

          <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">UDYAM / MSME</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
              <span style="font-size: 12.5px; font-weight: 800; color: #047857;">Medium Enterprise</span>
              <span class="badge-pass">COMPLIANT</span>
            </div>
          </div>

          <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">ANNUAL TURNOVER</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
              <span style="font-size: 12.5px; font-weight: 800; color: #047857;">INR 18.50 Cr (UDIN Ver.)</span>
              <span class="badge-pass">EXCEEDS REQ</span>
            </div>
          </div>

          <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 12px 14px; border-radius: 10px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B;">OEM MAF CERTIFICATE</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
              <span style="font-size: 12.5px; font-weight: 800; color: #047857;">Dell Partner Active</span>
              <span class="badge-pass">VERIFIED</span>
            </div>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 12px; border-top: 1px solid #E2E8F0; flex-wrap: wrap; gap: 10px;">
          <div style="display: flex; align-items: center; gap: 8px; font-size: 11.5px; color: #475569;">
            <i class="fa-solid fa-lock" style="color: #059669;"></i>
            <span>SHA-256 Audit Seal: <code style="font-family:'JetBrains Mono'; font-weight:700;">e8b9...4901f</code></span>
          </div>
          <button onclick="openAuthScreen('LOGIN')" class="btn-action" style="font-size: 11px; padding: 6px 14px;">
            <i class="fa-solid fa-arrow-right"></i> Open Officer Evaluation Matrix
          </button>
        </div>
      </div>
    </section>

    <!-- ================================================== -->
    <!-- SECTION 7: GRAND SOVEREIGN CTA & PUBLIC FOOTER     -->
    <!-- ================================================== -->
    <section class="landing-section">
      <div class="cta-banner-indian">
        <!-- 24-Spoke Watermark -->
        <svg style="position: absolute; right: -40px; top: -40px; width: 320px; height: 320px; opacity: 0.08; color: #F59E0B; pointer-events: none;" class="chakra-rotate-slow" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="4"/>
          <circle cx="100" cy="100" r="14" fill="currentColor"/>
          <line x1="100" y1="100" x2="100" y2="18" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="182" y2="100" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="100" y2="182" stroke="currentColor" stroke-width="2"/>
          <line x1="100" y1="100" x2="18" y2="100" stroke="currentColor" stroke-width="2"/>
        </svg>

        <div class="section-header-tag" style="background: rgba(255,255,255,0.1); border-color: var(--accent); color: var(--accent);">
          <i class="fa-solid fa-award"></i>
          <span>ATMANIRBHAR BHARAT • DIGITAL PUBLIC PROCUREMENT</span>
        </div>
        <div style="font-size: 28px; font-weight: 900; letter-spacing: -0.5px;">Ready to Experience BodhZ in Action?</div>
        <div style="font-size: 14.5px; color: #CBD5E1; max-width: 640px; line-height: 1.6;">
          Access your authorized role-based workspace to evaluate live procurement tenders, verify 13 statutory gateways, or prepare vendor proposals.
        </div>
        <div style="display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; justify-content: center;">
          <button onclick="openAuthScreen('LOGIN')" class="btn-hero-primary">
            <i class="fa-solid fa-arrow-right-to-bracket"></i>
            <span>Sign In to Workspace</span>
          </button>
          <button onclick="openAuthScreen('REGISTER')" class="btn-hero-secondary">
            <i class="fa-solid fa-user-plus"></i>
            <span>Register Account</span>
          </button>
          <button onclick="openDemoModeModal()" class="btn-hero-secondary" style="border-color: var(--accent); color: var(--accent);">
            <i class="fa-solid fa-bolt"></i>
            <span>⚡ Evaluator Demo Launcher</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Public Footer with Tricolor Heritage Stripe -->
    <footer class="public-footer-indian" id="security">
      <div style="max-width: 1180px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 18px;">
        <div style="text-align: left;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <img src="/static/bodhz_logo.png" style="width: 28px; height: 28px; background: #FFF; border-radius: 6px; padding: 2px;" alt="BodhZ">
            <span style="font-size: 15px; font-weight: 900; color: #FFFFFF;">BodhZ</span>
            <span style="font-size: 10px; background: rgba(245,158,11,0.2); color: var(--accent); padding: 2px 6px; border-radius: 4px; font-weight: 800;">SIH26100</span>
          </div>
          <div style="font-size: 11.5px; color: #94A3B8; margin-top: 6px;">AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement</div>
          <div style="font-size: 10.5px; color: #64748B; margin-top: 3px;">Designed for Government Procurement Officers & State Directorate Overseers.</div>
        </div>

        <div style="display: flex; gap: 20px; font-size: 12px; font-weight: 700; align-items: center;">
          <a class="public-nav-link" onclick="scrollToSection('how-it-works')">How It Works</a>
          <a class="public-nav-link" onclick="scrollToSection('capabilities')">Capabilities</a>
          <a class="public-nav-link" onclick="scrollToSection('sources')">13 Gateways</a>
          <a class="public-nav-link" onclick="openAuthScreen('LOGIN')">Officer Portal</a>
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

        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 18px; text-align: center; backdrop-filter: blur(8px); margin: 20px 0;">
          <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF;">Role-Aware Authenticated Session</div>
          <div style="font-size: 11.5px; color: #94A3B8; margin-top: 4px;">Procurement Officer • Bid Uploader • DTE Department</div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center;">
          <button onclick="returnToPublicLanding()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #CBD5E1; padding: 7px 14px; border-radius: 6px; font-size: 11.5px; font-weight: 700; cursor: pointer;">
            ← Back to Public Portal
          </button>
          <span style="font-size: 11px; color: #64748B; font-weight: 700;">SIH26100 Prototype</span>
        </div>
      </div>

      <div class="auth-right-form-pane">
        <!-- Sign In Form -->
        <div id="authPaneSignIn" style="display: flex; flex-direction: column;">
          <div style="margin-bottom: 16px;">
            <div style="font-size: 22px; font-weight: 900; color: var(--primary); letter-spacing: -0.5px;">Sign In to Workspace</div>
            <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 2px;">Enter your credentials or click a demo persona below to evaluate:</div>
            
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

        <!-- Registration Form Pane -->
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
                <input type="password" id="regPassword" class="auth-field" placeholder="min 8 chars" style="padding-left: 12px;" required>
              </div>
              <div class="form-group">
                <label class="form-label">Confirm Password</label>
                <input type="password" id="regConfirmPassword" class="auth-field" placeholder="re-enter password" style="padding-left: 12px;" required>
              </div>
            </div>

            <button type="submit" class="btn-auth-primary">
              <span>CREATE ACCOUNT</span>
              <i class="fa-solid fa-user-plus"></i>
            </button>
          </form>

          <div style="text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 12px;">
            Already registered? <span onclick="switchAuthMode('LOGIN')" style="color: var(--primary); font-weight: 800; cursor: pointer; text-decoration: underline;">Sign In</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- DEMO MODE MODAL -->
  <div id="demoModeModal" style="display: none; position: fixed; inset: 0; background: rgba(10,25,47,0.75); z-index: 2000; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: #FFFFFF; width: 100%; max-width: 520px; border-radius: 14px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 10px;">
        <div style="font-size: 16px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-bolt" style="color: var(--accent);"></i>
          <span>SIH Evaluator Persona Selector</span>
        </div>
        <button onclick="closeDemoModeModal()" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #64748B;">✕</button>
      </div>

      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div onclick="launchDemoPersona('shubham')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer;">
          <div style="font-size: 13px; font-weight: 800; color: var(--primary);">1. Senior Procurement Officer (Central GeM)</div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Officer Shubham • Full 10-Section Decision Support Suite</div>
        </div>

        <div onclick="launchDemoPersona('officer_dte')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer;">
          <div style="font-size: 13px; font-weight: 800; color: #B45309;">2. State Directorate Officer (DTE Maharashtra)</div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Dr. Rajesh Kumar • Department Oversight & COE Tenders</div>
        </div>

        <div onclick="launchDemoPersona('bidder_tata')" style="background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 12px 14px; border-radius: 8px; cursor: pointer;">
          <div style="font-size: 13px; font-weight: 800; color: #047857;">3. Bid Uploader / Vendor Representative</div>
          <div style="font-size: 11.5px; color: #64748B; margin-top: 3px;">Rajiv Mehta • Tata Advanced Training • Bid Portal</div>
        </div>
      </div>
    </div>
  </div>

  <!-- DTE CLARIFICATION / FINDING MODAL -->
  <div id="dteClarificationModal" style="display: none; position: fixed; inset: 0; background: rgba(10,25,47,0.75); z-index: 2100; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: #FFFFFF; width: 100%; max-width: 540px; border-radius: 14px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 10px;">
        <div style="font-size: 15px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-clipboard-question" style="color: var(--accent);"></i>
          <span>Record Department Review Finding / Clarification</span>
        </div>
        <button onclick="closeDTEClarificationModal()" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #64748B;">✕</button>
      </div>

      <div>
        <div style="font-size: 12px; color: #64748B;">Target Bidder:</div>
        <div id="dteClarifyBidderName" style="font-size: 15px; font-weight: 900; color: var(--primary);">Tata Advanced Training & Systems Ltd</div>
      </div>

      <input type="hidden" id="dteClarifyBidId">

      <div class="form-group">
        <label class="form-label">Action Type:</label>
        <select id="dteClarifyActionType" class="form-input">
          <option value="REQUEST_CLARIFICATION">Request Bidder Statutory Clarification</option>
          <option value="DEPARTMENT_OVERSIGHT_NOTE">Record Department Oversight Observation</option>
          <option value="RECOMMEND_TECHNICAL_REVIEW">Recommend In-Depth Technical Audit</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Department Findings / Clarification Text:</label>
        <textarea id="dteClarifyNotes" class="form-input" rows="4" placeholder="Enter specific clause reference or document discrepancy to record..."></textarea>
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button onclick="closeDTEClarificationModal()" class="btn-action" style="background: #E2E8F0; color: #334155;">Cancel</button>
        <button onclick="submitDTEClarification()" class="btn-warning"><i class="fa-solid fa-signature"></i> Save to Audit Record</button>
      </div>
    </div>
  </div>

  <!-- BIDDER CLARIFICATION RESPONSE MODAL -->
  <div id="bidderClarificationModal" style="display: none; position: fixed; inset: 0; background: rgba(10,25,47,0.75); z-index: 2100; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: #FFFFFF; width: 100%; max-width: 540px; border-radius: 14px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 10px;">
        <div style="font-size: 15px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-reply-all" style="color: #059669;"></i>
          <span>Respond to Committee Clarification Request</span>
        </div>
        <button onclick="closeBidderClarificationModal()" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #64748B;">✕</button>
      </div>

      <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 10px 14px; border-radius: 8px;">
        <div style="font-size: 11px; font-weight: 700; color: #92400E;">OFFICIAL COMMITTEE QUERY:</div>
        <div id="bidderClarifyQueryText" style="font-size: 13px; font-weight: 700; color: #78350F; margin-top: 3px;">Please clarify...</div>
      </div>

      <input type="hidden" id="bidderClarifyQueryId">

      <div class="form-group">
        <label class="form-label">Bidder Official Response Statement:</label>
        <textarea id="bidderClarifyResponseText" class="form-input" rows="4" placeholder="Enter your detailed technical/statutory clarification response..."></textarea>
      </div>

      <div class="form-group">
        <label class="form-label">Supporting Document Name / Reference:</label>
        <input type="text" id="bidderClarifyDocName" class="form-input" placeholder="e.g. Tata_OEM_MAF_Clarification_Confirmation.pdf">
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button onclick="closeBidderClarificationModal()" class="btn-action" style="background: #E2E8F0; color: #334155;">Cancel</button>
        <button onclick="submitBidderClarificationResponse()" class="btn-success"><i class="fa-solid fa-paper-plane"></i> Submit Response</button>
      </div>
    </div>
  </div>

  <!-- RAW API GATEWAY PAYLOAD MODAL -->
  <div id="vercenterPayloadModal" style="display: none; position: fixed; inset: 0; background: rgba(10,25,47,0.75); z-index: 2200; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: #FFFFFF; width: 100%; max-width: 600px; border-radius: 14px; border: 1px solid var(--border); padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #F1F5F9; padding-bottom: 10px;">
        <div style="font-size: 15px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-code" style="color: var(--accent);"></i>
          <span id="vercenterPayloadModalTitle">Government Registry Sandbox Response</span>
        </div>
        <button onclick="closeVercenterPayloadModal()" style="background: none; border: none; font-size: 16px; cursor: pointer; color: #64748B;">✕</button>
      </div>

      <div>
        <div style="font-size: 11px; color: #64748B; margin-bottom: 4px;">Direct Statutory API JSON Payload:</div>
        <pre id="vercenterPayloadPre" style="background: #0A192F; color: #38BDF8; font-family: 'JetBrains Mono', monospace; font-size: 11.5px; padding: 14px; border-radius: 8px; overflow-x: auto; max-height: 340px; margin: 0; border: 1px solid #1E293B;"></pre>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
        <span id="vercenterPayloadLatency" style="font-size: 11px; color: #64748B; font-family: 'JetBrains Mono';">Response Latency: 38ms</span>
        <button onclick="closeVercenterPayloadModal()" class="btn-action" style="padding: 6px 14px; font-size: 11.5px;">Close</button>
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
        <span id="topRibbonWorkspaceLabel">BodhZ Public Procurement Decision Support</span>
        <span>•</span>
        <span>SIH26100</span>
      </div>
      <div style="display: flex; gap: 16px; align-items: center;">
        <span style="color: #34D399; font-weight: 700;">● 13 Gateway Nodes Connected</span>
        <span>|</span>
        <a href="/docs" target="_blank" style="color: var(--accent); text-decoration: none; font-weight: 700;">API Docs</a>
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
      <aside class="sidebar" id="appSidebar">
        <div id="sidebarTenderWorkspaceSelectorBox" style="padding: 12px; border-bottom: 1px solid #1E293B;">
          <label style="font-size: 9.5px; font-weight: 800; color: var(--accent); text-transform: uppercase;">Active Tender Workspace</label>
          <select id="activeTenderSelector" class="form-input" style="background: #030F22; color: #FFFFFF; border-color: #334155; margin-top: 4px; font-size: 11px;" onchange="switchActiveTender(this.value)">
            <option value="">Loading Tenders...</option>
          </select>
        </div>

        <nav class="sidebar-menu" id="dynamicSidebarMenu"></nav>
      </aside>

      <main class="viewport">

        <!-- ============================================== -->
        <!-- WORKSPACE 1: PROCUREMENT OFFICER VIEWS (10)    -->
        <!-- ============================================== -->
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

            <table class="clean-table" style="margin-top: 6px;">
              <thead>
                <tr><th>Bidder Organization</th><th>GSTIN / PAN</th><th>Compliance Score</th><th>Risk Tier</th><th>Screening Status</th><th>Officer Decision</th><th>Actions</th></tr>
              </thead>
              <tbody id="dashBiddersTableBody"></tbody>
            </table>
          </div>
        </div>

        <div id="view-tenders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-pdf" style="color: #E65100;"></i> Ingest Tender Notice PDF & Auto-Extract Statutory Criteria</span>
            </div>
            <div class="dropzone-box" onclick="document.getElementById('tenderFileInput').click()">
              <i class="fa-solid fa-cloud-arrow-up" style="font-size: 28px; color: var(--primary); margin-bottom: 6px;"></i>
              <div style="font-size: 13px; font-weight: 800; color: var(--primary);">Click to Select Tender Document File (.pdf, .txt, .docx)</div>
              <input type="file" id="tenderFileInput" style="display: none;" onchange="handleTenderPDFUpload(this)">
            </div>
          </div>
          <div class="card-panel">
            <div class="card-title">Registered Procurement Tenders in System</div>
            <table class="clean-table">
              <thead><tr><th>Tender Number</th><th>Tender Title</th><th>Category</th><th>Lifecycle Status</th><th>Actions</th></tr></thead>
              <tbody id="tendersListTableBody"></tbody>
            </table>
          </div>
        </div>

        <div id="view-bidders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title"><span><i class="fa-solid fa-file-arrow-up"></i> Upload Bidder Submission Bundle & Run AI Verification</span></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div class="form-group"><label class="form-label">Bidder Legal Name:</label><input type="text" id="bidderNameInput" class="form-input" placeholder="e.g. Tata Advanced Training & Systems Ltd"></div>
              <div class="form-group"><label class="form-label">GSTIN / PAN / Udyam:</label><input type="text" id="bidderGstinInput" class="form-input" placeholder="e.g. 27AAACT1098F1Z5"></div>
            </div>
            <button onclick="submitBidderAndEvaluate()" class="btn-success" style="align-self: flex-end;"><i class="fa-solid fa-bolt"></i> RUN COMPLIANCE EVALUATION →</button>
          </div>
        </div>

        <div id="view-docintel" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel"><div class="card-title">Document Intelligence & Extraction Pipeline</div><table class="clean-table"><thead><tr><th>Document Filename</th><th>Extracted Entity</th><th>Value</th><th>Source Citation</th><th>OCR Confidence</th></tr></thead><tbody id="docIntelTableBody"></tbody></table></div>
        </div>

        <!-- 1.5 13 STATUTORY VERIFICATION GATEWAYS (LAYER 4) -->
        <div id="view-vercenter" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel" style="background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%); border-left: 5px solid var(--primary);">
            <div class="card-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
              <span><i class="fa-solid fa-network-wired" style="color: var(--primary);"></i> 13 Statutory Verification Gateway Nodes (Layer 4)</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span class="badge-pass" style="font-size: 10.5px;"><i class="fa-solid fa-shield-check"></i> ALL 13 NODES OPERATIONAL</span>
                <button onclick="reverifyAllGateways()" class="btn-success" style="font-size: 11px; padding: 4px 12px;">
                  <i class="fa-solid fa-arrows-rotate"></i> Ping & Re-Verify All 13 Nodes
                </button>
              </div>
            </div>
            <p style="font-size: 13px; color: #475569;">
              Automated multi-criteria verification pipeline connected directly to 13 statutory government registries, OEM repositories, and vigilance databases.
            </p>

            <div style="display: flex; gap: 14px; margin-top: 10px; align-items: center; flex-wrap: wrap; background: #FFFFFF; border: 1px solid #CBD5E1; padding: 10px 14px; border-radius: 8px;">
              <div style="font-size: 12px; font-weight: 800; color: var(--primary);">Select Submitted Bidder:</div>
              <select id="vercenterBidderSelect" class="form-input" style="max-width: 340px; font-weight: 700;" onchange="loadVercenterGatewaysForBidder(this.value)">
                <option value="">Loading Bidders...</option>
              </select>
              <div id="vercenterStatsSummaryPills" style="display: flex; gap: 6px; margin-left: auto; flex-wrap: wrap;"></div>
            </div>
          </div>

          <!-- Category Filters -->
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            <button onclick="filterVercenterCategory('ALL', this)" class="filter-pill active">All 13 Gateways</button>
            <button onclick="filterVercenterCategory('Taxation', this)" class="filter-pill">Taxation (GST)</button>
            <button onclick="filterVercenterCategory('Enterprise', this)" class="filter-pill">MSME & NSIC</button>
            <button onclick="filterVercenterCategory('Identity', this)" class="filter-pill">PAN / CBDT</button>
            <button onclick="filterVercenterCategory('Corporate', this)" class="filter-pill">MCA21 / Incorporation</button>
            <button onclick="filterVercenterCategory('Exemption', this)" class="filter-pill">Startup India</button>
            <button onclick="filterVercenterCategory('Labor', this)" class="filter-pill">EPFO & ESIC</button>
            <button onclick="filterVercenterCategory('Technical', this)" class="filter-pill">OEM MAF</button>
            <button onclick="filterVercenterCategory('Statutory', this)" class="filter-pill">Make in India</button>
            <button onclick="filterVercenterCategory('Quality', this)" class="filter-pill">ISO / BIS</button>
            <button onclick="filterVercenterCategory('Vigilance', this)" class="filter-pill">CPPP Debarment</button>
          </div>

          <!-- 13 Gateways Grid -->
          <div id="vercenterGatewaysGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px;">
            <!-- Rendered dynamically via JavaScript -->
          </div>
        </div>

        <div id="view-consistency" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel"><div class="card-title">Cross-Document Inconsistency Engine</div><table class="clean-table"><thead><tr><th>Check Type</th><th>Target Entities</th><th>Similarity Score</th><th>Severity</th><th>Findings Summary</th></tr></thead><tbody id="inconsistencyTableBody"></tbody></table></div>
        </div>

        <div id="view-matrix" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel"><div class="card-title">Official Multi-Bidder Comparative Evaluation Matrix</div><table class="clean-table"><thead><tr><th>Bidder Name</th><th>Score</th><th>Risk Tier</th><th>Screening</th><th>Modules</th><th>Issues</th><th>Officer Decision</th><th>Dossier</th></tr></thead><tbody id="comparativeMatrixTableBody"></tbody></table></div>
        </div>

        <div id="view-decision" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">Procurement Officer Final Decision (GFR 2017 Rule 144)</div>
            <div style="font-size: 16px; font-weight: 900; color: var(--primary);" id="decisionTargetBidderName">Tata Advanced Training & Systems Ltd</div>
            <div class="form-group" style="margin-top: 10px;">
              <label class="form-label">Official Qualification Decision:</label>
              <select id="officerDecisionChoice" class="form-input" style="font-weight: 800;">
                <option value="QUALIFIED">✓ QUALIFIED — Approved for Commercial Price Bid Opening</option>
                <option value="DISQUALIFIED">✕ DISQUALIFIED — Non-Compliant with Mandatory Terms</option>
                <option value="NEEDS_CLARIFICATION">⚠️ NEEDS CLARIFICATION — Issue Statutory Query</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Officer Audit Remarks:</label><textarea id="officerDecisionNotes" class="form-input" rows="3" placeholder="Enter official audit justification remarks..."></textarea></div>
            <button onclick="submitOfficerFinalDecision()" class="btn-action"><i class="fa-solid fa-signature"></i> RECORD BINDING DECISION UNDER GFR RULE 144</button>
          </div>
        </div>

        <div id="view-reports" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel"><div class="card-title">Printable Evaluation Dossier</div><iframe id="reportPreviewFrame" style="width: 100%; height: 600px; border: 1px solid #CBD5E1; border-radius: 8px;" src="about:blank"></iframe></div>
        </div>

        <div id="view-audittrail" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-shield-halved"></i> Cryptographic SHA-256 Audit Trail</span>
              <button onclick="exportAuditTrailJSON()" class="btn-action" style="font-size: 11px; padding: 4px 10px;"><i class="fa-solid fa-download"></i> Export JSON</button>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
              <input type="text" id="officerAuditSearchInput" placeholder="🔍 Search events..." class="form-input" style="width: 260px; padding: 5px 10px;" oninput="filterOfficerAuditEvents()">
            </div>
            <table class="clean-table"><thead><tr><th>Timestamp</th><th>Actor</th><th>Event Type</th><th>Details</th><th>SHA-256 Hash</th></tr></thead><tbody id="auditTrailTableBody"></tbody></table>
          </div>
        </div>

        <!-- ============================================================== -->
        <!-- WORKSPACE 2: DEDICATED BID UPLOADER & VENDOR WORKSPACE (11 VIEWS) -->
        <!-- ============================================================== -->

        <!-- 2.1 BIDDER DASHBOARD -->
        <div id="view-bidder-dashboard" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel" style="background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%); border-left: 5px solid #059669;">
            <div class="card-title">
              <span><i class="fa-solid fa-briefcase" style="color: #059669;"></i> Bid Uploader / Vendor Workspace</span>
              <span class="badge-open-bid" style="font-size: 10.5px;"><i class="fa-solid fa-building-circle-check"></i> VERIFIED VENDOR PORTAL</span>
            </div>
            <p style="font-size: 13px; color: #475569;">
              Welcome, <strong id="bidderDashWelcomeName" style="color: var(--primary);">Rajiv Mehta</strong> • Organization: <strong id="bidderDashCompanyName" style="color: #047857;">Tata Advanced Training & Systems Ltd</strong>
            </p>

            <!-- 5 Dedicated Bidder KPI Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-top: 10px;">
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px; cursor: pointer;" onclick="switchBidderView('bidder-tenders')">
                <div style="font-size: 10.5px; font-weight: 700; color: #64748B;">ACTIVE TENDERS</div>
                <div style="font-size: 22px; font-weight: 900; color: #0052CC;" id="bidderStatActiveTenders">3</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px; cursor: pointer;" onclick="switchBidderView('bidder-mybids')">
                <div style="font-size: 10.5px; font-weight: 700; color: #64748B;">MY BIDS</div>
                <div style="font-size: 22px; font-weight: 900; color: var(--primary);" id="bidderStatMyBids">2</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px; cursor: pointer;" onclick="switchBidderView('bidder-mybids')">
                <div style="font-size: 10.5px; font-weight: 700; color: #B45309;">DRAFT SUBMISSIONS</div>
                <div style="font-size: 22px; font-weight: 900; color: #B45309;" id="bidderStatDraftBids">0</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px; cursor: pointer;" onclick="switchBidderView('bidder-mybids')">
                <div style="font-size: 10.5px; font-weight: 700; color: #047857;">SUBMITTED BIDS</div>
                <div style="font-size: 22px; font-weight: 900; color: #047857;" id="bidderStatSubmittedBids">2</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px; cursor: pointer;" onclick="switchBidderView('bidder-clarifications')">
                <div style="font-size: 10.5px; font-weight: 700; color: #DC2626;">PENDING CLARIFICATIONS</div>
                <div style="font-size: 22px; font-weight: 900; color: #DC2626;" id="bidderStatPendingClarifications">0</div>
              </div>
            </div>
          </div>

          <!-- Quick Action Buttons -->
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button onclick="switchBidderView('bidder-tenders')" class="btn-action" style="padding: 10px 16px;"><i class="fa-solid fa-folder-open"></i> Browse Open Tenders</button>
            <button onclick="switchBidderView('bidder-start')" class="btn-success" style="padding: 10px 16px;"><i class="fa-solid fa-file-circle-plus"></i> + Start New Bid Proposal</button>
            <button onclick="switchBidderView('bidder-checklist')" class="btn-warning" style="padding: 10px 16px;"><i class="fa-solid fa-list-check"></i> Check Submission Completeness</button>
          </div>

          <!-- Recent Submissions Activity -->
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-clock-rotate-left" style="color: #0052CC;"></i> Recent Submission Activity</span>
              <span class="badge-pass">MY COMPANY RECORDS</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Tender Reference</th>
                  <th>Tender Title</th>
                  <th>Submission Timestamp</th>
                  <th>Submission Status</th>
                  <th>Lifecycle</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="bidderRecentActivityTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.2 AVAILABLE TENDERS CATALOG -->
        <div id="view-bidder-tenders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-folder-open" style="color: #0052CC;"></i> Available Procurement Tenders</span>
              <span class="badge-pass">PUBLIC GeM RFPs</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap;">
              <input type="text" id="bidderTendersSearchInput" placeholder="🔍 Search tender title, number or department..." class="form-input" style="max-width: 320px;" oninput="filterBidderTendersCatalog()">
              <button onclick="switchBidderView('bidder-start')" class="btn-success" style="font-size: 11.5px; padding: 6px 14px;"><i class="fa-solid fa-plus"></i> Start Bid</button>
            </div>
            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Tender ID</th>
                  <th>Tender Title</th>
                  <th>Procuring Organization</th>
                  <th>Closing Date</th>
                  <th>Requirements</th>
                  <th>My Submission</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="bidderAvailableTendersTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.3 TENDER DETAILS & SPECIFICATIONS -->
        <div id="view-bidder-tender-detail" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-contract" style="color: #0052CC;"></i> RFP Specifications & Submission Guidelines</span>
              <button onclick="switchBidderView('bidder-tenders')" class="btn-action" style="font-size: 11px; padding: 4px 10px;">← Back to Tenders</button>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #64748B;">RFP REFERENCE:</div>
              <div style="font-size: 16px; font-weight: 900; color: var(--primary); font-family: 'JetBrains Mono';" id="bidderDetailTenderNumber">DTE/2026/RFP/COE/4901</div>
              <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin-top: 4px;" id="bidderDetailTenderTitle">Establishment, Operationalization & Maintenance of Center of Excellence (COE)</div>
              <div style="font-size: 12px; color: #475569; margin-top: 6px;" id="bidderDetailTenderOrg">Directorate of Technical Education, Maharashtra</div>
            </div>

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
              <div>
                <div style="font-size: 12px; font-weight: 800; color: var(--primary); margin-bottom: 4px;">Tender Scope & Description:</div>
                <p style="font-size: 12.5px; color: #334155; line-height: 1.6;" id="bidderDetailTenderDesc">
                  RFP for selection of agency for setting up Center of Excellence & technical training facilities across State Government engineering institutes under DTE Maharashtra.
                </p>

                <div style="font-size: 12px; font-weight: 800; color: var(--primary); margin-top: 12px; margin-bottom: 4px;">Submission Instructions:</div>
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 10px; border-radius: 6px; font-size: 12px; color: #92400E; line-height: 1.5;" id="bidderDetailInstructions">
                  1. Upload clear, non-password-protected PDF copies of all statutory certificates.<br>
                  2. Ensure CA Turnover certificate includes UDIN.<br>
                  3. Manufacturer Authorization Form (MAF) must be on OEM official letterhead.<br>
                  4. Complete submission checklist before 17:00 IST on closing date.
                </div>
              </div>

              <div style="background: #F1F5F9; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-bottom: 8px;">Important Dates</div>
                <div style="font-size: 11.5px; color: #334155; display: flex; flex-direction: column; gap: 6px;">
                  <div><strong>Published:</strong> <span id="bidderDatePublished">15 Aug 2026</span></div>
                  <div><strong>Pre-Bid Meet:</strong> <span id="bidderDatePrebid">25 Aug 2026</span></div>
                  <div><strong>Closing Date:</strong> <span id="bidderDateClosing" style="color: #DC2626; font-weight: 800;">30 Sep 2026, 17:00 IST</span></div>
                  <div><strong>Tech Opening:</strong> <span id="bidderDateOpening">01 Oct 2026, 11:00 IST</span></div>
                </div>
                <button onclick="startBidderWizard(activeBidderSelectedTenderId)" class="btn-success" style="width: 100%; margin-top: 14px; padding: 8px 12px; font-size: 11px;">
                  <i class="fa-solid fa-file-circle-plus"></i> Start Bid for this Tender
                </button>
              </div>
            </div>

            <div class="card-title" style="margin-top: 16px;"><span>Required Statutory & Technical Clauses</span></div>
            <table class="clean-table">
              <thead>
                <tr><th>Module</th><th>Statutory Requirement Title</th><th>Mandatory?</th><th>Weight</th><th>Rule Type</th></tr>
              </thead>
              <tbody id="bidderDetailRequirementsTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.4 REQUIREMENT CHECKLIST -->
        <div id="view-bidder-checklist" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-list-check" style="color: #059669;"></i> Submission Requirement Checklist & Completeness Assistant</span>
              <span class="badge-review">TECHNICAL PRE-CHECK</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 8px;">
              <div>
                <div style="font-size: 11px; font-weight: 700; color: #64748B;">TARGET RFP:</div>
                <div style="font-size: 15px; font-weight: 900; color: var(--primary);" id="bidderChecklistTenderTitle">DTE/2026/RFP/COE/4901 — Center of Excellence</div>
              </div>
              <div style="display: flex; gap: 10px; align-items: center;">
                <span class="badge-pass" id="bidderChecklistStatusBadge">10 Uploaded / 0 Missing</span>
                <button onclick="switchBidderView('bidder-upload')" class="btn-action" style="font-size: 11px; padding: 6px 12px;"><i class="fa-solid fa-cloud-arrow-up"></i> Upload Document</button>
              </div>
            </div>

            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; font-size: 12px; padding: 10px 14px; border-radius: 6px; margin-top: 4px;">
              <i class="fa-solid fa-circle-info"></i> <strong>Submission Completeness Assistant:</strong> This checklist performs preliminary technical format & document presence verification. It does not declare official government qualification.
            </div>

            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Statutory Clause</th>
                  <th>Title</th>
                  <th>Mandatory?</th>
                  <th>Upload Status</th>
                  <th>Uploaded Document</th>
                  <th>Technical Validation Note</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="bidderChecklistTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.5 START NEW BID (WIZARD) -->
        <div id="view-bidder-start" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-circle-plus" style="color: #059669;"></i> Prepare & Submit New Bid Proposal</span>
              <span class="badge-pass">6-STEP SUBMISSION WIZARD</span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 14px;">
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">1. Select Tender</div>
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">2. Bidder Profile</div>
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">3. Upload Documents</div>
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">4. Completeness Check</div>
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">5. Declaration</div>
              <div class="filter-pill active" style="text-align: center; font-size: 11px;">6. Submit</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div class="form-group">
                <label class="form-label">Select Target Tender:</label>
                <select id="bidderWizardTenderSelect" class="form-input" onchange="onBidderWizardTenderChange(this.value)">
                  <option value="DTE/2026/RFP/COE/4901">DTE/2026/RFP/COE/4901 — Center of Excellence (DTE Maharashtra)</option>
                  <option value="NFL/CO/IT/VAPT/2026/08">NFL/CO/IT/VAPT/2026/08 — VAPT & Cyber Security Audit (NFL CPSE)</option>
                  <option value="GEM/2026/B/IIMR/6641">GEM/2026/B/IIMR/6641 — Agricultural Machinery (ICAR-IIMR)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Authorized Submitting Entity:</label>
                <input type="text" id="bidderWizardCompanyName" class="form-input" readonly value="Tata Advanced Training & Systems Ltd">
              </div>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; padding: 14px; border-radius: 8px; margin-top: 8px;">
              <div style="font-size: 13px; font-weight: 800; color: var(--primary); margin-bottom: 6px;">Entity GSTIN & PAN Verification:</div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; font-size: 12px;">
                <div><strong>GSTIN:</strong> <span style="font-family: 'JetBrains Mono';" id="bidderWizardGSTIN">27AAACT1098F1Z5</span></div>
                <div><strong>PAN:</strong> <span style="font-family: 'JetBrains Mono';" id="bidderWizardPAN">AAACT1098F</span></div>
                <div><strong>Udyam / MSME:</strong> <span style="font-family: 'JetBrains Mono';" id="bidderWizardUdyam">UDYAM-MH-01-0089241</span></div>
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px;">
              <button onclick="switchBidderView('bidder-upload')" class="btn-success" style="padding: 9px 18px;">
                Proceed to Document Upload (Step 3) →
              </button>
            </div>
          </div>
        </div>

        <!-- 2.6 DOCUMENT UPLOAD CENTER -->
        <div id="view-bidder-upload" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-cloud-arrow-up" style="color: #059669;"></i> Bid Document Upload & Pre-Validation</span>
              <span class="badge-pass">MULTI-DOCUMENT UPLOAD</span>
            </div>

            <div style="border: 2px dashed #CBD5E1; border-radius: 10px; padding: 24px; text-align: center; background: #F8FAFC;" id="bidderDragDropZone">
              <i class="fa-solid fa-file-pdf" style="font-size: 36px; color: #0052CC; margin-bottom: 8px;"></i>
              <div style="font-size: 14px; font-weight: 800; color: var(--primary);">Drag & Drop Document Bundle (PDF)</div>
              <div style="font-size: 12px; color: #64748B; margin-top: 3px;">or browse files from your computer</div>

              <div style="display: flex; justify-content: center; gap: 12px; align-items: center; margin-top: 14px; flex-wrap: wrap;">
                <select id="bidderUploadDocType" class="form-input" style="max-width: 240px; font-size: 11.5px;">
                  <option value="GST_CERT">GST Registration Certificate</option>
                  <option value="PAN_CARD">Income Tax PAN / TAN Card</option>
                  <option value="UDYAM_CERT">Udyam MSME Certificate</option>
                  <option value="OEM_MAF">Manufacturer Authorization (MAF)</option>
                  <option value="FINANCIAL">Audited CA Balance Sheets</option>
                  <option value="EXPERIENCE">Past Experience Certificates</option>
                  <option value="ISO_CERT">ISO 9001:2015 Certificate</option>
                  <option value="NON_BLACKLISTING">Non-Debarment Affidavit</option>
                </select>
                <input type="file" id="bidderFileInput" style="display: none;" onchange="handleBidderFileChosen(this)">
                <button type="button" onclick="document.getElementById('bidderFileInput').click()" class="btn-action" style="padding: 8px 14px; font-size: 11px;">
                  <i class="fa-solid fa-folder-open"></i> Browse PDF
                </button>
                <button type="button" onclick="uploadSimulatedBidderDoc()" class="btn-success" style="padding: 8px 14px; font-size: 11px;">
                  <i class="fa-solid fa-upload"></i> Upload & Validate
                </button>
              </div>
            </div>

            <div class="card-title" style="margin-top: 12px;"><span>Uploaded Documents for Active Bid</span></div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Document Name</th>
                  <th>Document Type</th>
                  <th>Upload Date</th>
                  <th>Processing Status</th>
                  <th>Validation Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="bidderUploadedDocsTableBody"></tbody>
            </table>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
              <button onclick="switchBidderView('bidder-checklist')" class="btn-action" style="font-size: 11px; padding: 7px 14px;">← View Checklist</button>
              <button onclick="switchBidderView('bidder-check')" class="btn-success" style="font-size: 11.5px; padding: 8px 18px;">Proceed to Completeness Check →</button>
            </div>
          </div>
        </div>

        <!-- 2.7 PRE-SUBMISSION COMPLETENESS CHECK -->
        <div id="view-bidder-check" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-clipboard-check" style="color: #0052CC;"></i> Bid Submission Completeness Check</span>
              <span class="badge-review">PRE-SUBMISSION VERIFICATION</span>
            </div>

            <!-- BID SUBMISSION CHECK BANNER -->
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #E0F2FE 100%); border: 1.5px solid #059669; border-radius: 10px; padding: 18px 22px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
              <div>
                <div style="font-size: 13px; font-weight: 800; color: #047857;">BID SUBMISSION CHECK SUMMARY</div>
                <div style="font-size: 22px; font-weight: 900; color: var(--primary); margin-top: 4px;" id="bidderCheckReadyText">
                  READY TO SUBMIT: <span style="color: #059669;">YES</span>
                </div>
                <div style="font-size: 12px; color: #334155; margin-top: 4px;">
                  Required Documents: <strong id="bidderCheckReqCount">10</strong> • Uploaded: <strong id="bidderCheckUploadCount" style="color: #059669;">10</strong> • Missing: <strong id="bidderCheckMissingCount" style="color: #059669;">0</strong>
                </div>
              </div>
              <div>
                <span class="badge-pass" style="font-size: 13px; padding: 6px 14px;" id="bidderCompletenessScoreBadge">100% COMPLETE</span>
              </div>
            </div>

            <div id="bidderMissingDocsAlert" style="display: none; background: #FEF2F2; border: 1px solid #FECACA; color: #B91C1C; padding: 12px 16px; border-radius: 8px; font-size: 12px;">
              <strong>Missing Mandatory Documents:</strong>
              <div id="bidderMissingDocsList" style="margin-top: 4px;"></div>
              <button onclick="switchBidderView('bidder-upload')" class="btn-action" style="margin-top: 8px; font-size: 10.5px; padding: 4px 10px;">Upload Missing Document</button>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #CBD5E1; padding: 14px; border-radius: 8px; margin-top: 8px;">
              <div style="font-size: 13px; font-weight: 800; color: var(--primary); margin-bottom: 6px;">Statutory Undertaking & Declaration:</div>
              <label style="display: flex; gap: 10px; align-items: flex-start; cursor: pointer; font-size: 12px; color: #334155;">
                <input type="checkbox" id="bidderDeclarationCheckbox" checked style="margin-top: 3px;">
                <span>
                  I hereby declare that all uploaded certificates, financial statements, and technology authorization letters are genuine, true, and issued by competent statutory authorities. I agree to abide by the provisions of GFR 2017 and GeM procurement rules.
                </span>
              </label>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px;">
              <button onclick="switchBidderView('bidder-upload')" class="btn-action" style="font-size: 11px; padding: 7px 14px;">← Back to Uploads</button>
              <button onclick="submitBidderOfficialProposal()" id="btnBidderFinalSubmit" class="btn-success" style="font-size: 13px; padding: 10px 24px; font-weight: 800;">
                <i class="fa-solid fa-paper-plane"></i> SUBMIT BID PROPOSAL
              </button>
            </div>
          </div>
        </div>

        <!-- 2.8 MY BIDS -->
        <div id="view-bidder-mybids" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-layer-group" style="color: #0052CC;"></i> My Bids & Submission Tracking</span>
              <span class="badge-pass">AUTHENTICATED BIDDER</span>
            </div>
            <p style="font-size: 12px; color: #64748B;">
              Track all submitted and draft proposals under your company account. Status updates in real-time as the procurement committee progresses with verification.
            </p>
            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Bid ID</th>
                  <th>Tender Reference</th>
                  <th>Submitted Date</th>
                  <th>Status</th>
                  <th>Document Completion</th>
                  <th>Last Updated</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="bidderMyBidsTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.9 CLARIFICATIONS & QUERIES -->
        <div id="view-bidder-clarifications" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-comments" style="color: #B45309;"></i> Clarification Requests & Committee Queries</span>
              <span class="badge-review">OVERSIGHT COMMUNICATION</span>
            </div>
            <p style="font-size: 12px; color: #64748B;">
              Respond to official clarification inquiries raised by Procurement Officers or State Directorate reviewers before the specified cutoff date.
            </p>
            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Query ID</th>
                  <th>Target Tender</th>
                  <th>Requested By</th>
                  <th>Question / Request</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="bidderClarificationsTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.10 SUBMISSION HISTORY -->
        <div id="view-bidder-history" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-clock-rotate-left" style="color: #0052CC;"></i> Submission History & Integrity Receipts</span>
              <span class="badge-pass">IMMUTABLE LEDGER</span>
            </div>
            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Submission Date</th>
                  <th>Tender Number</th>
                  <th>Generated Bid ID</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="bidderHistoryTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 2.11 COMPANY PROFILE -->
        <div id="view-bidder-profile" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-id-card" style="color: #059669;"></i> Bidder Organization Profile</span>
              <span class="badge-pass">VERIFIED ENTITY</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div class="form-group">
                <label class="form-label">Authorized Representative:</label>
                <input type="text" id="bidderProfileName" class="form-input" readonly value="Rajiv Mehta">
              </div>
              <div class="form-group">
                <label class="form-label">Company Legal Name:</label>
                <input type="text" id="bidderProfileCompany" class="form-input" readonly value="Tata Advanced Training & Systems Ltd">
              </div>
              <div class="form-group">
                <label class="form-label">GSTIN:</label>
                <input type="text" id="bidderProfileGSTIN" class="form-input" readonly style="font-family: 'JetBrains Mono';" value="27AAACT1098F1Z5">
              </div>
              <div class="form-group">
                <label class="form-label">PAN Number:</label>
                <input type="text" id="bidderProfilePAN" class="form-input" readonly style="font-family: 'JetBrains Mono';" value="AAACT1098F">
              </div>
              <div class="form-group">
                <label class="form-label">Udyam Registration:</label>
                <input type="text" id="bidderProfileUdyam" class="form-input" readonly style="font-family: 'JetBrains Mono';" value="UDYAM-MH-01-0089241">
              </div>
              <div class="form-group">
                <label class="form-label">Official Email:</label>
                <input type="email" id="bidderProfileEmail" class="form-input" value="rajiv.mehta@tatasystems.com">
              </div>
              <div class="form-group">
                <label class="form-label">Contact Phone:</label>
                <input type="text" id="bidderProfilePhone" class="form-input" value="+91 98222 33445">
              </div>
              <div class="form-group">
                <label class="form-label">Registered Office Address:</label>
                <input type="text" id="bidderProfileAddress" class="form-input" value="Tata Center, 24 Homi Mody Street, Fort, Mumbai, Maharashtra 400001">
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px;">
              <button onclick="saveBidderProfile()" class="btn-success"><i class="fa-solid fa-floppy-disk"></i> Save Profile Changes</button>
            </div>
          </div>
        </div>

        <!-- ============================================================== -->
        <!-- WORKSPACE 3: DEDICATED DTE MAHARASHTRA DEPARTMENT WORKSPACE    -->
        <!-- ============================================================== -->
        
        <!-- 3.1 DTE OVERVIEW & DASHBOARD -->
        <div id="view-dte-dashboard" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel" style="background: linear-gradient(135deg, #FFFFFF 0%, #FFFBEB 100%); border-left: 5px solid var(--accent);">
            <div class="card-title">
              <span><i class="fa-solid fa-building-columns" style="color: var(--accent);"></i> Directorate of Technical Education (DTE Maharashtra) Overview</span>
              <span class="badge-review" style="font-size: 10.5px;"><i class="fa-solid fa-shield-check"></i> DEPARTMENT OVERSIGHT CLEARED</span>
            </div>
            <p style="font-size: 13px; color: #475569;">
              Official Departmental Decision Support Dashboard for <strong>Directorate of Technical Education (DTE Maharashtra)</strong>. 
              Monitoring statewide COE infrastructure proposals and 13-gateway pre-qualification statutory compliance.
            </p>

            <!-- 6 Dedicated KPI Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 10px;">
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #64748B;">ACTIVE TENDERS</div>
                <div style="font-size: 22px; font-weight: 900; color: var(--primary);" id="dteStatActiveTenders">1</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #64748B;">TOTAL BIDS</div>
                <div style="font-size: 22px; font-weight: 900; color: var(--primary);" id="dteStatTotalBids">3</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #B45309;">UNDER REVIEW</div>
                <div style="font-size: 22px; font-weight: 900; color: #B45309;" id="dteStatBidsUnderReview">1</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #047857;">COMPLETED</div>
                <div style="font-size: 22px; font-weight: 900; color: #047857;" id="dteStatCompletedEvaluations">2</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #B91C1C;">HIGH-RISK BIDS</div>
                <div style="font-size: 22px; font-weight: 900; color: #B91C1C;" id="dteStatHighRiskBids">1</div>
              </div>
              <div style="background: #FFFFFF; border: 1px solid #CBD5E1; padding: 12px; border-radius: 8px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #2563EB;">PENDING ACTIONS</div>
                <div style="font-size: 22px; font-weight: 900; color: #2563EB;" id="dteStatPendingActions">2</div>
              </div>
            </div>
          </div>

          <!-- All Bids Processed Status Banner -->
          <div id="dteAllBidsProcessedBanner" style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1.5px solid #10B981; border-radius: 10px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <i class="fa-solid fa-circle-check" style="font-size: 28px; color: #059669;"></i>
              <div>
                <div style="font-size: 14px; font-weight: 800; color: #065F46;">ALL BIDS PROCESSED (3 Total / 3 Processed)</div>
                <div style="font-size: 11.5px; color: #047857;">Technical and statutory gateway verification is complete for DTE/2026/RFP/COE/4901.</div>
              </div>
            </div>
            <button onclick="switchDTEView('dte-shortlisted')" class="btn-success" style="font-size: 12px; padding: 8px 16px;">
              <i class="fa-solid fa-table-list"></i> VIEW QUALIFIED / SHORTLISTED BIDS →
            </button>
          </div>

          <!-- DTE Authorized Tenders Monitoring Table -->
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-list-check"></i> Authorized DTE Tenders Summary</span>
              <span class="badge-pass">DTE SCOPED</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Tender ID</th>
                  <th>Tender Title</th>
                  <th>Total Bids</th>
                  <th>Processed</th>
                  <th>Pending</th>
                  <th>High Risk</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="dteTendersOverviewTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.2 DTE TENDER MONITORING DEDICATED VIEW -->
        <div id="view-dte-tenders" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-list-check" style="color: #0052CC;"></i> DTE Maharashtra Tenders Monitoring Center</span>
              <span class="badge-pass">DEPARTMENT PORTFOLIO</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap;">
              <input type="text" id="dteTenderSearchInput" placeholder="🔍 Search tender reference or title..." class="form-input" style="max-width: 320px;" oninput="filterDTETendersTable()">
              <div style="display: flex; gap: 6px;">
                <span class="filter-pill active" onclick="filterDTETenderCategory('ALL', this)">All (1)</span>
                <span class="filter-pill" onclick="filterDTETenderCategory('ACTIVE', this)">Active / Open (1)</span>
                <span class="filter-pill" onclick="filterDTETenderCategory('EVALUATED', this)">Evaluated (1)</span>
              </div>
            </div>

            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Tender Reference</th>
                  <th>Tender Title</th>
                  <th>Category</th>
                  <th>Total Bids</th>
                  <th>Evaluation Progress</th>
                  <th>Risk Tier</th>
                  <th>Lifecycle Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="dteTendersMonitoringTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.3 DTE TENDER DETAIL & CLAUSES -->
        <div id="view-dte-tender-detail" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-file-contract" style="color: #0052CC;"></i> DTE Tender Clauses & Statutory Weight Calibration</span>
              <span class="badge-review">READ-ONLY AUDIT VIEW</span>
            </div>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
              <div>
                <div style="font-size: 11px; font-weight: 700; color: #64748B;">RFP REFERENCE:</div>
                <div style="font-size: 16px; font-weight: 900; color: var(--primary); font-family: 'JetBrains Mono';" id="dteDetailTenderNumber">DTE/2026/RFP/COE/4901</div>
                <div style="font-size: 13.5px; font-weight: 700; color: #1E293B; margin-top: 4px;" id="dteDetailTenderTitle">Establishment of Center of Excellence (COE) and Technical Training Centers</div>
              </div>
              <div style="text-align: right; display: flex; flex-direction: column; justify-content: center; align-items: flex-end;">
                <span class="badge-pass" id="dteDetailLifecycleStatus">ALL_BIDS_PROCESSED</span>
                <div style="font-size: 11px; color: #64748B; margin-top: 6px;">Total Bids Ingested: <strong id="dteDetailTotalBidsCount">3</strong></div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 14px;">
              <div style="background: #EFF6FF; border: 1px solid #BFDBFE; padding: 10px 14px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #1E40AF;">TOTAL CLAUSES</div>
                <div style="font-size: 20px; font-weight: 900; color: #1D4ED8;">10 Modules</div>
              </div>
              <div style="background: #F0FDF4; border: 1px solid #BBF7D0; padding: 10px 14px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #166534;">MANDATORY CRITERIA</div>
                <div style="font-size: 20px; font-weight: 900; color: #15803D;">10 / 10 (100%)</div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 10px 14px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #92400E;">CALIBRATED WEIGHT</div>
                <div style="font-size: 20px; font-weight: 900; color: #D97706;">100% Total</div>
              </div>
              <div style="background: #F8FAFC; border: 1px solid #CBD5E1; padding: 10px 14px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #475569;">STATUTORY AUDIT</div>
                <div style="font-size: 20px; font-weight: 900; color: #0A192F;">GFR Rule 144</div>
              </div>
            </div>

            <table class="clean-table">
              <thead>
                <tr>
                  <th style="width: 140px;">Module Code</th>
                  <th>Statutory Requirement Title</th>
                  <th style="width: 120px;">Mandatory?</th>
                  <th style="width: 160px;">Calibrated Weight</th>
                  <th style="width: 180px;">Evaluation Rule Type</th>
                </tr>
              </thead>
              <tbody id="dteDetailRequirementsTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.4 DTE BID MONITORING TABLE -->
        <div id="view-dte-bids" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-users-viewfinder"></i> DTE Authorized Bids Monitoring & Review</span>
              <span class="badge-pass">DTE/2026/RFP/COE/4901</span>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Bidder Legal Name</th>
                  <th>GSTIN / PAN</th>
                  <th>Compliance Score</th>
                  <th>Risk Level</th>
                  <th>Screening Status</th>
                  <th>Missing / Flags</th>
                  <th>Decision Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="dteBidsMonitoringTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.5 DTE COMPLIANCE & EVIDENCE BREAKDOWN -->
        <div id="view-dte-compliance" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-magnifying-glass-chart" style="color: #0052CC;"></i> Evidence-Driven Statutory Compliance Inspector</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <label style="font-size: 11px; font-weight: 700; color: #475569;">Select Bidder:</label>
                <select id="dteComplianceBidderSelect" class="form-input" style="width: 260px; font-size: 11px;" onchange="inspectDTEComplianceEvidence(this.value)"></select>
                <span id="dteComplianceBidderLabel" class="badge-pass">Tata Advanced Training</span>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 8px;">
              <div style="background: #F0FDF4; border: 1px solid #BBF7D0; padding: 10px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #166534;">COMPLIANT CLAUSES</div>
                <div style="font-size: 20px; font-weight: 900; color: #15803D;" id="dteCompliantCount">8</div>
              </div>
              <div style="background: #FEF2F2; border: 1px solid #FECACA; padding: 10px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #991B1B;">NON-COMPLIANT</div>
                <div style="font-size: 20px; font-weight: 900; color: #DC2626;" id="dteNonCompliantCount">0</div>
              </div>
              <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 10px; border-radius: 6px;">
                <div style="font-size: 10.5px; font-weight: 700; color: #92400E;">REVIEW REQUIRED</div>
                <div style="font-size: 20px; font-weight: 900; color: #D97706;" id="dteReviewCount">0</div>
              </div>
            </div>

            <table class="clean-table">
              <thead>
                <tr>
                  <th>Statutory Clause</th>
                  <th>Extracted Evidence</th>
                  <th>Gateway Status</th>
                  <th>Audit Findings</th>
                  <th>Source Citation</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody id="dteEvidenceBreakdownTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.6 DTE 13 GATEWAYS VIEW -->
        <div id="view-dte-gateways" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-network-wired" style="color: #059669;"></i> 13 Statutory Verification Registries & Verification Modes</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <label style="font-size: 11px; font-weight: 700; color: #475569;">Select Bidder:</label>
                <select id="dteGatewaysBidderSelect" class="form-input" style="width: 260px; font-size: 11px;" onchange="inspectDTEGateways(this.value)"></select>
                <span class="badge-pass">13 / 13 CONNECTORS</span>
              </div>
            </div>
            <table class="clean-table">
              <thead>
                <tr>
                  <th>Statutory Registry</th>
                  <th>Category</th>
                  <th>Verification Mode</th>
                  <th>Gateway Status</th>
                  <th>Verification Timestamp</th>
                </tr>
              </thead>
              <tbody id="dteGatewaysTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.7 DTE QUALIFIED / SHORTLISTED VIEW -->
        <div id="view-dte-shortlisted" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-trophy" style="color: var(--accent);"></i> Qualified / Shortlisted Bidders for Final Department Review</span>
              <span class="badge-pass" id="dteShortlistCountBadge">2 Bidders Qualified</span>
            </div>
            <p style="font-size: 12px; color: #64748B;">
              Summary of all bidders meeting pre-qualification thresholds under DTE Maharashtra RFP. Final commercial award is decided following financial bid opening.
            </p>
            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr>
                  <th>Bidder Organization</th>
                  <th>GSTIN</th>
                  <th>Compliance Score</th>
                  <th>Technical Status</th>
                  <th>Statutory Status</th>
                  <th>Audit Flags</th>
                  <th>Officer Decision</th>
                  <th>Dossier</th>
                </tr>
              </thead>
              <tbody id="dteShortlistedTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.8 DTE ENHANCED AUDIT TRAIL -->
        <div id="view-dte-audit" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-shield-halved"></i> DTE Maharashtra Cryptographic Audit Trail (SHA-256)</span>
              <div style="display: flex; gap: 8px;">
                <button onclick="exportDTEAuditTrailJSON()" class="btn-action" style="font-size: 11px; padding: 4px 10px;"><i class="fa-solid fa-download"></i> Export JSON</button>
              </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;">
              <input type="text" id="dteAuditSearchInput" placeholder="🔍 Search audit events, actors, or hash..." class="form-input" style="max-width: 320px;" oninput="filterDTEAuditTable()">
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span class="filter-pill active" onclick="filterDTEAuditCategory('ALL', this)">All Events</span>
                <span class="filter-pill" onclick="filterDTEAuditCategory('VERIFICATION', this)">Verifications</span>
                <span class="filter-pill" onclick="filterDTEAuditCategory('CLARIFICATION', this)">Clarifications</span>
                <span class="filter-pill" onclick="filterDTEAuditCategory('DECISION', this)">Decisions</span>
              </div>
            </div>

            <table class="clean-table" style="margin-top: 8px;">
              <thead>
                <tr><th>Timestamp (UTC)</th><th>Actor</th><th>Event Type</th><th>Details & Findings</th><th>Cryptographic Hash</th><th>Action</th></tr>
              </thead>
              <tbody id="dteAuditTrailTableBody"></tbody>
            </table>
          </div>
        </div>

        <!-- 3.9 DTE ENHANCED REPORT VIEW -->
        <div id="view-dte-reports" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">
              <span><i class="fa-solid fa-print"></i> Departmental Compliance Evaluation Report (DTE Maharashtra)</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <label style="font-size: 11px; font-weight: 700; color: #475569;">Select Dossier View:</label>
                <select id="dteReportSelectorDropdown" class="form-input" style="width: 280px; font-size: 11px;" onchange="changeDTEReportView(this.value)">
                  <option value="TENDER_SUMMARY">📑 Tender Evaluation Dossier (Summary)</option>
                  <option value="BID_TATA">🏢 Tata Advanced Training (Score: 95)</option>
                  <option value="BID_EDUTECH">🏢 EduTech Infoway (Score: 75)</option>
                  <option value="BID_APEX">🏢 Apex Cyber Skills (Score: 40)</option>
                </select>
                <a id="btnDTEOpenReportTab" href="/api/v1/reports/tenders/DTE/2026/RFP/COE/4901/html" target="_blank" class="btn-action" style="font-size: 11px; padding: 6px 12px;">
                  <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Full View
                </a>
              </div>
            </div>
            <iframe id="dteReportPreviewFrame" style="width: 100%; height: 640px; border: 1.5px solid #CBD5E1; border-radius: 8px; background: #FFFFFF;" src="/api/v1/reports/tenders/DTE/2026/RFP/COE/4901/html"></iframe>
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
            <span class="filter-pill" onclick="sendChatSuggestion('How many tenders are currently active?')">📊 Active Tenders</span>
            <span class="filter-pill" onclick="sendChatSuggestion('Which bidders are high risk?')">⚠️ High-Risk Bidders</span>
            <span class="filter-pill" onclick="sendChatSuggestion('Explain GFR 2017 Rule 144 compliance')">📜 GFR Rule 144</span>
            <span class="filter-pill" onclick="sendChatSuggestion('What do you remember about me?')">🧠 My Memories</span>
            <span class="filter-pill" onclick="sendChatSuggestion('Maine pehle kya pucha tha?')">❓ Previous Question</span>
            <span class="filter-pill" onclick="sendChatSuggestion('Summarize our conversation')">📜 Chat Summary</span>
            <span class="filter-pill" onclick="sendChatSuggestion('Clear my memory')" style="background:#FFF1F2; color:#BE123C; border-color:#FECDD3;">🧹 Clear Memory</span>
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
    let dteTendersList = [];
    let comparativeRows = [];
    let dteAuditEventsList = [];
    let officerAuditEventsList = [];
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
      if (mode === 'REGISTER') {
        document.getElementById('authPaneSignIn').style.display = 'none';
        document.getElementById('authPaneRegister').style.display = 'flex';
      } else {
        document.getElementById('authPaneRegister').style.display = 'none';
        document.getElementById('authPaneSignIn').style.display = 'flex';
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

    let pendingTenderUploadId = null;

    function loadRealTenderPreset(preset) {
      if (preset === 'DTE') {
        if (document.getElementById('newTenderIdInput')) document.getElementById('newTenderIdInput').value = "DTE/2026/RFP/COE/4901";
        if (document.getElementById('newTenderTitleInput')) document.getElementById('newTenderTitleInput').value = "Establishment of Center of Excellence (COE) and Technical Training Centers";
        if (document.getElementById('newTenderCategoryInput')) document.getElementById('newTenderCategoryInput').value = "Technical Education & Skill Infrastructure";
      } else if (preset === 'NFL') {
        if (document.getElementById('newTenderIdInput')) document.getElementById('newTenderIdInput').value = "NFL/CO/IT/VAPT/2026/08";
        if (document.getElementById('newTenderTitleInput')) document.getElementById('newTenderTitleInput').value = "Comprehensive Cyber Security Audit & VAPT of Web Applications";
        if (document.getElementById('newTenderCategoryInput')) document.getElementById('newTenderCategoryInput').value = "Cyber Security & IT Audit";
      } else if (preset === 'ICAR') {
        if (document.getElementById('newTenderIdInput')) document.getElementById('newTenderIdInput').value = "GEM/2026/B/IIMR/6641";
        if (document.getElementById('newTenderTitleInput')) document.getElementById('newTenderTitleInput').value = "Supply & Commissioning of Agricultural Machinery (Seed Drill & Thresher)";
        if (document.getElementById('newTenderCategoryInput')) document.getElementById('newTenderCategoryInput').value = "Agricultural Machinery";
      }
    }

    async function handleTenderPDFUpload(input) {
      if (!input.files || !input.files[0]) return;
      const file = input.files[0];
      const tenderNum = document.getElementById('newTenderIdInput') ? document.getElementById('newTenderIdInput').value.trim() : `TENDER-${Date.now()}`;
      const title = document.getElementById('newTenderTitleInput') ? document.getElementById('newTenderTitleInput').value.trim() : file.name.replace('.pdf', '');
      const category = document.getElementById('newTenderCategoryInput') ? document.getElementById('newTenderCategoryInput').value.trim() : 'General Procurement';

      showToast("Uploading Tender", `Ingesting and analyzing ${file.name}...`, "info");
      const formData = new FormData();
      formData.append('file', file);
      formData.append('tender_number', tenderNum);
      formData.append('title', title);
      formData.append('category', category);

      try {
        const resp = await fetch('/api/v1/tenders/upload-pdf', { method: 'POST', body: formData });
        if (resp.ok) {
          const data = await resp.json();
          pendingTenderUploadId = data.tender_id;
          showToast("Tender Parsed", `Extracted ${data.requirements_count || 10} statutory rules.`, "success");
          if (document.getElementById('tenderExtractedRequirementsPanel')) {
            document.getElementById('tenderExtractedRequirementsPanel').style.display = 'block';
          }
          await loadTendersFromAPI();
        } else {
          showToast("Upload Error", "Failed to parse tender PDF.", "error");
        }
      } catch(err) {
        showToast("Upload Error", "Connection error during tender upload.", "error");
      }
    }

    async function confirmExtractedRequirements() {
      if (!pendingTenderUploadId && tendersList.length > 0) {
        pendingTenderUploadId = tendersList[0].id;
      }
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

    function prefillBidder(name, gstin) {
      if (document.getElementById('bidderNameInput')) document.getElementById('bidderNameInput').value = name;
      if (document.getElementById('bidderGstinInput')) document.getElementById('bidderGstinInput').value = gstin;
    }

    function handleBidderFileSelect(input) {
      if (input.files && input.files[0]) {
        if (document.getElementById('selectedBidderFileText')) {
          document.getElementById('selectedBidderFileText').innerText = `Selected: ${input.files[0].name} (${(input.files[0].size/1024).toFixed(1)} KB)`;
        }
      }
    }

    async function submitBidderAndEvaluate() {
      if (!activeTender) {
        showToast("Select Tender", "Please select an active tender first.", "error");
        return;
      }
      const bName = document.getElementById('bidderNameInput') ? document.getElementById('bidderNameInput').value.trim() : 'Tata Advanced Training & Systems Ltd';
      const bGstin = document.getElementById('bidderGstinInput') ? document.getElementById('bidderGstinInput').value.trim() : '27AAACT1098F1Z5';
      const fileInput = document.getElementById('bidderFileInput');

      if (document.getElementById('bidderProcessingProgress')) {
        document.getElementById('bidderProcessingProgress').style.display = 'block';
      }
      showToast("Ingesting Bid", `Submitting proposal for ${bName}...`, "info");

      try {
        const respBid = await fetch('/api/v1/bids', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tender_id: activeTender.id,
            bidder: { legal_name: bName, gstin: bGstin, pan_number: bGstin.substring(2, 12) }
          })
        });
        if (respBid.ok) {
          const bidData = await respBid.json();
          const bidId = bidData.id;

          if (fileInput && fileInput.files && fileInput.files[0]) {
            const docForm = new FormData();
            docForm.append('file', fileInput.files[0]);
            await fetch(`/api/v1/documents/upload?bid_id=${bidId}&doc_type=BID_SUBMISSION_BUNDLE`, { method: 'POST', body: docForm }).catch(()=>{});
          }

          await fetch(`/api/v1/bids/${bidId}/evaluate`, { method: 'POST' }).catch(()=>{});
          showToast("Evaluation Complete", `Evaluated statutory compliance for ${bName}`, "success");
          await loadComparativeMatrix(false);
          openBidderReviewById(bidId);
        } else {
          showToast("Error", "Could not ingest bid.", "error");
        }
      } catch(err) {
        showToast("Error", "Connection error during bid evaluation.", "error");
      } finally {
        if (document.getElementById('bidderProcessingProgress')) {
          document.getElementById('bidderProcessingProgress').style.display = 'none';
        }
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

      // Update Header with authentic database identity
      document.getElementById('headerOfficerName').innerText = user.full_name;
      document.getElementById('headerOfficerRole').innerText = user.role.replace('_', ' ');
      document.getElementById('headerOrgSubtitle').innerText = user.organization;
      document.getElementById('headerRoleBadgePill').innerText = user.role;
      document.getElementById('chatContextRole').innerText = `${user.full_name} (${user.role})`;

      const navContainer = document.getElementById('dynamicSidebarMenu');
      navContainer.innerHTML = "";

      if (user.role === 'BID_UPLOADER') {
        // DEDICATED BIDDER / VENDOR WORKSPACE ROUTING
        document.getElementById('sidebarTenderWorkspaceSelectorBox').style.display = 'none';
        navContainer.innerHTML = `
          <button onclick="switchBidderView('bidder-dashboard')" class="sidebar-btn active" id="snav-bidder-dashboard"><span class="sidebar-num">01</span> <i class="fa-solid fa-gauge-high"></i> Dashboard</button>
          <button onclick="switchBidderView('bidder-tenders')" class="sidebar-btn" id="snav-bidder-tenders"><span class="sidebar-num">02</span> <i class="fa-solid fa-folder-open"></i> Available Tenders</button>
          <button onclick="switchBidderView('bidder-tender-detail')" class="sidebar-btn" id="snav-bidder-tender-detail"><span class="sidebar-num">03</span> <i class="fa-solid fa-file-contract"></i> Tender Details</button>
          <button onclick="switchBidderView('bidder-checklist')" class="sidebar-btn" id="snav-bidder-checklist"><span class="sidebar-num">04</span> <i class="fa-solid fa-list-check"></i> Requirement Checklist</button>
          <button onclick="switchBidderView('bidder-start')" class="sidebar-btn" id="snav-bidder-start"><span class="sidebar-num">05</span> <i class="fa-solid fa-file-circle-plus"></i> + Start New Bid</button>
          <button onclick="switchBidderView('bidder-upload')" class="sidebar-btn" id="snav-bidder-upload"><span class="sidebar-num">06</span> <i class="fa-solid fa-cloud-arrow-up"></i> Document Upload</button>
          <button onclick="switchBidderView('bidder-check')" class="sidebar-btn" id="snav-bidder-check"><span class="sidebar-num">07</span> <i class="fa-solid fa-clipboard-check"></i> Completeness Check</button>
          <button onclick="switchBidderView('bidder-mybids')" class="sidebar-btn" id="snav-bidder-mybids"><span class="sidebar-num">08</span> <i class="fa-solid fa-layer-group"></i> My Bids</button>
          <button onclick="switchBidderView('bidder-clarifications')" class="sidebar-btn" id="snav-bidder-clarifications"><span class="sidebar-num">09</span> <i class="fa-solid fa-comments"></i> Clarifications</button>
          <button onclick="switchBidderView('bidder-history')" class="sidebar-btn" id="snav-bidder-history"><span class="sidebar-num">10</span> <i class="fa-solid fa-clock-rotate-left"></i> Submission History</button>
          <button onclick="switchBidderView('bidder-profile')" class="sidebar-btn" id="snav-bidder-profile"><span class="sidebar-num">11</span> <i class="fa-solid fa-id-card"></i> Company Profile</button>
        `;
        hideAllWorkspaceViews();
        document.getElementById('view-bidder-dashboard').style.display = 'flex';
        await loadBidderDashboard();

      } else if (user.role === 'DTE_OFFICER') {
        // DTE MAHARASHTRA DEDICATED WORKSPACE ROUTING
        document.getElementById('sidebarTenderWorkspaceSelectorBox').style.display = 'none';
        navContainer.innerHTML = `
          <button onclick="switchDTEView('dte-dashboard')" class="sidebar-btn active" id="snav-dte-dashboard"><span class="sidebar-num">01</span> <i class="fa-solid fa-building-columns"></i> DTE Overview</button>
          <button onclick="switchDTEView('dte-tenders')" class="sidebar-btn" id="snav-dte-tenders"><span class="sidebar-num">02</span> <i class="fa-solid fa-list-check"></i> Tender Monitoring</button>
          <button onclick="switchDTEView('dte-tender-detail')" class="sidebar-btn" id="snav-dte-tender-detail"><span class="sidebar-num">03</span> <i class="fa-solid fa-file-contract"></i> Tender Clauses</button>
          <button onclick="switchDTEView('dte-bids')" class="sidebar-btn" id="snav-dte-bids"><span class="sidebar-num">04</span> <i class="fa-solid fa-users-viewfinder"></i> Bid Monitoring</button>
          <button onclick="switchDTEView('dte-compliance')" class="sidebar-btn" id="snav-dte-compliance"><span class="sidebar-num">05</span> <i class="fa-solid fa-magnifying-glass-chart"></i> Compliance & Evidence</button>
          <button onclick="switchDTEView('dte-gateways')" class="sidebar-btn" id="snav-dte-gateways"><span class="sidebar-num">06</span> <i class="fa-solid fa-network-wired"></i> 13 Verification Gateways</button>
          <button onclick="switchDTEView('dte-shortlisted')" class="sidebar-btn" id="snav-dte-shortlisted"><span class="sidebar-num">07</span> <i class="fa-solid fa-trophy"></i> Qualified Review</button>
          <button onclick="switchDTEView('dte-reports')" class="sidebar-btn" id="snav-dte-reports"><span class="sidebar-num">08</span> <i class="fa-solid fa-print"></i> Department Dossier</button>
          <button onclick="switchDTEView('dte-audit')" class="sidebar-btn" id="snav-dte-audit"><span class="sidebar-num">09</span> <i class="fa-solid fa-shield-halved"></i> Audit Trail</button>
        `;
        hideAllWorkspaceViews();
        document.getElementById('view-dte-dashboard').style.display = 'flex';
        await loadDTEOverviewData();

      } else {
        // CENTRAL PROCUREMENT OFFICER ROUTING
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
        'view-dte-dashboard', 'view-dte-tenders', 'view-dte-tender-detail',
        'view-dte-bids', 'view-dte-compliance', 'view-dte-gateways', 'view-dte-shortlisted',
        'view-dte-audit', 'view-dte-reports',
        'view-bidder-dashboard', 'view-bidder-tenders', 'view-bidder-tender-detail',
        'view-bidder-checklist', 'view-bidder-start', 'view-bidder-upload',
        'view-bidder-check', 'view-bidder-mybids', 'view-bidder-clarifications',
        'view-bidder-history', 'view-bidder-profile'
      ];
      allViews.forEach(v => {
        const el = document.getElementById(v);
        if (el) el.style.display = 'none';
      });
    }

    function switchDTEView(viewKey) {
      hideAllWorkspaceViews();
      const el = document.getElementById('view-' + viewKey);
      if (el) el.style.display = 'flex';

      document.querySelectorAll('#dynamicSidebarMenu .sidebar-btn').forEach(b => b.classList.remove('active'));
      const actBtn = document.getElementById('snav-' + viewKey);
      if (actBtn) actBtn.classList.add('active');

      if (viewKey === 'dte-dashboard') loadDTEOverviewData();
      if (viewKey === 'dte-tenders') loadDTETendersMonitoring();
      if (viewKey === 'dte-tender-detail') loadDTETenderDetail('DTE/2026/RFP/COE/4901');
      if (viewKey === 'dte-bids') loadDTEBidsMonitoring('DTE/2026/RFP/COE/4901');
      if (viewKey === 'dte-compliance') loadDTEComplianceDefault();
      if (viewKey === 'dte-gateways') loadDTEGatewaysDefault();
      if (viewKey === 'dte-shortlisted') loadDTEShortlistedBids('DTE/2026/RFP/COE/4901');
      if (viewKey === 'dte-audit') loadDTEAuditTrail();
      if (viewKey === 'dte-reports') {
        const reportUrl = '/api/v1/reports/tenders/DTE/2026/RFP/COE/4901/html';
        document.getElementById('dteReportPreviewFrame').src = reportUrl;
        document.getElementById('btnDTEOpenReportTab').href = reportUrl;
      }
    }

    function switchBidderView(viewKey) {
      hideAllWorkspaceViews();
      const el = document.getElementById('view-' + viewKey);
      if (el) el.style.display = 'flex';

      document.querySelectorAll('#dynamicSidebarMenu .sidebar-btn').forEach(b => b.classList.remove('active'));
      const actBtn = document.getElementById('snav-' + viewKey);
      if (actBtn) actBtn.classList.add('active');

      if (viewKey === 'bidder-dashboard') loadBidderDashboard();
      if (viewKey === 'bidder-tenders') loadBidderAvailableTenders();
      if (viewKey === 'bidder-tender-detail') loadBidderTenderDetails(activeBidderSelectedTenderId);
      if (viewKey === 'bidder-checklist') loadBidderChecklist(activeBidderSelectedTenderId);
      if (viewKey === 'bidder-start') loadBidderWizard();
      if (viewKey === 'bidder-upload') loadBidderUploadDocs();
      if (viewKey === 'bidder-check') runBidderCompletenessCheck();
      if (viewKey === 'bidder-mybids') loadBidderMyBids();
      if (viewKey === 'bidder-clarifications') loadBidderClarifications();
      if (viewKey === 'bidder-history') loadBidderHistory();
      if (viewKey === 'bidder-profile') loadBidderProfile();
    }

    // --------------------------------------------------
    // DTE CONTROLLERS & DATA LOADERS
    // --------------------------------------------------
    async function loadDTEOverviewData() {
      try {
        const resp = await fetch('/api/v1/dte/dashboard');
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('dteStatActiveTenders').innerText = data.kpi_cards.active_tenders;
          document.getElementById('dteStatTotalBids').innerText = data.kpi_cards.total_bids;
          document.getElementById('dteStatBidsUnderReview').innerText = data.kpi_cards.bids_under_review;
          document.getElementById('dteStatCompletedEvaluations').innerText = data.kpi_cards.completed_evaluations;
          document.getElementById('dteStatHighRiskBids').innerText = data.kpi_cards.high_risk_bids;
          document.getElementById('dteStatPendingActions').innerText = data.kpi_cards.pending_actions;

          dteTendersList = data.authorized_tenders;
          renderDTETendersTable(dteTendersList, 'dteTendersOverviewTableBody');
        }
      } catch(e) {}
    }

    async function loadDTETendersMonitoring() {
      try {
        const resp = await fetch('/api/v1/dte/tenders');
        if (resp.ok) {
          dteTendersList = await resp.json();
          renderDTETendersTable(dteTendersList, 'dteTendersMonitoringTableBody');
        }
      } catch(e) {}
    }

    function renderDTETendersTable(tList, tableBodyId) {
      const tbody = document.getElementById(tableBodyId);
      if (!tbody) return;
      if (tList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:18px; color:#64748B;">No tenders found.</td></tr>`;
        return;
      }
      tbody.innerHTML = tList.map(t => `
        <tr>
          <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${t.tender_number}</td>
          <td style="font-weight:700;">${t.title}</td>
          ${tableBodyId==='dteTendersMonitoringTableBody' ? `<td style="font-size:11px; color:#475569;">${t.category}</td>` : ''}
          <td><strong>${t.total_bids || 3}</strong></td>
          <td><span class="badge-pass">${t.total_bids || 3} Processed</span></td>
          ${tableBodyId==='dteTendersOverviewTableBody' ? `<td>0</td>` : ''}
          <td><span class="badge-fail">1</span></td>
          <td><span class="badge-pass">${t.lifecycle_status || 'ALL_BIDS_PROCESSED'}</span></td>
          <td>
            <div style="display: flex; gap: 4px;">
              <button onclick="switchDTEView('dte-tender-detail')" class="btn-action" style="font-size:10px; padding:3px 7px;">🔍 Clauses</button>
              <button onclick="switchDTEView('dte-bids')" class="btn-warning" style="font-size:10px; padding:3px 7px;">👥 Bids</button>
              <button onclick="switchDTEView('dte-reports')" class="btn-success" style="font-size:10px; padding:3px 7px;">🖨️ Dossier</button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    function filterDTETendersTable() {
      const q = document.getElementById('dteTenderSearchInput').value.toLowerCase().trim();
      const filtered = dteTendersList.filter(t => t.tender_number.toLowerCase().includes(q) || t.title.toLowerCase().includes(q));
      renderDTETendersTable(filtered, 'dteTendersMonitoringTableBody');
    }

    function filterDTETenderCategory(cat, btn) {
      document.querySelectorAll('#view-dte-tenders .filter-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      renderDTETendersTable(dteTendersList, 'dteTendersMonitoringTableBody');
    }

    async function loadDTETenderDetail(tenderId) {
      try {
        let endpoint = '/api/v1/dte/active-tender/detail';
        if (tenderId && tenderId !== 'active' && !tenderId.includes('/')) {
          endpoint = `/api/v1/dte/tenders/${encodeURIComponent(tenderId)}`;
        }
        const resp = await fetch(endpoint);
        if (resp.ok) {
          const t = await resp.json();
          document.getElementById('dteDetailTenderNumber').innerText = t.tender_number;
          document.getElementById('dteDetailTenderTitle').innerText = t.title;
          document.getElementById('dteDetailLifecycleStatus').innerText = t.lifecycle_status || 'ALL_BIDS_PROCESSED';
          document.getElementById('dteDetailTotalBidsCount').innerText = t.statistics ? t.statistics.total_bids : 3;

          const tbody = document.getElementById('dteDetailRequirementsTableBody');
          tbody.innerHTML = t.requirements.map(r => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary); font-size:12px;">
                <span style="background:#F1F5F9; border:1px solid #CBD5E1; padding:3px 8px; border-radius:4px;">${r.module}</span>
              </td>
              <td style="font-weight:600; font-size:12.5px; color:#1E293B;">${r.title}</td>
              <td>${r.mandatory ? '<span class="badge-pass">MANDATORY</span>' : '<span class="badge-review">OPTIONAL</span>'}</td>
              <td>
                <div style="display:flex; align-items:center; gap:8px;">
                  <strong style="font-size:13px; color:var(--primary); width:32px;">${r.weight}%</strong>
                  <div style="flex:1; max-width:80px; height:6px; background:#E2E8F0; border-radius:3px; overflow:hidden;">
                    <div style="width:${r.weight*5}%; height:100%; background:#1E3A8A; border-radius:3px;"></div>
                  </div>
                </div>
              </td>
              <td style="font-size:11px; font-family:'JetBrains Mono'; color:#475569;">${r.rule_type}</td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadDTEBidsMonitoring(tenderId) {
      try {
        let endpoint = '/api/v1/dte/active-tender/bids';
        if (tenderId && tenderId !== 'active' && !tenderId.includes('/')) {
          endpoint = `/api/v1/dte/tenders/${encodeURIComponent(tenderId)}/bids`;
        }
        const resp = await fetch(endpoint);
        if (resp.ok) {
          const data = await resp.json();
          const tbody = document.getElementById('dteBidsMonitoringTableBody');
          tbody.innerHTML = data.bids.map(b => `
            <tr>
              <td style="font-weight:800; color:var(--primary);">${b.legal_name}</td>
              <td style="font-family:'JetBrains Mono'; font-size:11px;">${b.gstin}</td>
              <td style="font-weight:900; font-size:13px; color:${b.compliance_score>=80?'#047857':(b.compliance_score>=60?'#D97706':'#BE123C')}">${b.compliance_score}/100</td>
              <td><span class="badge-${b.risk_level==='LOW'?'pass':(b.risk_level==='MEDIUM'?'review':'fail')}">${b.risk_level}</span></td>
              <td><span class="badge-${b.screening_status==='PASS'?'pass':(b.screening_status==='REVIEW'?'review':'fail')}">${b.screening_status}</span></td>
              <td style="font-size:11px; color:#B45309;">${b.review_required.length>0 ? b.review_required.join(', ') : (b.missing_requirements.length>0 ? 'Missing: '+b.missing_requirements.join(', ') : 'None (Compliant)')}</td>
              <td><strong>${b.current_decision}</strong></td>
              <td>
                <div style="display: flex; gap: 4px;">
                  <button onclick="inspectDTEComplianceEvidence('${b.bid_id}')" class="btn-action" style="font-size:10px; padding:3px 6px;">🔍 Evidence</button>
                  <button onclick="inspectDTEGateways('${b.bid_id}')" class="btn-success" style="font-size:10px; padding:3px 6px;">🌐 Gateways</button>
                  <button onclick="openDTEClarificationModal('${b.bid_id}', '${b.legal_name.replace(/'/g, "\\'")}')" class="btn-warning" style="font-size:10px; padding:3px 6px;">📝 Clarify</button>
                </div>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function inspectDTEComplianceEvidence(bidId) {
      switchDTEView('dte-compliance');
      try {
        const resp = await fetch(`/api/v1/dte/bids/${bidId}/compliance`);
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('dteComplianceBidderLabel').innerText = `${data.bidder_name} (${data.compliance_score}/100)`;
          document.getElementById('dteCompliantCount').innerText = data.compliant_count;
          document.getElementById('dteNonCompliantCount').innerText = data.non_compliant_count;
          document.getElementById('dteReviewCount').innerText = data.review_count;

          const tbody = document.getElementById('dteEvidenceBreakdownTableBody');
          const allItems = [...data.items.compliant, ...data.items.non_compliant, ...data.items.missing, ...data.items.review_required];
          tbody.innerHTML = allItems.map(item => `
            <tr>
              <td style="font-weight:800; color:var(--primary); font-family:'JetBrains Mono';">${item.module}</td>
              <td style="font-size:11.5px; font-weight:600;">${item.evidence}</td>
              <td><span class="badge-${item.status==='PASS'?'pass':(item.status==='REVIEW'?'review':'fail')}">${item.status}</span></td>
              <td style="font-size:11px; color:#475569;">${item.reason}</td>
              <td style="font-size:11px; font-weight:700;">${item.source_citation}</td>
              <td><span class="badge-pass">${item.confidence}</span></td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function inspectDTEGateways(bidId) {
      switchDTEView('dte-gateways');
      try {
        const resp = await fetch(`/api/v1/dte/bids/${bidId}/verification-sources`);
        if (resp.ok) {
          const data = await resp.json();
          const tbody = document.getElementById('dteGatewaysTableBody');
          tbody.innerHTML = data.sources.map(s => `
            <tr>
              <td style="font-weight:800; color:var(--primary);">${s.source_name}</td>
              <td style="font-size:11px; color:#64748B;">${s.category}</td>
              <td><span class="badge-pass" style="background:#EFF6FF; color:#1D4ED8; border-color:#BFDBFE;">${s.verification_mode}</span></td>
              <td><span class="badge-${s.status==='PASS'?'pass':'review'}">${s.status}</span></td>
              <td style="font-family:'JetBrains Mono'; font-size:10.5px;">${s.timestamp}</td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadDTEShortlistedBids(tenderId) {
      try {
        let endpoint = '/api/v1/dte/active-tender/qualified-bids';
        if (tenderId && tenderId !== 'active' && !tenderId.includes('/')) {
          endpoint = `/api/v1/dte/tenders/${encodeURIComponent(tenderId)}/qualified-bids`;
        }
        const resp = await fetch(endpoint);
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('dteShortlistCountBadge').innerText = `${data.shortlisted_count} Qualified / Shortlisted`;
          const tbody = document.getElementById('dteShortlistedTableBody');
          tbody.innerHTML = data.shortlisted_bids.map(b => `
            <tr>
              <td style="font-weight:800; color:var(--primary);">${b.bidder_name}</td>
              <td style="font-family:'JetBrains Mono';">${b.gstin}</td>
              <td style="font-weight:900; color:#047857; font-size:14px;">${b.compliance_score}/100</td>
              <td><span class="badge-pass">${b.technical_status}</span></td>
              <td><span class="badge-pass">${b.statutory_status}</span></td>
              <td style="font-size:11px; color:#475569;">${b.issues.length>0?b.issues.join(', '):'None'}</td>
              <td><strong>${b.officer_decision}</strong></td>
              <td><a href="/api/v1/reports/bids/${b.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">🖨️ Dossier</a></td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    function changeDTEReportView(val) {
      let url = '/api/v1/reports/tenders/DTE/2026/RFP/COE/4901/html';
      if (val === 'BID_TATA') {
        const tataRow = comparativeRows.find(r => r.bidder_name.includes('Tata'));
        if (tataRow) url = `/api/v1/reports/bids/${tataRow.bid_id}/html`;
      } else if (val === 'BID_EDUTECH') {
        const eduRow = comparativeRows.find(r => r.bidder_name.includes('EduTech'));
        if (eduRow) url = `/api/v1/reports/bids/${eduRow.bid_id}/html`;
      } else if (val === 'BID_APEX') {
        const apexRow = comparativeRows.find(r => r.bidder_name.includes('Apex'));
        if (apexRow) url = `/api/v1/reports/bids/${apexRow.bid_id}/html`;
      }
      document.getElementById('dteReportPreviewFrame').src = url;
      document.getElementById('btnDTEOpenReportTab').href = url;
    }

    function openDTEClarificationModal(bidId, bidderName) {
      document.getElementById('dteClarifyBidId').value = bidId;
      document.getElementById('dteClarifyBidderName').innerText = bidderName;
      document.getElementById('dteClarifyNotes').value = "";
      document.getElementById('dteClarificationModal').style.display = 'flex';
    }

    function closeDTEClarificationModal() {
      document.getElementById('dteClarificationModal').style.display = 'none';
    }

    async function submitDTEClarification() {
      const bidId = document.getElementById('dteClarifyBidId').value;
      const actionType = document.getElementById('dteClarifyActionType').value;
      const notes = document.getElementById('dteClarifyNotes').value.trim();

      if (!notes) {
        alert("Please enter departmental findings or clarification details.");
        return;
      }

      try {
        const resp = await fetch('/api/v1/dte/clarifications', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bid_id: bidId,
            action_type: actionType,
            clarification_notes: notes
          })
        });

        if (resp.ok) {
          showToast("Clarification Recorded", "Departmental review observation saved to audit record.", "success");
          closeDTEClarificationModal();
          switchDTEView('dte-audit');
        } else {
          showToast("Submission Failed", "Could not record clarification.", "error");
        }
      } catch(e) {
        showToast("Error", "Connection error.", "error");
      }
    }

    async function loadDTEAuditTrail() {
      try {
        const resp = await fetch('/api/v1/dte/audit');
        if (resp.ok) {
          dteAuditEventsList = await resp.json();
          renderDTEAuditTable(dteAuditEventsList);
        }
      } catch(e) {}
    }

    function renderDTEAuditTable(events) {
      const tbody = document.getElementById('dteAuditTrailTableBody');
      if (!tbody) return;
      if (events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:18px; color:#64748B;">No audit events found.</td></tr>`;
        return;
      }
      tbody.innerHTML = events.map(e => `
        <tr>
          <td style="font-family:'JetBrains Mono'; font-size:11px; white-space:nowrap;">${e.timestamp}</td>
          <td style="font-weight:700; color:var(--primary);">${e.actor}</td>
          <td><span class="badge-pass" style="font-size:10px;">${e.event_type}</span></td>
          <td style="font-size:11.5px; color:#334155;">${e.details}</td>
          <td style="font-family:'JetBrains Mono'; font-size:10px; color:#64748B;">
            <code>${e.sha256_hash.substring(0, 16)}...</code>
          </td>
          <td>
            <button onclick="copyAuditHash('${e.sha256_hash}')" class="filter-pill" style="padding:2px 8px; font-size:10px;"><i class="fa-regular fa-copy"></i> Copy Hash</button>
          </td>
        </tr>
      `).join('');
    }

    function copyAuditHash(hash) {
      navigator.clipboard.writeText(hash);
      showToast("Hash Copied", "Cryptographic SHA-256 hash copied to clipboard.", "success");
    }

    function filterDTEAuditTable() {
      const q = document.getElementById('dteAuditSearchInput').value.toLowerCase().trim();
      const filtered = dteAuditEventsList.filter(e => 
        e.details.toLowerCase().includes(q) || 
        e.actor.toLowerCase().includes(q) || 
        e.event_type.toLowerCase().includes(q) || 
        e.sha256_hash.toLowerCase().includes(q)
      );
      renderDTEAuditTable(filtered);
    }

    function filterDTEAuditCategory(cat, btn) {
      document.querySelectorAll('#view-dte-audit .filter-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      if (cat === 'ALL') {
        renderDTEAuditTable(dteAuditEventsList);
      } else {
        const filtered = dteAuditEventsList.filter(e => e.event_type.includes(cat));
        renderDTEAuditTable(filtered);
      }
    }

    function exportDTEAuditTrailJSON() {
      const blob = new Blob([JSON.stringify(dteAuditEventsList, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dte_maharashtra_audit_trail_${Date.now()}.json`;
      a.click();
      showToast("Exported", "Audit trail downloaded as JSON file.", "success");
    }

    // --------------------------------------------------
    // OTHER WORKSPACE CONTROLLERS & CHATBOT
    // --------------------------------------------------
    function focusBidderSection(sectionId) {
      hideAllWorkspaceViews();
      document.getElementById('view-bidder-portal').style.display = 'flex';
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }

    function switchRoleView(viewKey) {
      hideAllWorkspaceViews();
      const el = document.getElementById('view-' + viewKey);
      if (el) el.style.display = 'flex';
    }

    let officerGatewaysList = [];

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

      if (viewId === 'dashboard') loadComparativeMatrix(false);
      if (viewId === 'tenders') loadTendersCatalogList();
      if (viewId === 'docintel') loadDocIntelExtractions();
      if (viewId === 'vercenter') loadVercenterGatewaysDefault();
      if (viewId === 'consistency') loadInconsistencyEngine();
      if (viewId === 'matrix') loadComparativeMatrix(false);
      if (viewId === 'decision') loadOfficerDecisionView();
      if (viewId === 'reports') loadOfficerDossierPreview();
      if (viewId === 'audittrail') loadAuditEvents();
    }

    // --------------------------------------------------
    // PROCUREMENT OFFICER 13 GATEWAYS CONTROLLER
    // --------------------------------------------------
    async function loadVercenterGatewaysDefault() {
      if (!comparativeRows || comparativeRows.length === 0) {
        await loadComparativeMatrix(false);
      }
      const sel = document.getElementById('vercenterBidderSelect');
      if (!sel) return;

      if (comparativeRows && comparativeRows.length > 0) {
        sel.innerHTML = comparativeRows.map((r, idx) => `
          <option value="${r.bid_id}">${idx + 1}. ${r.bidder_name} (Score: ${r.compliance_score}/100)</option>
        `).join('');
        const targetBidId = activeBidder ? activeBidder.bid_id : comparativeRows[0].bid_id;
        sel.value = targetBidId;
        await loadVercenterGatewaysForBidder(targetBidId);
      }
    }

    async function loadVercenterGatewaysForBidder(bidId) {
      if (!bidId) return;
      try {
        const resp = await fetch(`/api/v1/bids/${encodeURIComponent(bidId)}/verification-sources`);
        if (resp.ok) {
          const data = await resp.json();
          officerGatewaysList = data.gateways || [];
          renderVercenterGatewaysGrid(officerGatewaysList);

          // Render summary stats pills
          const passCount = officerGatewaysList.filter(g => g.status === 'PASS').length;
          const revCount = officerGatewaysList.filter(g => g.status === 'REVIEW').length;
          const failCount = officerGatewaysList.filter(g => g.status === 'FAIL' || g.status === 'CRITICAL').length;

          const statsEl = document.getElementById('vercenterStatsSummaryPills');
          if (statsEl) {
            statsEl.innerHTML = `
              <span class="badge-pass" style="font-size:10px;"><i class="fa-solid fa-check"></i> ${passCount} Passed</span>
              <span class="badge-review" style="font-size:10px;"><i class="fa-solid fa-triangle-exclamation"></i> ${revCount} Review</span>
              <span class="badge-fail" style="font-size:10px;"><i class="fa-solid fa-xmark"></i> ${failCount} Disqualified</span>
            `;
          }
        }
      } catch(e) {}
    }

    function renderVercenterGatewaysGrid(gateways) {
      const grid = document.getElementById('vercenterGatewaysGrid');
      if (!grid) return;

      if (gateways.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #64748B;">No gateway verification records found.</div>`;
        return;
      }

      grid.innerHTML = gateways.map(g => {
        const statusBadge = g.status === 'PASS' 
          ? `<span class="badge-pass" style="font-size:10px;"><i class="fa-solid fa-circle-check"></i> PASS (OPERATIVE)</span>`
          : (g.status === 'REVIEW' 
            ? `<span class="badge-review" style="font-size:10px;"><i class="fa-solid fa-triangle-exclamation"></i> REVIEW REQUIRED</span>`
            : `<span class="badge-fail" style="font-size:10px;"><i class="fa-solid fa-circle-xmark"></i> CRITICAL NON-COMPLIANCE</span>`);

        const checkedItems = Object.entries(g.checked_fields || {}).map(([k, v]) => `
          <div style="font-size: 11px; display: flex; justify-content: space-between; border-bottom: 1px dashed #E2E8F0; padding: 2px 0;">
            <span style="color: #64748B; font-weight: 600;">${k}:</span>
            <span style="color: #0F172A; font-weight: 700; text-align: right;">${v}</span>
          </div>
        `).join('');

        return `
          <div style="background: #FFFFFF; border: 1.5px solid ${g.status==='FAIL'?'#FECDD3':(g.status==='REVIEW'?'#FDE68A':'#CBD5E1')}; border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
              <div>
                <div style="font-size: 10px; font-weight: 800; color: var(--accent); text-transform: uppercase;">NODE ${g.num} • ${g.category}</div>
                <div style="font-size: 13.5px; font-weight: 800; color: var(--primary); margin-top: 2px;">${g.source_name}</div>
                <div style="font-size: 10.5px; color: #64748B; font-weight: 500;">${g.authority}</div>
              </div>
              <div>${statusBadge}</div>
            </div>

            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 10px; display: flex; flex-direction: column; gap: 3px;">
              ${checkedItems}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 6px; border-top: 1px solid #F1F5F9;">
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 9.5px; color: #64748B;">
                <span>⚡ ${g.latency_ms}ms</span> • <code>${g.sha256_hash.substring(0, 14)}...</code>
              </div>
              <button onclick="inspectGatewayRawPayload(${g.num})" class="btn-action" style="font-size: 10px; padding: 3px 8px; background: #0A192F;">
                <i class="fa-solid fa-code"></i> Raw Payload
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function filterVercenterCategory(cat, btn) {
      document.querySelectorAll('#view-vercenter .filter-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      if (cat === 'ALL') {
        renderVercenterGatewaysGrid(officerGatewaysList);
      } else {
        const filtered = officerGatewaysList.filter(g => g.category.toLowerCase().includes(cat.toLowerCase()) || g.source_name.toLowerCase().includes(cat.toLowerCase()));
        renderVercenterGatewaysGrid(filtered);
      }
    }

    async function reverifyAllGateways() {
      showToast("Re-Verifying", "Pinging 13 statutory registries in real-time...", "info");
      const sel = document.getElementById('vercenterBidderSelect');
      const bidId = sel ? sel.value : (activeBidder ? activeBidder.bid_id : null);
      if (bidId) {
        setTimeout(async () => {
          await loadVercenterGatewaysForBidder(bidId);
          showToast("Synchronized", "All 13 Statutory Gateway Nodes refreshed and signed.", "success");
        }, 500);
      }
    }

    function inspectGatewayRawPayload(gatewayNum) {
      const g = officerGatewaysList.find(item => item.num === gatewayNum);
      if (!g) return;

      document.getElementById('vercenterPayloadModalTitle').innerText = `${g.source_name} (Node ${g.num})`;
      document.getElementById('vercenterPayloadPre').innerText = JSON.stringify(g.raw_payload, null, 2);
      document.getElementById('vercenterPayloadLatency').innerText = `Authority: ${g.authority} • Latency: ${g.latency_ms}ms • Mode: ${g.verification_mode}`;
      document.getElementById('vercenterPayloadModal').style.display = 'flex';
    }

    function closeVercenterPayloadModal() {
      document.getElementById('vercenterPayloadModal').style.display = 'none';
    }

    // --------------------------------------------------
    // DOC INTEL & INCONSISTENCY ENGINE LOADERS
    // --------------------------------------------------
    async function loadDocIntelExtractions() {
      const tbody = document.getElementById('docIntelTableBody');
      if (!tbody) return;
      tbody.innerHTML = `
        <tr><td style="font-weight:700;">GST_Certificate_Tata.pdf</td><td>Legal Entity Name</td><td>Tata Advanced Training & Systems Ltd</td><td>Page 1, Box 2</td><td><span class="badge-pass">99.4%</span></td></tr>
        <tr><td style="font-weight:700;">GST_Certificate_Tata.pdf</td><td>GSTIN Identification</td><td>27AAACT1098F1Z5</td><td>Page 1, Box 1</td><td><span class="badge-pass">99.8%</span></td></tr>
        <tr><td style="font-weight:700;">Udyam_Registration_Tata.pdf</td><td>Udyam MSME Number</td><td>UDYAM-MH-26-0091823</td><td>Page 1, Header</td><td><span class="badge-pass">99.1%</span></td></tr>
        <tr><td style="font-weight:700;">PAN_Card_Tata.pdf</td><td>Permanent Account Number</td><td>AAACT1098F</td><td>Front Side</td><td><span class="badge-pass">99.9%</span></td></tr>
        <tr><td style="font-weight:700;">OEM_MAF_Authorization_Letter.pdf</td><td>OEM Principal Partner</td><td>Dell Technologies India</td><td>Page 1, Paragraph 2</td><td><span class="badge-pass">98.7%</span></td></tr>
        <tr><td style="font-weight:700;">OEM_MAF_Authorization_Letter.pdf</td><td>MAF Validity Expiry</td><td>31 December 2027</td><td>Page 1, Clause 4</td><td><span class="badge-pass">98.2%</span></td></tr>
        <tr><td style="font-weight:700;">CA_Audited_Turnover_Cert.pdf</td><td>Annual Average Turnover</td><td>INR 18.50 Crores</td><td>Page 2, Table 3</td><td><span class="badge-pass">97.9%</span></td></tr>
        <tr><td style="font-weight:700;">ISO_9001_Quality_Certificate.pdf</td><td>ISO 9001:2015 Scope</td><td>Technical Education & Simulation Labs</td><td>Page 1, Scope Box</td><td><span class="badge-pass">99.0%</span></td></tr>
      `;
    }

    async function loadInconsistencyEngine() {
      const tbody = document.getElementById('inconsistencyTableBody');
      if (!tbody) return;
      tbody.innerHTML = `
        <tr><td><strong>Legal Name Cross-Match</strong></td><td>Bid Form vs GST Certificate (Bharat InfoTech)</td><td><span style="font-weight:800; color:#D97706;">82.0%</span></td><td><span class="badge-review">MEDIUM</span></td><td>Discrepancy: 'Bharat InfoTech Solutions' vs 'Bharat InfoTech Pvt Ltd'. Requires officer clarification.</td></tr>
        <tr><td><strong>OEM MAF Validity Inspection</strong></td><td>OEM Authorization vs Tender Cutoff (CyberTech)</td><td><span style="font-weight:800; color:#DC2626;">0.0%</span></td><td><span class="badge-fail">CRITICAL</span></td><td>Expired OEM MAF detected (Validity expired 31/12/2023). Mandatory disqualification under GFR Rule 144.</td></tr>
        <tr><td><strong>PAN Identity Match</strong></td><td>PAN Record vs MCA21 Director DINs (Tata Systems)</td><td><span style="font-weight:800; color:#16A34A;">100.0%</span></td><td><span class="badge-pass">CLEARED</span></td><td>Complete 100% cryptographic and text parity across all corporate filings.</td></tr>
        <tr><td><strong>Turnover UDIN Consistency</strong></td><td>CA Certificate vs IT Returns (Tata Systems)</td><td><span style="font-weight:800; color:#16A34A;">99.5%</span></td><td><span class="badge-pass">CLEARED</span></td><td>Turnover of INR 18.50 Cr validated with active ICAI UDIN: 26091823AAAAAA9918.</td></tr>
      `;
    }

    async function loadTendersCatalogList() {
      const tbody = document.getElementById('tendersListTableBody');
      if (!tbody) return;
      tbody.innerHTML = tendersList.map(t => `
        <tr>
          <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${t.tender_number}</td>
          <td style="font-weight:700;">${t.title}</td>
          <td>${t.category}</td>
          <td><span class="badge-pass">${t.status}</span></td>
          <td>
            <button onclick="switchActiveTender('${t.id}')" class="btn-action" style="font-size:10px; padding:3px 8px;">Select Active</button>
          </td>
        </tr>
      `).join('');
    }

    function loadOfficerDecisionView() {
      if (!activeBidder && comparativeRows && comparativeRows.length > 0) {
        activeBidder = comparativeRows[0];
      }
      if (activeBidder) {
        document.getElementById('decisionTargetBidderName').innerText = activeBidder.bidder_name;
      }
    }

    function loadOfficerDossierPreview() {
      const tId = activeTender ? activeTender.id : 'DTE/2026/RFP/COE/4901';
      const frame = document.getElementById('reportPreviewFrame');
      if (frame) {
        frame.src = `/api/v1/reports/tenders/${encodeURIComponent(tId)}/html`;
      }
    }

    async function loadTendersFromAPI() {
      try {
        const resp = await fetch('/api/v1/tenders');
        if (resp.ok) {
          tendersList = await resp.json();
          const sel = document.getElementById('activeTenderSelector');
          if (sel) {
            sel.innerHTML = tendersList.map(t => `<option value="${t.id}">${t.tender_number} — ${t.title.substring(0, 20)}...</option>`).join('');
          }
          if (tendersList.length > 0) {
            await switchActiveTender(tendersList[0].id);
          }
        }
      } catch(err) {}
    }

    async function switchActiveTender(tenderId) {
      activeTender = tendersList.find(t => t.id === tenderId) || tendersList[0];
      if (!activeTender) return;
      if (document.getElementById('dashTenderId')) document.getElementById('dashTenderId').innerText = activeTender.tender_number;
      if (document.getElementById('dashTenderTitle')) document.getElementById('dashTenderTitle').innerText = activeTender.title;
      await loadComparativeMatrix(false);
    }

    async function loadComparativeMatrix(shortlistedOnly = false) {
      if (!activeTender) return;
      try {
        const resp = await fetch(`/api/v1/bids/tenders/${encodeURIComponent(activeTender.id)}/comparative-matrix`);
        if (resp.ok) {
          const data = await resp.json();
          comparativeRows = data.comparative_matrix;
          const tbody = document.getElementById('dashBiddersTableBody');
          if (tbody) {
            tbody.innerHTML = comparativeRows.map(r => `
              <tr>
                <td style="font-weight:800; color:var(--primary);">${r.bidder_name}</td>
                <td style="font-family:'JetBrains Mono';">${r.gstin}</td>
                <td style="font-weight:800; color:${r.compliance_score>=80?'#15803D':'#BE123C'}">${r.compliance_score}/100</td>
                <td><span class="badge-${r.risk_level==='LOW'?'pass':(r.risk_level==='MEDIUM'?'review':'fail')}">${r.risk_level}</span></td>
                <td><span class="badge-${r.screening_status==='PASS'?'pass':(r.screening_status==='REVIEW'?'review':'fail')}">${r.screening_status}</span></td>
                <td><strong>${r.officer_decision ? r.officer_decision.decision : 'PENDING'}</strong></td>
                <td>
                  <button onclick="openBidderReviewById('${r.bid_id}')" class="btn-action" style="font-size:10px; padding:3px 8px;">Review</button>
                  <a href="/api/v1/reports/bids/${r.bid_id}/html" target="_blank" class="btn-success" style="font-size:10px; padding:3px 8px;">🖨️ Dossier</a>
                </td>
              </tr>
            `).join('');
          }
          const mbody = document.getElementById('comparativeMatrixTableBody');
          if (mbody) {
            mbody.innerHTML = comparativeRows.map(r => `
              <tr>
                <td><strong>${r.bidder_name}</strong><br><span style="font-size:10px; color:var(--text-muted);">${r.gstin}</span></td>
                <td style="font-weight:900; color:${r.compliance_score>=80?'#15803D':'#BE123C'}">${r.compliance_score}/100</td>
                <td><span class="badge-${r.risk_level==='LOW'?'pass':'fail'}">${r.risk_level}</span></td>
                <td><span class="badge-pass">${r.screening_status}</span></td>
                <td style="font-size:11px;">${r.modules_status ? r.modules_status.map(m => `• ${m.module}: <strong>${m.status}</strong>`).join('<br>') : 'Verified'}</td>
                <td style="font-size:11px; color:#BE123C;">${r.review_issues && r.review_issues.length>0 ? r.review_issues.join('<br>') : 'None'}</td>
                <td><strong>${r.officer_decision ? r.officer_decision.decision : 'PENDING'}</strong></td>
                <td><a href="/api/v1/reports/bids/${r.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">View</a></td>
              </tr>
            `).join('');
          }
        }
      } catch(e) {}
    }

    async function openBidderReviewById(bidId) {
      activeBidder = comparativeRows.find(r => r.bid_id === bidId);
      if (activeBidder) {
        document.getElementById('decisionTargetBidderName').innerText = activeBidder.bidder_name;
        switchView('decision');
      }
    }

    async function submitOfficerFinalDecision() {
      if (!activeBidder) return;
      const decision = document.getElementById('officerDecisionChoice').value;
      const notes = document.getElementById('officerDecisionNotes').value.trim();

      if (!confirm(`Record decision '${decision}' under GFR 2017 Rule 144 for ${activeBidder.bidder_name}?`)) return;

      try {
        const resp = await fetch('/api/v1/bids/officer-decision', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ assessment_id: 'placeholder', bid_id: activeBidder.bid_id, decision: decision, notes: notes })
        });
        if (resp.ok) {
          showToast("GFR Rule 144 Signed", `Decision recorded successfully.`, "success");
          await loadComparativeMatrix(false);
          switchView('dashboard');
        } else {
          const err = await resp.json().catch(() => ({}));
          alert(err.detail || "Decision failed.");
        }
      } catch(e) {}
    }

    async function loadAuditEvents() {
      try {
        const resp = await fetch('/api/v1/audit');
        if (resp.ok) {
          officerAuditEventsList = await resp.json();
          renderOfficerAuditTable(officerAuditEventsList);
        }
      } catch(e) {}
    }

    function renderOfficerAuditTable(events) {
      const tbody = document.getElementById('auditTrailTableBody');
      if (!tbody) return;
      tbody.innerHTML = events.map(e => `
        <tr>
          <td style="font-family:'JetBrains Mono'; font-size:11px;">${e.timestamp}</td>
          <td style="font-weight:700;">${e.actor}</td>
          <td><span class="badge-pass">${e.event_type}</span></td>
          <td style="font-size:11.5px;">${e.details}</td>
          <td style="font-family:'JetBrains Mono'; font-size:10px; color:#64748B;"><code>${e.sha256_hash.substring(0, 16)}...</code></td>
        </tr>
      `).join('');
    }

    function filterOfficerAuditEvents() {
      const q = document.getElementById('officerAuditSearchInput').value.toLowerCase().trim();
      const filtered = officerAuditEventsList.filter(e => e.details.toLowerCase().includes(q) || e.actor.toLowerCase().includes(q) || e.event_type.toLowerCase().includes(q));
      renderOfficerAuditTable(filtered);
    }

    function exportAuditTrailJSON() {
      const blob = new Blob([JSON.stringify(officerAuditEventsList, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bodhz_audit_trail_${Date.now()}.json`;
      a.click();
    }

    async function loadBidderPortalData() {
      try {
        const respTenders = await fetch('/api/v1/tenders');
        if (respTenders.ok) {
          tendersList = await respTenders.json();
          const sel = document.getElementById('bidderOpenTendersDropdown');
          sel.innerHTML = tendersList.map(t => `<option value="${t.id}">${t.tender_number} — ${t.title.substring(0, 45)}...</option>`).join('');
          renderBidderTendersCatalogCards(tendersList);
        }
        const respSubs = await fetch('/api/v1/bids/my-submissions');
        if (respSubs.ok) {
          const subData = await respSubs.json();
          const tbody = document.getElementById('bidderSubmissionsTableBody');
          tbody.innerHTML = subData.submissions.map(s => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${s.tender_number}</td>
              <td style="font-weight:700;">${s.tender_title}</td>
              <td>${s.submission_date}</td>
              <td style="font-weight:900; color:#047857;">${s.compliance_score || 95}/100</td>
              <td><span class="badge-${s.screening_status==='PASS'?'pass':'review'}">${s.screening_status}</span></td>
              <td><span class="badge-pass">13/13 Verified</span></td>
              <td><a href="/api/v1/reports/bids/${s.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">🖨️ Dossier</a></td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    // --------------------------------------------------
    // DTE VERIFICATION GATEWAYS & COMPLIANCE DEFAULT LOADERS
    // --------------------------------------------------
    async function loadDTEGatewaysDefault() {
      try {
        const resp = await fetch('/api/v1/dte/active-tender/bids');
        if (resp.ok) {
          const data = await resp.json();
          const bids = data.bids || [];
          const sel = document.getElementById('dteGatewaysBidderSelect');
          if (sel && bids.length > 0) {
            sel.innerHTML = bids.map(b => `<option value="${b.bid_id}">${b.legal_name} (Score: ${b.compliance_score}/100)</option>`).join('');
          }
          if (bids.length > 0) {
            await inspectDTEGateways(bids[0].bid_id);
          }
        }
      } catch(e) {}
    }

    async function loadDTEComplianceDefault() {
      try {
        const resp = await fetch('/api/v1/dte/active-tender/bids');
        if (resp.ok) {
          const data = await resp.json();
          const bids = data.bids || [];
          const sel = document.getElementById('dteComplianceBidderSelect');
          if (sel && bids.length > 0) {
            sel.innerHTML = bids.map(b => `<option value="${b.bid_id}">${b.legal_name} (Score: ${b.compliance_score}/100)</option>`).join('');
          }
          if (bids.length > 0) {
            await inspectDTEComplianceEvidence(bids[0].bid_id);
          }
        }
      } catch(e) {}
    }

    // --------------------------------------------------
    // DEDICATED BIDDER WORKSPACE CONTROLLERS
    // --------------------------------------------------
    let activeBidderSelectedTenderId = 'DTE/2026/RFP/COE/4901';
    let activeBidderCurrentBidId = 'bid_tata_01';
    let bidderAllTendersList = [];

    async function loadBidderDashboard() {
      try {
        const resp = await fetch('/api/v1/bidder/dashboard');
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('bidderDashWelcomeName').innerText = data.user.full_name;
          document.getElementById('bidderDashCompanyName').innerText = data.user.company;
          document.getElementById('bidderStatActiveTenders').innerText = data.kpi_cards.active_tenders;
          document.getElementById('bidderStatMyBids').innerText = data.kpi_cards.my_bids;
          document.getElementById('bidderStatDraftBids').innerText = data.kpi_cards.draft_submissions;
          document.getElementById('bidderStatSubmittedBids').innerText = data.kpi_cards.submitted_bids;
          document.getElementById('bidderStatPendingClarifications').innerText = data.kpi_cards.pending_clarifications;

          const tbody = document.getElementById('bidderRecentActivityTableBody');
          tbody.innerHTML = data.recent_activity.map(act => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${act.tender_id}</td>
              <td style="font-weight:700;">${act.tender_title}</td>
              <td style="font-size:11.5px; color:#475569;">${act.submitted_at}</td>
              <td><span class="badge-${act.status==='SUBMITTED'||act.status==='PROCESSING'?'pass':'review'}">${act.status}</span></td>
              <td><span class="badge-pass" style="font-size:10.5px;">${act.screening_status}</span></td>
              <td>
                <button onclick="viewBidderTenderDetails('${act.tender_id}')" class="btn-action" style="font-size:10.5px; padding:3px 8px;">View Details</button>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadBidderAvailableTenders() {
      try {
        const resp = await fetch('/api/v1/bidder/tenders');
        if (resp.ok) {
          bidderAllTendersList = await resp.json();
          renderBidderAvailableTendersTable(bidderAllTendersList);
        }
      } catch(e) {}
    }

    function renderBidderAvailableTendersTable(tList) {
      const tbody = document.getElementById('bidderAvailableTendersTableBody');
      if (!tbody) return;
      if (tList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:18px; color:#64748B;">No open tenders found.</td></tr>`;
        return;
      }
      tbody.innerHTML = tList.map(t => `
        <tr>
          <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${t.tender_number}</td>
          <td style="font-weight:700;">${t.title}</td>
          <td style="font-size:11.5px; color:#475569;">${t.procuring_entity}</td>
          <td style="font-size:11px; font-weight:700; color:#DC2626;">${t.closing_date}</td>
          <td><span class="badge-pass">${t.requirements_count} Clauses</span></td>
          <td><span class="badge-${t.my_submission_status==='SUBMITTED'?'pass':'review'}">${t.my_submission_status}</span></td>
          <td>
            <div style="display: flex; gap: 4px;">
              <button onclick="viewBidderTenderDetails('${t.id}')" class="btn-action" style="font-size:10px; padding:3px 7px;">🔍 View Tender</button>
              <button onclick="viewBidderTenderChecklist('${t.id}')" class="btn-warning" style="font-size:10px; padding:3px 7px;">📋 Checklist</button>
              <button onclick="startBidderWizard('${t.id}')" class="btn-success" style="font-size:10px; padding:3px 7px;"><i class="fa-solid fa-plus"></i> Start Bid</button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    function filterBidderTendersCatalog() {
      const q = document.getElementById('bidderTendersSearchInput').value.toLowerCase().trim();
      const filtered = bidderAllTendersList.filter(t => 
        t.tender_number.toLowerCase().includes(q) || 
        t.title.toLowerCase().includes(q) || 
        t.procuring_entity.toLowerCase().includes(q)
      );
      renderBidderAvailableTendersTable(filtered);
    }

    async function viewBidderTenderDetails(tenderId) {
      activeBidderSelectedTenderId = tenderId;
      switchBidderView('bidder-tender-detail');
      try {
        const resp = await fetch(`/api/v1/bidder/tenders/${encodeURIComponent(tenderId)}`);
        if (resp.ok) {
          const t = await resp.json();
          document.getElementById('bidderDetailTenderNumber').innerText = t.tender_number;
          document.getElementById('bidderDetailTenderTitle').innerText = t.title;
          document.getElementById('bidderDetailTenderOrg').innerText = t.procuring_entity;
          document.getElementById('bidderDetailTenderDesc').innerText = t.description;

          if (t.important_dates) {
            document.getElementById('bidderDatePublished').innerText = t.important_dates.published_date;
            document.getElementById('bidderDatePrebid').innerText = t.important_dates.pre_bid_meeting;
            document.getElementById('bidderDateClosing').innerText = t.important_dates.closing_date;
            document.getElementById('bidderDateOpening').innerText = t.important_dates.technical_opening;
          }

          const tbody = document.getElementById('bidderDetailRequirementsTableBody');
          tbody.innerHTML = t.statutory_requirements.map(r => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary); font-size:11.5px;">${r.module}</td>
              <td style="font-weight:600; color:#1E293B;">${r.title}</td>
              <td>${r.mandatory ? '<span class="badge-pass">MANDATORY</span>' : '<span class="badge-review">OPTIONAL</span>'}</td>
              <td><strong>${r.weight}%</strong></td>
              <td style="font-family:'JetBrains Mono'; font-size:11px; color:#475569;">${r.rule_type}</td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function viewBidderTenderChecklist(tenderId) {
      activeBidderSelectedTenderId = tenderId;
      switchBidderView('bidder-checklist');
      await loadBidderChecklist(tenderId);
    }

    async function loadBidderChecklist(tenderId) {
      try {
        const tId = tenderId || activeBidderSelectedTenderId;
        const resp = await fetch(`/api/v1/bidder/tenders/${encodeURIComponent(tId)}/checklist`);
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('bidderChecklistTenderTitle').innerText = `${data.tender_number} — ${data.tender_title}`;
          document.getElementById('bidderChecklistStatusBadge').innerText = `${data.uploaded_count} Uploaded / ${data.missing_count} Missing`;

          const tbody = document.getElementById('bidderChecklistTableBody');
          tbody.innerHTML = data.checklist.map(item => `
            <tr>
              <td style="font-weight:800; color:var(--primary); font-family:'JetBrains Mono';">${item.module}</td>
              <td style="font-weight:600;">${item.title}</td>
              <td>${item.mandatory ? '<span class="badge-pass">REQUIRED</span>' : '<span class="badge-review">OPTIONAL</span>'}</td>
              <td><span class="badge-${item.uploaded ? 'pass' : (item.mandatory ? 'fail' : 'review')}">${item.uploaded ? 'UPLOADED' : 'MISSING'}</span></td>
              <td style="font-size:11px; font-family:'JetBrains Mono'; color:#334155;">${item.document_name || '—'}</td>
              <td style="font-size:11.5px; color:#475569;">${item.technical_validation_note}</td>
              <td>
                <button onclick="switchBidderView('bidder-upload')" class="btn-action" style="font-size:10px; padding:3px 7px;">${item.uploaded ? 'Replace' : 'Upload'}</button>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    function startBidderWizard(tenderId) {
      if (tenderId) activeBidderSelectedTenderId = tenderId;
      switchBidderView('bidder-start');
      loadBidderWizard();
    }

    function loadBidderWizard() {
      const sel = document.getElementById('bidderWizardTenderSelect');
      if (sel) sel.value = activeBidderSelectedTenderId;
    }

    function onBidderWizardTenderChange(val) {
      activeBidderSelectedTenderId = val;
    }

    async function loadBidderUploadDocs() {
      try {
        const resp = await fetch('/api/v1/bidder/bids');
        if (resp.ok) {
          const bids = await resp.json();
          if (bids.length > 0) {
            activeBidderCurrentBidId = bids[0].bid_id;
            const singleResp = await fetch(`/api/v1/bidder/bids/${activeBidderCurrentBidId}`);
            if (singleResp.ok) {
              const single = await singleResp.json();
              const tbody = document.getElementById('bidderUploadedDocsTableBody');
              tbody.innerHTML = single.documents.map(doc => `
                <tr>
                  <td style="font-weight:700; color:var(--primary);"><i class="fa-regular fa-file-pdf" style="color:#DC2626;"></i> ${doc.name}</td>
                  <td style="font-size:11px; color:#475569;">${doc.type}</td>
                  <td style="font-size:11px;">${doc.uploaded_at}</td>
                  <td><span class="badge-pass">${doc.processing_status}</span></td>
                  <td><span class="badge-pass">${doc.validation_status}</span></td>
                  <td>
                    <button onclick="deleteBidderDoc('${doc.id}')" class="btn-action" style="font-size:10px; padding:2px 7px; color:#BE123C;"><i class="fa-solid fa-trash"></i></button>
                  </td>
                </tr>
              `).join('');
            }
          }
        }
      } catch(e) {}
    }

    function handleBidderFileChosen(input) {
      if (input.files && input.files[0]) {
        uploadSimulatedBidderDoc(input.files[0].name);
      }
    }

    async function uploadSimulatedBidderDoc(fileName) {
      const docType = document.getElementById('bidderUploadDocType').value;
      const finalName = fileName || `Tata_${docType}_Document_${Date.now()}.pdf`;
      try {
        const resp = await fetch(`/api/v1/bidder/bids/${activeBidderCurrentBidId}/documents/upload`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ document_type: docType, document_name: finalName })
        });
        if (resp.ok) {
          showToast("Document Uploaded", `${finalName} uploaded and pre-validated.`, "success");
          await loadBidderUploadDocs();
        }
      } catch(e) {
        showToast("Upload Error", "Could not upload document.", "error");
      }
    }

    async function deleteBidderDoc(docId) {
      try {
        const resp = await fetch(`/api/v1/bidder/bids/${activeBidderCurrentBidId}/documents/${docId}`, { method: 'DELETE' });
        if (resp.ok) {
          showToast("Document Removed", "File removed from draft submission.", "success");
          await loadBidderUploadDocs();
        }
      } catch(e) {}
    }

    async function runBidderCompletenessCheck() {
      try {
        const resp = await fetch(`/api/v1/bidder/bids/${activeBidderCurrentBidId}/completeness-check`);
        if (resp.ok) {
          const data = await resp.json();
          document.getElementById('bidderCheckReadyText').innerHTML = `READY TO SUBMIT: <span style="color:${data.ready_to_submit ? '#059669' : '#DC2626'}">${data.ready_to_submit ? 'YES' : 'NO'}</span>`;
          document.getElementById('bidderCheckReqCount').innerText = data.required_documents_count;
          document.getElementById('bidderCheckUploadCount').innerText = data.uploaded_count;
          document.getElementById('bidderCheckMissingCount').innerText = data.missing_count;
          document.getElementById('bidderCompletenessScoreBadge').innerText = `${data.completeness_percentage}% COMPLETE`;

          const alertBox = document.getElementById('bidderMissingDocsAlert');
          if (data.missing_mandatory && data.missing_mandatory.length > 0) {
            alertBox.style.display = 'block';
            document.getElementById('bidderMissingDocsList').innerText = data.missing_mandatory.join(', ');
          } else {
            alertBox.style.display = 'none';
          }
        }
      } catch(e) {}
    }

    async function submitBidderOfficialProposal() {
      const chk = document.getElementById('bidderDeclarationCheckbox');
      if (chk && !chk.checked) {
        alert("Please confirm the statutory undertaking declaration checkbox before final submission.");
        return;
      }
      const btn = document.getElementById('btnBidderFinalSubmit');
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Submitting & Generating SHA-256 Receipt...`;

      try {
        const resp = await fetch(`/api/v1/bidder/bids/${activeBidderCurrentBidId}/submit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ declaration_confirmed: true })
        });
        if (resp.ok) {
          const res = await resp.json();
          showToast("Bid Submitted Successfully!", `Generated Bid Reference: ${res.bid_reference}`, "success");
          alert(`Official Submission Confirmation\n\nBid Reference ID: ${res.bid_reference}\nTimestamp: ${res.submission_timestamp}\nSHA-256 Receipt: ${res.receipt_hash}\n\nYour proposal has been successfully lodged for procurement evaluation.`);
          switchBidderView('bidder-mybids');
        } else {
          showToast("Submission Failed", "Completeness check failed.", "error");
        }
      } catch(e) {
        showToast("Error", "Submission connection failure.", "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> SUBMIT BID PROPOSAL`;
      }
    }

    async function loadBidderMyBids() {
      try {
        const resp = await fetch('/api/v1/bidder/bids');
        if (resp.ok) {
          const bids = await resp.json();
          const tbody = document.getElementById('bidderMyBidsTableBody');
          tbody.innerHTML = bids.map(b => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${b.bid_id}</td>
              <td style="font-weight:700;">${b.tender_number}<br><span style="font-size:10.5px; color:#64748B;">${b.tender_title}</span></td>
              <td style="font-size:11.5px;">${b.submitted_at}</td>
              <td><span class="badge-${b.status==='SUBMITTED'||b.status==='PROCESSING'?'pass':'review'}">${b.status}</span></td>
              <td><span class="badge-pass">${b.document_completion}</span></td>
              <td style="font-size:11px; color:#64748B;">${b.last_updated}</td>
              <td>
                <a href="/api/v1/reports/bids/${b.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">🖨️ View Receipt</a>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadBidderClarifications() {
      try {
        const resp = await fetch('/api/v1/bidder/clarifications');
        if (resp.ok) {
          const clist = await resp.json();
          const tbody = document.getElementById('bidderClarificationsTableBody');
          if (clist.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:18px; color:#64748B;">No pending clarification queries.</td></tr>`;
            return;
          }
          tbody.innerHTML = clist.map(c => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary); font-size:11.5px;">${c.query_id}</td>
              <td style="font-weight:700; font-size:11.5px;">${c.tender_number}</td>
              <td style="font-size:11.5px; color:#475569;">${c.requested_by}</td>
              <td style="font-size:12px; color:#1E293B;">${c.question_text}</td>
              <td style="font-size:11px; font-weight:700; color:#DC2626;">${c.due_date}</td>
              <td><span class="badge-${c.status==='PENDING'?'review':'pass'}">${c.status}</span></td>
              <td>
                <button onclick="openBidderClarificationModal('${c.query_id}', '${c.question_text.replace(/'/g, "\\'")}')" class="btn-success" style="font-size:10.5px; padding:3px 8px;">Respond →</button>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    function openBidderClarificationModal(queryId, text) {
      document.getElementById('bidderClarifyQueryId').value = queryId;
      document.getElementById('bidderClarifyQueryText').innerText = text;
      document.getElementById('bidderClarifyResponseText').value = "";
      document.getElementById('bidderClarifyDocName').value = "";
      document.getElementById('bidderClarificationModal').style.display = 'flex';
    }

    function closeBidderClarificationModal() {
      document.getElementById('bidderClarificationModal').style.display = 'none';
    }

    async function submitBidderClarificationResponse() {
      const qId = document.getElementById('bidderClarifyQueryId').value;
      const respText = document.getElementById('bidderClarifyResponseText').value.trim();
      const docName = document.getElementById('bidderClarifyDocName').value.trim();

      if (!respText) {
        alert("Please enter your clarification response text.");
        return;
      }

      try {
        const resp = await fetch(`/api/v1/bidder/clarifications/${qId}/respond`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ response_text: respText, response_doc_name: docName })
        });
        if (resp.ok) {
          showToast("Clarification Submitted", "Response submitted to procurement committee.", "success");
          closeBidderClarificationModal();
          await loadBidderClarifications();
        }
      } catch(e) {
        showToast("Error", "Could not submit response.", "error");
      }
    }

    async function loadBidderHistory() {
      try {
        const resp = await fetch('/api/v1/bidder/bids');
        if (resp.ok) {
          const bids = await resp.json();
          const tbody = document.getElementById('bidderHistoryTableBody');
          tbody.innerHTML = bids.map(b => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-size:11px;">${b.submitted_at}</td>
              <td style="font-weight:700;">${b.tender_number}</td>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${b.bid_id}</td>
              <td><span class="badge-pass">${b.status}</span></td>
              <td>
                <a href="/api/v1/reports/bids/${b.bid_id}/html" target="_blank" class="btn-action" style="font-size:10px; padding:3px 8px;">View Official Receipt</a>
              </td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadBidderProfile() {
      try {
        const resp = await fetch('/api/v1/bidder/profile');
        if (resp.ok) {
          const p = await resp.json();
          document.getElementById('bidderProfileName').value = p.representative_name;
          document.getElementById('bidderProfileCompany').value = p.company_name;
          document.getElementById('bidderProfileGSTIN').value = p.gstin;
          document.getElementById('bidderProfilePAN').value = p.pan_number;
          document.getElementById('bidderProfileUdyam').value = p.udyam_reg;
          document.getElementById('bidderProfileEmail').value = p.email;
          document.getElementById('bidderProfilePhone').value = p.phone;
          document.getElementById('bidderProfileAddress').value = p.address;
        }
      } catch(e) {}
    }

    async function saveBidderProfile() {
      const email = document.getElementById('bidderProfileEmail').value.trim();
      const phone = document.getElementById('bidderProfilePhone').value.trim();
      const address = document.getElementById('bidderProfileAddress').value.trim();

      try {
        const resp = await fetch('/api/v1/bidder/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, phone: phone, address: address })
        });
        if (resp.ok) {
          showToast("Profile Updated", "Entity contact details saved successfully.", "success");
        }
      } catch(e) {
        showToast("Error", "Could not save profile.", "error");
      }
    }

    // --------------------------------------------------
    // AI CHATBOT CONTROLLER (ROLE-AWARE & ADAPTIVE MEMORY)
    // --------------------------------------------------
    let chatConversationHistory = [];

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

      // Track in active conversational memory
      chatConversationHistory.push({ sender: 'user', text: text });

      try {
        let endpoint = '/api/v1/bids/ai-chat';
        let bodyPayload = {
          message: text,
          user_name: activeUser ? activeUser.username : 'visitor',
          user_role: activeUser ? activeUser.role : 'PROCUREMENT_OFFICER',
          tender_id: activeTender ? activeTender.id : null,
          bidder_id: activeBidder ? activeBidder.bid_id : null,
          history: chatConversationHistory.slice(-10)
        };

        if (activeUser && activeUser.role === 'BID_UPLOADER') {
          endpoint = '/api/v1/bidder/chat';
          bodyPayload = {
            message: text,
            tender_id: activeBidderSelectedTenderId,
            history: chatConversationHistory.slice(-10)
          };
        }

        const resp = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bodyPayload)
        });
        if (resp.ok) {
          const res = await resp.json();
          chatConversationHistory.push({ sender: 'assistant', text: res.reply });

          let memoryBadge = '';
          if (res.source === 'ADAPTIVE_MEMORY_ENGINE' || (res.model && res.model.includes('Memory'))) {
            memoryBadge = `<span style="font-size:9.5px; background:#EFF6FF; color:#1D4ED8; padding:2px 6px; border-radius:4px; font-weight:800; margin-left:6px; border:1px solid #BFDBFE;">🧠 Recalled from Memory</span>`;
          }

          area.innerHTML += `
            <div class="chat-msg-bot">
              <div style="font-weight: 800; color: #0A192F; margin-bottom: 4px; display:flex; align-items:center;">
                <span>BodhZ AI Assistant</span>
                ${memoryBadge}
              </div>
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
