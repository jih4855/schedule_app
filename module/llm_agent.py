import ollama
import google.generativeai as genai
from openai import OpenAI
from module.memory import MemoryManager

class LLM_Agent:
    def __init__(self, model_name:str, provider:str='ollama', api_key:str=None, session_id:str ="default_session", max_history:int =10):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_key = api_key
        self.session_id = session_id
        self.max_history = max_history
        if self.provider not in ['ollama', 'genai', 'openai']:
            raise ValueError("Provider must be either 'ollama', 'genai' or 'openai'")

    def __call__(self, system_prompt:str, user_message:str, memory:bool=False, task:str=None, multi_agent_response:str=None) -> str:
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
                memory_manager = MemoryManager()
                history = memory_manager.get_history(self.session_id)
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

            # 한 번만 호출
            response = ollama.chat(model=self.model_name, messages=messages)
            # print(messages) # 디버깅용 출력
            # 메모리에 저장
            if memory:
                history.append({"role": "user", "content": full_context})
                history.append({"role": "assistant", "content": response["message"]["content"]})
                memory_manager.save_history(self.session_id, history)
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
                memory_manager = MemoryManager()
                history = memory_manager.get_history(self.session_id)
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
                memory_manager.save_history(self.session_id, history)
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
                memory_manager = MemoryManager()
                history = memory_manager.get_history(self.session_id)
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
                history.append({"role": "user", "content": full_context})
                history.append({"role": "assistant", "content": response.choices[0].message.content})
                memory_manager.save_history(self.session_id, history)
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response with OpenAI: {e}"


    def aggregate_responses(self, system_prompt:str, user_message:str, task:str=None, responses:list=None) -> str:
        
        # responses가 None일 경우 빈 리스트로 초기화
        responses = responses or []
        
        # 에이전트 메시지 구성
        agent_msgs = []
        for idx, resp in enumerate(responses):
            agent_msgs.append({"role": "user", "content": f"Agent {idx+1} response: {resp}"})
        # 최종 응답 생성
        final_response = self.__call__(system_prompt, user_message, task=task, multi_agent_response=agent_msgs)
        return final_response
    
    

class Multi_modal_agent(LLM_Agent):
    def __call__(self, system_prompt: str, user_message: str, image_path: str = None, **kwargs) -> str:
        """
        이미지 입력을 포함한 LLM 응답 생성. memory=True로 설정하면 대화 기록을 메모리에 저장하고 불러옴.
        Args:
            system_prompt (str): 시스템 프롬프트
            user_message (str): 사용자 메시지
            image_path (str, optional): 이미지 파일 경로
            **kwargs: LLM_Agent의 __call__ 메서드에 전달할 추가 인자들 (memory, task, multi_agent_response 등)
        Returns:
            str: LLM의 응답
        """
        try:
            if image_path:
                if self.provider == 'ollama':
                    # Ollama의 이미지 입력 형식에 맞게 메시지 구성
                    response = ollama.chat(
                        model=self.model_name,
                        messages=[{
                            'role': 'system',
                            'content': f'''당신은 이미지 분석 전문가입니다.
                                중요한 규칙:
                                1. 이미지가 업로드되지 않았거나 경로에 문제가 있다면 정확히 "이미지가 제공되지 않았거나 읽을 수 없습니다"라고 응답하세요.
                                2. 현재 모델이 이미지를 지원하지 않는다면 "현재 모델은 이미지 처리를 지원하지 않습니다. 멀티모달 모델을 사용해주세요"라고 응답하세요.
                                3. 이미지가 정상적으로 보이는 경우에만 구체적으로 분석하여 답변하세요.
                                사용자 요청: {system_prompt}'''
                        }, {
                            'role': 'user',
                            'content': f'{user_message}',
                            'images': [image_path]
                        }]
                    )
                    return response['message']['content']
                
                elif self.provider == 'genai':
                    # 새로운 genai 멀티모달 로직
                    import google.generativeai as genai
                    from PIL import Image
                    
                    genai.configure(api_key=self.api_key)
                    model = genai.GenerativeModel(self.model_name)
                    
                    # 이미지 로드
                    image = Image.open(image_path)
                    
                    # 프롬프트 구성
                    full_prompt = f"""당신은 이미지 분석 전문가입니다.
                    {system_prompt}
                    
                    사용자 요청: {user_message}"""
                    
                    # 멀티모달 생성
                    contents = [full_prompt, image]
                    response = model.generate_content(contents)
                    return response.text
                
                else:
                    raise ValueError("Image input is only supported with 'ollama' or 'genai' providers.")
            
            else:
                # 이미지가 없는 경우 부모 클래스 메서드 호출
                return super().__call__(system_prompt, user_message, **kwargs)
                
        except Exception as e:
            return f"Error generating response with multi-modal input: {e}"
