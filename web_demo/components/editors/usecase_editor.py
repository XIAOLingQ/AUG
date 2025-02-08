import streamlit as st
from utils.uml import get_uml_diagram, create_usecase_template, get_existing_actors, get_existing_usecases, get_name_mapping
import re
import time


def render_usecase_diagram_editor(code_key, message_idx, current_code):
    """Render use case diagram editor"""
    # Initialize with template if new code
    if not current_code or '@startuml' not in current_code:
        current_code = create_usecase_template()
        st.session_state[code_key] = current_code

    # Actor operations
    with st.expander("👤 Actor Operations", expanded=False):
        tabs = st.tabs(["Add Actor", "Delete Actor"])
        with tabs[0]:
            render_add_actor(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_actor(code_key, message_idx, current_code)
    
    # Use case operations
    with st.expander("📌 Use Case Operations", expanded=False):
        tabs = st.tabs(["Add Use Case", "Delete Use Case"])
        with tabs[0]:
            render_add_usecase(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_usecase(code_key, message_idx, current_code)
            
    
    # Relationship operations
    with st.expander("🔗 Relationship Operations", expanded=False):
        tabs = st.tabs(["Add Relationship", "Delete Relationship"])
        with tabs[0]:
            render_add_usecase_relation(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_usecase_relation(code_key, message_idx, current_code)


def render_add_actor(code_key, message_idx, current_code):
    """Render add actor interface"""
    actor_name = st.text_input("Actor Name", key=f"actor_name_{message_idx}")
    description = st.text_area(
        "Description (Optional)", 
        height=100,
        key=f"actor_desc_{message_idx}"
    )
    
    if st.button("Add Actor", key=f"add_actor_{message_idx}", type="primary"):
        if not actor_name:
            st.error("Please enter actor name")
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
        st.success(f"Actor '{actor_name}' has been added")
        st.rerun()

def render_add_usecase(code_key, message_idx, current_code):
    """Render add use case interface"""
    usecase_name = st.text_input("Use Case Name", key=f"usecase_name_{message_idx}")
    description = st.text_area(
        "Description (Optional)", 
        height=100,
        key=f"usecase_desc_{message_idx}"
    )
    
    if st.button("Add Use Case", key=f"add_usecase_{message_idx}", type="primary"):
        if not usecase_name:
            st.error("Please enter use case name")
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
        st.success(f"Use case '{usecase_name}' has been added")
        st.rerun()

def render_delete_actor(code_key, message_idx, current_code):
    """Render delete actor interface"""
    existing_actors = get_existing_actors(current_code)
    if existing_actors:
        actor_to_delete = st.selectbox(
            "Select actor to delete",
            options=existing_actors,
            key=f"delete_actor_{message_idx}"
        )
        
        if st.button("Delete Actor", key=f"delete_actor_btn_{message_idx}", type="primary"):
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
            st.success(f"Actor '{actor_to_delete}' and related relationships have been deleted")
            st.rerun()
    else:
        st.info("No actors to delete")

def render_delete_usecase(code_key, message_idx, current_code):
    """Render delete use case interface"""
    existing_usecases = get_existing_usecases(current_code)
    if existing_usecases:
        usecase_to_delete = st.selectbox(
            "Select use case to delete",
            options=existing_usecases,
            key=f"delete_usecase_{code_key}_{message_idx}"
        )
        
        if st.button(
            "Delete Use Case", 
            key=f"delete_usecase_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            lines = current_code.split('\n')
            new_lines = []
            skip_note = False
            
            # Get all possible identifiers for the use case (original name and aliases)
            usecase_aliases = set()
            usecase_aliases.add(usecase_to_delete)
            
            # Find use case aliases
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_delete}"' in line_stripped and ' as ' in line_stripped:
                        alias = line_stripped.split(' as ')[-1].strip()
                        usecase_aliases.add(alias)
            
            # Add quoted versions
            quoted_aliases = {f'"{alias}"' for alias in usecase_aliases}
            usecase_aliases.update(quoted_aliases)
            
            for line in lines:
                line_stripped = line.strip()
                should_skip = False
                
                # Check if it's a use case definition line
                if line_stripped.startswith('usecase '):
                    if any(alias in line_stripped for alias in usecase_aliases):
                        should_skip = True
                        continue
                
                # Check if it's a relationship line
                # Extend relationship detection patterns to include all possible forms
                if any(pattern in line_stripped for pattern in ['-->', '.>', '--|>', '-']):
                    # Extract relationship source and target, support more formats
                    # Match the following formats:
                    # 1. "source" --> "target"
                    # 2. source --> target
                    # 3. actor --> UC1
                    relation_patterns = [
                        r'(["\w]+)\s*(?:-->|\.>|--\|>)\s*(["\w]+)',  # Standard format
                        r'"([^"]+)"\s*(?:-->|\.>|--\|>)\s*"([^"]+)"',  # Quoted format
                        r'(\w+)\s*(?:-->|\.>|--\|>)\s*(\w+)'  # Unquoted format
                    ]
                    
                    for pattern in relation_patterns:
                        relation_match = re.match(pattern, line_stripped)
                        if relation_match:
                            source = relation_match.group(1).strip('"')
                            target = relation_match.group(2).strip('"')
                            
                            # Check if source or target matches the use case to delete
                            if (source in usecase_aliases or 
                                target in usecase_aliases or 
                                source.strip('"') in usecase_aliases or 
                                target.strip('"') in usecase_aliases):
                                should_skip = True
                                print(f"Skipping relationship line: {line_stripped}")  # Debug output
                                break
                
                # Check note blocks
                if line_stripped.startswith('note '):
                    if any(alias in line_stripped for alias in usecase_aliases):
                        skip_note = True
                        should_skip = True
                elif skip_note:
                    if line_stripped == 'end note':
                        skip_note = False
                    should_skip = True
                
                # Keep the line if it shouldn't be skipped
                if not should_skip:
                    new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"Use case '{usecase_to_delete}' and related content have been deleted")
            st.rerun()
    else:
        st.info("No use cases to delete")

def render_add_usecase_relation(code_key, message_idx, current_code):
    """Render add use case relationship interface"""
    st.subheader("Add Relationship")
    
    # Get existing actors and use cases
    actors = get_existing_actors(current_code)
    usecases = get_existing_usecases(current_code)
    name_map = get_name_mapping(current_code)
    
    # Combine all possible sources and targets
    all_elements = actors + usecases
    
    # Generate unique timestamp
    timestamp = int(time.time() * 1000)
    
    # Source selection
    source = st.selectbox(
        "Source Element",
        [name_map.get(elem, elem) for elem in all_elements],
        key=f"source_{code_key}_{timestamp}"
    )
    
    # Relationship type selection
    relation_type = st.selectbox(
        "Relationship Type",
        ["-->>", "-->", ".>>", "..>", "<|--", "*--", "o--"],
        key=f"relation_type_{code_key}_{timestamp}"
    )
    
    # Target selection
    target = st.selectbox(
        "Target Element",
        [name_map.get(elem, elem) for elem in all_elements],
        key=f"target_{code_key}_{timestamp}"
    )
    
    # Relationship description (optional)
    description = st.text_input(
        "Relationship Description (Optional)",
        key=f"relation_desc_{code_key}_{timestamp}"
    )
    
    # Add button, adjust column ratio to make button align left
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Add Relationship", key=f"add_relation_{code_key}_{timestamp}", type="primary"):
            if source and target:
                # Reverse lookup original names
                source_original = next((k for k, v in name_map.items() if v == source), source)
                target_original = next((k for k, v in name_map.items() if v == target), target)
                
                # Build relationship statement
                relation = f"{source_original} {relation_type}"
                if description:
                    relation += f" : {description}"
                relation += f" {target_original}"
                
                # Insert new relationship before @enduml
                lines = current_code.split('\n')
                insert_index = next(i for i, line in enumerate(lines) if '@enduml' in line)
                lines.insert(insert_index, relation)
                
                # Update code
                st.session_state[code_key] = '\n'.join(lines)
                st.success(f"Relationship added: {relation}")
                st.rerun()

def render_delete_usecase_relation(code_key, message_idx, current_code):
    """Render delete relationship interface"""
    relations = []
    lines = current_code.split('\n')
    
    # Get complete name mapping for all use cases
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
    
    print("Use case name mapping:", usecase_names)
    
    for line in lines:
        line_stripped = line.strip()
        print("Processing line:", line_stripped)
        
        # Check if contains relationship
        if '-->' in line_stripped or '.>' in line_stripped or '--|>' in line_stripped:
            # Use regex to extract relationship source and target
            # Match formats: source --> target or "source" --> "target"
            relation_match = re.match(r'(["\w]+)\s*(?:-->|\.>|--\|>)\s*(["\w]+)', line_stripped)
            
            if relation_match:
                source = relation_match.group(1).strip('"')
                target = relation_match.group(2).strip('"')
                
                print(f"Found relationship: {source} -> {target}")
                
                # Replace use case aliases with full names
                display_source = usecase_names.get(source, source)
                display_target = usecase_names.get(target, target)
                
                print(f"Source: {source} -> {display_source}")
                print(f"Target: {target} -> {display_target}")
                
                # Build display relationship text
                # Keep original format, just replace names
                display_line = line_stripped
                
                # Replace target (consider both quoted and unquoted cases)
                if target in usecase_names:
                    display_line = re.sub(
                        rf'\b{target}\b',
                        display_target,
                        display_line
                    )
                
                # Replace source
                if source in usecase_names:
                    display_line = re.sub(
                        rf'\b{source}\b',
                        display_source,
                        display_line
                    )
                
                print("Display line:", display_line)
                relations.append((display_line, line_stripped))
    
    print("Found relationships:", relations)
    
    if relations:
        relation_to_delete = st.selectbox(
            "Select relationship to delete",
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
            "Delete Relationship", 
            key=f"delete_relation_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            original_line = next(r[1] for r in relations if r[0] == relation_to_delete)
            new_lines = [line for line in lines if line.strip() != original_line]
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success("Relationship has been deleted")
            st.rerun()
    else:
        st.info("No relationships to delete")

def render_modify_usecase(code_key, message_idx, current_code):
    """Render modify use case interface"""
    existing_usecases = get_existing_usecases(current_code)
    if not existing_usecases:
        st.info("No use cases to modify")
        return
        
    usecase_to_modify = st.selectbox(
        "Select use case to modify",
        options=existing_usecases,
        key=f"modify_usecase_{message_idx}"
    )
    
    new_usecase_name = st.text_input("New use case name", value=usecase_to_modify, key=f"new_usecase_name_{message_idx}")
    description = st.text_area(
        "Description (Optional)", 
        height=100,
        key=f"modify_usecase_desc_{message_idx}"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Save Changes", key=f"save_modify_usecase_{message_idx}", type="primary"):
            if not new_usecase_name:
                st.error("Please enter use case name")
                return
                
            if new_usecase_name != usecase_to_modify and new_usecase_name in existing_usecases:
                st.error(f"Use case name '{new_usecase_name}' already exists")
                return
            
            lines = current_code.split('\n')
            new_lines = []
            
            # Find original use case definition and alias
            old_alias = None
            old_as_line = None
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_modify}"' in line_stripped:
                        if ' as ' in line_stripped:
                            old_as_line = line_stripped
                            old_alias = line_stripped.split(' as ')[1].strip()
            
            # If there's an old alias, create new alias
            new_alias = None
            if old_alias:
                new_alias = old_alias  # Keep original alias
            
            # Process each line
            for line in lines:
                line_stripped = line.strip()
                updated_line = line_stripped
                
                # Handle use case definition line
                if line_stripped.startswith('usecase '):
                    if f'"{usecase_to_modify}"' in line_stripped:
                        if old_as_line:
                            # Keep as structure but update name
                            updated_line = f'usecase "{new_usecase_name}" as {old_alias}'
                        else:
                            updated_line = f'usecase "{new_usecase_name}"'
                        
                        # Add description (if provided)
                        new_lines.append(updated_line)
                        if description.strip():
                            new_lines.append(f'note right of {old_alias or new_usecase_name}')
                            new_lines.append(f'  {description}')
                            new_lines.append('end note')
                        continue
                
                # Handle relationship lines
                if any(rel in line_stripped for rel in ['-->', '.>', '--|>', '-', '--']):
                    # Handle quoted cases
                    if f'"{usecase_to_modify}"' in updated_line:
                        updated_line = updated_line.replace(f'"{usecase_to_modify}"', f'"{new_usecase_name}"')
                    
                    # Handle unquoted cases
                    if old_alias:
                        # Keep original alias
                        continue
                    else:
                        # Handle original name in various positions in relationships
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
                
                # Handle note blocks
                if line_stripped.startswith('note '):
                    if old_alias and f'of {old_alias}' in updated_line:
                        # Keep original alias
                        continue
                    elif f'of {usecase_to_modify}' in updated_line:
                        updated_line = updated_line.replace(f'of {usecase_to_modify}', f'of {new_usecase_name}')
                
                new_lines.append(updated_line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"Use case '{usecase_to_modify}' has been modified to '{new_usecase_name}'")
            st.rerun()