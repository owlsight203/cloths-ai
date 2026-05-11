from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import ImageUpload, Prediction, QuestionAnswer
from .forms import SignUpForm, LoginForm
from django.contrib.auth.models import User

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import requests
import json
import os


# =======================
# 🔐 CONFIG OPENROUTER
# =======================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =======================
# 🤖 LOAD MODEL AI (1 lần)
# =======================
# Sử dụng path từ environment hoặc hardcoded path
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    r"D:\DATASET\modelAI\my_clothing_classifier_model-20260415T052259Z-3-001\my_clothing_classifier_model"
)

try:
    model = tf.keras.layers.TFSMLayer(
        MODEL_PATH,
        call_endpoint='serving_default'
    )
except Exception as e:
    print(f"⚠️ Lỗi khi load model: {e}")
    print(f"⚠️ Đường dẫn: {MODEL_PATH}")
    model = None

classes = ["áo thun", "váy", "áo khoác", "quần short", "quần jean"]


# =======================
# 🧠 AI NHẬN DIỆN ẢNH
# =======================
def predict_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = model(img_array)
        pred = list(pred.values())[0].numpy()[0]

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

        Hãy đưa ra lời khuyên giặt cho loại quần áo: {label}

        Yêu cầu:
        - Ngắn gọn
        - Dễ hiểu
        - 3-5 dòng
        - Tiếng Việt
        - Không lan man
        """

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"API lỗi: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Lỗi: {str(e)}"


# =======================
# 💬 OPENROUTER - TRẢ LỜI CÂU HỎI
# =======================
def answer_question(question, clothing_label):
    try:
        prompt = f"""
        Bạn là chuyên gia về thời trang và quần áo.
        
        Quần áo được phát hiện: {clothing_label}
        Câu hỏi của người dùng: {question}
        
        Hãy trả lời câu hỏi một cách:
        - Ngắn gọn (2-4 dòng)
        - Rõ ràng
        - Dễ hiểu
        - Tiếng Việt
        - Liên quan đến loại quần áo được phát hiện
        """

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Không thể trả lời câu hỏi lúc này"

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

