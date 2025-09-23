---
layout: default
title: Dev Log
charset: utf-8
---

# 개발 로그 (Dev Log)

이 파일은 개발 과정에서 발견한 문제, 해결 방법, 시행착오, 팁 등을 기록하는 공간입니다.

---

## 2025-09-23: 코드 하이라이팅 문제 해결
- 증상: class="tok-kw"가 텍스트로 노출됨
- 원인: 정규식 치환 시 HTML 이스케이프 미흡
- 해결: escapeHtml 함수 개선, code-vscode 클래스 추가

- 발견: LLM_agent 모듈 메모리 관련 로직 변경 
- 해결 및 수정
    client = OpenAI(api_key=self.api_key)

                # messages 리스트 구성 (Ollama와 유사한 방식)
                messages = [
                    {"role": "system", "content": system_prompt}
                ]
                # 메모리 기능이 활성화된 경우, 이전 대화 기록을 불러와서 포함
                history = []
                if memory:
                    history = self.memory_manager.get_history(self.session_id)
                    if self.max_history and len(history) > self.max_history:
                        history = history[-self.max_history:]
                    messages.extend(history)
                
                # 모든 내용을 하나의 리스트로 결합
                full_context = user_message
                # task가 있으면 추가
                if task:
                    full_context += f' task: {str(task)}'
                # multi_agent_response가 있으면 추가
                if multi_agent_response:
                    full_context += f' 다른 에이전트의 응답: {str(multi_agent_response)}'
                # 메모리 기능이 활성화된 경우, 이전 대화 기록을 불러와서 포함
                messages.append({"role": "user", "content": full_context})

                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages
                )
                # 메모리에 저장
                if memory:
                    history.append({"role": "user", "content": user_message}) > user_message > full_context로 수정(유저 메시지만 저장하던 방식에서 llm에 전달된 모든 텍스트 저장)
                    history.append({"role": "assistant", "content": response.choices[0].message.content})
                    self.memory_manager.save_history(self.session_id, history)
                return response.choices[0].message.content
---

## 2025-09-22: 결과물 폴더 gitignore 처리
- 증상: AI 생성 결과물이 git에 계속 추가됨
- 해결: .gitignore에 폴더 추가, git rm --cached로 제거

---

## 2025-09-21: 정적 문서 구조 설계
- 목적: GitHub Pages에서 간단하게 볼 수 있는 문서 구조 필요
- 선택: index.html + scripts.js + styles.css 분리, Bootstrap 최소 사용
