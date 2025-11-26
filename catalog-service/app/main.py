from fastapi import FastAPI, HTTPException, Depends
from .db import Base, engine, SessionLocal
from .models import Book
from fastapi.middleware.cors import CORSMiddleware
from .schemas import BookIn
from sqlalchemy.orm import Session
import os

# OTel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = FastAPI(title="catalog-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Порт React застосунку
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "catalog-service"}))
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

@app.post("/api/catalog/books")
def add_book(book: BookIn, db: Session = Depends(get_db)):
    b = Book(**book.dict())
    db.add(b); db.commit(); db.refresh(b)
    return {"status": "added", "id": b.id}

@app.get("/api/catalog/books")
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@app.get("/api/catalog/search")
def search(query: str, db: Session = Depends(get_db)):
    q = f"%{query.lower()}%"
    results = db.query(Book).filter(Book.title.ilike(q)).all()
    return results
