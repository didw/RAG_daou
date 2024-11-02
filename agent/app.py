import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/generate', methods=['POST'])
def generate():
    context = request.json.get('context')
    query = request.json.get('query')

    # 답변 생성 로직 (여기서는 OpenAI GPT-3 모델 사용 예시)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "query": query,
                        "context": context
                    })
                }
            ],
            # response_format=json,
            model="gpt-4o",
            temperature=0.1,
            seed=2024
        )
        answer = chat_completion.choices[0].message.content
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
