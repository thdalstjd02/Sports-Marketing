import os
import shutil
import json
import gc
from flask import Flask, render_template
from PIL import Image, ImageOps

app = Flask(__name__)

# ==========================================
# [1] 시스템 초기화 및 폴더 설정
# ==========================================
def initialize_system():
    # static 폴더 초기화 (최적화된 이미지 저장소)
    if os.path.exists('static'):
        shutil.rmtree('static')
    os.makedirs('static', exist_ok=True)

    # 프로젝트 원본 폴더가 없으면 경고 방지용 생성
    project_folders = ['project1', 'project2', 'project3', 'project4']
    for folder in project_folders:
        os.makedirs(folder, exist_ok=True)

# ==========================================
# [2] 이미지 처리 로직
# ==========================================
final_images = { 'project1': [], 'project2': [], 'project3': [], 'project4': [] }
profile_img_path = 'https://via.placeholder.com/150/333/fff?text=No+Profile'

def process_images():
    global profile_img_path
    
    # 2-1. 프로필 사진 처리
    possible_profiles = ['profile.jpg', 'profile.png', 'profile.jpeg']
    for p_file in possible_profiles:
        if os.path.exists(p_file):
            try:
                with Image.open(p_file) as img:
                    img = ImageOps.exif_transpose(img)
                    img = img.convert("RGB")
                    img.thumbnail((400, 400))
                    dst_path = f"static/profile_optimized.jpg"
                    img.save(dst_path, quality=85, optimize=True)
                    profile_img_path = f"/static/profile_optimized.jpg"
                    print(f"🧑‍💼 [성공] 프로필 사진 처리 완료: {p_file}")
                break
            except Exception as e:
                print(f"⚠️ 프로필 처리 중 오류: {e}")

    # 2-2. 프로젝트 사진 처리
    project_folders = ['project1', 'project2', 'project3', 'project4']
    
    for folder_name in project_folders:
        if not os.path.exists(folder_name): continue
        
        files = sorted(os.listdir(folder_name))
        processed_count = 0
        
        for filename in files:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')): 
                continue
            
            src_path = os.path.join(folder_name, filename)
            new_filename = f"{folder_name}_{filename}"
            dst_path = os.path.join("static", new_filename)
            
            try:
                with Image.open(src_path) as img:
                    img = ImageOps.exif_transpose(img)
                    img = img.convert("RGB")
                    img.thumbnail((800, 800))
                    img.save(dst_path, quality=80, optimize=True)
                
                # 웹 경로 형식으로 저장 (/static/...)
                final_images[folder_name].append(f"/static/{new_filename}")
                processed_count += 1
                gc.collect() # 메모리 정리
            except Exception as e:
                print(f"⚠️ 이미지 처리 에러 ({filename}): {e}")

        # 사진이 없을 경우 더미 이미지
        if processed_count == 0:
            final_images[folder_name].append("https://via.placeholder.com/800x600/333/fff?text=No+Image")
        else:
            print(f"📸 [{folder_name}] {processed_count}장 처리 완료")

# 서버 시작 전 초기화 실행
initialize_system()
process_images()

# ==========================================
# [3] 라우팅 (페이지 연결)
# ==========================================
@app.route('/')
def home():
    # 사용자 정보
    user_info = { 
        "name": "송민성", 
        "title": "Sports Marketing", 
        "email": "vexx045@gmail.com" 
    }
    
    # Python 데이터를 HTML로 전달
    return render_template('index.html', 
                           user=user_info,
                           profile_img_path=profile_img_path,
                           js_data_project1=json.dumps(final_images['project1']),
                           js_data_project2=json.dumps(final_images['project2']),
                           js_data_project3=json.dumps(final_images['project3']),
                           js_data_project4=json.dumps(final_images['project4']),
                           preload_img=final_images['project1'][0] if final_images['project1'] else "")

if __name__ == '__main__':
    # 로컬에서 실행 시
    app.run(debug=True, port=5000)