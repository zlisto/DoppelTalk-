import streamlit as st
import os
import time
from utils import get_persona_prompt, get_persona_response

# App configuration
st.set_page_config(
    page_title="Persona App",
    page_icon="🤖",
    layout="wide",
)

# Initialize session state variables if they don't exist
if "agent_dict" not in st.session_state:
    st.session_state.agent_dict = {}

# Sidebar for navigation
with st.sidebar:
    st.title("Persona App")
    page = st.radio("Navigate", ["Home", "Agents", "Persona Chat", "Persona Debate"])

# Home page - Create agents
if page == "Home":
    st.title("Create New Agent")
    
    # Input field for agent name
    agent_name = st.text_input("Agent Name", key="agent_name_input")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, TXT, CSV)", 
                                     type=["pdf", "docx", "txt", "csv"])
    
    # Create agent button
    if st.button("Create Agent"):
        if agent_name and uploaded_file:
            # Save the uploaded file temporarily
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Generate persona prompt
            try:
                persona_prompt = get_persona_prompt(agent_name, file_path)
                st.session_state.agent_dict[agent_name] = persona_prompt
                st.success(f"Agent {agent_name} created!")
            except Exception as e:
                st.error(f"Error creating agent: {e}")
            
            # Clean up
            os.remove(file_path)
        else:
            st.warning("Please provide both an agent name and upload a file.")

# Agents page - View agent prompts
elif page == "Agents":
    st.title("View Agents")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to Home to create agents.")
    else:
        # Dropdown to select an agent
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent", agent_names)
        
        # Display agent prompt
        if selected_agent:
            st.subheader(f"{selected_agent}'s Persona Prompt")
            st.text_area("Prompt", st.session_state.agent_dict[selected_agent], 
                         height=400, disabled=True)

# Persona Chat page - Chat with an agent
elif page == "Persona Chat":
    st.title("Chat with an Agent")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to Home to create agents.")
    else:
        # Initialize chat history if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_persona_prompt" not in st.session_state:
            st.session_state.current_persona_prompt = None
        
        # Dropdown to select an agent
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent", agent_names, 
                                    key="chat_agent_selector")
        
        # Reset chat if agent changes
        if selected_agent and (st.session_state.current_persona_prompt != 
                              st.session_state.agent_dict[selected_agent]):
            st.session_state.current_persona_prompt = st.session_state.agent_dict[selected_agent]
            st.session_state.messages = []
            st.rerun()
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])
        
        # Chat input
        if selected_agent:
            user_message = st.chat_input("Type your message here...")
            if user_message:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_message})
                st.chat_message("user").write(user_message)
                
                # Get agent response
                with st.spinner("Agent is thinking..."):
                    persona_response = get_persona_response(
                        st.session_state.current_persona_prompt,
                        st.session_state.messages
                    )
                
                # Print for debugging
                print(f"[DEBUG] {selected_agent} response: {persona_response}")
                
                # Add agent response to chat
                st.session_state.messages.append({"role": "assistant", "content": persona_response})
                st.chat_message("assistant").write(persona_response)
                
                # Rerun to update the UI
                st.rerun()

# Persona Debate page - Two agents chat with each other
elif page == "Persona Debate":
    st.title("Agents Debate")
    
    if len(st.session_state.agent_dict) < 2:
        st.info("You need at least two agents. Go to Home to create more agents.")
    else:
        # Initialize debate variables if not exists
        if "agent_name_1" not in st.session_state:
            st.session_state.agent_name_1 = None
        if "agent_name_2" not in st.session_state:
            st.session_state.agent_name_2 = None
        if "persona_prompt_1" not in st.session_state:
            st.session_state.persona_prompt_1 = None
        if "persona_prompt_2" not in st.session_state:
            st.session_state.persona_prompt_2 = None
        if "messages_1" not in st.session_state:
            st.session_state.messages_1 = []
        if "messages_2" not in st.session_state:
            st.session_state.messages_2 = []
        if "debate_history" not in st.session_state:
            st.session_state.debate_history = []
        
        # Two columns for agent selection
        col1, col2 = st.columns(2)
        
        # Agent 1 selection
        with col1:
            agent_names = list(st.session_state.agent_dict.keys())
            selected_agent_1 = st.selectbox("Agent 1", agent_names, 
                                            key="debate_agent_1_selector")
            
            if selected_agent_1 != st.session_state.agent_name_1:
                st.session_state.agent_name_1 = selected_agent_1
                st.session_state.persona_prompt_1 = st.session_state.agent_dict[selected_agent_1]
                st.session_state.messages_1 = []
                st.session_state.debate_history = []
                # Initialize with a greeting
                if not st.session_state.messages_1:
                    agent_1_message = "Hi there! Nice to meet you."
                    st.session_state.messages_1.append({
                        "role": "assistant", 
                        "content": agent_1_message
                    })
                    st.session_state.debate_history.append(("Agent 1", agent_1_message))
                    
                    # Add this as a user message for Agent 2
                    if "messages_2" in st.session_state:
                        st.session_state.messages_2 = [{
                            "role": "user", 
                            "content": agent_1_message
                        }]
        
        # Agent 2 selection
        with col2:
            agent_names = list(st.session_state.agent_dict.keys())
            selected_agent_2 = st.selectbox("Agent 2", agent_names, 
                                            key="debate_agent_2_selector")
            
            if selected_agent_2 != st.session_state.agent_name_2:
                st.session_state.agent_name_2 = selected_agent_2
                st.session_state.persona_prompt_2 = st.session_state.agent_dict[selected_agent_2]
                st.session_state.messages_2 = []
                
                # If Agent 1 already sent a message, add it to Agent 2's messages
                if st.session_state.debate_history:
                    first_message = st.session_state.debate_history[0][1]
                    st.session_state.messages_2 = [{
                        "role": "user", 
                        "content": first_message
                    }]
        
        # Debate container
        debate_container = st.container()
        with debate_container:
            st.subheader("Debate")
            # Display debate history
            for agent, message in st.session_state.debate_history:
                if agent == "Agent 1":
                    st.chat_message("assistant", name=st.session_state.agent_name_1).write(message)
                else:
                    st.chat_message("assistant", name=st.session_state.agent_name_2).write(message)
        
        # Make agents converse button
        if st.button("Make Agents Converse"):
            if selected_agent_1 and selected_agent_2:
                # Agent 2 responds
                with st.spinner(f"{selected_agent_2} is thinking..."):
                    agent_2_message = get_persona_response(
                        st.session_state.persona_prompt_2,
                        st.session_state.messages_2
                    )
                    
                    # Add message to both agents' history
                    st.session_state.messages_2.append({
                        "role": "assistant", 
                        "content": agent_2_message
                    })
                    st.session_state.messages_1.append({
                        "role": "user", 
                        "content": agent_2_message
                    })
                    
                    # Add to debate history
                    st.session_state.debate_history.append(("Agent 2", agent_2_message))
                    
                    # Display in chat
                    st.chat_message("assistant", name=selected_agent_2).write(agent_2_message)
                    
                    # Wait
                    time.sleep(2)
                
                # Agent 1 responds
                with st.spinner(f"{selected_agent_1} is thinking..."):
                    agent_1_message = get_persona_response(
                        st.session_state.persona_prompt_1,
                        st.session_state.messages_1
                    )
                    
                    # Add message to both agents' history
                    st.session_state.messages_1.append({
                        "role": "assistant", 
                        "content": agent_1_message
                    })
                    st.session_state.messages_2.append({
                        "role": "user", 
                        "content": agent_1_message
                    })
                    
                    # Add to debate history
                    st.session_state.debate_history.append(("Agent 1", agent_1_message))
                    
                    # Display in chat
                    st.chat_message("assistant", name=selected_agent_1).write(agent_1_message)
                    
                    # Wait
                    time.sleep(2)
                
                # Rerun to update the UI
                st.rerun()