import streamlit as st
from stream.utils.uml import (
    get_uml_diagram, 
    create_sequence_template, 
    get_existing_participants,
    get_name_mapping
)

def render_sequence_diagram_editor(code_key, message_idx, current_code):
    """渲染时序图编辑器"""
    # 如果是新代码，使用模板初始化
    if not current_code or '@startuml' not in current_code:
        current_code = create_sequence_template()
        st.session_state[code_key] = current_code

    # 参与者操作
    with st.expander("👥 参与者操作", expanded=False):
        tabs = st.tabs(["添加参与者", "删除参与者"])
        with tabs[0]:
            render_add_participant(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_participant(code_key, message_idx, current_code)
    
    # 消息操作
    with st.expander("💬 消息操作", expanded=False):
        tabs = st.tabs(["添加消息", "删除消息"])
        with tabs[0]:
            render_add_message(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_message(code_key, message_idx, current_code)

def render_add_participant(code_key, message_idx, current_code):
    """渲染添加参与者界面"""
    participant_type = st.selectbox(
        "参与者类型",
        [
            ("participant", "普通参与者"),
            ("actor", "参与者"),
            ("boundary", "边界"),
            ("control", "控制器"),
            ("entity", "实体"),
            ("database", "数据库")
        ],
        format_func=lambda x: x[1],
        key=f"participant_type_{message_idx}"
    )
    
    participant_name = st.text_input("参与者名称", key=f"participant_name_{message_idx}")
    description = st.text_area(
        "描述 (可选)", 
        height=100,
        key=f"participant_desc_{message_idx}"
    )
    
    if st.button("添加参与者", key=f"add_participant_{message_idx}", type="primary"):
        if not participant_name:
            st.error("请输入参与者名称")
            return

        lines = current_code.split('\n')
        participant_str = f'\n{participant_type[0]} "{participant_name}"'
        if description.strip():
            participant_str += f' as {participant_name.replace(" ", "_")}\n'
            participant_str += f'note over {participant_name.replace(" ", "_")}: {description}\n'
        else:
            participant_str += '\n'
        
        insert_pos = next((i for i, line in enumerate(lines) 
            if '@enduml' in line.lower()), len(lines)-1)
        lines.insert(insert_pos, participant_str)
        st.session_state[code_key] = '\n'.join(lines)
        st.success(f"参与者 '{participant_name}' 已添加")
        st.rerun()

def render_delete_participant(code_key, message_idx, current_code):
    """渲染删除参与者界面"""
    participants = get_existing_participants(current_code)
    if participants:
        participant_to_delete = st.selectbox(
            "选择要删除的参与者",
            options=[p[0] for p in participants],
            format_func=lambda x: f"{x} ({dict(participants)[x]})",
            key=f"delete_participant_{message_idx}"
        )
        
        if st.button("删除参与者", key=f"delete_participant_btn_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            new_lines = []
            skip_note = False
            for line in lines:
                line_stripped = line.strip()
                # 跳过参与者定义
                if any(f'{ptype} "{participant_to_delete}"' in line_stripped 
                      for ptype, _ in participants):
                    continue
                # 跳过注释
                if line_stripped.startswith('note over') and participant_to_delete.replace(" ", "_") in line_stripped:
                    skip_note = True
                    continue
                if skip_note and ':' in line_stripped:
                    skip_note = False
                    continue
                # 跳过相关消息
                if participant_to_delete.replace(" ", "_") in line_stripped and ('->' in line_stripped or '<-' in line_stripped):
                    continue
                new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"参与者 '{participant_to_delete}' 及其相关消息已被删除")
            st.rerun()
    else:
        st.info("没有可删除的参与者")

def render_add_message(code_key, message_idx, current_code):
    """渲染添加消息界面"""
    name_map = get_name_mapping(current_code)  # 获取名称映射
    existing_participants = get_existing_participants(current_code)
    if existing_participants:
        participant_names = [p[0] for p in existing_participants]  # 使用原始名称
        
        source = st.selectbox(
            "发送者",
            options=participant_names,
            key=f"source_{message_idx}"
        )
        
        message_type = st.selectbox(
            "消息类型",
            [
                ("->", "同步消息"),
                ("-->", "异步消息"),
                ("->>", "同步响应"),
                ("-->>", "异步响应"),
                ("->o", "丢失消息"),
                ("->x", "销毁消息")
            ],
            format_func=lambda x: x[1],
            key=f"message_type_{message_idx}"
        )
        
        target = st.selectbox(
            "接收者",
            options=participant_names,
            key=f"target_{message_idx}"
        )
        
        message_text = st.text_input("消息内容", key=f"message_text_{message_idx}")
        
        # 激活/停用选项
        activate = st.checkbox("激活接收者", key=f"activate_{message_idx}")
        deactivate = st.checkbox("停用接收者", key=f"deactivate_{message_idx}")
        
        if st.button("添加消息", key=f"add_message_{message_idx}", type="primary"):
            if not message_text:
                st.error("请输入消息内容")
                return

            lines = current_code.split('\n')
            message_lines = []
            
            # 获取源和目标的别名（如果有）
            source_alias = next((alias for alias, name in name_map.items() if name == source), source)
            target_alias = next((alias for alias, name in name_map.items() if name == target), target)
            
            if activate:
                message_lines.append(f'activate "{target_alias}"')
            
            message_lines.append(f'"{source_alias}" {message_type[0]} "{target_alias}": {message_text}')
            
            if deactivate:
                message_lines.append(f'deactivate "{target_alias}"')
            
            insert_pos = next(i for i, line in enumerate(lines) 
                if '@enduml' in line.lower())
            lines[insert_pos:insert_pos] = message_lines
            
            st.session_state[code_key] = '\n'.join(lines)
            st.success("消息已添加")
            st.rerun()

def render_delete_message(code_key, message_idx, current_code):
    """渲染删除消息界面"""
    name_map = get_name_mapping(current_code)  # 获取名称映射
    messages = []
    lines = current_code.split('\n')
    
    # 创建反向映射（原始名称到别名）
    reverse_map = {v: k for k, v in name_map.items()}
    
    for line in lines:
        line_stripped = line.strip()
        if any(arrow in line_stripped for arrow in ['->', '-->', '->>', '-->>>', '->o', '->x']):
            if ':' in line_stripped:  # 确保是消息行
                # 解析消息行
                parts = line_stripped.split(':')
                message_part = parts[0]
                content_part = ':'.join(parts[1:])
                
                # 提取源和目标
                message_parts = message_part.split()
                if len(message_parts) >= 3:
                    source = message_parts[0].strip('"')
                    arrow = message_parts[1]
                    target = message_parts[2].strip('"')
                    
                    # 使用原始名称（如果有映射）
                    source_display = name_map.get(source, source)
                    target_display = name_map.get(target, target)
                    
                    # 构建显示用的消息
                    display_message = f'"{source_display}" {arrow} "{target_display}"{content_part}'
                    messages.append((display_message, line_stripped))
    
    if messages:
        message_to_delete = st.selectbox(
            "选择要删除的消息",
            options=[m[0] for m in messages],
            key=f"delete_message_{message_idx}",
            format_func=lambda x: x.replace('->', '→')
                                  .replace('-->', '⇢')
                                  .replace('->>', '⇒')
                                  .replace('-->>>', '⇛')
                                  .replace('->o', '→○')
                                  .replace('->x', '→×')
                                  .replace('"', '')  # 移除显示中的引号
        )
        
        if st.button("删除消息", key=f"delete_message_btn_{message_idx}", type="primary"):
            # 找到对应的原始行进行删除
            original_line = next(m[1] for m in messages if m[0] == message_to_delete)
            new_lines = [line for line in lines if line.strip() != original_line]
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success("消息已删除")
            st.rerun()
    else:
        st.info("没有可删除的消息")