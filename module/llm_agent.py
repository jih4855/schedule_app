import ollama
import google.generativeai as genai
from openai import OpenAI
from module.memory import MemoryManager

class LLM_Agent:
    def __init__(self, model_name:str, provider:str='ollama', api_key:str=None, session_id:str ="default_session", max_history:int =10):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_key = api_key
        self.memory_manager = MemoryManager()
        self.session_id = session_id
        self.max_history = max_history
        if self.provider not in ['ollama', 'genai', 'openai']:
            raise ValueError("Provider must be either 'ollama', 'genai' or 'openai'")

    def generate_response(self, system_prompt:str, user_message:str, memory:bool=False, task:str=None, multi_agent_response:str=None) -> str:
        """
        LLM 응답 생성. memory=True로 설정하면 대화 기록을 메모리에 저장하고 불러옴.
        Args:
            system_prompt (str): 시스템 프롬프트
            user_message (str): 사용자 메시지
            memory (bool): 메모리 기능 활성화 여부
            task (str, optional): 추가 작업 설명
            multi_agent_response (str, optional): 다른 에이전트의 응답
        Returns:
            str: LLM의 응답
        """

        if not system_prompt or not user_message:
            raise ValueError("Both system_prompt and user_message must be provided.")
        try:
            if self.provider == 'ollama':
                return self._generate_ollama_response(system_prompt, user_message, memory, task, multi_agent_response)
            elif self.provider == 'genai':
                return self._generate_genai_response(system_prompt, user_message, memory, task, multi_agent_response)
            elif self.provider == 'openai':
                return self._generate_openai_response(system_prompt, user_message, memory, task, multi_agent_response)
            else:
                return "Unsupported provider."
        except Exception as e:
            return f"Error generating response: {e}"

    def _generate_ollama_response(self, system_prompt:str, user_message:str, memory:bool=False, task:str=None, multi_agent_response:str=None):
        try:
            # messages 리스트 먼저 구성
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
            
            messages.append({"role": "user", "content": full_context})

            # 한 번만 호출
            response = ollama.chat(model=self.model_name, messages=messages)
            # print(messages) # 디버깅용 출력
            # 메모리에 저장
            if memory:
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": response["message"]["content"]})
                self.memory_manager.save_history(self.session_id, history)
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating response with Ollama: {e}"


    def _generate_genai_response(self, system_prompt:str, user_message:str, memory:bool=False, task:str=None, multi_agent_response:str=None):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            # 모든 내용을 하나의 문자열로 결합
            combined_prompt = system_prompt
            
            history = []
            if memory:
                history = self.memory_manager.get_history(self.session_id)
                if self.max_history and len(history) > self.max_history:
                    history = history[-self.max_history:]
                for msg in history:
                    combined_prompt += f"\n\n이전 대화 기록:\n{msg['role']}: {msg['content']}"

            if user_message:
                combined_prompt += f"\n\n{user_message}"
            if task:
                combined_prompt += f"\n\n작업: {task}"
            if multi_agent_response:
                combined_prompt += f"\n\n다른 에이전트의 응답: {str(multi_agent_response)}"

            # 문자열 하나만 전달!
            response = model.generate_content(combined_prompt)            
            # 메모리에 저장
            if memory:
                history.append({"role": "user", "content": combined_prompt})
                # 응답은 아직 없으므로 빈 문자열로 저장
                history.append({"role": "assistant", "content": response.text})
                self.memory_manager.save_history(self.session_id, history)
            return response.text
        
        except Exception as e:
            return f"Error generating response with GenAI: {e}"

    def _generate_openai_response(self, system_prompt, user_message, memory=False, task=None, multi_agent_response=None) -> str:
        try:
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
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": response.choices[0].message.content})
                self.memory_manager.save_history(self.session_id, history)
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response with OpenAI: {e}"

    def aggregate_responses(self, system_prompt:str, user_message:str, task:str=None, responses:list=None) -> str:
        # 에이전트 응답만 메시지로 구성(중복 system/user 방지)
        agent_msgs = []
        for idx, resp in enumerate(responses or []):
            agent_msgs.append({"role": "user", "content": f"Agent {idx+1} response: {resp}"})
        
        # 최종 메시지를 생성 (system/user는 generate_response에서 조립)
        final_response = self.generate_response(system_prompt, user_message, task=task, multi_agent_response=agent_msgs)
        return final_response

    # 호환용 별칭: 기존 문서/예제에서 사용한 이름을 지원
    def multi_agent_interaction(self, system_prompt:str, user_message:str, task:str=None, responses:list=None) -> str:
        """
        Scatter–Gather 스타일의 응답 집계. responses에는 개별 에이전트 응답 문자열 리스트를 전달.
        내부적으로 aggregate_responses로 위임.
        """
        if responses is None:
            responses = []
        return self.aggregate_responses(system_prompt, user_message, task=task, responses=responses)