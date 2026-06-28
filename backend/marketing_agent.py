import os, csv, time, sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
MARKETING_CSV = DATA_DIR / "marketing_posts.csv"
MARKETING_CSV.parent.mkdir(exist_ok=True)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if not MARKETING_CSV.exists():
    with open(MARKETING_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["created_at", "platform", "content"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

MARKETING_PROMPT = """أنت خبير تسويق محتوى رقمي متخصص في سوق الشغل والموارد البشرية بالمغرب.

المطلوب: توليد 5 منشورات قصيرة ومنظمة (100-150 كلمة) لمنصات LinkedIn/Instagram بالدارجة المغربية أو العربية المبسطة.

يجب أن تغطي المواضيع التالية (واحد لكل منشور):
1. نصائح لاجتياز أنظمة ATS في السيرة الذاتية
2. أهمية الرسالة التحفيزية وكيفية كتابتها
3. أخطاء شائعة في السير الذاتية
4. كيف تبرز مهاراتك حتى بدون خبرة كبيرة
5. نصائح للبحث عن وظيفة في المغرب

لكل منشور:
- اكتب المحتوى
- حدد المنصة (LinkedIn أو Instagram)
- أضف 5 هاشتاغات مناسبة

الصيغة المطلوبة (لكل منشور):
---
المنصة: [LinkedIn/Instagram]
المحتوى: [النص]
الهاشتاغات: #[كلمة] #[كلمة] #[كلمة] #[كلمة] #[كلمة]
---
"""

def generate_posts():
    try:
        response = model.generate_content(MARKETING_PROMPT)
        text = response.text
    except Exception as e:
        text = f"خطأ في التوليد: {e}"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    posts = text.split("---")
    with open(MARKETING_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for post in posts:
            post = post.strip()
            if not post:
                continue
            platform = "LinkedIn/Instagram"
            if "المنصة:" in post:
                for line in post.split("\n"):
                    if "المنصة:" in line:
                        platform = line.split(":", 1)[1].strip()
                        break
            w.writerow([now, platform, post])
    print(f"📱 تم توليد {len([p for p in posts if p.strip()])} منشور تسويقي")
    print(f"   محفوظ في: {MARKETING_CSV}")

if __name__ == "__main__":
    generate_posts()
