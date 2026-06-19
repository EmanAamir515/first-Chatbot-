import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="eChatBot", page_icon="🤖")
st.title("eChatBot")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = "conv_001"

# Sidebar
with st.sidebar:
    st.header("sideBar")
    
    # c1 , c2 = st.columns(2)
    # with c1:
    #     if st.but
    
    cid = st.text_input("Conversation ID:", value=st.session_state.conversation_id)
    if st.button("Switch Convo"):
        if cid != st.session_state.conversation_id or True:
            st.session_state.conversation_id = cid
            st.session_state.messages = []
            # Load existing conversation
            try:
                response = requests.get(f"http://localhost:8000/get/{cid}")
                if response.status_code == 200:
                    history = response.json()
                    
                    st.session_state.messages = history
                    # for msg in history:
                    #     st.session_state.messages.append(msg)
            except:
                pass
            st.rerun()
    
    if st.button("Clear Chat"):
        response = requests.get(f"http://localhost:8000/delete/{cid}")
        st.session_state.messages = []
        st.rerun()

# Display messages
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖" ## adding these to ovewrite build in icons

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    # Get bot response with streaming
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Use streaming endpoint
            response = requests.post(
                "http://localhost:8000/post_stream",
                json={
                    "Cid": st.session_state.conversation_id,
                    "role": "user",
                    "content": prompt
                },
                stream=True
            )
            
            if response.status_code == 200:
                counter = 0
                for line in response.iter_lines(chunk_size=1):
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            full_response += data
                            counter += 1
                            
                            if counter % 3 ==0:
                                message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to server. Make sure FastAPI is running!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

