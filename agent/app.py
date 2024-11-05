import os
import json
import logging
import traceback
from flask import Flask, request, jsonify
from openai import OpenAI

# 기본 로거 설정
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_instructions(request_type: str) -> str:
    if request_type == "trend_analysis":
        return "당신은 패션, 뷰티, 음식 분야의 트렌드 분석에 전문성을 갖춘 전문가입니다. 주어진 문맥을 기반으로 주요 트렌드를 요약하여 제공하세요."
    elif request_type == "tourist_search":
        return "당신은 여행 전문가로서 사용자의 관심사와 최신 트렌드를 반영하여 관광지를 추천합니다. 관광지의 이름, 주요 특징, 여행 팁과 같은 필수 정보를 포함해 설명하세요."
    else:
        return "현재 입력한 사용자 요청이 '트렌드 분석' 또는 '관광지 검색'에 대한 요청아닙니다. 그에 따라 Fallback 메시지를 생성해야합니다. 사용자 입력에 맞는 Fallback 메시지를 작성해주세요."

# 1. 사용자 입력 분류 엔드포인트
@app.route('/classify', methods=['POST'])
def classify():
    text = request.json.get('text')
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "당신은 사용자 요청이 '트렌드 분석', '관광지 검색', 또는 그 외 (fallback) 중 무엇에 해당하는지 분류하는 분류 전문가입니다. 주어진 사용자 요청을 분석하여 해당하는 요청 유형을 정확하게 분류하세요. 분류 결과를 '트렌드 분석', '관광지 검색', 또는 'fallback' 중 하나로 선택해주세요."},
                {"role": "user", "content": f"사용자 입력: {text}"}
            ],
            model="gpt-4o-mini",
            temperature=0.3
        )
        classification = response.choices[0].message.content.strip()
        logger.debug(f"Classification: {classification}")
        if "트렌드 분석" in classification:
            classification = "trend_analysis"
        elif "관광지 검색" in classification:
            classification = "tourist_search"
        else:
            classification = "fallback"
    except Exception as e:
        logger.error(f"Classification Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'classification': classification})

# 2. 답변 적절성 평가 엔드포인트
@app.route('/evaluate', methods=['POST'])
def evaluate():
    user_input = request.json.get('user_input')
    answer = request.json.get('answer')
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "당신은 답변의 적절성을 평가하는 평가자입니다. 주어진 답변이 사용자 입력에 대해 적절한지 또는 수정이 필요한지를 평가하세요. 적절하다면 '네'를, 그렇지 않다면 '아니오' 라고 답변해주세요."},
                {"role": "user", "content": f"사용자 입력: {user_input}, 답변: {answer}"}
            ],
            model="gpt-4o-mini",
            temperature=0.1
        )
        evaluation_result = response.choices[0].message.content.strip().lower()
        logger.debug(f"Evaluation result: {evaluation_result}")
        is_appropriate = "네" in evaluation_result
    except Exception as e:
        logger.error(f"Evaluation Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'is_appropriate': is_appropriate})

# 3. Query Rewrite 엔드포인트
@app.route('/rewrite', methods=['POST'])
def rewrite():
    query = request.json.get('query')
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "당신은 사용자 쿼리를 더 명확하고 완전하게 하기 위해 다듬는 쿼리 재작성 전문가입니다. 주어진 쿼리를 다시 작성하여 이해와 검색 효과를 높이세요."},
                {"role": "user", "content": f"다음 사용자 입력을 관광지 검색, 혹은 패션 트렌드 분석 등에 맞게 재작성해주세요: {query}"}
            ],
            model="gpt-4o-mini",
            temperature=0.5
        )
        rewritten_query = response.choices[0].message.content.strip()
        logger.debug(f"Rewritten query: {rewritten_query}")
    except Exception as e:
        logger.error(f"Rewrite Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    return jsonify({'rewritten_query': rewritten_query})

# 4. 정보 생성 엔드포인트
@app.route('/generate', methods=['POST'])
def generate():
    context = request.json.get('context')
    query = request.json.get('query')
    request_type = request.json.get('type')

    instructions = generate_instructions(request_type)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": json.dumps({"사용자 입력": query, "관련 문서": context})}
            ],
            model="gpt-4o-mini",
            temperature=0.5,
            seed=2024
        )
        answer = chat_completion.choices[0].message.content
        logger.debug(f"Answer: {answer}")
    except Exception as e:
        logger.error(f"Generate Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': answer})

# 5. 사용자 입력과 비교해 관련성이 높은 문서 추출 엔드포인트
@app.route('/rank_documents', methods=['POST'])
def rank_documents():
    documents = request.json.get('documents')
    query = request.json.get('query')

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "사용자가 제공한 쿼리에 따라 가장 적합한 문서를 선택하는 전문가입니다. 주어진 문서 중 관련성이 높은 문서 2개를 선택해주세요."},
                {"role": "user", "content": f"쿼리: {query}\n문서들: {documents}"}
            ],
            model="gpt-4o-mini",
            temperature=0.2
        )
        top_document = response.choices[0].message.content.strip()
        logger.debug(f"Top document: {top_document}")
    except Exception as e:
        logger.error(f"Rank Documents Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'top_document': top_document})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
