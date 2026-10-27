# FastAPI Library Management System (PostgreSQL)

یک سیستم مدیریت کتابخانه که با فریم‌ورک **FastAPI** و پایگاه داده **PostgreSQL** ساخته شده است. داده‌ها داخل دیتابیس ذخیره می‌شوند و با ری‌استارت سرور پاک نمی‌شوند. آدرس و رمز دیتابیس از طریق متغیرهای محیطی (`.env`) خوانده می‌شود و روی گیت‌هاب قرار نمی‌گیرد.

## امکانات

- ارتباط واقعی با پایگاه داده **PostgreSQL** به کمک SQLAlchemy و درایور `psycopg` (v3)
- مشاهده لیست همه کتاب‌ها
- ثبت کتاب جدید با اعتبارسنجی Pydantic
- مشاهده اطلاعات یک کتاب مشخص با شناسه‌ی عددی
- ویرایش بخشی از اطلاعات یک کتاب (PATCH)
- حذف کتاب
- مستندات تعاملی خودکار (Swagger UI و ReDoc)

## تکنولوژی‌ها

- Python 3.9+
- FastAPI
- PostgreSQL & pgAdmin 4
- SQLAlchemy (ORM)
- Psycopg (v3)
- Pydantic v2
- Uvicorn
- Python-dotenv

## ساختار پروژه

```
.
├── database.py       # تنظیمات اتصال به دیتابیس و سشن‌ها
├── models.py         # مدل‌های ORM دیتابیس (SQLAlchemy)
├── main.py           # مسیرها و اندپوینت‌های FastAPI
├── .env              # متغیرهای محیطی و تنظیمات محرمانه (روی گیت‌هاب نمی‌رود)
├── .gitignore        # فایل‌های نادیده‌گرفته‌شده توسط گیت
├── requirements.txt  # پکیج‌ها و وابستگی‌های پروژه
└── README.md         # مستندات پروژه
```

## پیش‌نیازها

- Python 3.9 یا بالاتر
- PostgreSQL نصب‌شده و در حال اجرا (و در صورت تمایل pgAdmin 4 برای مدیریت گرافیکی)

## نصب و راه‌اندازی

### ۱. کلون کردن پروژه

```bash
git clone <repo-url>
cd <repo-folder>
```

### ۲. ساخت و فعال‌سازی محیط مجازی

```bash
python -m venv venv
venv\Scripts\activate        # ویندوز
# source venv/bin/activate   # لینوکس و مک
```

### ۳. نصب پکیج‌ها

```bash
pip install -r requirements.txt
```

### ۴. ساخت دیتابیس

جدول `books` به‌صورت خودکار موقع اجرای برنامه ساخته می‌شود، اما خود دیتابیس باید از قبل وجود داشته باشد. در pgAdmin روی `Databases` کلیک راست کنید و `Create ← Database` را بزنید و نام آن را `library_db` بگذارید. یا در Query Tool دستور زیر را اجرا کنید:

```sql
CREATE DATABASE library_db;
```

### ۵. تنظیم متغیرهای محیطی

در پوشه‌ی اصلی پروژه، یک فایل به نام `.env` بسازید و آدرس دیتابیس خود را طبق فرمت زیر داخل آن قرار دهید:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/library_db
```

*(توجه: اگر رمز عبور شما کاراکتر خاصی مثل `@` دارد، آن را به `%40` تبدیل کنید.)*

### ۶. اجرای سرور

```bash
uvicorn main:app --reload
```

سرور روی `http://127.0.0.1:8000` اجرا می‌شود.

مستندات تعاملی برای تست اندپوینت‌ها:

* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

| متد | مسیر | توضیح | کد موفقیت |
| --- | --- | --- | --- |
| GET | `/books` | دریافت لیست همه کتاب‌ها از دیتابیس | 200 |
| POST | `/books` | ثبت کتاب جدید در دیتابیس | 201 |
| GET | `/books/{id}` | دریافت اطلاعات یک کتاب با شناسه | 200 |
| PATCH | `/books/{id}` | ویرایش اطلاعات کتاب در دیتابیس | 200 |
| DELETE | `/books/{id}` | حذف کتاب از دیتابیس | 200 |

## مدل داده (جدول `books`)

| فیلد | نوع | الزامی | قوانین |
| --- | --- | --- | --- |
| id | int | - | کلید اصلی، تولید خودکار (Auto-increment) |
| title | string | بله | بین ۱ تا ۱۵۰ کاراکتر |
| author | string | بله | بین ۱ تا ۱۰۰ کاراکتر |
| year | int | بله | بزرگ‌تر از ۰ |
| summary | string | خیر | می‌تواند `null` باشد |

## نمونه درخواست

```bash
curl -X POST http://127.0.0.1:8000/books -H "Content-Type: application/json" -d "{\"title\": \"Clean Code\", \"author\": \"Robert C. Martin\", \"year\": 2008, \"summary\": \"A handbook of agile software craftsmanship\"}"
```

## خطاها

| کد | معنی |
| --- | --- |
| 404 | کتابی با این شناسه در دیتابیس پیدا نشد |
| 422 | داده‌های ورودی نامعتبر است (مثلاً `title` خالی یا بیش‌ازحد بلند، یا `year` منفی) |

## نکات

- داده‌ها در PostgreSQL ذخیره می‌شوند و با ری‌استارت سرور حفظ می‌شوند.
- در ویندوز اگر از PowerShell استفاده می‌کنید، به‌جای `curl` از `curl.exe` استفاده کنید یا مستقیماً از `/docs` تست کنید.
