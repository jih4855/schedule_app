from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# 4비트 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# 모델 로드 (자동 4비트 양자화)
model = AutoModelForCausalLM.from_pretrained(
    "naver-hyperclovax/HyperCLOVAX-SEED-Think-14B",
    quantization_config=bnb_config,
    trust_remote_code=True
)