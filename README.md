sarmad/
├── backend/
│   ├── main.py              # Sarmad API (port 8000)
│   ├── reports_manager.py   # [NEW] إدارة البلاغات
│   ├── data_generator.py    # توليد البيانات
│   ├── nlp_engine.py        
│   └── search_algorithm.py  
├── mockx/
│   ├── server.py            # [MODIFY] MockX API (port 8001)
│   ├── pages/               # [NEW] صفحات MockX
│   │   ├── index.html       # الصفحة الرئيسية
│   │   ├── search.html      # صفحة البحث
│   │   └── trends.html      # صفحة الترندات
│   └── styles.css           # [NEW] أنماط موحدة
├── reports-portal/          # [NEW] بوابة البلاغات العامة
│   ├── index.html           # صفحة تقديم البلاغ
│   ├── success.html         # صفحة تأكيد الاستلام
│   └── styles.css           
└── graphs/                  # الرسوم البيانية (موجود)
