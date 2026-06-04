from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.backend.database import SessionLocal, StoreVisit, ZoneVisit, PosTransaction
import os

app = FastAPI(title="Apex Retail Store Intelligence API")

# Webhook Payload Schema 
class EdgeEvent(BaseModel):
    store_id: str
    visitor_id: str
    event_type: str  # "entry", "exit", "zone_entry", "zone_exit"
    zone_id: str | None = None  
    timestamp: datetime
    is_staff: bool = False
    camera_id: str

# Dashboard UI Endpoint
@app.get("/", response_class=FileResponse)
def serve_dashboard():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "frontend", "dashboard.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dashboard UI not found.")
    return FileResponse(file_path)

# Live Webhook Receiver
@app.post("/api/live-events")
def ingest_live_edge_data(event: EdgeEvent):
    db = SessionLocal()
    try:
        # Store Entry/ Exit
        if event.event_type == "entry":
            existing = db.query(StoreVisit).filter_by(visitor_id=event.visitor_id, store_id=event.store_id).first()
            if not existing:
                db.add(StoreVisit(store_id=event.store_id, visitor_id=event.visitor_id, entry_time=event.timestamp))
        elif event.event_type == "exit":
            visit = db.query(StoreVisit).filter_by(visitor_id=event.visitor_id, store_id=event.store_id, exit_time=None).first()
            if visit: visit.exit_time = event.timestamp # type: ignore
        
        # ZOne Entry/ Exit 
        elif event.event_type == "zone_entry":
            db.add(ZoneVisit(store_id=event.store_id, visitor_id=event.visitor_id, zone_id=event.zone_id, entry_time=event.timestamp))
        elif event.event_type == "zone_exit":
            z_visit = db.query(ZoneVisit).filter_by(visitor_id=event.visitor_id, store_id=event.store_id, zone_id=event.zone_id, exit_time=None).first()
            if z_visit: z_visit.exit_time = event.timestamp # type: ignore

        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# Enterprise Analytics Endpoint
@app.get("/api/metrics")
def get_store_metrics(store_id: str = Query(...)):
    db = SessionLocal()
    try:
        # Traffic & Transactions
        visitors = db.query(StoreVisit).filter(StoreVisit.store_id == store_id, StoreVisit.is_staff == False).count()
        transactions = db.query(func.count(PosTransaction.id)).filter(PosTransaction.store_id == store_id).scalar() or 0
        conversion_rate = (transactions / visitors * 100) if visitors > 0 else 0.0

        # Dwell Time Calculations
        completed_zone_visits = db.query(ZoneVisit).filter(ZoneVisit.store_id == store_id, ZoneVisit.exit_time.isnot(None)).all()
        
        dwell_data: dict[str, list[float]] = {"Z_ENTRANCE": [], "Z_AISLE": [], "Z_CHECKOUT": []}
        
        for zv in completed_zone_visits:
            z_id = str(zv.zone_id) 
            
            if z_id in dwell_data:
                duration = (zv.exit_time - zv.entry_time).total_seconds()  # type: ignore
                dwell_data[z_id].append(duration)
                
        def get_avg_time(zone_list):
            if not zone_list: return "--"
            avg_sec = sum(zone_list) / len(zone_list)
            m, s = divmod(int(avg_sec), 60)
            return f"{m}m {s}s"

        return {
            "store_id": store_id,
            "total_visitors": visitors,
            "total_transactions": transactions,
            "conversion_rate": round(conversion_rate, 2),
            "dwell_entrance": get_avg_time(dwell_data["Z_ENTRANCE"]),
            "dwell_aisle": get_avg_time(dwell_data["Z_AISLE"]),
            "dwell_checkout": get_avg_time(dwell_data["Z_CHECKOUT"])
        }
    finally:
        db.close()