from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from typing import List, Dict, AsyncGenerator
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

async def generate_stream(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True
        )
        
        inputs = {key: value.to(device) for key, value in inputs.items()}
        streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True, skip_prompt=True)
        
        # 设置生成参数
        gen_kwargs = {
            "max_new_tokens": 5000,
            "do_sample": True,
            "top_k": 1,
            "streamer": streamer
        }
        
        # 在后台线程中运行模型生成
        thread = Thread(target=model.generate, kwargs={**inputs, **gen_kwargs})
        thread.start()
        
        # 从streamer中获取生成的文本
        for text in streamer:
            if text:
                # 直接yield每个文本片段
                yield text
                
    except Exception as e:
        print(f"生成过程发生错误: {str(e)}")
        yield f"错误: {str(e)}"

@app.post("/")
async def generate_response(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="消息列表不能为空")
    
    print("收到请求，开始处理...")
    
    async def response_stream():
        async for text in generate_stream(request.messages):
            # 为每个文本片段创建JSON响应
            chunk = {
                "status": 200,
                "data": {
                    "content": text
                }
            }
            yield json.dumps(chunk, ensure_ascii=False) + "\n"
    
    return StreamingResponse(
        response_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)