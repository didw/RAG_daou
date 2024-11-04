import requests
import os
import pandas as pd

# LoadBalancer의 외부 URL로 설정하며 포트를 명시하지 않음 (기본 포트 80 사용)
QUERY_URL = os.getenv('QUERY_URL', 'http://k8s-default-apigatew-b334012b26-af978099376a3e4b.elb.ap-northeast-2.amazonaws.com/query')

def send_query(text):
    response = requests.post(QUERY_URL, json={'text': text})
    if response.status_code != 200:
        print(f"Query Error: {response.text}")
        return None

    answer = response.json().get('answer')
    return answer


def main():
    queries = [
        "올 가을 유행하는 뷰티 관련 키워드가 무엇인지 알려주세요.",
        "최근 넷플릭스 화제작 ‘흑백요리사’가 트렌드에 어떤 영향을 미쳤는지 알려주세요.",
        "가을 꽃을 만끽할 수 있는 관광지는 어디가 좋을 지 추천해주세요."
    ]
    for query in queries:
        print(f"Query: {query}")
        answer = send_query(query)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
