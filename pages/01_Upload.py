import streamlit as st
import os
from utils import fetch_and_check_parent_member_table


if not st.user.is_logged_in:
    # ask to login
    # message to please login with an icon
    st.markdown("⚠️ Please login to register a new user")
    st.stop()

# get the parent member table
try:
    parent_folder_id = fetch_and_check_parent_member_table(st.user.email)[1]
except Exception as e:
    st.error("Error fetching parent member table! No parent folder or parent registered!")
    st.stop()

# check if path is exists
try:
    if not os.path.exists(parent_folder_id):
        os.makedirs(parent_folder_id)
except Exception as e:
    st.error("Error creating parent folder! No parent folder or parent registered!")
    st.stop()

# title for uploading
st.title("🏥 CareTaker Upload")
st.markdown("*Upload your documents*")

# show existing files
with st.sidebar:
    if os.path.exists(parent_folder_id):
        st.markdown("### 📁 Existing Files")
        for file_ in os.listdir(parent_folder_id):
            st.markdown(f"- {file_}")

# file upload
files = st.file_uploader("Upload your documents", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

# submit button
if st.button("Upload"):
    # save these files inside the parent folder
    for file_ in files:
        with open(os.path.join(parent_folder_id, file_.name), "wb") as f:
            f.write(file_.getbuffer())
    # upload success message
    st.toast("Files uploaded successfully!")
        
    
