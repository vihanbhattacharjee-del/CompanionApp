import streamlit as st
import pandas as pd
import os


# constants
DB_CSV_NAME = "users.csv"
DB_MEMBER_NAME = "members.csv"
DB_MEMBER_PARENT_NAME = "member_parent.csv"

# functions
def save_parent_registration(parent_name, primary_doctor, contact_email,other_doctors = None, emergency_contact = None):
    try:
        if os.path.exists(DB_CSV_NAME):
            df = pd.read_csv(DB_CSV_NAME)
        else:
            df = pd.DataFrame(columns=["parent_name", "primary_doctor", "contact_email", "other_doctors", "emergency_contact"])
        # info dict
        info_dict = {
            "parent_name": parent_name,
            "primary_doctor": primary_doctor,
            "contact_email": contact_email,
            "other_doctors": other_doctors,
            "emergency_contact": emergency_contact
        }
        df.loc[len(df)] = info_dict
        df.to_csv(DB_CSV_NAME, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving parent registration: {str(e)}")
        return False


def save_member_information(member_name, member_email, member_illness = None, other_info = None):
    try:
        if os.path.exists(DB_MEMBER_NAME):
            df = pd.read_csv(DB_MEMBER_NAME)
        else:
            df = pd.DataFrame(columns=["family_member_name", "family_member_email", "family_member_illness", "family_member_other_info"])

        # create rhe info dict
        info_dict = {
            "family_member_name": member_name,
            "family_member_email": member_email,
            "family_member_illness": member_illness,
            "family_member_other_info": other_info
        }
        # add to the dataframe
        df.loc[len(df)] = info_dict
        df.to_csv(DB_MEMBER_NAME, index=False)
        
        return True
    except Exception as error:
        st.error(f"Error saving member information: {str(error)}")
        return False


def parent_member_table(id, parent_email, member_email):
    try:
        if os.path.exists(DB_MEMBER_PARENT_NAME):
            df = pd.read_csv(DB_MEMBER_PARENT_NAME)
        else:
            df = pd.DataFrame(columns=["id", "parent_email", "member_email"])
        # create the info dict
        info_dict = {
            "id": id,
            "parent_email": parent_email,
            "member_email": member_email
        }
        # add to dataframe
        df.loc[len(df)] = info_dict
        df.to_csv(DB_MEMBER_PARENT_NAME, index=False)
        
        return True
    except Exception as error:
        st.error(f"Error saving parent member table: {str(error)}")
        return False


def fetch_and_check_parent_registration(email):
    try:
        if os.path.exists(DB_CSV_NAME):
            df = pd.read_csv(DB_CSV_NAME)
            email_data = df[df["contact_email"] == email].values[0].tolist()
            if email_data:
                return (True, email_data)
            else:
                return (False, None)
        else:
            return (False, None)
    except Exception as e:
        return (False, None)


def fetch_and_check_member_exists(email):
    try:
        if os.path.exists(DB_MEMBER_NAME):
            df = pd.read_csv(DB_MEMBER_NAME)
            email_data = df[df["family_member_email"] == email].values[0].tolist()
            if email_data:
                return (True, email_data)
            else:
                return (False, None)
        else:
            return (False, None)
    except Exception as e:
        return (False, None)


def fetch_and_check_parent_member_table(email):
    id_ = None
    try:
        if os.path.exists(DB_MEMBER_PARENT_NAME):
            df = pd.read_csv(DB_MEMBER_PARENT_NAME)
            id_df = df[df["parent_email"] == email]
            if id_df.empty:
                id_ = df[df["member_email"] == email]["id"].values[0]
                return (True, id_)
            else:
                id_ = id_df["id"].values[0]
                return (True, id_)
                
        return (False, None)
    except Exception as e:
        return (False, None)
