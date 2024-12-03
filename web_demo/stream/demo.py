import asyncio
import streamlit as st
import uuid
from zhipuai import ZhipuAI
from plantuml import PlantUML
import re
import httpx
import json

llm_serve_url = "http://36.50.226.35:33642"
# Constants
plantuml = PlantUML(url='http://www.plantuml.com/plantuml/png/')
DEFAULT_USER_ID = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 添加一个新的状态来追踪是否需要重置
if 'should_reset' not in st.session_state:
    st.session_state.should_reset = False

# Page config
st.set_page_config(page_title="Chat Application", layout="wide")

def get_uml_diagram(uml_code):
    """Generate PlantUML diagram URL using public server"""
    try:
        url = plantuml.get_url(uml_code)
        return url
    except Exception as e:
        st.error(f"Error generating UML diagram: {str(e)}")
        return None

def reset_chat():
    """Reset chat history"""
    st.session_state.should_reset = True

def create_message_container(role, content, message_idx):
    with st.chat_message(role):
        parts = re.split(r'(```[\s\S]*?```)', content, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            if stripped_part.startswith('```') and stripped_part.endswith('```'):
                unique_key = f"{role}_{message_idx}_{i}"
                code_key = f"code_{unique_key}"
                editor_key = f"editor_{unique_key}"
                edit_mode_key = f"edit_mode_{unique_key}"
                
                if edit_mode_key not in st.session_state:
                    st.session_state[edit_mode_key] = False
                
                show_image_key = f"show_image_{unique_key}"
                if show_image_key not in st.session_state:
                    st.session_state[show_image_key] = True
                
                code = stripped_part.strip('`').strip()
                first_line = code.split('\n')[0] if '\n' in code else ''
                
                if first_line.lower() in ['plantuml', 'uml']:
                    code = '\n'.join(code.split('\n')[1:])  # 移除第一行
                
                if code_key not in st.session_state:
                    st.session_state[code_key] = code
                
                num_lines = len(code.split('\n'))
                height = max(min(num_lines * 24, 400), 100)
                
                with st.container():
                    col1, col2 = st.columns([0.7, 0.3])
                    
                    with col1:
                        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
                        edit_mode = st.toggle('编辑模式', key=edit_mode_key)
                        
                        if edit_mode:
                            st.markdown("""
                                <style>
                                .stTextArea textarea {
                                    font-family: monospace !important;
                                    line-height: 1.4 !important;
                                    padding: 10px !important;
                                }
                                </style>
                            """, unsafe_allow_html=True)
                            
                            edited_code = st.text_area(
                                "编辑代码",
                                value=st.session_state[code_key],
                                key=editor_key,
                                height=height
                            )
                        else:
                            st.code(st.session_state[code_key], language='java')
                            edited_code = st.session_state[code_key]
                        
                        if edited_code != st.session_state[code_key]:
                            st.session_state[code_key] = edited_code
                    
                    # 处理PlantUML图表
                    if first_line.lower() in ['plantuml', 'uml']:
                        with col2:
                            if '@startuml' in edited_code.lower() and '@enduml' in edited_code.lower():
                                st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
                                show_image = st.toggle('显示图片', key=show_image_key)
                                
                                if show_image:
                                    try:
                                        diagram_url = get_uml_diagram(edited_code)
                                        if diagram_url:
                                            st.image(diagram_url, use_container_width=True)
                                        else:
                                            st.error("生成UML图失败")
                                    except Exception as e:
                                        st.error(f"生成UML图错误: {str(e)}")
            else:
                if stripped_part:
                    st.markdown(stripped_part)

async def get_bot_response(messages_history):
    timeout = httpx.Timeout(30.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                llm_serve_url,
                json={'messages': messages_history},
                timeout=timeout
            )
            
            response_data = response.json()
            print(f"原始响应: {response_data}")
            
            if isinstance(response_data, dict) and response_data.get('status') == 200:
                content = response_data.get('data', {}).get('content', '')
                if content:
                    return content
            return "无法获取有效响应"
                        
        except Exception as e:
            print(f"API请求错误: {str(e)}")
            return f"发生错误: {str(e)}"

def main():
    # 检查是否需要重置
    if st.session_state.should_reset:
        st.session_state.messages = []
        st.session_state.should_reset = False
    
    # 添加样式
    st.markdown("""
        <style>
        /* 输入框容器样式 */
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 0 !important;
            left: 20px !important;
            padding: 1rem !important;
            width: calc(100% - 180px) !important;
            background-color: #0E1117 !important;
            z-index: 999 !important;
        }
        
        /* 输入框本身的样式 */
        div[data-testid="stChatInput"] input {
            background-color: #262730 !important;
            opacity: 1 !important;
            background-color: #0E1117 !important;
        }
        
        /* 重置按钮样式 - 只针对 secondary 类型的按钮 */
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
        
        /* 生成UML按钮样式 - 针对 primary 类型的按钮 */
        button[kind="primary"] {
            background-color: #1E88E5 !important;
            border: none !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            transition: background-color 0.3s !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #1976D2 !important;
        }
        
        /* 为底部固定元素留出空间 */
        section.main > div.block-container {
            padding-bottom: 80px !important;
            background-color: #0E1117 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 显示所有历史消息
    for idx, message in enumerate(st.session_state.messages):
        create_message_container(message["role"], message["content"], idx)

    # 创建固定在底部的输入区域
    with st.container():
        prompt = st.chat_input("在这里输入您的消息...")
        if st.button("重置聊天", key="reset_button", type="secondary", on_click=reset_chat):
            pass

    if prompt:
        # 直接添加到消息历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        messages_history = [
            {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"},
        ] + st.session_state.messages

        try:
            async def run_conversation():
                try:
                    response = await get_bot_response(messages_history)
                    return response
                except Exception as e:
                    return f"处理响应时出错: {str(e)}"

            # 运行异步任务
            final_response = asyncio.run(run_conversation())
            
            if final_response:
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            
            # 使用 rerun 重新加载页面
            st.rerun()

        except Exception as e:
            st.error(f"Error getting response from API: {str(e)}")

if __name__ == "__main__":
    main()