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
    dte_router
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
    }

    .public-nav-links { display: flex; gap: 24px; align-items: center; font-size: 13px; font-weight: 700; }
    .public-nav-link { color: #CBD5E1; text-decoration: none; transition: color 0.2s; cursor: pointer; }
    .public-nav-link:hover { color: var(--accent); }

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
      transition: all 0.2s;
    }

    .btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 22px rgba(245, 158, 11, 0.45); }

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

    .btn-hero-secondary:hover { background: rgba(255, 255, 255, 0.15); border-color: #FFFFFF; }

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

    .trust-item { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 800; color: var(--primary); letter-spacing: 0.5px; }
    .trust-item i { color: #059669; font-size: 14px; }

    .landing-section { max-width: 1140px; margin: 48px auto; padding: 0 24px; width: 100%; position: relative; }
    .section-header { text-align: center; margin-bottom: 28px; }
    .section-title { font-size: 24px; font-weight: 900; color: var(--primary); letter-spacing: -0.5px; }
    .section-desc { font-size: 13.5px; color: var(--text-muted); margin-top: 4px; }

    .solve-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .solve-card { background: #FFFFFF; border: 1px solid var(--border); border-radius: 12px; padding: 22px; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
    .solve-item { display: flex; align-items: flex-start; gap: 10px; margin-top: 10px; font-size: 12.5px; color: #475569; }

    .flow-grid-5 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
    .flow-step-card { background: #FFFFFF; border: 1px solid var(--border); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.02); transition: transform 0.2s; }
    .flow-num { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 800; color: var(--accent); background: #FFFBEB; border: 1px solid #FDE68A; padding: 2px 6px; border-radius: 4px; width: fit-content; }

    .ver-source-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
    .ver-source-pill { background: #FFFFFF; border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 700; color: var(--primary); box-shadow: 0 1px 3px rgba(0,0,0,0.02); }

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
        <a class="public-nav-link" onclick="scrollToSection('sources')">Verification Sources</a>
        <a class="public-nav-link" onclick="openAuthScreen('LOGIN')">Officer Portal</a>
      </div>

      <div style="display: flex; gap: 10px; align-items: center;">
        <button onclick="openAuthScreen('LOGIN')" class="btn-hero-secondary" style="padding: 7px 16px; font-size: 12px;">Sign In</button>
        <button onclick="openAuthScreen('REGISTER')" class="btn-hero-primary" style="padding: 7px 16px; font-size: 12px;">Register</button>
        <button onclick="openDemoModeModal()" class="filter-pill" style="background: rgba(245,158,11,0.2); color: var(--accent); border-color: var(--accent); font-size: 11px;">⚡ Evaluator Demo</button>
      </div>
    </nav>

    <!-- Hero Section -->
    <header class="landing-hero" id="hero">
      <div class="landing-hero-container">
        <div>
          <div class="landing-badge">
            <i class="fa-solid fa-shield-halved"></i>
            <span>SIH26100 • PUBLIC PROCUREMENT DECISION SUPPORT</span>
          </div>
          <h1 class="landing-title">
            BodhZ — AI-Powered Integrated Bid Compliance Verification Platform
          </h1>
          <p class="landing-subtitle">
            Evidence-based decision support for faster, more consistent and auditable bid compliance verification across Central GeM and State Departments (DTE Maharashtra).
          </p>

          <div class="landing-cta-row">
            <button onclick="openAuthScreen('LOGIN')" class="btn-hero-primary">
              <i class="fa-solid fa-arrow-right-to-bracket"></i>
              <span>Sign In to Workspace</span>
            </button>
            <button onclick="openDemoModeModal()" class="btn-hero-secondary">
              <i class="fa-solid fa-bolt"></i>
              <span>Select Demo Persona</span>
            </button>
          </div>
        </div>

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
              <div style="font-size: 11px; color: #94A3B8;">Cross-checked against 13 statutory registries</div>
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

    <!-- Trust Strip -->
    <div class="trust-strip">
      <div class="trust-item"><i class="fa-solid fa-microchip"></i> AI-ASSISTED</div>
      <div class="trust-item"><i class="fa-solid fa-file-shield"></i> EVIDENCE-BASED</div>
      <div class="trust-item"><i class="fa-solid fa-fingerprint"></i> AUDITABLE</div>
      <div class="trust-item"><i class="fa-solid fa-user-check"></i> HUMAN-CONTROLLED</div>
    </div>
  </div>

  <!-- ================================================== -->
  <!-- 2. ULTRA-PREMIUM AUTHENTICATION SPLIT SCREEN       -->
  <!-- ================================================== -->
  <div id="view-auth" class="auth-page-wrapper" style="display: none;">
    <div class="auth-card">
      <div class="auth-left-brand">
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

        <div id="view-vercenter" style="display: none; flex-direction: column; gap: 18px;">
          <div class="card-panel">
            <div class="card-title">13 Statutory Verification Gateway Nodes (Layer 4)</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px;">
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏭 Udyam / MSME Portal</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🧾 GSTN Portal</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🪪 PAN / Income Tax</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
              <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:8px;"><strong>🏢 MCA21 Registry</strong><div class="badge-pass" style="margin-top:6px;">SANDBOX ACTIVE</div></div>
            </div>
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
        <!-- WORKSPACE 2: BID UPLOADER & TENDERS CATALOG PORTAL             -->
        <!-- ============================================================== -->
        <div id="view-bidder-portal" style="display: none; flex-direction: column; gap: 20px;">
          <div class="card-panel" style="border-left: 5px solid #059669;">
            <div class="card-title"><span><i class="fa-solid fa-briefcase" style="color: #059669;"></i> Bidder & Vendor Self-Service Workspace</span><span class="badge-open-bid">VENDOR AUTHORIZED</span></div>
            <p style="font-size: 13px; color: #475569;">Welcome, <strong id="bidderPortalOrgName" style="color: var(--primary);">Tata Advanced Training & Systems Ltd</strong>.</p>
          </div>

          <div class="card-panel" id="bidderCatalogSection">
            <div class="card-title"><span><i class="fa-solid fa-folder-open" style="color: #0052CC;"></i> Published Open Tenders Catalog</span></div>
            <div id="bidderTendersCatalogGrid" class="tender-catalog-grid"></div>
          </div>

          <div class="card-panel" id="bidderSubmissionFormSection">
            <div class="card-title"><span><i class="fa-solid fa-cloud-arrow-up" style="color: #059669;"></i> Submit Bid Proposal Bundle</span></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div class="form-group"><label class="form-label">Target Procurement Tender:</label><select id="bidderOpenTendersDropdown" class="form-input"><option value="">Loading Tenders...</option></select></div>
              <div class="form-group"><label class="form-label">Bidder Legal Name:</label><input type="text" id="bidderPortalNameInput" class="form-input" value="Tata Advanced Training & Systems Ltd"></div>
            </div>
            <button onclick="submitBidderPortalProposal()" id="btnSubmitBidderProposal" class="btn-success" style="align-self: flex-end;"><i class="fa-solid fa-paper-plane"></i> SUBMIT PROPOSAL →</button>
          </div>

          <div class="card-panel" id="bidderSubmissionsSection">
            <div class="card-title">My Bid Submissions</div>
            <table class="clean-table"><thead><tr><th>Tender Number</th><th>Tender Title</th><th>Date</th><th>Score</th><th>Status</th><th>Gateways</th><th>Dossier</th></tr></thead><tbody id="bidderSubmissionsTableBody"></tbody></table>
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
              <span><i class="fa-solid fa-file-contract"></i> DTE Tender Clauses & Statutory Weight Calibration</span>
              <span class="badge-review">READ-ONLY AUDIT VIEW</span>
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
              <div>
                <div style="font-size: 11px; color: #64748B;">RFP REFERENCE:</div>
                <div style="font-size: 16px; font-weight: 900; color: var(--primary);" id="dteDetailTenderNumber">DTE/2026/RFP/COE/4901</div>
                <div style="font-size: 13px; font-weight: 700; color: #334155; margin-top: 4px;" id="dteDetailTenderTitle">Establishment of Center of Excellence (COE) and Technical Training Centers</div>
              </div>
              <div style="text-align: right;">
                <span class="badge-pass" id="dteDetailLifecycleStatus">ALL_BIDS_PROCESSED</span>
                <div style="font-size: 11px; color: #64748B; margin-top: 6px;">Total Bids Ingested: <strong id="dteDetailTotalBidsCount">3</strong></div>
              </div>
            </div>

            <table class="clean-table" style="margin-top: 10px;">
              <thead>
                <tr><th>Module Code</th><th>Statutory Requirement Title</th><th>Mandatory?</th><th>Weight (%)</th><th>Evaluation Rule Type</th></tr>
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
              <span><i class="fa-solid fa-magnifying-glass-chart"></i> Evidence-Driven Statutory Compliance Inspector</span>
              <span id="dteComplianceBidderLabel" class="badge-pass">Tata Advanced Training</span>
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
              <span><i class="fa-solid fa-network-wired"></i> 13 Statutory Verification Registries & Verification Modes</span>
              <span class="badge-pass">13 / 13 CONNECTORS</span>
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
        // BIDDER PORTAL ROUTING
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
        'view-bidder-portal', 'view-dte-dashboard', 'view-dte-tenders', 'view-dte-tender-detail',
        'view-dte-bids', 'view-dte-compliance', 'view-dte-gateways', 'view-dte-shortlisted',
        'view-dte-audit', 'view-dte-reports'
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
      if (viewKey === 'dte-shortlisted') loadDTEShortlistedBids('DTE/2026/RFP/COE/4901');
      if (viewKey === 'dte-audit') loadDTEAuditTrail();
      if (viewKey === 'dte-reports') {
        const reportUrl = '/api/v1/reports/tenders/DTE/2026/RFP/COE/4901/html';
        document.getElementById('dteReportPreviewFrame').src = reportUrl;
        document.getElementById('btnDTEOpenReportTab').href = reportUrl;
      }
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
        const resp = await fetch(`/api/v1/dte/tenders/${encodeURIComponent(tenderId)}`);
        if (resp.ok) {
          const t = await resp.json();
          document.getElementById('dteDetailTenderNumber').innerText = t.tender_number;
          document.getElementById('dteDetailTenderTitle').innerText = t.title;
          document.getElementById('dteDetailLifecycleStatus').innerText = t.lifecycle_status;
          document.getElementById('dteDetailTotalBidsCount').innerText = t.statistics.total_bids;

          const tbody = document.getElementById('dteDetailRequirementsTableBody');
          tbody.innerHTML = t.requirements.map(r => `
            <tr>
              <td style="font-family:'JetBrains Mono'; font-weight:800; color:var(--primary);">${r.module}</td>
              <td style="font-weight:600;">${r.title}</td>
              <td>${r.mandatory ? '<span class="badge-pass">MANDATORY</span>' : '<span class="badge-review">OPTIONAL</span>'}</td>
              <td><strong>${r.weight}%</strong></td>
              <td style="font-size:11px; font-family:'JetBrains Mono'; color:#475569;">${r.rule_type}</td>
            </tr>
          `).join('');
        }
      } catch(e) {}
    }

    async function loadDTEBidsMonitoring(tenderId) {
      try {
        const resp = await fetch(`/api/v1/dte/tenders/${encodeURIComponent(tenderId)}/bids`);
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
        const resp = await fetch(`/api/v1/dte/tenders/${encodeURIComponent(tenderId)}/qualified-bids`);
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

      if (viewId === 'matrix') loadComparativeMatrix(false);
      if (viewId === 'audittrail') loadAuditEvents();
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

    function renderBidderTendersCatalogCards(tList) {
      const grid = document.getElementById('bidderTendersCatalogGrid');
      if (!grid) return;
      grid.innerHTML = tList.map(t => `
        <div class="tender-card-item" id="tender-card-${t.id}">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-family:'JetBrains Mono'; font-weight:800; font-size:11px; background:#F1F5F9; padding:2px 8px; border-radius:4px;">${t.tender_number}</span>
              <span class="badge-open-bid">OPEN FOR BIDDING</span>
            </div>
            <div style="font-size:13.5px; font-weight:800; color:var(--primary); margin-top:8px;">${t.title}</div>
            <div style="font-size:11px; color:#64748B; margin-top:4px;"><i class="fa-solid fa-tag"></i> ${t.category || 'Procurement'}</div>
          </div>
          <div style="border-top:1px solid #F1F5F9; padding-top:10px; display:flex; justify-content:flex-end;">
            <button onclick="selectTenderForBidSubmission('${t.id}')" class="btn-success" style="font-size:11px; padding:5px 12px;"><i class="fa-solid fa-paper-plane"></i> Apply / Submit Bid</button>
          </div>
        </div>
      `).join('');
    }

    function selectTenderForBidSubmission(tenderId) {
      const sel = document.getElementById('bidderOpenTendersDropdown');
      sel.value = tenderId;
      const formSec = document.getElementById('bidderSubmissionFormSection');
      if (formSec) formSec.scrollIntoView({ behavior: 'smooth' });
    }

    async function submitBidderPortalProposal() {
      const tenderId = document.getElementById('bidderOpenTendersDropdown').value;
      const bName = document.getElementById('bidderPortalNameInput').value.trim() || 'Tata Advanced Training & Systems Ltd';
      if (!tenderId) return alert("Select tender.");

      try {
        const respBid = await fetch('/api/v1/bids', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tender_id: tenderId, bidder: { legal_name: bName, gstin: '27AAACT1098F1Z5', pan_number: 'AAACT1098F' } })
        });
        const bidData = await respBid.json();
        await fetch(`/api/v1/bids/${bidData.id}/evaluate`, { method: 'POST' });
        showToast("Bid Submitted", "Proposal submitted & 13 gateways checked!", "success");
        await loadBidderPortalData();
        focusBidderSection('bidderSubmissionsSection');
      } catch(e) {
        showToast("Error", "Submission failed.", "error");
      }
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
            user_role: activeUser ? activeUser.role : 'DTE_OFFICER',
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
