import streamlit as st
from stream.utils.uml import get_uml_diagram, create_usecase_template
import re


def get_existing_actors(code):
    """从 PlantUML 代码中提取现有的 Actor"""
    actors = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('actor '):
            actor_name = line.split(' ')[1].strip('"')
            actors.append(actor_name)
    return actors

def get_existing_usecases(code):
    """从 PlantUML 代码中提取现有的用例"""
    usecases = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('usecase '):
            # 提取双引号中的用例名称
            match = re.search(r'usecase\s*"([^"]+)"', line)
            if match:
                usecase_name = match.group(1)
                usecases.append(usecase_name)
    return usecases

def render_usecase_diagram_editor(code_key, message_idx, current_code):
    """渲染用例图编辑器"""
    # 如果是新代码，使用模板初始化
    if not current_code or '@startuml' not in current_code:
        current_code = create_usecase_template()
        st.session_state[code_key] = current_code

    # Actor 操作
    with st.expander("👤 Actor 操作", expanded=False):
        tabs = st.tabs(["添加 Actor", "删除 Actor"])
        with tabs[0]:
            render_add_actor(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_actor(code_key, message_idx, current_code)
    
    # 用例操作
    with st.expander("📌 用例操作", expanded=False):
        tabs = st.tabs(["添加用例", "删除用例"])
        with tabs[0]:
            render_add_usecase(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_usecase(code_key, message_idx, current_code)
    
    # 关系操作
    with st.expander("🔗 关系操作", expanded=False):
        tabs = st.tabs(["添加关系", "删除关系"])
        with tabs[0]:
            render_add_usecase_relation(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_usecase_relation(code_key, message_idx, current_code)


def render_add_actor(code_key, message_idx, current_code):
    """渲染添加 Actor 界面"""
    actor_name = st.text_input("Actor 名称", key=f"actor_name_{message_idx}")
    description = st.text_area(
        "描述 (可选)", 
        height=100,
        key=f"actor_desc_{message_idx}"
    )
    
    if st.button("添加 Actor", key=f"add_actor_{message_idx}", type="primary"):
        if not actor_name:
            st.error("请输入 Actor 名称")
            return

        lines = current_code.split('\n')
        actor_str = f'\nactor "{actor_name}"'
        if description.strip():
            actor_str += f' as {actor_name.replace(" ", "_")}\n'
            actor_str += f'note right of {actor_name.replace(" ", "_")}\n'
            actor_str += f'  {description}\n'
            actor_str += 'end note\n'
        else:
            actor_str += '\n'
        
        insert_pos = next((i for i, line in enumerate(lines) 
            if '@enduml' in line.lower()), len(lines)-1)
        lines.insert(insert_pos, actor_str)
        st.session_state[code_key] = '\n'.join(lines)
        st.success(f"Actor '{actor_name}' 已添加")
        st.rerun()

def render_add_usecase(code_key, message_idx, current_code):
    """渲染添加用例界面"""
    usecase_name = st.text_input("用例名称", key=f"usecase_name_{message_idx}")
    description = st.text_area(
        "描述 (可选)", 
        height=100,
        key=f"usecase_desc_{message_idx}"
    )
    
    if st.button("添加用例", key=f"add_usecase_{message_idx}", type="primary"):
        if not usecase_name:
            st.error("请输入用例名称")
            return

        lines = current_code.split('\n')
        usecase_str = f'\nusecase "{usecase_name}"'
        if description.strip():
            usecase_str += f' as {usecase_name.replace(" ", "_")}\n'
            usecase_str += f'note right of {usecase_name.replace(" ", "_")}\n'
            usecase_str += f'  {description}\n'
            usecase_str += 'end note\n'
        else:
            usecase_str += '\n'
        
        insert_pos = next((i for i, line in enumerate(lines) 
            if '@enduml' in line.lower()), len(lines)-1)
        lines.insert(insert_pos, usecase_str)
        st.session_state[code_key] = '\n'.join(lines)
        st.success(f"用例 '{usecase_name}' 已添加")
        st.rerun()

def render_delete_actor(code_key, message_idx, current_code):
    """渲染删除 Actor 界面"""
    existing_actors = get_existing_actors(current_code)
    if existing_actors:
        actor_to_delete = st.selectbox(
            "选择要删除的 Actor",
            options=existing_actors,
            key=f"delete_actor_{message_idx}"
        )
        
        if st.button("删除 Actor", key=f"delete_actor_btn_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            new_lines = []
            for line in lines:
                line_stripped = line.strip()
                if (not line_stripped.startswith(f'actor {actor_to_delete}') and 
                    not any(pattern.format(actor_to_delete) in line_stripped for pattern in [
                        '{}', '{} -->', '--> {}', '{} <|--', '--|> {}'
                    ])):
                    new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"Actor '{actor_to_delete}' 及其相关关系已被删除")
            st.rerun()
    else:
        st.info("没有可删除的 Actor")

def render_delete_usecase(code_key, message_idx, current_code):
    """渲染删除用例界面"""
    existing_usecases = get_existing_usecases(current_code)
    if existing_usecases:
        usecase_to_delete = st.selectbox(
            "选择要删除的用例",
            options=existing_usecases,
            key=f"delete_usecase_{message_idx}"
        )
        
        if st.button("删除用例", key=f"delete_usecase_btn_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            new_lines = []
            skip_note = False
            
            for line in lines:
                should_skip = False
                line_stripped = line.strip()
                
                # 检查是否是用例定义行
                if line_stripped.startswith('usecase '):
                    match = re.search(r'usecase\s*"([^"]+)"', line_stripped)
                    if match and match.group(1) == usecase_to_delete:
                        should_skip = True
                
                # 检查注释块
                if line_stripped.startswith('note ') and usecase_to_delete.replace(" ", "_") in line_stripped:
                    skip_note = True
                    should_skip = True
                elif skip_note:
                    if line_stripped == 'end note':
                        skip_note = False
                    should_skip = True
                
                # 检查关系行
                usecase_id = usecase_to_delete.replace(" ", "_")
                if any(pattern in line_stripped for pattern in [
                    f'{usecase_id} -->', 
                    f'--> {usecase_id}',
                    f'{usecase_id} .>',
                    f'.> {usecase_id}',
                    f'{usecase_id} --|>',
                    f'--|> {usecase_id}',
                    f'"{usecase_to_delete}"'
                ]):
                    should_skip = True
                
                if not should_skip:
                    new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"用例 '{usecase_to_delete}' 及其相关关系已被删除")
            st.rerun()
    else:
        st.info("没有可删除的用例")

def render_add_usecase_relation(code_key, message_idx, current_code):
    """渲染添加关系界面"""
    existing_actors = get_existing_actors(current_code)
    existing_usecases = get_existing_usecases(current_code)
    all_elements = existing_actors + existing_usecases
    
    if all_elements:
        source = st.selectbox(
            "源元素",
            options=all_elements,
            key=f"source_{message_idx}"
        )
        
        relation = st.selectbox(
            "关系类型", 
            [
                ("-->", "关联"),
                (".>", "包含/扩展"),
                ("--|>", "泛化")
            ],
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=f"relation_{message_idx}"
        )
        
        target = st.selectbox(
            "目标元素",
            options=all_elements,
            key=f"target_{message_idx}"
        )
        
        if relation[0] == ".>":
            stereotype = st.selectbox(
                "构造型",
                ["<<include>>", "<<extend>>"],
                key=f"stereotype_{message_idx}"
            )
        else:
            stereotype = None
        
        label = st.text_input("关系标签(可选)", key=f"label_{message_idx}")
        
        if st.button("添加关系", key=f"add_relation_{message_idx}", type="primary"):
            lines = current_code.split('\n')
            source_id = source.replace(" ", "_")
            target_id = target.replace(" ", "_")
            
            relation_str = f"{source_id} {relation[0]} {target_id}"
            if stereotype:
                relation_str += f" : {stereotype}"
            elif label.strip():
                relation_str += f" : {label}"
            relation_str += "\n"
            
            insert_pos = next(i for i, line in enumerate(lines) 
                if '@enduml' in line.lower())
            lines.insert(insert_pos, relation_str)
            st.session_state[code_key] = '\n'.join(lines)
            st.success("关系已添加")
            st.rerun()
    else:
        st.info("请先添加 Actor 或用例")

def render_delete_usecase_relation(code_key, message_idx, current_code):
    """渲染删除关系界面"""
    relations = []
    lines = current_code.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if any(rel in line_stripped for rel in [
            "-->", ".>", "--|>", "<<include>>", "<<extend>>"
        ]):
            relations.append(line_stripped)
    
    if relations:
        relation_to_delete = st.selectbox(
            "选择要删除的关系",
            options=relations,
            key=f"delete_relation_{message_idx}",
            format_func=lambda x: (x.replace(" --> ", " → ")     # 使用箭头表示关联
                                 .replace(" .> ", " ⊲ ")         # 使用三角形表示包含/扩展
                                 .replace(" --|> ", " ⯈ "))      # 使用箭头表示泛化
        )
        
        if st.button("删除关系", key=f"delete_relation_btn_{message_idx}", type="primary"):
            new_lines = [line for line in lines if line.strip() != relation_to_delete]
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success("关系已删除")
            st.rerun()
    else:
        st.info("没有可删除的关系")