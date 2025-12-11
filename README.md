# سرمد - Sarmad

نظام ذكي لتتبع مصادر المحتوى الفيروسي المخالف على منصات التواصل الاجتماعي.

##  التشغيل السريع

```bash
# تشغيل خادم MockX (محاكي تويتر)
cd sarmad
python3 -m uvicorn mockx.server:app --port 8001 --reload

# تشغيل خادم Sarmad (في terminal آخر)
python3 -m uvicorn backend.main:app --port 8000 --reload
```

##  هيكل المشروع

```
sarmad/
├── backend/           # خادم Sarmad الرئيسي
│   ├── main.py        # API endpoints
│   ├── reports_manager.py  # إدارة البلاغات
│   ├── nlp_engine.py  # استخراج البصمة الدلالية
│   └── search_algorithm.py  # خوارزمية البحث الثنائي
├── mockx/             # محاكي تويتر
│   ├── server.py      # MockX API
│   ├── index.html     # الصفحة الرئيسية
│   └── pages/         # صفحات إضافية
├── sarmad-dashboard/  # لوحة تحكم سرمد
├── reports-portal/    # بوابة البلاغات العامة
├── frontend/          # واجهة التحليل الأصلية
└── graphs/            # رسوم بيانية للانتشار
```

## 🔗 الروابط

| الصفحة | الرابط |
|--------|--------|
| MockX الرئيسية | http://localhost:8001 |
| البحث المتقدم | http://localhost:8001/pages/search.html |
| الترندات | http://localhost:8001/pages/trends.html |
| لوحة تحكم سرمد | http://localhost:8000/dashboard |
| بوابة البلاغات | http://localhost:8000/reports |
| واجهة التحليل | http://localhost:8000 |

## ⚙️ API Endpoints

### Sarmad (port 8000)
- `GET /api/status` - حالة النظام
- `GET /api/tweets` - قائمة التغريدات
- `POST /api/reports` - تقديم بلاغ
- `GET /api/reports` - قائمة البلاغات
- `WS /ws/analysis` - WebSocket للتحليل المباشر

### MockX (port 8001)
- `GET /api/v2/tweets` - Timeline
- `GET /api/v2/tweets/search` - بحث
- `GET /api/v2/trends` - الترندات
- `GET /api/v2/data/export` - تصدير البيانات

## 📋 المتطلبات

```
python >= 3.9
fastapi
uvicorn
httpx
```
