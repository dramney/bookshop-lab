from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine, SessionLocal
from .models import User
from .schemas import RegisterIn, LoginIn, TokenOut
from .utils import hash_password, verify_password, create_access_token
import os
import redis

# OpenTelemetry init
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = FastAPI(title="auth-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Порт React застосунку
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"}))
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
from opentelemetry import trace
trace.set_tracer_provider(provider)
FastAPIInstrumentor().instrument_app(app)

Base.metadata.create_all(bind=engine)
r = redis.Redis(host="redis", port=6379, decode_responses=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/auth/register", response_model=dict)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "User exists")

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        role=data.role,
        email=data.email
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Створюємо порожній кошик у Redis
    r.hset(f"cart:{user.id}", mapping={"total": 0})

    # (можна опублікувати подію UserRegistered у RabbitMQ)

    return {"status": "registered", "user_id": user.id}


@app.post("/api/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(user.username, user.role)
    return {"access_token": token, "user_id": user.id}