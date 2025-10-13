#!/usr/bin/env python3
"""
Rate Limit 테스트 스크립트
LLM 처리 시간을 고려한 비동기 테스트
"""
import requests
import time
from datetime import datetime

# 설정
API_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJcdWM4MTVcdWM3NzhcdWQ2YTgiLCJleHAiOjE3NjAyOTA4MDB9.1MNkp2ml1jW0dIcnnFvm_boUg7k36h1bQDSNyg2BbEo"
TOTAL_REQUESTS = 100

def test_rate_limit():
    """Rate Limit 테스트 실행"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    data = {"text": "테스트"}

    success_count = 0
    rate_limit_count = 0
    error_count = 0

    print("=" * 60)
    print(f"Rate Limit 테스트 시작 ({TOTAL_REQUESTS}회 연속 요청)")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    start_time = time.time()

    for i in range(1, TOTAL_REQUESTS + 1):
        try:
            response = requests.post(
                f"{API_URL}/api/schedules/parse-and-create",
                headers=headers,
                json=data,
                timeout=30
            )

            status = response.status_code

            if status == 429:
                print(f"요청 #{i}: HTTP {status} ⚠️ RATE LIMIT!")
                rate_limit_count += 1
                # Rate Limit 걸리면 잠시 대기
                if rate_limit_count == 1:
                    print("   → Rate Limit 처음 발생! 계속 테스트합니다...")
            elif status in [200, 201]:
                print(f"요청 #{i}: HTTP {status} ✅")
                success_count += 1
            else:
                print(f"요청 #{i}: HTTP {status} ❌")
                error_count += 1

        except requests.exceptions.Timeout:
            print(f"요청 #{i}: TIMEOUT ⏱️")
            error_count += 1
        except Exception as e:
            print(f"요청 #{i}: ERROR - {str(e)}")
            error_count += 1

    elapsed_time = time.time() - start_time

    print()
    print("=" * 60)
    print("테스트 완료!")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"소요 시간: {elapsed_time:.2f}초")
    print("=" * 60)
    print(f"✅ 성공:      {success_count:3d} / {TOTAL_REQUESTS}")
    print(f"⚠️  Rate Limit: {rate_limit_count:3d} / {TOTAL_REQUESTS}")
    print(f"❌ 에러:      {error_count:3d} / {TOTAL_REQUESTS}")
    print("=" * 60)

    # 결과 분석
    if rate_limit_count > 0:
        print(f"\n🎯 Rate Limit이 {success_count}번째 요청 이후 작동했습니다!")
    else:
        print(f"\n⚠️  {TOTAL_REQUESTS}번 요청 중 Rate Limit이 발생하지 않았습니다.")
        print("   → 처리 시간이 너무 길거나, 1분 이상 소요되어 제한이 초기화되었을 수 있습니다.")

if __name__ == "__main__":
    test_rate_limit()
