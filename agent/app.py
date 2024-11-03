import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI
from autogen import MultiAgent

app = Flask(__name__)

# OpenAI API 초기화
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# 에이전트 초기화
multi_agent = MultiAgent()

# 트렌드 에이전트 정의
class TrendAgent:
    def __init__(self, client):
        self.client = client

    def analyze_trends(self, context):
        # 트렌드 분석 요청
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a trend analysis expert focused on fashion, beauty, and food trends."},
                {"role": "user", "content": f"Analyze the following news data for trending topics: {context}"}
            ],
            model="gpt-4",
            temperature=0.5
        )
        trend_summary = response.choices[0].message.content
        return trend_summary

# 관광명소 에이전트 정의
class TouristAgent:
    def __init__(self, client):
        self.client = client

    def recommend_places(self, trends, user_interest):
        # 관광명소 추천 요청
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in recommending travel destinations based on user interests and trends."},
                {"role": "user", "content": f"Recommend tourist attractions based on these trends: {trends}. User interest: {user_interest}"}
            ],
            model="gpt-4",
            temperature=0.5
        )
        place_recommendations = response.choices[0].message.content
        return place_recommendations

# 에이전트 인스턴스 생성 및 MultiAgent에 등록
trend_agent = TrendAgent(client)
tourist_agent = TouristAgent(client)

multi_agent.register("TrendAgent", trend_agent)
multi_agent.register("TouristAgent", tourist_agent)

# API 엔드포인트 정의
@app.route('/generate', methods=['POST'])
def generate():
    context = request.json.get('context')
    user_interest = request.json.get('user_interest')

    try:
        # 트렌드 에이전트로 트렌드 요약 생성
        trend_summary = trend_agent.analyze_trends(context)

        # 관광명소 에이전트로 관광명소 추천 생성
        place_recommendations = tourist_agent.recommend_places(trend_summary, user_interest)

        # 종합 정보 생성
        answer = {
            "trend_summary": trend_summary,
            "place_recommendations": place_recommendations
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
