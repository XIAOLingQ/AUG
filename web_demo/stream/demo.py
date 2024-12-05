import asyncio
import streamlit as st
import uuid
import re
import httpx
import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stream.components.uml_editor import render_uml_editor

# Constants
DEFAULT_USER_ID = str(uuid.uuid4())
llm_serve_url = "http://36.50.226.35:33642"

if 'messages' not in st.session_state:
    st.session_state.messages = []

    

# 添加一个新的状态来追踪是否需要重置
if 'should_reset' not in st.session_state:
    st.session_state.should_reset = False

# 添加一个新的状态来追踪图表更新
if 'needs_update' not in st.session_state:
    st.session_state.needs_update = False

# Page config
st.set_page_config(page_title="Chat Application", layout="wide")

def reset_chat():
    """Reset chat history"""
    st.session_state.should_reset = True

def create_message_container(role, content, message_idx, is_new=False):
    """
    创建消息容器
    :param role: 角色（user/assistant）
    :param content: 消息内容
    :param message_idx: 消息索
    :param is_new: 是否是新消息，用于控制是否需要重新渲染
    """
    with st.chat_message(role):
        parts = re.split(r'(```[\s\S]*?```)', content, flags=re.DOTALL)
        
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            if stripped_part.startswith('```') and stripped_part.endswith('```'):
                unique_key = f"{role}_{message_idx}_{i}"
                code_key = f"code_{unique_key}"
                
                code = stripped_part.strip('`').strip()
                first_line = code.split('\n')[0] if '\n' in code else ''
                
                if first_line.lower() in ['plantuml', 'uml']:
                    code = '\n'.join(code.split('\n')[1:])
                    # 只在新消息时更新代码
                    if is_new:
                        st.session_state[code_key] = code
                    
                    if '@startuml' in code.lower() and '@enduml' in code.lower():
                        # 只在新消息时渲染编辑器
                        if is_new:
                            render_uml_editor(code_key, unique_key)
                        else:
                            # 对于旧消息，只显示代码
                            st.code(st.session_state.get(code_key, code), language='plantuml')
                else:
                    # 对于非UML代码块，直接显示
                    st.code(code, language=first_line.lower())
            else:
                if stripped_part:
                    st.markdown(stripped_part)

def create_empty_response_container():
    """创建一个空的响应容器并返回它"""
    # 只创建一个空的占位符，不创建聊天消息
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
                                            print(f"收到内容: {content}")
                                            full_content += content
                                            # 使用占位符更新内容
                                            message_placeholder.markdown(full_content + "▌")
                                            await asyncio.sleep(0.05)
                                            
                                    elif data.get('status') == 500:
                                        error_msg = data.get('error', '未知错误')
                                        print(f"服务器错误: {error_msg}")
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
    # 检查是否需要重置
    if st.session_state.should_reset:
        st.session_state.messages = []
        st.session_state.should_reset = False
    
    # 添加样式
    st.markdown("""
        <style>
        /* ===== 聊天输入框样式 ===== */
        /* 输入框容器：固定在底部，自适应主题背景色 */
        div[data-testid="stChatInput"] {
            position: fixed !important;          /* 固定定位 */
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
            border: 1px solid var(--primary-color) !important; /* 使用主题色作为边框 */
            border-radius: 4px !important;      /* 圆角边框 */
            color: var(--text-color) !important; /* 使用系统主题文字颜色 */
            font-size: 1rem !important;         /* 标准字体大小 */
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
            right: 140px !important;           /* 与重置���钮保持距离 */
            background-color: var(--primary-color) !important; /* 使用主题色 */
            border-radius: 4px !important;     /* 圆角 */
            transition: all 0.3s ease !important; /* 过渡动画 */
        }
        
        /* ===== 重置按钮样式 ===== */
        /* 次要按钮：固定在右下角，跟随主题 */
        button[kind="secondary"] {
            position: fixed !important;          /* 固定定位 */
            bottom: 16px !important;            /* 距底部距离 */
            right: 20px !important;             /* 右侧留白 */
            z-index: 999 !important;            /* 确保在最上层 */
            margin: 0 !important;               /* 清除外边距 */
            width: 100px !important;            /* 减小固宽度 */
            height: calc(1rem * 2 + 1.5em) !important; /* 与输入框等高 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
            border: 1px solid var(--primary-color) !important; /* 使用主题色边框 */
            color: var(--text-color) !important; /* 使用系统主题文字颜色 */
            border-radius: 4px !important;       /* 圆角 */
            transition: all 0.3s ease !important; /* 过渡动画 */
            min-width: 80px !important;          /* 最小宽度 */
            font-size: 0.9rem !important;        /* 稍微减小字 */
            padding: 0 8px !important;           /* 减小内边距 */
        }

        /* 重置按钮悬停效果 */
        button[kind="secondary"]:hover {
            background-color: var(--primary-color-light) !important; /* 使用浅色主题色 */
            border-color: var(--primary-color) !important;
        }

        /* 在小屏幕上调整布局 */
        @media (max-width: 768px) {
            div[data-testid="stChatInput"] {
                width: calc(100% - 120px) !important; /* 减小输入框宽度 */
                max-width: calc(100% - 120px) !important;
            }
            
            div[data-testid="stChatInput"] button {
                right: 110px !important;        /* 调整发送按钮位置 */
            }
            
            button[kind="secondary"] {
                width: 80px !important;         /* 更小的重置按钮 */
                right: 10px !important;         /* 减小右侧间距 */
            }
        }
        
        /* ===== 主要按钮样式 ===== */
        /* 生成UML按钮：使用主题色 */
        button[kind="primary"] {
            background-color: var(--primary-color) !important; /* 使用主题色 */
            border: none !important;              /* 无边框 */
            color: white !important;              /* 色文字 */
            padding: 0.5rem 1rem !important;      /* 内边距 */
            border-radius: 4px !important;        /* 圆角 */
            transition: all 0.3s ease !important; /* 颜色过动画 */
        }
        
        /* 主要按钮悬停效果 */
        button[kind="primary"]:hover {
            background-color: var(--primary-color-dark) !important; /* 使用深色主题色 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; /* 添加阴影 */
        }
        
        /* ===== 布局调整 ===== */
        /* 主容器：为固定元素预留空间 */
        section.main > div.block-container {
            padding-bottom: calc(2rem + 1.5em) !important; /* 为输入留出空间 */
            background-color: var(--background-color) !important; /* 使用系统主题背景色 */
        }

        /* ===== 欢迎页面样式 ===== */
        /* 大标题：AUG */
        .big-title {
            text-align: center;                   /* 居中对齐 */
            padding: 2rem 0;                      /* 上下内边距 */
            color: var(--primary-color);          /* 使用主题色 */
            font-size: 4rem;                      /* 大字体 */
            font-weight: bold;                    /*  */
            margin-top: 20vh;                     /* 顶部外边距 */
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2); /* 文字阴影 */
        }

        /* 副标题：AI UML Generator */
        .subtitle {
            text-align: center;                   /* 居中齐 */
            color: var(--text-color-secondary);   /* 使次要文字颜色 */
            font-size: 1.5rem;                    /* 中等字体 */
            margin-top: 1rem;                     /* 顶部外边距 */
        }
        </style>
    """, unsafe_allow_html=True)

    # 如果没有消息历史，显示大标题
    if not st.session_state.messages:
        st.markdown("""
            <div class="big-title">AUG</div>
            <div class="subtitle">Automantic UML Generator</div>
        """, unsafe_allow_html=True)
    else:
        # 显示所有历史消息
        for idx, message in enumerate(st.session_state.messages):
            create_message_container(message["role"], message["content"], idx)

    # 创建固定在底部输入区域
    with st.container():
        prompt = st.chat_input("在这里输入您的消息...")
        if st.button("置聊天", key="reset_button", type="secondary", on_click=reset_chat):
            pass

    if prompt:
        # 立即显示用户输入
        create_message_container("user", prompt, len(st.session_state.messages), True)
        
        # 添加到消息历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        messages_history = [
            {"role": "system", "content": "你是动化需求建模工具AUG，你的任务是根据用户输入的案例进行需求分析和使用plantuml代码进行需求建模。用户会让你对生成的plantuml根据五大标准进行评价打分"},
        ] + st.session_state.messages

        try:
            # 创建临时占位符用于流式显示
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
                # 将完整响应添加到消息历史
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                # 创建新的消息容器并渲染代码段
                create_message_container("assistant", final_response, len(st.session_state.messages)-1, True)
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