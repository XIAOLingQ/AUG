import streamlit as st
from stream.utils.uml import (
    get_uml_diagram, 
    create_sequence_template, 
    get_existing_participants,
    get_name_mapping
)

def render_sequence_diagram_editor(code_key, message_idx, current_code):
    """Render sequence diagram editor"""
    # Initialize with template if new code
    if not current_code or '@startuml' not in current_code:
        current_code = create_sequence_template()
        st.session_state[code_key] = current_code

    # Participant operations
    with st.expander("👥 Participant Operations", expanded=False):
        tabs = st.tabs(["Add Participant", "Delete Participant"])
        with tabs[0]:
            render_add_participant(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_participant(code_key, message_idx, current_code)
    
    # Message operations
    with st.expander("💬 Message Operations", expanded=False):
        tabs = st.tabs(["Add Message", "Delete Message"])
        with tabs[0]:
            render_add_message(code_key, message_idx, current_code)
        with tabs[1]:
            render_delete_message(code_key, message_idx, current_code)

def render_add_participant(code_key, message_idx, current_code):
    """Render add participant interface"""
    participant_type = st.selectbox(
        "Participant Type",
        [
            ("participant", "Normal Participant"),
            ("actor", "Actor"),
            ("boundary", "Boundary"),
            ("control", "Controller"),
            ("entity", "Entity"),
            ("database", "Database")
        ],
        format_func=lambda x: x[1],
        key=f"participant_type_{code_key}_{message_idx}"
    )
    
    participant_name = st.text_input(
        "Participant Name", 
        key=f"participant_name_{code_key}_{message_idx}"
    )
    description = st.text_area(
        "Description (Optional)", 
        height=100,
        key=f"participant_desc_{code_key}_{message_idx}"
    )
    
    if st.button(
        "Add Participant", 
        key=f"add_participant_btn_{code_key}_{message_idx}", 
        type="primary"
    ):
        if not participant_name:
            st.error("Please enter participant name")
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
        st.success(f"Participant '{participant_name}' has been added")
        st.rerun()

def render_delete_participant(code_key, message_idx, current_code):
    """Render delete participant interface"""
    participants = get_existing_participants(current_code)
    if participants:
        participant_to_delete = st.selectbox(
            "Select participant to delete",
            options=[p[0] for p in participants],
            format_func=lambda x: f"{x} ({dict(participants)[x]})",
            key=f"delete_participant_{code_key}_{message_idx}"
        )
        
        if st.button(
            "Delete Participant", 
            key=f"delete_participant_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            lines = current_code.split('\n')
            new_lines = []
            skip_note = False
            
            # Get all possible identifiers for the participant (original name and aliases)
            participant_aliases = set()  # Use set to avoid duplicates
            participant_aliases.add(participant_to_delete)
            
            # Find all possible aliases
            for line in lines:
                line_stripped = line.strip()
                # Check if it's a participant definition line
                if any(line_stripped.startswith(prefix) for prefix in [
                    'participant ', 'actor ', 'boundary ', 
                    'control ', 'entity ', 'database '
                ]):
                    # If it contains the participant name to delete
                    if f'"{participant_to_delete}"' in line_stripped:
                        # Check for alias
                        if ' as ' in line_stripped:
                            alias = line_stripped.split(' as ')[-1].strip()
                            participant_aliases.add(alias)
                            # Also add underscore version
                            participant_aliases.add(alias.replace(" ", "_"))
            
            # Add variants of original name
            participant_aliases.add(participant_to_delete.replace(" ", "_"))
            
            # Add quoted versions of all names
            quoted_aliases = {f'"{alias}"' for alias in participant_aliases}
            participant_aliases.update(quoted_aliases)
            
            for line in lines:
                line_stripped = line.strip()
                should_skip = False
                
                # Check if it's a participant definition line
                if any(line_stripped.startswith(prefix) for prefix in [
                    'participant ', 'actor ', 'boundary ', 
                    'control ', 'entity ', 'database '
                ]):
                    if any(alias in line_stripped for alias in participant_aliases):
                        should_skip = True
                        continue
                
                # Check note blocks
                if line_stripped.startswith('note over'):
                    if any(alias in line_stripped for alias in participant_aliases):
                        skip_note = True
                        should_skip = True
                elif skip_note:
                    if line_stripped.endswith('end note'):
                        skip_note = False
                    should_skip = True
                
                # Check activate/deactivate lines
                if any(f'{action} {alias}' in line_stripped 
                      for action in ['activate', 'deactivate']
                      for alias in participant_aliases):
                    should_skip = True
                
                # Check message lines
                if any(pattern.format(alias) in line_stripped 
                      for alias in participant_aliases
                      for pattern in [
                          '{}', '{} ->', '-> {}', '{} -->', '--> {}',
                          '{} ->>', '->> {}', '{} -->>', '-->> {}',
                          '{} ->o', '->o {}', '{} ->x', '->x {}'
                      ]):
                    should_skip = True
                
                # Keep the line if it shouldn't be skipped
                if not should_skip:
                    new_lines.append(line)
            
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success(f"Participant '{participant_to_delete}' and related content have been deleted")
            st.rerun()
    else:
        st.info("No participants to delete")

def render_add_message(code_key, message_idx, current_code):
    """Render add message interface"""
    name_map = get_name_mapping(current_code)  # Get name mapping
    existing_participants = get_existing_participants(current_code)
    if existing_participants:
        participant_names = [p[0] for p in existing_participants]  # Use original names
        
        source = st.selectbox(
            "Sender",
            options=participant_names,
            key=f"source_{code_key}_{message_idx}"
        )
        
        message_type = st.selectbox(
            "Message Type",
            [
                ("->", "Synchronous Message"),
                ("-->", "Asynchronous Message"),
                ("->>", "Synchronous Response"),
                ("-->>", "Asynchronous Response"),
                ("->o", "Lost Message"),
                ("->x", "Destroy Message")
            ],
            format_func=lambda x: x[1],
            key=f"message_type_{code_key}_{message_idx}"
        )
        
        target = st.selectbox(
            "Receiver",
            options=participant_names,
            key=f"target_{code_key}_{message_idx}"
        )
        
        message_text = st.text_input(
            "Message Content", 
            key=f"message_text_{code_key}_{message_idx}"
        )
        
        activate = st.checkbox(
            "Activate Receiver", 
            key=f"activate_{code_key}_{message_idx}"
        )
        deactivate = st.checkbox(
            "Deactivate Receiver", 
            key=f"deactivate_{code_key}_{message_idx}"
        )
        
        if st.button(
            "Add Message", 
            key=f"add_message_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            if not message_text:
                st.error("Please enter message content")
                return

            lines = current_code.split('\n')
            message_lines = []
            
            # Get source and target aliases (if any)
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
            st.success("Message has been added")
            st.rerun()

def render_delete_message(code_key, message_idx, current_code):
    """Render delete message interface"""
    name_map = get_name_mapping(current_code)  # Get name mapping
    messages = []
    lines = current_code.split('\n')
    
    # Create reverse mapping (original name to alias)
    reverse_map = {v: k for k, v in name_map.items()}
    
    for line in lines:
        line_stripped = line.strip()
        if any(arrow in line_stripped for arrow in ['->', '-->', '->>', '-->>>', '->o', '->x']):
            if ':' in line_stripped:  # Make sure it's a message line
                # Parse message line
                parts = line_stripped.split(':')
                message_part = parts[0]
                content_part = ':'.join(parts[1:])
                
                # Extract source and target
                message_parts = message_part.split()
                if len(message_parts) >= 3:
                    source = message_parts[0].strip('"')
                    arrow = message_parts[1]
                    target = message_parts[2].strip('"')
                    
                    # Use original names (if mapped)
                    source_display = name_map.get(source, source)
                    target_display = name_map.get(target, target)
                    
                    # Build display message
                    display_message = f'"{source_display}" {arrow} "{target_display}"{content_part}'
                    messages.append((display_message, line_stripped))
    
    if messages:
        message_to_delete = st.selectbox(
            "Select message to delete",
            options=[m[0] for m in messages],
            key=f"delete_message_{code_key}_{message_idx}",
            format_func=lambda x: x.replace('->', '→')
                                  .replace('-->', '⇢')
                                  .replace('->>', '⇒')
                                  .replace('-->>>', '⇛')
                                  .replace('->o', '→○')
                                  .replace('->x', '→×')
                                  .replace('"', '')
        )
        
        if st.button(
            "Delete Message", 
            key=f"delete_message_btn_{code_key}_{message_idx}", 
            type="primary"
        ):
            # Find corresponding original line to delete
            original_line = next(m[1] for m in messages if m[0] == message_to_delete)
            new_lines = [line for line in lines if line.strip() != original_line]
            st.session_state[code_key] = '\n'.join(new_lines)
            st.success("Message has been deleted")
            st.rerun()
    else:
        st.info("No messages to delete")