import streamlit as st
import os
from openai import OpenAI

from llm import streaming_question_answering, streaming_pdf_explanation, QA_MODEL, image_description_generator
from llm import encode_image, IMAGE_INSTRUCTIONS
from utils import fetch_and_check_parent_member_table


def onchange_selecbox():
    st.session_state.messages = []


if not st.user.is_logged_in:
    # ask to login
    # message to please login with an icon
    st.markdown("⚠️ Please login to access the medical chat assistant")
    st.stop()

# Page title and description
st.title("🤖 CareTaker Assistant")
st.markdown("*Ask questions about your documents and get AI-powered insights*")

# get the parent member table
try:
    parent_folder_id = fetch_and_check_parent_member_table(st.user.email)[1]
except Exception as e:
    st.error("Error fetching parent member table! No parent folder or parent registered!")
    st.stop()

# check if path is exists
try:
    if not os.path.exists(parent_folder_id):
        # cannot chat as no documents are uploaded
        st.markdown("⚠️ Please upload documents to chat")
        st.stop()
except Exception as e:
    st.error("Error checking parent folder! No parent folder or parent registered!")
    st.stop()

# File selection with better styling
st.markdown("### 📁 Select Document")
selected_file = st.selectbox(
    "Choose a document to chat with:", 
    os.listdir(parent_folder_id), 
    index=None,
    help="Select a document to ask questions about",
    on_change=onchange_selecbox
)

if not selected_file:
    st.markdown("⚠️ Please select a file to chat with")
    st.stop()

# Display selected file info
st.markdown(f"**Currently chatting with:** `{selected_file}`")
st.markdown("---")

client = OpenAI(api_key= st.secrets["llm"]["OPENAI_API_KEY"])

select_image = False
if not st.session_state.messages:
    st.session_state.messages = []
    # check the selected file type
    if selected_file.endswith(".pdf"):
        select_image = False
        pdf_path = os.path.join(parent_folder_id, selected_file)
        with st.spinner("📄 Analyzing PDF content..."):
            user_query, pdf_explanation = streaming_pdf_explanation(pdf_path)
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.session_state.messages.append({"role": "assistant", "content": pdf_explanation})
    else:
        select_image = True
        image_path = os.path.join(parent_folder_id, selected_file)
        with st.spinner("🖼️ Analyzing image content..."):
            # user_image_message, image_description = image_description_generator(image_path)
            api_message_content = {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": IMAGE_INSTRUCTIONS},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                                    }
                                },
                            ],
                        }
            response = client.chat.completions.create(
                    model=QA_MODEL,
                    messages=[
                        api_message_content
                    ],
                )
            print(response)
        st.session_state.messages.append(api_message_content)
        st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    
# Display chat messages
for messge_index, message in enumerate(st.session_state.messages):
    if messge_index == 0:
        continue
    with st.chat_message(message["role"], avatar="🧑‍⚕️" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# Enhanced chat input
if prompt := st.chat_input("Ask about your document...", key="medical_chat"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧑‍⚕️"):
        if select_image:
            message_list = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages]
            stream = client.chat.completions.create(
                model=QA_MODEL,
                messages=[
                    api_message_content
                ],
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            stream = client.chat.completions.create(
            model=QA_MODEL,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Quick action buttons at the bottom
st.markdown("---")
col1, col2 = st.columns(2)

with col2:
    if st.button("📄 Upload More", use_container_width=True):
        st.switch_page("pages/01_Upload.py")

with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
