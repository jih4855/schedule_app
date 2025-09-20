# 필요한 라이브러리 설치
# !pip install diffusers transformers accelerate

import torch
from diffusers import StableDiffusion3Pipeline

# 사용할 모델을 지정하여 파이프라인을 로드합니다.
# "stabilityai/stable-diffusion-3.5-medium"는 2.5B 파라미터의 효율적인 SD 3.5 모델입니다.
pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", torch_dtype=torch.bfloat16)

# GPU가 사용 가능하다면 GPU로 모델을 이동시킵니다.
pipe = pipe.to("mps" if torch.backends.mps.is_available() else "cpu")

# 생성할 이미지에 대한 텍스트 프롬프트를 작성합니다.
prompt = """
"""

# 파이프라인을 실행하여 이미지를 생성합니다. (SD 3.5용 파라미터 추가)
image = pipe(prompt, num_inference_steps=28, guidance_scale=3.5).images[0]  

# 생성된 이미지를 저장합니다.
image.save("image_test.png")