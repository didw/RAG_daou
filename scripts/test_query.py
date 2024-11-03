import requests
import os
import pandas as pd

# LoadBalancer의 외부 URL로 설정하며 포트를 명시하지 않음 (기본 포트 80 사용)
QUERY_URL = os.getenv('QUERY_URL', 'http://k8s-default-apigatew-b334012b26-af978099376a3e4b.elb.ap-northeast-2.amazonaws.com/query')

def query(text):
    response = requests.post(QUERY_URL, json={'text': text})
    if response.status_code != 200:
        print(f"Query Error: {response.text}")
        return None

    answer = response.json().get('answer')
    return answer


def main():
    text = "테스트를 위한 입력 문장입니다."
    answer = query(text)
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
