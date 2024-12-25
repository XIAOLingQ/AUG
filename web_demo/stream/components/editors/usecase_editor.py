import streamlit as st
from stream.utils.uml import get_uml_diagram, create_usecase_template, get_existing_actors, get_existing_usecases, get_name_mapping
import re
import time


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
            key=f"delete_usecase_{code_key}_{message_idx}"
        )
        
        if st.button(
            "删除用例", 
            key=f"delete_usecase_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            lines = current_code.split('\n')
            new_lines = []
            skip_note = False
            
            # 获取用例的所有可能标识符（原名和别名）
            usecase_aliases = set()
            usecase_aliases.add(usecase_to_delete)
            
            # 查找用例的别名
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_delete}"' in line_stripped and ' as ' in line_stripped:
                        alias = line_stripped.split(' as ')[-1].strip()
                        usecase_aliases.add(alias)
            
            # 添加带引号的版本
            quoted_aliases = {f'"{alias}"' for alias in usecase_aliases}
            usecase_aliases.update(quoted_aliases)
            
            for line in lines:
                line_stripped = line.strip()
                should_skip = False
                
                # 检查是否是用例定义行
                if line_stripped.startswith('usecase '):
                    if any(alias in line_stripped for alias in usecase_aliases):
                        should_skip = True
                        continue
                
                # 检查是否是关系行
                # 扩展关系检测模式，包括所有可能的关系形式
                if any(pattern in line_stripped for pattern in ['-->', '.>', '--|>', '-']):
                    # 提取关系的源和目标，支持更多格式
                    # 匹配以下格式：
                    # 1. "source" --> "target"
                    # 2. source --> target
                    # 3. actor --> UC1
                    relation_patterns = [
                        r'(["\w]+)\s*(?:-->|\.>|--\|>)\s*(["\w]+)',  # 标准格式
                        r'"([^"]+)"\s*(?:-->|\.>|--\|>)\s*"([^"]+)"',  # 带引号格式
                        r'(\w+)\s*(?:-->|\.>|--\|>)\s*(\w+)'  # 不带引号格式
                    ]
                    
                    for pattern in relation_patterns:
                        relation_match = re.match(pattern, line_stripped)
                        if relation_match:
                            source = relation_match.group(1).strip('"')
                            target = relation_match.group(2).strip('"')
                            
                            # 检查源或目标是否匹配要删除的用例
                            if (source in usecase_aliases or 
                                target in usecase_aliases or 
                                source.strip('"') in usecase_aliases or 
                                target.strip('"') in usecase_aliases):
                                should_skip = True
                                print(f"跳过关系行: {line_stripped}")  # 调试输出
                                break
                
                # 检查注释块
                if line_stripped.startswith('note '):
                    if any(alias in line_stripped for alias in usecase_aliases):
                        skip_note = True
                        should_skip = True
                elif skip_note:
                    if line_stripped == 'end note':
                        skip_note = False
                    should_skip = True
                
                # 如果不需要跳过，则保留该行
                if not should_skip:
                    new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"用例 '{usecase_to_delete}' 及其相关内容已被删除")
            st.rerun()
    else:
        st.info("没有可删除的用例")

def render_add_usecase_relation(code_key, message_idx, current_code):
    """渲染添加用例关系的界面"""
    st.subheader("添加关系")
    
    # 获取现有的Actor和用例
    actors = get_existing_actors(current_code)
    usecases = get_existing_usecases(current_code)
    name_map = get_name_mapping(current_code)
    
    # 合并所有可能的源和目标
    all_elements = actors + usecases
    
    # 生成唯一的时间戳
    timestamp = int(time.time() * 1000)
    
    # 源选择
    source = st.selectbox(
        "源元素",
        [name_map.get(elem, elem) for elem in all_elements],
        key=f"source_{code_key}_{timestamp}"
    )
    
    # 关系类型选择
    relation_type = st.selectbox(
        "关系类型",
        ["-->>", "-->", ".>>", "..>", "<|--", "*--", "o--"],
        key=f"relation_type_{code_key}_{timestamp}"
    )
    
    # 目标选择
    target = st.selectbox(
        "目标元素",
        [name_map.get(elem, elem) for elem in all_elements],
        key=f"target_{code_key}_{timestamp}"
    )
    
    # 关系描述（可选）
    description = st.text_input(
        "关系描述（可选）",
        key=f"relation_desc_{code_key}_{timestamp}"
    )
    
    # 添加按钮，调整列比例让按钮靠左
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("添加关系", key=f"add_relation_{code_key}_{timestamp}", type="primary"):
            if source and target:
                # 反向查找原始名称
                source_original = next((k for k, v in name_map.items() if v == source), source)
                target_original = next((k for k, v in name_map.items() if v == target), target)
                
                # 构建关系语句
                relation = f"{source_original} {relation_type}"
                if description:
                    relation += f" : {description}"
                relation += f" {target_original}"
                
                # 在@enduml之前插入新关系
                lines = current_code.split('\n')
                insert_index = next(i for i, line in enumerate(lines) if '@enduml' in line)
                lines.insert(insert_index, relation)
                
                # 更新代码
                st.session_state[code_key] = '\n'.join(lines)
                st.success(f"已添加关系：{relation}")
                st.rerun()

def render_delete_usecase_relation(code_key, message_idx, current_code):
    """渲染删除关系界面"""
    relations = []
    lines = current_code.split('\n')
    
    # 获取所有用例的完整名称映射
    usecase_names = {}
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('usecase '):
            if ' as ' in line_stripped:
                parts = line_stripped.split(' as ')
                name_part = parts[0].strip()
                alias = parts[1].strip()
                name_match = re.search(r'"([^"]+)"', name_part)
                if name_match:
                    full_name = name_match.group(1)
                    usecase_names[alias] = full_name
            else:
                name_match = re.search(r'"([^"]+)"', line_stripped)
                if name_match:
                    full_name = name_match.group(1)
                    usecase_names[full_name] = full_name
    
    print("用例名称映射:", usecase_names)
    
    for line in lines:
        line_stripped = line.strip()
        print("处理行:", line_stripped)
        
        # 检查是否包含关系
        if '-->' in line_stripped or '.>' in line_stripped or '--|>' in line_stripped:
            # 使用正则表达式提取关系的源和目标
            # 匹配形式：source --> target 或 "source" --> "target"
            relation_match = re.match(r'(["\w]+)\s*(?:-->|\.>|--\|>)\s*(["\w]+)', line_stripped)
            
            if relation_match:
                source = relation_match.group(1).strip('"')
                target = relation_match.group(2).strip('"')
                
                print(f"取的关系: {source} -> {target}")
                
                # 替换用例别名为完整名称
                display_source = usecase_names.get(source, source)
                display_target = usecase_names.get(target, target)
                
                print(f"源: {source} -> {display_source}")
                print(f"目标: {target} -> {display_target}")
                
                # 构建显示用的关系文本
                # 保持原始格式，只替换名称
                display_line = line_stripped
                
                # 替换目标（需要考虑有无引号的情况）
                if target in usecase_names:
                    display_line = re.sub(
                        rf'\b{target}\b',
                        display_target,
                        display_line
                    )
                
                # 替换源
                if source in usecase_names:
                    display_line = re.sub(
                        rf'\b{source}\b',
                        display_source,
                        display_line
                    )
                
                print("显示行:", display_line)
                relations.append((display_line, line_stripped))
    
    print("找到的关系:", relations)
    
    if relations:
        relation_to_delete = st.selectbox(
            "选择要删除的关系",
            options=[r[0] for r in relations],
            key=f"delete_relation_{code_key}_{message_idx}",
            format_func=lambda x: (x.replace(" --> ", " → ")
                                 .replace(" -> ", " → ")
                                 .replace(" .> ", " ⊲ ")
                                 .replace(" --|> ", " ⯈ ")
                                 .replace(" <|-- ", " ⯇ ")
                                 .replace('"', ''))
        )
        
        if st.button(
            "删除关系", 
            key=f"delete_relation_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            original_line = next(r[1] for r in relations if r[0] == relation_to_delete)
            new_lines = [line for line in lines if line.strip() != original_line]
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success("关系已删除")
            st.rerun()
    else:
        st.info("没有可删除的关系")

def render_modify_usecase(code_key, message_idx, current_code):
    """渲染修改用例界面"""
    existing_usecases = get_existing_usecases(current_code)
    if not existing_usecases:
        st.info("没有可修改的用例")
        return
        
    usecase_to_modify = st.selectbox(
        "选择要修改的用例",
        options=existing_usecases,
        key=f"modify_usecase_{message_idx}"
    )
    
    new_usecase_name = st.text_input("新用例名称", value=usecase_to_modify, key=f"new_usecase_name_{message_idx}")
    description = st.text_area(
        "描述 (可选)", 
        height=100,
        key=f"modify_usecase_desc_{message_idx}"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("保存修改", key=f"save_modify_usecase_{message_idx}", type="primary"):
            if not new_usecase_name:
                st.error("请输入用例名称")
                return
                
            if new_usecase_name != usecase_to_modify and new_usecase_name in existing_usecases:
                st.error(f"用例名称 '{new_usecase_name}' 已存在")
                return
            
            lines = current_code.split('\n')
            new_lines = []
            
            # 查找原始用例定义和别名
            old_alias = None
            old_as_line = None
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_modify}"' in line_stripped:
                        if ' as ' in line_stripped:
                            old_as_line = line_stripped
                            old_alias = line_stripped.split(' as ')[1].strip()
            
            # 如果有旧的别名，创建新的别名
            new_alias = None
            if old_alias:
                new_alias = old_alias  # 保持原有的别名
            
            # 处理每一行
            for line in lines:
                line_stripped = line.strip()
                updated_line = line_stripped
                
                # 处理用例定义行
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_modify}"' in line_stripped:
                        if old_as_line:
                            # 保持as结构，但更新名称
                            updated_line = f'usecase "{new_usecase_name}" as {old_alias}'
                        else:
                            updated_line = f'usecase "{new_usecase_name}"'
                        
                        # 添加描述（如果有）
                        new_lines.append(updated_line)
                        if description.strip():
                            new_lines.append(f'note right of {old_alias or new_usecase_name}')
                            new_lines.append(f'  {description}')
                            new_lines.append('end note')
                        continue
                
                # 处理关系行
                if any(rel in line_stripped for rel in ['-->', '.>', '--|>', '-', '--']):
                    # 处理带引号的情况
                    if f'"{usecase_to_modify}"' in updated_line:
                        updated_line = updated_line.replace(f'"{usecase_to_modify}"', f'"{new_usecase_name}"')
                    
                    # 处理不带引号的情况
                    if old_alias:
                        # 保持原有的别名
                        continue
                    else:
                        # 处理原始名称在关系中的各种位置
                        patterns = [
                            (f'{usecase_to_modify} --', f'{new_usecase_name} --'),
                            (f'-- {usecase_to_modify}', f'-- {new_usecase_name}'),
                            (f'{usecase_to_modify} :', f'{new_usecase_name} :'),
                            (f' {usecase_to_modify} ', f' {new_usecase_name} '),
                            (f'"{usecase_to_modify}"', f'"{new_usecase_name}"'),
                            (f'{usecase_to_modify}--', f'{new_usecase_name}--'),
                            (f'--{usecase_to_modify}', f'--{new_usecase_name}'),
                            (f'{usecase_to_modify}->', f'{new_usecase_name}->'),
                            (f'->{usecase_to_modify}', f'->{new_usecase_name}'),
                            (f'{usecase_to_modify} ->', f'{new_usecase_name} ->'),
                            (f'-> {usecase_to_modify}', f'-> {new_usecase_name}'),
                        ]
                        for old_pattern, new_pattern in patterns:
                            updated_line = updated_line.replace(old_pattern, new_pattern)
                
                # 处理注释块
                if line_stripped.startswith('note '):
                    if old_alias and f'of {old_alias}' in updated_line:
                        # 保持原有的别名
                        continue
                    elif f'of {usecase_to_modify}' in updated_line:
                        updated_line = updated_line.replace(f'of {usecase_to_modify}', f'of {new_usecase_name}')
                
                new_lines.append(updated_line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"用例 '{usecase_to_modify}' 已修改为 '{new_usecase_name}'")
            st.rerun()