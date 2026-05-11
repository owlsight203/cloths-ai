# 👕 Cloths AI - Ứng Dụng Nhận Diện Quần Áo Bằng AI

Ứng dụng web Django sử dụng AI để nhận diện loại quần áo từ ảnh, cung cấp lời khuyên giặt và trả lời câu hỏi về quần áo.

## ✨ Tính Năng

- 🎨 **Nhận diện quần áo** - Upload ảnh và AI sẽ nhận diện loại quần áo
- 🧺 **Lời khuyên giặt** - Nhận lời khuyên chi tiết cách giặt phù hợp
- ❓ **Q&A thông minh** - Đặt câu hỏi về quần áo và nhận câu trả lời từ AI
- 👤 **Quản lý tài khoản** - Đăng ký, đăng nhập và lưu lịch sử
- 📊 **Lịch sử dự đoán** - Xem lại các lần nhận diện trước đó

## 🚀 Cài Đặt

### 1. Clone Repository
```bash
git clone https://github.com/owlsight203/cloths-ai.git
cd cloths-ai
```

### 2. Tạo Virtual Environment
```bash
python -m venv env
source env/Scripts/activate  # Windows
# hoặc
source env/bin/activate  # Linux/Mac
```

### 3. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Environment Variables
```bash
cp .env.example .env
# Chỉnh sửa .env với API key của bạn
```

### 5. Tạo Database
```bash
python manage.py migrate
```

### 6. Chạy Server
```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## ⚙️ Cấu Hình

### Biến Môi Trường (.env)
- `OPENROUTER_API_KEY` - API key từ [OpenRouter](https://openrouter.ai/)
- `MODEL_PATH` - Đường dẫn đến model TensorFlow
- `SECRET_KEY` - Django secret key
- `DEBUG` - Mode debug (True/False)
- `ALLOWED_HOSTS` - Hosts được phép (phẩy tách)

## 📋 Yêu Cầu

- Python 3.10+
- Django 5.2.13
- TensorFlow 2.15.0
- Xem `requirements.txt` để biết đầy đủ

## 🔐 Bảo Mật

- ⚠️ **KHÔNG** commit file `.env` lên GitHub
- File `.env` đã được thêm vào `.gitignore`
- Sử dụng `.env.example` để hướng dẫn cấu hình

## 📚 Cấu Trúc Dự Án

```
cloths-ai/
├── Cloths_Predict/
│   ├── __init__.py
│   ├── settings.py      # Django settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── predict/
│   ├── migrations/
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   └── signup.html
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── manage.py
├── requirements.txt
├── .env                 # (Không commit)
├── .env.example         # Template
├── .gitignore
└── README.md
```

## 🧠 Công Nghệ Sử Dụng

- **Backend**: Django 5.2
- **AI/ML**: TensorFlow, Keras
- **API**: OpenRouter (GPT-4o Mini)
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript

## 📝 Hướng Dẫn Sử Dụng

1. **Đăng Ký/Đăng Nhập**
   - Truy cập `/signup/` để tạo tài khoản
   - Hoặc `/login/` để đăng nhập

2. **Upload Ảnh**
   - Chọn ảnh quần áo từ máy tính
   - Nhấn "Upload & Nhận Diện"

3. **Xem Kết Quả**
   - Loại quần áo được nhận diện
   - Độ chính xác (%)
   - Lời khuyên cách giặt

4. **Đặt Câu Hỏi**
   - Nhập câu hỏi về quần áo đó
   - Nhấn "Hỏi"
   - AI sẽ trả lời tức thì

## 🐛 Troubleshooting

### Lỗi: Model không tìm thấy
- Kiểm tra `MODEL_PATH` trong `.env`
- Đảm bảo model TensorFlow được đặt ở vị trí đúng

### Lỗi: API Key không hợp lệ
- Lấy API key từ https://openrouter.ai/
- Thêm vào biến `OPENROUTER_API_KEY` trong `.env`

### Lỗi: Database
```bash
python manage.py migrate
python manage.py migrate --run-syncdb
```

## 📧 Liên Hệ

Nếu có câu hỏi hoặc vấn đề, vui lòng tạo Issue trên GitHub.

## 📄 License

MIT License - Xem LICENSE file để biết chi tiết
 
