from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
import os
import torch
import uvicorn
from fastapi import FastAPI, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
from fastapi.responses import JSONResponse, StreamingResponse
import json
import json
import os
from transformers import TextStreamer  # 添加这个导入
import asyncio
from transformers import TextIteratorStreamer

# 定义请求体结构
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]  # 历史记录，以 role 和 content 对象列表的形式

app = FastAPI()


# 设置环境变量
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# 模型路径
MODEL_PATH = "/root/autodl-tmp/AUG/"

# 检查是否使用 GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    device_map="auto"  # 使用 accelerate 进行设备自动分配
).eval()  # 删除 .to(device) 调用

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
    
    gen_kwargs = {
        "max_new_tokens": 5000,
        "do_sample": True,
        "top_k": 1,
        "temperature": 0.7,
        "repetition_penalty": 1.1,
        "streamer": TextIteratorStreamer(tokenizer, skip_special_tokens=True)
    }
    
    async def response_generator():
        try:
            streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)
            gen_kwargs["streamer"] = streamer
            
            # 在后台线程中运行模型生成
            generation_task = asyncio.create_task(
                asyncio.to_thread(
                    model.generate,
                    **inputs,
                    **gen_kwargs
                )
            )
            
            # 逐个产出生成的token
            async for text in streamer:
                yield json.dumps({
                    "status": 200,
                    "data": {
                        "content": text,
                        "stop": False
                    }
                }, ensure_ascii=False) + "\n"
            
            # 发送结束标记
            yield json.dumps({
                "status": 200,
                "data": {
                    "content": "",
                    "stop": True
                }
            }, ensure_ascii=False)
            
            await generation_task  # 等待生成完成
            
        except Exception as e:
            yield json.dumps({
                "status": 500,
                "error": str(e)
            }, ensure_ascii=False)
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
    
# 代码内启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)
