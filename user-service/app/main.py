from fastapi import FastAPI, Header, HTTPException, Depends
from .db import Base, engine, SessionLocal
from .models import Profile
import os
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware

# OTel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = FastAPI(title="user-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Порт React застосунку
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "user-service"}))
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
from opentelemetry import trace
trace.set_tracer_provider(provider)
FastAPIInstrumentor().instrument_app(app)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret_auth")

def get_current_username(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return data["sub"]
    except Exception:
        raise HTTPException(401, "Invalid token")

@app.get("/api/users/me")
def me(username: str = Depends(get_current_username), db=Depends(get_db)):
    profile = db.query(Profile).filter(Profile.username==username).first()
    if not profile:
        profile = Profile(username=username, display_name=username)
        db.add(profile); db.commit(); db.refresh(profile)
    return {"username": profile.username, "display_name": profile.display_name, "bio": profile.bio, "contact_email": profile.contact_email}

@app.post("/api/users/me")
def update_profile(payload: dict, username: str = Depends(get_current_username), db=Depends(get_db)):
    profile = db.query(Profile).filter(Profile.username==username).first()
    if not profile:
        profile = Profile(username=username)
        db.add(profile)
    if "display_name" in payload: profile.display_name = payload["display_name"]
    if "bio" in payload: profile.bio = payload["bio"]
    if "contact_email" in payload: profile.contact_email = payload["contact_email"]
    db.commit(); db.refresh(profile)
    return {"status": "updated"}
