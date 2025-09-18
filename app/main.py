import os
from typing import Optional
from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, desc
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .db import Base, engine, SessionLocal
from .models import Feedback
from .schemas import FeedbackIn, StatusIn

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pulsefeedback.db")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
PROJECT_ID = os.getenv("PROJECT_ID", "").strip()
INGEST_TOKEN = os.getenv("INGEST_TOKEN", "").strip()

app = FastAPI(title="PulseFeedback")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- Sessão simples para Admin -------------------
SECRET = os.getenv("ADMIN_SESSION_SECRET", "change-this-secret")
signer = URLSafeSerializer(SECRET, salt="pulsefeedback-admin")

def is_authed(request: Request) -> bool:
    cookie = request.cookies.get("pf_admin")
    if not cookie: return False
    try:
        data = signer.loads(cookie)
        return data.get("ok") is True
    except BadSignature:
        return False

def require_auth(request: Request):
    if not is_authed(request):
        raise HTTPException(status_code=401, detail="unauthorized")

# ------------------- Painel -------------------
@app.get("/", response_class=HTMLResponse)
def admin_home(request: Request, q: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    if not is_authed(request):
        return templates.TemplateResponse("login.html", {"request": request})
    stmt = select(Feedback).order_by(desc(Feedback.created_at))
    if q:
        stmt = stmt.filter(or_(Feedback.title.ilike(f"%{q}%"), Feedback.description.ilike(f"%{q}%"), Feedback.page_url.ilike(f"%{q}%")))
    if status in {"open","review","resolved","rejected"}:
        stmt = stmt.filter(Feedback.status == status)
    items = db.scalars(stmt.limit(300)).all()
    return templates.TemplateResponse("index.html", {"request": request, "items": items, "q": q, "status": status})

@app.post("/admin/login")
def admin_login(token: str = Form(...)):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="token inválido")
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("pf_admin", signer.dumps({"ok": True}), httponly=True, samesite="lax")
    return resp

@app.post("/admin/feedback/{fid}/status")
def admin_set_status(fid: int, status: str = Form(...), request: Request = None, db: Session = Depends(get_db)):
    require_auth(request)
    if status not in {"open","review","resolved","rejected"}:
        raise HTTPException(status_code=400, detail="status inválido")
    f = db.get(Feedback, fid)
    if not f: raise HTTPException(status_code=404, detail="not found")
    f.status = status; db.add(f); db.commit()
    return RedirectResponse(url="/", status_code=303)

# ------------------- API -------------------
@app.post("/api/ingest")
def api_ingest(payload: FeedbackIn, request: Request, db: Session = Depends(get_db)):
    if request.headers.get("X-Project-ID") != PROJECT_ID or request.headers.get("X-Ingest-Token") != INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")
    f = Feedback(
        title=payload.title.strip(),
        type=payload.type,
        description=payload.description,
        page_url=str(payload.page_url) if payload.page_url else None,
        user_agent=payload.user_agent or request.headers.get("User-Agent")
    )
    db.add(f); db.commit(); db.refresh(f)
    return {"status":"stored","id":f.id}

@app.get("/api/feedback")
def api_list(q: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(Feedback).order_by(desc(Feedback.created_at))
    if q:
        stmt = stmt.filter(or_(Feedback.title.ilike(f"%{q}%"), Feedback.description.ilike(f"%{q}%"), Feedback.page_url.ilike(f"%{q}%")))
    if status in {"open","review","resolved","rejected"}:
        stmt = stmt.filter(Feedback.status == status)
    items = db.scalars(stmt.limit(200)).all()
    return [{"id": i.id, "title": i.title, "type": i.type, "status": i.status, "page_url": i.page_url, "created_at": i.created_at.isoformat()} for i in items]

@app.post("/api/feedback/{fid}/status")
def api_status(fid: int, payload: StatusIn, request: Request, db: Session = Depends(get_db)):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")
    f = db.get(Feedback, fid)
    if not f: raise HTTPException(status_code=404, detail="not found")
    f.status = payload.status; db.add(f); db.commit()
    return {"status":"ok"}
