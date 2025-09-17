import os
import sys

# Ensure module import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module.llm_agent import LLM_Agent


def test_aggregate_responses_passes_only_agent_messages(monkeypatch):
    captured = {}

    def fake_generate(self, system_prompt, user_message, memory=False, task=None, multi_agent_response=None):
        captured['system_prompt'] = system_prompt
        captured['user_message'] = user_message
        captured['task'] = task
        captured['multi_agent_response'] = multi_agent_response
        return "OK"

    monkeypatch.setattr(LLM_Agent, 'generate_response', fake_generate, raising=False)

    agent = LLM_Agent(model_name="dummy", provider='ollama', api_key=None, session_id="t1", max_history=5)
    out = agent.aggregate_responses(
        system_prompt="SYS",
        user_message="USER",
        task="REDUCE",
        responses=["R1", "R2"]
    )

    assert out == "OK"
    msgs = captured['multi_agent_response']
    assert isinstance(msgs, list)
    # Should not inject system/user again; only agent responses
    assert all(isinstance(m, dict) and m.get('role') == 'user' for m in msgs)
    assert "Agent 1 response" in msgs[0]['content']