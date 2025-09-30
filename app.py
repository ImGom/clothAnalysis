from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import json
from PIL import Image
import google.generativeai as genai
import io
import re

load_dotenv()
app = Flask(__name__)

# JSON 데이터 로드
with open('data/clothing_db.json', 'r', encoding='utf-8') as f:
    DB = json.load(f)['items']

with open('data/config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

# Gemini 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def normalize_attributes(raw_attrs):
    """AI 응답을 config.json 기반으로 정규화"""
    normalized = {}
    
    for category, attrs in raw_attrs.items():
        if attrs is None:
            continue
        
        # 색상 정규화
        color_lower = attrs['color'].lower()
        matched_color = attrs['color']
        for standard_color, variants in CONFIG['colors'].items():
            if any(variant.lower() in color_lower for variant in variants):
                matched_color = standard_color
                break
        
        # 타입 정규화
        type_lower = attrs['type'].lower()
        matched_type = attrs['type']
        
        category_types = CONFIG['types'].get(category, {})
        for standard_type, variants in category_types.items():
            if any(variant.lower() in type_lower for variant in variants):
                matched_type = standard_type
                break
        
        normalized[category] = {
            'color': matched_color,
            'type': matched_type
        }
    
    return normalized

def find_best_match_in_db(category, color, type_val):
    """DB에서 가장 적합한 항목 찾기"""
    
    # 완전 일치
    for item in DB:
        if (item['category'] == category and 
            item['color'] == color and 
            item['type'] == type_val):
            return item
    
    # 색상만 일치
    candidates = [item for item in DB 
                  if item['category'] == category and item['color'] == color]
    if candidates:
        for item in candidates:
            if type_val.lower() in item['type'].lower() or item['type'].lower() in type_val.lower():
                return item
        return candidates[0]
    
    # 카테고리만 일치
    category_items = [item for item in DB if item['category'] == category]
    if category_items:
        return category_items[0]
    
    return None

def analyze_and_match(image_bytes):
    """전신 이미지에서 의류 분석 후 DB 매칭"""
    
    prompt = """이미지 속 인물이 착용한 의류를 분석하세요.

**중요: 아래 목록의 값만 사용하세요**

색상: gray, blue, red, green, yellow, purple, orange, brown, white, black

상의(top): shirts, crewneckt, hoodie, sweater, cardigan, coat, scrubs, hanbok, sportsbra
하의(bottom): shorts, jeans, cargopants, slacks, yogapants, skirt
신발(shoes): boots, flats, flipflops, loafers, oxfords, running, sneakers

JSON 형식으로만 답변:
{
    "top": {"color": "색상", "type": "종류"} 또는 null,
    "bottom": {"color": "색상", "type": "종류"} 또는 null,
    "shoes": {"color": "색상", "type": "종류"} 또는 null
}

JSON만 출력하세요."""

    image = Image.open(io.BytesIO(image_bytes))
    response = model.generate_content([prompt, image])
    
    text = response.text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        raw_attributes = json.loads(json_match.group())
    else:
        raw_attributes = json.loads(text)
    
    # 속성 정규화
    attributes = normalize_attributes(raw_attributes)
    
    results = []
    for category, attrs in attributes.items():
        matched = find_best_match_in_db(category, attrs['color'], attrs['type'])
        
        if matched:
            # 이미지 경로 보정
            image_path = matched['image']
            if not image_path.startswith('/'):
                image_path = '/' + image_path
            
            results.append({
                "category": category,
                "extracted": f"{attrs['color']} {attrs['type']}",
                "matched_item": {
                    **matched,
                    "image": image_path
                }
            })
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        results = analyze_and_match(image_bytes)
        
        return jsonify({"matches": results})
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)