# CV Express — نظام السيرة الذاتية المؤتمت

نظام متكامل يستخدم الذكاء الاصطناعي (Gemini API) لتوليد سير ذاتية احترافية ورسائل تحفيزية.

## هيكل المشروع

```
cv_express_automation/
├── backend/
│   ├── main.py            # FastAPI server
│   ├── cv_agent.py        # CV generation agent
│   └── marketing_agent.py # Social media content agent
├── frontend/
│   └── index.html         # Arabic landing page
├── data/
│   ├── orders.csv         # Customer orders
│   ├── marketing_posts.csv
│   ├── uploads/           # Payment screenshots
│   └── outputs/           # Generated CVs (.md)
└── .env                   # GEMINI_API_KEY
```

## التشغيل

1. تأكد من تثبيت المتطلبات:
```bash
pip install fastapi uvicorn google-generativeai python-dotenv python-multipart jinja2
```

2. شغل الخادم:
```bash
python backend/main.py
```

3. افتح المتصفح على: http://127.0.0.1:8000

## استخدام الوكلاء

### توليد السيرة الذاتية للطلبات المعتمدة:
```bash
python backend/cv_agent.py
```

### توليد منشورات تسويقية:
```bash
python backend/marketing_agent.py
```

### تأكيد طلب (API):
```bash
curl -X POST http://127.0.0.1:8000/api/approve/CV-XXXXXX
```
