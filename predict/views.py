import requests
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import ImageUpload, Prediction, QuestionAnswer
from .forms import SignUpForm, LoginForm
from django.contrib.auth.models import User

import os
import tensorflow as tf
import numpy as np
from django.conf import settings

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    "model/my_clothing_classifier_model"
)

model = None
infer = None

try:
    loaded = tf.saved_model.load(MODEL_PATH)
    infer = loaded.signatures["serving_default"]
    model = loaded
    print("✅ Model loaded OK")
except Exception as e:
    print("❌ Model load error:", e)

classes = ["áo thun", "váy", "áo khoác", "quần short", "quần jean"]
# =======================
# 🧠 AI NHẬN DIỆN ẢNH
# =======================
from tensorflow.keras.preprocessing import image

def predict_image(img_path):
    try:
        if infer is None:
            return {"label": "Model chưa load", "confidence": 0}

        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.convert_to_tensor(img_array, dtype=tf.float32)

        pred = infer(img_array)

        output_key = list(pred.keys())[0]
        pred = pred[output_key].numpy()[0]

        idx = np.argmax(pred)

        return {
            "label": classes[idx],
            "confidence": round(float(pred[idx]) * 100, 2)
        }

    except Exception as e:
        return {
            "label": f"Lỗi predict: {str(e)}",
            "confidence": 0
        }
# =======================
# 🧺 OPENROUTER - TƯ VẤN GIẶT
# =======================
def get_wash_advice(label):
    try:
        prompt = f"""
Bạn là chuyên gia giặt giũ.

Quần áo: {label}

Trả lời ngắn gọn 3-5 dòng.
"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://cloths-ai.onrender.com",
                "X-Title": "cloths-ai"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()

        if response.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"]

        return f"API lỗi: {data}"

    except Exception as e:
        return f"Lỗi: {str(e)}"
# =======================
# 💬 OPENROUTER - TRẢ LỜI CÂU HỎI
# =======================
def answer_question(question, clothing_label):
    try:
        prompt = f"""
Quần áo: {clothing_label}
Câu hỏi: {question}

Trả lời ngắn gọn 2-4 dòng.
"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://cloths-ai.onrender.com",
                "X-Title": "cloths-ai"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()

        if response.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"]

        return f"API lỗi: {data}"

    except Exception as e:
        return f"Lỗi: {str(e)}"

# =======================
# 🌐 VIEW CHÍNH
# =======================
def index(request):
    context = {}
    
    # Lấy ảnh cuối cùng đã upload (nếu có)
    latest_image = None

    if request.method == 'POST':
        image_file = request.FILES.get('image')

        if image_file:
            # 💾 Lưu ảnh
            obj = ImageUpload.objects.create(image=image_file)
            latest_image = obj

            # 🤖 AI 1: nhận diện
            prediction = predict_image(obj.image.path)
            print(f"Prediction: {prediction}")  # Debug

            # 💾 Lưu kết quả dự đoán
            Prediction.objects.create(
                image=obj,
                label=prediction['label'],
                confidence=prediction['confidence'],
                model_name="MobileNetV2"
            )

            # 🧺 AI 2: tư vấn giặt
            wash_advice = get_wash_advice(prediction['label'])
            print(f"Wash advice: {wash_advice}")  # Debug

            context = {
                'image_id': obj.id,
                'image_url': obj.image.url,
                'label': prediction['label'],
                'confidence': prediction['confidence'],
                'wash_advice': wash_advice
            }
            print(f"Context: {context}")  # Debug
        else:
            context['error'] = "Vui lòng chọn ảnh"

    return render(request, 'index.html', context)


# =======================
# 💬 API TRẢ LỜI CÂU HỎI (AJAX)
# =======================
def ask_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_id = data.get('image_id')
            question = data.get('question')
            clothing_label = data.get('clothing_label')

            if not question or not clothing_label:
                return JsonResponse({'error': 'Thiếu thông tin'}, status=400)

            # 🤖 AI trả lời câu hỏi
            answer = answer_question(question, clothing_label)

            # 💾 Lưu Q&A vào database
            if image_id:
                try:
                    image_obj = ImageUpload.objects.get(id=image_id)
                    
                    # Xác định user - nếu chưa login, tạo hoặc dùng user Anonymous
                    if request.user.is_authenticated:
                        user = request.user
                    else:
                        # Tạo user anonymous nếu chưa có
                        user, created = User.objects.get_or_create(username='anonymous')
                    
                    QuestionAnswer.objects.create(
                        user=user,
                        image=image_obj,
                        question=question,
                        answer=answer
                    )
                except ImageUpload.DoesNotExist:
                    pass

            return JsonResponse({
                'success': True,
                'question': question,
                'answer': answer
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Phương thức không được hỗ trợ'}, status=405)


# =======================
# 🔐 ĐĂNG NHẬP
# =======================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng {username}! Đăng nhập thành công.')
                return redirect('index')
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'login.html', context)


# =======================
# 🔓 ĐĂNG XUẤT
# =======================
def logout_view(request):
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('index')


# =======================
# 📝 ĐĂNG KÝ
# =======================
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Tự động đăng nhập sau khi đăng ký
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Chào mừng {username}! Tài khoản của bạn đã được tạo.')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'signup.html', context)

