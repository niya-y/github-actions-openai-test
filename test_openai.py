import os
from openai import OpenAI

# 환경 변수에서 가져오기

client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# 간단한 질문 보내기
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "user", "content": "여보세요, 나야. 거기 잘 지내니?"}
    ],
)

# 결과 출력
print(f"응답: {response.choices[0].message}")
