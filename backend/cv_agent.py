import os, csv, json, time, sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
BASE = Path(__file__).resolve().parent.parent
ORDERS_CSV = BASE / "data" / "orders.csv"
OUTPUTS_DIR = BASE / "data" / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

CV_PROMPT = """أنت خبير توظيف وكاتب سير ذاتية محترف. اكتب سيرة ذاتية ورسالة تحفيزية بالعربية للمستخدم التالي.

بيانات المستخدم:
- الاسم: {full_name}
- البريد: {email}
- النبذة: {bio}
- الوظيفة المستهدفة: {target_job}

المطلوب:
1. **السيرة الذاتية (CV)** — منسقة، احترافية، متوافقة مع ATS. الأقسام: المعلومات الشخصية، الملخص المهني، الخبرات، المهارات، التعليم، الشهادات (إن وجدت).
2. **رسالة تحفيزية (Cover Letter)** — موجهة لصاحب العمل، تسلط الضوء على مهارات المستخدم ولماذا هو المرشح المناسب.

الرجاء استخدام لغة عربية فصحى مبسطة (أو عربية مهنية) مع إمكانية إضافة بعض المصطلحات الإنجليزية عند الضرورة. استخدم تنسيق Markdown نظيف.
"""

def generate_cv(order):
    full_name = order["full_name"].strip().replace(" ", "_")
    prompt = CV_PROMPT.format(**order)
    try:
        response = model.generate_content(prompt)
        text = response.text
    except Exception as e:
        text = f"# خطأ في التوليد\n\n{str(e)}"
    out_file = OUTPUTS_DIR / f"{full_name}_cv.md"
    out_file.write_text(text, encoding="utf-8")
    print(f"📝 تم توليد السيرة الذاتية: {out_file}")
    return str(out_file)

def process_approved_orders():
    if not ORDERS_CSV.exists():
        print("⚠️ لا يوجد ملف طلبات")
        return
    rows = []
    with open(ORDERS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    for row in rows:
        if row["status"] == "Approved" and not row.get("cv_generated", ""):
            print(f"🤖 جاري توليد CV للطلب {row['order_id']}...")
            path = generate_cv(row)
            row["cv_generated"] = path
            row["cv_status"] = "Done"
    with open(ORDERS_CSV, "w", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

if __name__ == "__main__":
    process_approved_orders()
