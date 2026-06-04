from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/store_intelligence.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class StoreVisit(Base):
    __tablename__ = "store_visits"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    visitor_id = Column(String, index=True)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime, nullable=True)
    is_staff = Column(Boolean, default=False)

class ZoneVisit(Base):
    __tablename__ = "zone_visits"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    visitor_id = Column(String, index=True)
    zone_id = Column(String, index=True) 
    entry_time = Column(DateTime)
    exit_time = Column(DateTime, nullable=True)

class PosTransaction(Base):
    __tablename__ = "pos_transactions"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    timestamp = Column(DateTime)
    total_price = Column(Float) 

Base.metadata.create_all(bind=engine)