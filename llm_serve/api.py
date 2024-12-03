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
    }
    
    async def response_generator():
        try:
            with torch.no_grad():
                input_length = inputs["input_ids"].shape[1]
                output = model.generate(**inputs, **gen_kwargs)[0]
                new_tokens = output[input_length:]
                response = tokenizer.decode(new_tokens, skip_special_tokens=True)
                
                yield json.dumps({
                    "status": 200,
                    "data": {
                        "content": response.strip()
                    }
                }, ensure_ascii=False)  # 确保正确编码
        except Exception as e:
            error_response = {"status": 500, "error": str(e)}
            yield json.dumps(error_response, ensure_ascii=False)
    
    return StreamingResponse(
        response_generator(),
        media_type="application/json"
    )
    
# 代码内启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6006)
