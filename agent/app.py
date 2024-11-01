from flask import Flask, request, jsonify
import openai  # OpenAI API를 사용하는 경우

app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수나 다른 안전한 방법으로 관리 권장)
openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/generate', methods=['POST'])
def generate():
    context = request.json.get('context')
    query = request.json.get('query')

    # 답변 생성 로직 (여기서는 OpenAI GPT-3 모델 사용 예시)
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Context: {context}\nQuestion: {query}\nAnswer:",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        answer = response.choices[0].text.strip()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
