import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from module.llm_agent import LLM_Agent
from Fast_api.schemas.schedule import ScheduleCreate
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List
import json
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from Fast_api.core.config import settings


def parse_natural_language_to_schedules(user_input: str) -> List[ScheduleCreate]:
    KST = ZoneInfo('Asia/Seoul')
    now = datetime.now(KST)
    model = settings.model_name
    provider = settings.provider
    api_key = settings.api_key

    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after_tomorrow = (now + timedelta(days=2)).strftime("%Y-%m-%d")

    system_prompt = "당신은 일정 파싱 전문가입니다. 자연어를 정확한 JSON 배열로 변환하세요."

    user_message = f"""
=== 현재 시간 정보 ===
현재 날짜 및 시간: {now.strftime("%Y-%m-%d %H:%M:%S")} ({now.strftime("%A")}, {weekday_kr}요일)
오늘: {now.strftime("%Y-%m-%d")}
내일: {tomorrow}
모레: {day_after_tomorrow}

=== 사용자 입력 ===
"{user_input}"

=== 출력 형식 ===
다음 JSON 배열 형식으로만 출력하세요:
[
  {{
    "title": "일정 제목",
    "description": "상세 설명 또는 null",
    "scheduled_at": "YYYY-MM-DDTHH:MM:SS"
  }}
]

=== 파싱 규칙 ===
1. 날짜: "오늘"→{now.strftime("%Y-%m-%d")}, "내일"→{tomorrow}, "모레"→{day_after_tomorrow}
2. 시간: "오전 9시"→09:00:00, "오후 2시"→14:00:00, 미지정 시→09:00:00
3. 여러 일정은 각각 별도 JSON 객체
4. scheduled_at는 반드시 ISO 8601 형식
5. JSON 배열만 출력, 다른 텍스트 금지
"""

    llm = LLM_Agent(model_name=model, provider=provider, api_key=api_key)

    # 타임아웃 1분 적용
    with ThreadPoolExecutor() as executor:
        future = executor.submit(llm, system_prompt, user_message)
        try:
            response = future.result(timeout=60)
        except FuturesTimeoutError:
            raise TimeoutError("LLM 응답 시간이 1분을 초과했습니다.")

    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    schedules_data = json.loads(cleaned)

    schedules = []
    for data in schedules_data:
        schedule = ScheduleCreate(
            title=data["title"],
            description=data.get("description"),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"])
        )
        schedules.append(schedule)

    return schedules