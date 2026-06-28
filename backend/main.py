import os, csv, uuid, shutil, asyncio, sys
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

load_dotenv()

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"
ORDERS_CSV = DATA_DIR / "orders.csv"
UPLOADS_DIR = DATA_DIR / "uploads"

DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

if not ORDERS_CSV.exists():
    with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["order_id","created_at","full_name","email","bio","target_job","screenshot_path","status"])

app = FastAPI(title="CV Express")

app.mount("/frontend", StaticFiles(directory=str(BASE/"frontend")), name="frontend")

@app.get("/")
async def root():
    html = (BASE / "frontend" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)

@app.post("/submit-order")
async def submit_order(
    full_name: str = Form(...),
    email: str = Form(...),
    bio: str = Form(""),
    target_job: str = Form(...),
    payment_screenshot: UploadFile = None
):
    order_id = f"CV-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    screenshot_path = ""
    if payment_screenshot:
        ext = Path(payment_screenshot.filename).suffix if payment_screenshot.filename else ".jpg"
        fname = f"{order_id}{ext}"
        dest = UPLOADS_DIR / fname
        with open(dest, "wb") as f:
            content = await payment_screenshot.read()
            f.write(content)
        screenshot_path = str(dest)
    with open(ORDERS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([order_id, now, full_name, email, bio, target_job, screenshot_path, "Pending_Payment_Verification"])
    print(f"\n{'='*50}")
    print(f"📦 طلب جديد: {order_id}")
    print(f"   الاسم: {full_name}")
    print(f"   البريد: {email}")
    print(f"   الوظيفة: {target_job}")
    print(f"{'='*50}\n")
    return JSONResponse({"message": f"✅ تم استلام طلبك {order_id}! في انتظار تأكيد الدفع.", "order_id": order_id})

@app.get("/api/orders")
async def list_orders():
    orders = []
    if ORDERS_CSV.exists():
        with open(ORDERS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                orders.append(row)
    return JSONResponse(orders)

@app.post("/api/approve/{order_id}")
async def approve_order(order_id: str):
    rows = []
    found = False
    with open(ORDERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["order_id"] == order_id:
                row["status"] = "Approved"
                found = True
            rows.append(row)
    if not found:
        raise HTTPException(404, "الطلب غير موجود")
    with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"✅ تم تأكيد الدفع: {order_id}")
    return JSONResponse({"message": f"تم تأكيد الطلب {order_id}"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
