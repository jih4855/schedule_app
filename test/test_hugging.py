from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer

model_name = "naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to(device="mps")
processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# LLM Example
# It is recommended to use the chat template with HyperCLOVAX models.
# Using the chat template allows you to easily format your input in ChatML style.
llm_chat = [
        {"role": "system", "content": [{"type": "text", "text": "you are helpful assistant!"}]},
        {
                "role": "user", 
                "content": [{"type": "text", "text": "이미지에서 명확히 보이는 텍스트만 추출해주세요. 확실하지 않은 정보는 '불분명'이라고 표시해주세요."}, {"type": "image", "image": "스크린샷 2025-09-18 오전 4.10.01.png"}]
        }
]
model_inputs = processor.apply_chat_template(
        llm_chat, tokenize=True, return_dict=True, return_tensors="pt", add_generation_prompt=True
)
model_inputs = model_inputs.to(device="mps")

# Please adjust parameters like top_p appropriately for your use case.
output_ids = model.generate(
        **model_inputs,
        max_new_tokens=64,
        do_sample=True,
        top_p=0.6,
        temperature=0.5,
        repetition_penalty=1.0,
)
print("=" * 80)
print("LLM EXAMPLE")
print(processor.batch_decode(output_ids)[0])
print("=" * 80)