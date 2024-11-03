import os
from flask import Flask, request, jsonify
from autogen import AssistantAgent, UserProxyAgent

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Create AssistantAgent instances
trend_agent = AssistantAgent(
    name="TrendAgent",
    system_message="You are a trend analysis expert focused on fashion, beauty, and food trends.",
    llm_config={"model": "gpt-4", "api_key": openai_api_key},
)

tourist_agent = AssistantAgent(
    name="TouristAgent",
    system_message="You are an expert in recommending travel destinations based on user interests and trends.",
    llm_config={"model": "gpt-4", "api_key": openai_api_key},
)

# Create a UserProxyAgent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False,
)

@app.route('/generate', methods=['POST'])
def generate():
    context = request.json.get('context')
    query = request.json.get('query')

    try:
        # Analyze trends
        user_proxy.initiate_chat(
            trend_agent,
            message=f"Analyze the following news data for trending topics: {context}"
        )
        trend_summary = user_proxy.last_message()["content"]

        # Recommend places
        user_proxy.initiate_chat(
            tourist_agent,
            message=f"Recommend tourist attractions based on these trends: {trend_summary}. query: {query}"
        )
        place_recommendations = user_proxy.last_message()["content"]

        # Combine results
        answer = {
            "trend_summary": trend_summary,
            "place_recommendations": place_recommendations
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
