import streamlit as st
from stream.utils.uml import get_uml_diagram, get_diagram_type
from stream.components.editors.class_editor import render_class_diagram_editor
from stream.components.editors.usecase_editor import render_usecase_diagram_editor
from stream.components.editors.sequence_editor import render_sequence_diagram_editor

def render_uml_editor(code_key, message_idx):
    """渲染 UML 编辑器组件"""
    current_code = st.session_state[code_key]
    
    # 添加样式
    st.markdown("""
        <style>
        /* ===== 图像容器样式 ===== */
        div[data-testid="stImage"] {
            max-width: auto !important;
            margin: auto !important;
        }
        
        /* ===== 可展开面板样式 ===== */
        /* 面板容器 */
        div[data-testid="stExpander"] {
            background-color: var(--background-color) !important;  /* 使用系统背景色 */
            border: 1px solid var(--primary-color) !important;    /* 添加边框 */
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        /* 面板头部 */
        div[data-testid="stExpander"] > div:first-child {
            background-color: var(--primary-color-light) !important;  /* 使用浅色主题色 */
            border-radius: 4px 4px 0 0;
            color: var(--text-color) !important;                     /* 使用系统文字颜色 */
        }
        
        /* 面板内容区 */
        div[data-testid="stExpander"] > div:last-child {
            background-color: var(--background-color) !important;     /* 使用系统背景色 */
            border-radius: 0 0 4px 4px;
        }
        
        /* ===== 下载按钮样式 ===== */
        .download-button {
            display: inline-block;
            background-color: var(--primary-color) !important;        /* 使用系统主题色 */
            color: var(--background-color) !important;                /* 使用背景色作为文字颜色 */
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-align: center;
            margin-top: 10px;
            width: 120px;
            font-weight: bold;                                       /* 加粗文字 */
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);                 /* 添加文字阴影 */
            transition: all 0.3s ease;                               /* 添加过渡动画 */
        }
        
        /* 下载按钮悬停效果 */
        .download-button:hover {
            background-color: #4CAF50 !important;                    /* 使用浅绿色 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);                  /* 添加阴影 */
            transform: translateY(-1px);                             /* 轻微上浮效果 */
        }
        
        /* ===== 文本区域样式 ===== */
        .stTextArea textarea {
            font-family: monospace;                                   /* 等宽字体 */
            font-size: 14px;
            line-height: 1.4;
            background-color: var(--background-color) !important;     /* 使用系统背景色 */
            color: var(--text-color) !important;                     /* 使用系统文字颜色 */
            border: 1px solid var(--primary-color) !important;       /* 添加边框 */
        }
        
        /* ===== 标签页样式 ===== */
        /* 标签页列表 */
        div[data-baseweb="tab-list"] {
            background-color: var(--background-color) !important;     /* 使用系统背景色 */
            border-bottom: 2px solid var(--primary-color) !important; /* 添加底部边框 */
        }
        
        /* 标签页面板 */
        div[data-baseweb="tab-panel"] {
            background-color: var(--background-color) !important;     /* 使用系统背景色 */
            padding: 1rem;                                           /* 添加内边距 */
            border: 1px solid var(--primary-color) !important;       /* 添加边框 */
            border-top: none;                                        /* 移除顶部边框 */
        }

        /* ===== 按钮样式 ===== */
        /* 所有类型的按钮通用样式 */
        button[kind] {
            background-color: var(--primary-color) !important;        /* 使用系统主题色 */
            color: var(--background-color) !important;               /* 使用背景色作为文字颜色 */
            font-weight: bold !important;                            /* 加粗文字 */
            text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;      /* 添加文字阴影 */
            transition: all 0.3s ease !important;                    /* 添加过渡动画 */
        }

        /* 按钮悬停效果 */
        button[kind]:hover {
            background-color: #4CAF50 !important;                    /* 使用浅绿色 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;       /* 添加阴影 */
            transform: translateY(-1px) !important;                  /* 轻微上浮效果 */
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建两列布局
    edit_col, preview_col = st.columns([0.5, 0.5])
    
    with edit_col:
        st.subheader("UML 编辑器")
        
        # 为每个组件创建唯一的 key
        edit_mode_key = f"edit_mode_{code_key}_{message_idx}"
        
        # 添加编辑模式切换
        edit_mode = st.radio(
            "编辑模式",
            ["可视化编辑", "代码编辑"],
            horizontal=True,
            key=edit_mode_key
        )
        
        if edit_mode == "代码编辑":
            # 为文本区域添加唯一的 key
            text_area_key = f"text_area_{code_key}_{message_idx}"
            new_code = st.text_area(
                "PlantUML 代码", 
                current_code, 
                height=400,
                key=text_area_key
            )
            if new_code != current_code:
                st.session_state[code_key] = new_code
                current_code = new_code
        else:
            # 可视化编辑器
            diagram_type = get_diagram_type(current_code)
            if diagram_type == "class":
                render_class_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "usecase":
                render_usecase_diagram_editor(code_key, message_idx, current_code)
            elif diagram_type == "sequence":
                render_sequence_diagram_editor(code_key, message_idx, current_code)
            else:
                st.warning("未识别的图表类型")
    
    with preview_col:
        st.subheader("预览")
        # 显示当前的 PlantUML 代码
        with st.expander("📝 查看 PlantUML 代码", expanded=False):
            st.code(current_code, language='java')
            
        # 显示图像预览
        diagram_data = get_uml_diagram(current_code)
        if diagram_data:
            st.image(diagram_data['url'], width=600)
            
            # 下载按钮
            download_filename = f"uml_diagram_{message_idx}.{diagram_data['format']}"
            download_link = f'''
            <div style="text-align: center;">
                <a href="data:image/{diagram_data["format"]};base64,{diagram_data["data"]}" 
                   download="{download_filename}">
                    <button class="download-button">下载图表</button>
                </a>
            </div>
            '''
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.error("生成UML图失败，请检查代码���法")