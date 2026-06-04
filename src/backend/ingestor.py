import pandas as pd
from datetime import datetime
from src.backend.database import SessionLocal, PosTransaction

def ingest_pos_csv(file_path: str):
    db = SessionLocal()
    print(f"Ingesting POS transactions and duplicating for store-1 and store-2...")
    
    df = pd.read_csv(file_path)
    unique_orders = df.drop_duplicates(subset=['order_id'])
    
    for _, row in unique_orders.iterrows():
        try:
            datetime_str = f"{row['order_date']} {row['order_time']}"
            dt_obj = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S")
            total_price = float(row['total_amount'])
            
            # Add transaction to Stores 1 & 2
            sale_1 = PosTransaction(store_id="store-1", timestamp=dt_obj, total_price=total_price)
            db.add(sale_1)
            
            sale_2 = PosTransaction(store_id="store-2", timestamp=dt_obj, total_price=total_price)
            db.add(sale_2)
            
        except Exception as e:
            print(f"⚠️ Error parsing POS row: {e}")

    db.commit()
    db.close()
    print("POS Ingestion Complete. Transactions are pre-filled.")
    
if __name__ == "__main__":
    ingest_pos_csv("data/POS - sample transactions.csv")