from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from typing import List, Dict
from fastapi.responses import StreamingResponse
import json
import asyncio
from threading import Thread

# 定义请求体结构
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

app = FastAPI()

# 设置环境变量
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# 模型路径
MODEL_PATH = "/root/autodl-tmp/glm-4-9b-chat/"

# 检查是否使用 GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    device_map="auto"
).eval()

@app.post("/")
async def generate_response(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="消息列表不能为空")
    
    inputs = tokenizer.apply_chat_template(
        request.messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
        return_dict=True
    )
    
    inputs = {key: value.to(device) for key, value in inputs.items()}
    
    streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True, skip_prompt=True)
    gen_kwargs = {
        "max_new_tokens": 5000,
        "do_sample": True,
        "top_k": 1,
        "streamer": streamer
    }
    
    async def response_generator():
        try:
            # 在单独的线程中运行模型生成
            thread = Thread(target=model.generate, kwargs={**inputs, **gen_kwargs})
            thread.start()
            
            # 从streamer中获取生成的文本
            for text in streamer:
                if text:
                    yield json.dumps({
                        "status": 200,
                        "data": {
                            "content": text
                        }
                    }, ensure_ascii=False) + "\n"
            
        except Exception as e:
            error_response = {"status": 500, "error": str(e)}
            yield json.dumps(error_response, ensure_ascii=False)
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)