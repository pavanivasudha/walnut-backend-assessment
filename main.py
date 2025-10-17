from fastapi import FastAPI, BackgroundTasks, HTTPException
from datetime import datetime
from typing import Dict
import asyncio

app = FastAPI()

transactions_db: Dict[str, Dict] = {}

@app.get("/")
def health_check():
    return {
        "status": "HEALTHY",
        "current_time": datetime.utcnow().isoformat() + "Z"
    }

async def process_transaction(transaction_id: str):
    print(f"Processing transaction {transaction_id} ...")
    await asyncio.sleep(3) 

    transactions_db[transaction_id]["status"] = "PROCESSED"
    transactions_db[transaction_id]["processed_at"] = datetime.utcnow().isoformat() + "Z"
    print(f"✅ Transaction {transaction_id} processed!")

@app.post("/v1/webhooks/transactions")
async def receive_webhook(payload: Dict, background_tasks: BackgroundTasks):
    required_fields = ["transaction_id", "source_account", "destination_account", "amount", "currency"]

    if not all(field in payload for field in required_fields):
        raise HTTPException(status_code=400, detail="Missing required fields")

    transaction_id = payload["transaction_id"]

    transactions_db[transaction_id] = {
        "transaction_id": transaction_id,
        "source_account": payload["source_account"],
        "destination_account": payload["destination_account"],
        "amount": payload["amount"],
        "currency": payload["currency"],
        "status": "PROCESSING",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "processed_at": None
    }

    background_tasks.add_task(process_transaction, transaction_id)

    return {"status": 202}

@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    transaction = transactions_db.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
