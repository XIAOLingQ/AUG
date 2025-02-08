import asyncio
import streamlit as st
import uuid
import re
import httpx
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stream.components.uml_editor import render_uml_editor

# Constants
DEFAULT_USER_ID = str(uuid.uuid4())
llm_serve_url = "http://36.50.226.35:17169"

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 添加一个新的状态来追踪是否需要重置
if 'should_reset' not in st.session_state:
    st.session_state.should_reset = False

# 添加一个新的状态来追踪图表更新
if 'needs_update' not in st.session_state:
    st.session_state.needs_update = False

# 添加一个新的状态变量
if 'show_export_form' not in st.session_state:
    st.session_state.show_export_form = False

# 获取图标文件的绝对路径
icon_path = os.path.join(os.path.dirname(__file__), "static", "images", "favicon.png")

# Page config
st.set_page_config(
    page_title="AUG - Automated UML Generation", 
    page_icon=icon_path,
    layout="wide"
)

def reset_chat():
    """Reset chat history and all UML related states"""
    st.session_state.should_reset = True
    st.session_state.messages = []  # 清除聊天记录
    
    # 清除所有与 UML 编辑器相关的 session state
    keys_to_delete = []
    for key in st.session_state.keys():
        # 添加 code_key 相关的匹配模式
        if any(key.startswith(prefix) for prefix in [
            "attr_",        # 属性相关
            "method_",      # 方法相关
            "modify_",      # 修改类相关
            "last_modified_", # 最后修改的类
            "usecase_",     # 用例图相关
            "actor_",       # Actor相关
            "relation_",    # 关系相关
            "participant_", # 时序图参与者相关
            "message_",     # 时序图消息相关
            "code_",        # 代码相关，修改为完整前缀
            "diagram_",     # 图表相关
            "text_area_",   # 文本区域相关
            "edit_mode_"    # 编辑模式相关
        ]) or "code_key" in key:  # 特别检查包含 code_key 的键
            keys_to_delete.append(key)
    
    # 删除收到的键
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

def create_message_container(role, content, message_idx):
    with st.chat_message(role):
        parts = re.split(r'(```[\s\S]*?```)', content, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            if stripped_part.startswith('```') and stripped_part.endswith('```'):
                code = stripped_part.strip('`').strip()
                first_line = code.split('\n')[0] if '\n' in code else ''
                
                if first_line.lower() in ['plantuml', 'uml']:
                    # 提取实际的 UML 代码
                    code = '\n'.join(code.split('\n')[1:])
                    
                    # 根据图表类型生成不同的 key
                    diagram_type = "unknown"
                    if '@startuml' in code.lower() and '@enduml' in code.lower():
                        if 'class' in code.lower():
                            diagram_type = "class"
                        elif 'usecase' in code.lower() or 'actor' in code.lower():
                            diagram_type = "usecase"
                        elif 'participant' in code.lower() or '->' in code.lower():
                            diagram_type = "sequence"
                    
                    # 使用图表类型作为 key 的一部分
                    unique_key = f"{role}_{message_idx}_{i}_{diagram_type}"
                    code_key = f"code_{unique_key}"
                    
                    # 确保代码被正确存储在 session_state 中
                    if code_key not in st.session_state:
                        st.session_state[code_key] = code
                    
                    if '@startuml' in code.lower() and '@enduml' in code.lower():
                        render_uml_editor(code_key, message_idx)
            else:
                if stripped_part:
                    st.markdown(stripped_part)

def create_empty_response_container():
    """创建一个空的响应容器并返回它"""
    # 只创建一个空的占位符，不创建聊天息
    return st.empty()

async def get_bot_response(messages_history, placeholder):
    timeout = httpx.Timeout(30.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                llm_serve_url,
                json={'messages': messages_history},
                timeout=timeout
            )
            
            full_content = ""
            buffer = ""
            
            # 创建临时的聊天消息容器用于流式显示
            with placeholder.chat_message("assistant"):
                message_placeholder = st.empty()
                
                async for chunk in response.aiter_bytes():
                    try:
                        buffer += chunk.decode('utf-8')
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if not line.strip():
                                continue
                            
                            try:
                                data = json.loads(line)
                                if isinstance(data, dict):
                                    if data.get('status') == 200:
                                        content = data.get('data', {}).get('content', '')
                                        if content:
                                            full_content += content
                                            # 使用占位符更新内容
                                            message_placeholder.markdown(full_content + "▌")
                                            await asyncio.sleep(0.05)
                                            
                                    elif data.get('status') == 500:
                                        error_msg = data.get('error', '未知错误')
                                        print(f"服务错误: {error_msg}")
                                        message_placeholder.markdown(f"服务器错误: {error_msg}")
                                        return None, error_msg
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {str(e)}, 行内容: {line}")
                                continue
                    except UnicodeDecodeError as e:
                        print(f"解码错误: {str(e)}")
                        continue
                
                # 最后一次更新，移除光标
                message_placeholder.markdown(full_content)
                await asyncio.sleep(0.1)  # 短暂延迟确保最后的内容显示完成
                return full_content, None
                    
        except Exception as e:
            print(f"API请求错误: {str(e)}")
            with placeholder.chat_message("assistant"):
                st.error(f"发生错误: {str(e)}")
            return None, str(e)

def main():
    # 在 header 区域添加按钮
    with st.container():
        st.button("Submit Chat", key="submit_chat_button", type="primary", 
                 on_click=lambda: st.session_state.update({"show_export_form": True}))
    

    # 添加样式
    st.markdown("""
        <style>

        button[data-testid="submit_chat_button"] {
            position: relative !important;
            top: auto !important;
            right: auto !important;
            width: 120px !important;
            background-color: var(--primary-color) !important;
            color: green !important;
            border: none !important;
            border-radius: 4px !important;
            margin-top: 1rem !important;
        }
                        

        

        /* 提交对话按钮悬停效果 */
        button[data-testid="submit_chat_button"]:hover {
            background-color: var(--primary-color-dark) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }


        /* ===== 聊天输入框样式 ===== */
        /* 输入框容器：固定在底部，自适应主题背景色 */
        div[data-testid="stChatInput"] {
            position: fixed !important;          /* 定定位 */
            bottom: 16px !important;               /* 贴底部 */
            left: 20px !important;              /* 左侧留白 */
            padding: 0 !important;              /* 移除内距使容器与输入框大小一致 */
            width: calc(100% - 160px) !important; /* 宽度计算，预留更多重置按钮空间 */
            z-index: 999 !important;            /* 确保在最上层 */
            background-color: transparent !important; /* 透明背景，继承系统主题 */
            max-width: calc(100% - 160px) !important; /* 最大宽度限制 */
        }
        
        /* 输入框本身：继承系统主题色 */
        div[data-testid="stChatInput"] input {
            width: calc(100% - 20px) !important; /* 输入框宽留发送按钮空间 */
            height: 100% !important;            /* 占满容器高度 */
            padding: 1rem !important;           /* 统一的内边距 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
            border: 1px solid var(--primary-color) !important; /* 用主题色作为边框 */
            border-radius: 4px !important;      /* 圆角边框 */
            color: var(--text-color) !important; /* 使用系统主题文字颜色 */
            font-size: 1rem !important;         /* 标字体大小 */
            line-height: 1.5 !important;        /* 行高 */
            transition: all 0.3s ease !important; /* 平滑过渡效果 */
            margin-right: 20px !important;      /* 与发送按钮的间距 */
        }

        /* 输入框聚焦时的样式 */
        div[data-testid="stChatInput"] input:focus {
            outline: none !important;           /* 移除默认聚焦轮廓 */
            border-color: var(--primary-color) !important; /* 用主题色 */
            box-shadow: 0 0 0 2px var(--primary-color-light) !important; /* 主题色阴影 */
        }

        /* 发送按钮容器 */
        div[data-testid="stChatInput"] button {
            right: 140px !important;           /* 与重置按钮保��距离 */
            background-color: var(--primary-color) !important; /* 使用主题色 */
            border-radius: 4px !important;     /* 圆角 */
            transition: all 0.3s ease !important; /* 过渡动画 */
        }
        
        /* ===== 重置按钮样式 ===== */
        /* 次要按钮：固定在右下角，跟主题 */
        button[kind="secondary"] {
            position: fixed !important;
            bottom: 16px !important;
            right: 0 !important;
            z-index: 999 !important;
            margin: 0 !important;
            width: 120px !important;
            background-color: #262730 !important;
            border: 1px solid #4a4a4a !important;
            color: white !important;
            background-color: #0E1117 !important;
        }

        /* 重置按钮悬停效果 */
        button[kind="secondary"]:hover {
            background-color: #4CAF50 !important;  /* 绿色背景 */
            color: #FFD700 !important;  /* 保持金黄色文字 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }

        /* 在小屏幕上调整布局 */
        @media (max-width: 768px) {
            div[data-testid="stChatInput"] {
                width: calc(100% - 120px) !important; /* 减小输入框��度 */
                max-width: calc(100% - 120px) !important;
            }
            
            div[data-testid="stChatInput"] button {
                right: 110px !important;        /* 调整发送按钮位置 */
            }
            
            button[kind="secondary"] {
                width: 80px !important;         /* 更小的置按钮 */
                right: 10px !important;         /* 减小右侧间距 */
            }
        }
        
        /* 主要按钮悬停效果 */
        button[kind="primary"]:hover {
            background-color: var(--primary-color-dark) !important; /* 使用深色主题色 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; /* 添加阴影 */
        }
        
        /* ===== 布局调整 ===== */
        /* 主容器：为固定元素预留 */
        section.main > div.block-container {
            padding-bottom: calc(2rem + 1.5em) !important; /* 为输入留出空间 */
            background-color: var(--background-color) !important; /* 使用系统主题景色 */
        }

        /* ===== 欢迎页面样式 ===== */
        /* 大标题：AUG */
        .big-title {
            text-align: center;                   /* 居中对齐 */
            padding: 2rem 0;                      /* 上下内边距 */
            color: var(--primary-color);          /* 使用主题色 */
            font-size: 4rem;                      /* 大字体 */
            font-weight: bold;                    /*  */
            margin-top: 17vh;                     /* 顶部外边距 */
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2); /* 文字阴影 */
        }

        /* 副标题：AI UML Generator */
        .subtitle {
            text-align: center;                   /* 居中齐 */
            color: var(--text-color-secondary);   /* 使次要文字颜色 */
            font-size: 1.5rem;                    /* 中等字体 */
            margin-top: 1rem;                     /* 顶部外边距 */
        }

        /* ===== 导出按钮样式 ===== */
        button[data-testid="export_button"] {
            position: fixed !important;
            top: 16px !important;
            left: 16px !important;
            z-index: 999 !important;
            margin: 0 !important;
            width: 120px !important;
            background-color: #262730 !important;
            border: 1px solid #4a4a4a !important;
            color: white !important;
            background-color: #0E1117 !important;
        }

        /* 导出按钮悬停效果 */
        button[kind="primary"]:hover {
            background-color: var(--primary-color-dark) !important; /* 深色主题 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; /* 添加阴影 */
            transform: translateY(-1px) !important;  /* 悬停效果 */
        }

        
        /* 导出表单样式 - 统一使用深色题 */
        .stForm {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgb(14, 17, 23) !important;  /* 深色背景 */
            color: rgb(255, 255, 255) !important;  /* 白色文字 */
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid var(--primary-color) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            width: 80%;
            max-width: 600px;
        }

        /* 表单内部元素样式 */
        .stForm input, .stForm textarea {
            background-color: rgb(28, 32, 40) !important;  /* 深色输入框 */
            color: rgb(255, 255, 255) !important;  /* 白色文字 */
            border-color: var(--primary-color) !important;
            caret-color: rgb(255, 255, 255) !important;  /* 白色光标 */
        }

        .stForm label, .stForm .stMarkdown {
            color: rgb(255, 255, 255) !important;  /* 白色文字 */
        }

        /* 表单按钮样式 */
        .stForm button {
            background-color: rgb(28, 32, 40) !important;  /* 深色按钮背景 */
            color: rgb(255, 255, 255) !important;  /* 白��文字 */
            border-color: var(--primary-color) !important;
        }

        /* 按钮悬停效果 */
        .stForm button:hover {
            background-color: rgb(38, 42, 50) !important;  /* 稍浅一点的深色 */
            border-color: var(--primary-color) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 检查是否需要重置
    if st.session_state.should_reset:
        st.session_state.messages = []
        st.session_state.should_reset = False

    # 如果没有消息历史，显示大标题
    if not st.session_state.messages:
        st.markdown("""
            <div class="big-title">AUG</div>
            <div class="subtitle">Automated UML Generation</div>
        """, unsafe_allow_html=True)
    else:
        # 显示所历史消息
        for idx, message in enumerate(st.session_state.messages):
            create_message_container(message["role"], message["content"], idx)

    # 创建固定在底部的输入区域
    with st.container():
        prompt = st.chat_input("Input your message here...")
        if st.button("Reset Chat", key="reset_button", type="secondary", on_click=reset_chat):
            pass

    # 添加导出表单
    if st.session_state.show_export_form:
        with st.form(key="export_form"):
            st.subheader("Export Chat")
            instruction = st.text_area("Task Description", help="Please describe the task goal of this conversation")
            system = st.text_area("System Prompt", help="Please enter the system prompt")
            
            if st.form_submit_button("Confirm Export"):
                try:
                    # 读取现有数据以确定下一个ID
                    export_file = f"export_{datetime.now().strftime('%Y%m%d')}.json"
                    try:
                        with open(export_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                            if not isinstance(existing_data, list):
                                existing_data = []
                            next_id = len(existing_data)
                    except (FileNotFoundError, json.JSONDecodeError):
                        existing_data = []
                        next_id = 0
                    
                    # 获取消息历史，除了最后一组对话
                    history = []
                    for i in range(0, len(st.session_state.messages)-2, 2):
                        if i+1 < len(st.session_state.messages):
                            user_msg = st.session_state.messages[i]["content"]
                            ai_msg = st.session_state.messages[i+1]["content"]
                            history.append([user_msg, ai_msg])
                    
                    # 最后一组对话分别作为input和output
                    last_user_msg = ""
                    last_ai_msg = ""
                    if len(st.session_state.messages) >= 2:
                        last_user_msg = st.session_state.messages[-2]["content"]
                        last_ai_msg = st.session_state.messages[-1]["content"]
                    
                    export_data = {
                        "instruction": instruction,
                        "input": last_user_msg,  # 用户的最后一条消息
                        "output": last_ai_msg,   # AI的最后一条回复
                        "system": system,
                        "history": history,      # 之前的对话历史
                        "id": next_id
                    }
                    
                    existing_data.append(export_data)
                    
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=4)
                    
                    st.success("Chat has been exported successfully!")
                    st.session_state.show_export_form = False
                except Exception as e:
                    st.error(f"导出失败: {str(e)}")
            
            if st.form_submit_button("Cancel"):
                st.session_state.show_export_form = False

    if prompt:
        # 立即显示户输入
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 添加到消息历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        messages_history = [
            {"role": "system", "content": "Use clarifying dialogues, such as:User: Generate a Class Diagram.  Output: Please tell me more detailed information, such as attributes, methods, and so on. You are AUG, an automated requirements modeling tool. Your task is to assist users with requirements modeling. (Please use standard PlantUML language for drawing)."},
        ] + st.session_state.messages

        try:
            # 显示加载状态
            with st.spinner('正在思考中...'):
                # 创建时占位符用于流式显示
                temp_placeholder = create_empty_response_container()
                
                async def run_conversation():
                    try:
                        response, error = await get_bot_response(messages_history, temp_placeholder)
                        return response, error
                    except Exception as e:
                        return None, f"处理响应时出错: {str(e)}"

                # 运行异步任务获取完整响应
                final_response, error = asyncio.run(run_conversation())
                
                
                # 清除临时占位符
                temp_placeholder.empty()
                
                if final_response:
                    print(f"收到完整响应: {final_response}")
                    # 将完整响应添到消息历史
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                    # 创建新的消息容器并渲染代码段
                    create_message_container("assistant", final_response, len(st.session_state.messages)-1)
                elif error:
                    st.error(f"Error: {error}")

        except Exception as e:
            st.error(f"Error getting response from API: {str(e)}")

    # 添加处理编辑器消息的 JavaScript
    st.markdown("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'uml-export') {
            // 更新编辑区域的内容
            const textArea = document.querySelector('textarea');
            if (textArea) {
                textArea.value = event.data.content;
                textArea.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()