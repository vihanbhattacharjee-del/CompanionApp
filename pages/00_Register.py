import streamlit as st
import pandas as pd
import os
import time

from utils import (
    fetch_and_check_parent_registration,
    fetch_and_check_member_exists,
    save_parent_registration,
    save_member_information,
    parent_member_table,
    fetch_and_check_parent_member_table
)


# session state
if "is_parent_registered" not in st.session_state:
    st.session_state.is_parent_registered = False

if "is_member_registered" not in st.session_state:
    st.session_state.is_member_registered = False

# app logic
if not st.user.is_logged_in:
    # message to please login with an icon
    st.markdown("⚠️ Please login to register a new user")
    st.stop()

# check if the user is already registered
if fetch_and_check_parent_registration(st.user.email)[0]:
    st.session_state.is_parent_registered = True
    # diplay the info in a table
    with st.sidebar:
        user_details = fetch_and_check_parent_registration(st.user.email)[1]
        print("User details:", user_details)
        st.subheader("User Details")
        st.markdown("**User Name:** " + user_details[0])
        st.markdown("**Primary Consultant:** " + user_details[1])
        st.markdown("**Contact Email:** " + user_details[2])
        if pd.notna(user_details[3]):
            st.markdown("**Other Consultant:** " + user_details[3])
        st.markdown("**Emergency Contact:** " + user_details[4])

# check if the user is a member
if fetch_and_check_member_exists(st.user.email)[0]:
    st.session_state.is_member_registered = True

# title for registering
st.title("🏥 CareTaker Register")
st.markdown("*Register as a Primary Account Holder*")

# two tabs foe parent and familary registration
parent_tab, family_tab = st.tabs(["Become Parent/Guardian", "Add Family Member"])

with family_tab:
    st.markdown("## 📝 Add Family Member")
    # only a parent/guardian can add family members
    if not st.session_state.is_parent_registered:
        st.markdown("⚠️ You are not registered as a parent/guardian")
    else:
        # form to add family members    
        with st.form("family_form"):
            st.markdown("### 📝 Family Member Information")
            # field to add the member name, email addresses, problem, and any other relevant information
            member_name = st.text_input("Family Member Name *", placeholder="Enter the family member's name")
            member_email = st.text_input("Family Member Email *", placeholder="Enter the family member's email")
            member_illness = st.text_input("Family Member Problem", placeholder="Enter the family member's problem")
            member_other_info = st.text_area("Family Member Other Information", placeholder="Enter any other relevant information")
            
            # Submit button
            st.markdown("---")
            fam_submitted = st.form_submit_button("🚀 Complete Registration", type="primary", use_container_width=True)
            if fam_submitted:
                # member name and emai are compulsory
                # add the validation
                if member_name and member_email:
                    # add to the database
                    if save_member_information(member_name, member_email, member_illness, member_other_info) and parent_member_table(st.user.sub, st.user.email, member_email):
                        st.success("✅ Family member added successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to add family member")

with parent_tab:
    if st.session_state.is_parent_registered:
        st.markdown("⚠️ You are already registered as a parent/guardian")

    # member cannot sign as parent
    elif st.session_state.is_member_registered:
        st.markdown("⚠️ You are already registered as a family member")

    # form to register as a parent user
    else:
        with st.form("registration_form"):
            st.markdown("### � Parent/Guardian Information")
            
            # Parent name field
            parent_name = st.text_input(
                "Parent/Guardian Name *",
                placeholder="Enter your full name",
                help="This will be the primary account holder name"
            )
        
            # Primary care doctor field
            primary_doctor = st.text_input(
                "Primary Care Consultant Name *",
                placeholder="Mr. Smith",
                help="Enter your primary care consultant's name"
            )
            
            # Other doctors field
            other_doctors = st.text_area(
                "Other Specialists",
                placeholder="Mr. Johnson \nMr. Williams \nMr. Brown ",
                help="List any other consultant or specialists you see regularly, one per line"
            )
            
            # Additional information
            st.markdown("### 📝 Additional Information")
            
            contact_email = st.text_input(
                "Contact Email (Must be your gmail you are logged in with) *",
                placeholder="your.email@example.com",
                help="Email for important medical notifications"
            )
            
            emergency_contact = st.text_input(
                "Emergency Contact Name & Phone",
                placeholder="John Doe - (555) 123-4567",
                help="Who should we contact in case of emergency?"
            )
            
            # Submit button
            st.markdown("---")
            submitted = st.form_submit_button("🚀 Complete Registration", type="primary", use_container_width=True)
            
            if submitted:
                if parent_name and primary_doctor and contact_email and emergency_contact:
                    # save the records
                    if save_parent_registration(parent_name, primary_doctor, contact_email, other_doctors, emergency_contact):
                        st.success("✅ Registration submitted successfully!")
                        st.balloons()
                        # wait around for 5 seconds
                        time.sleep(5)
                        st.rerun()
                    
                    # Display submitted information
                    st.markdown("### 📄 Registration Summary")
                    st.markdown(f"**Parent/Guardian:** {parent_name}")
                    st.markdown(f"**Primary Care Consultant:** {primary_doctor}")
                    if other_doctors:
                        st.markdown(f"**Other Consultant:**\n{other_doctors}")
                    st.markdown(f"**Contact Email:** {contact_email}")
                    if emergency_contact:
                        st.markdown(f"**Emergency Contact:** {emergency_contact}")
                    
                    st.info("🔔 You can now start uploading medical documents and manage access for family members and caretakers.")
                else:
                    st.error("❌ Please fill in all required fields marked with *")
