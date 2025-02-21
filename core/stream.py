# app.py

import streamlit as st
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
from decouple import config


import os

# Disable OAuthlib's HTTPS verification when running locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# OAuth client setup
client_id = config("CLIENT_ID")
client_secret = config("CLIENT_SECRET")
authorization_base_url = 'http://localhost:8000/o/authorize/'
token_url = 'http://localhost:8000/o/token/'

client = WebApplicationClient(client_id)

# Streamlit app
import streamlit as st
import requests
from urllib.parse import urlencode
import streamlit as st
import requests
import streamlit as st
import urllib.parse as urlparse
from urllib.parse import parse_qs
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

session_state = SessionState(token='')

def get_query_params():
    if not st.query_params:
        print("No query params")
        return login_page()
    query_params = st.query_params
    if 'token' in query_params :
        session_state.token = query_params['token']
        print("token saved")
        st.write('Token saved successfully!')
        return project_list()



# Function to fetch projects for the authenticated user
def fetch_user_projects():
    token = session_state.token
    print("Token ",token)

    if token:
        api_url = "http://localhost:8000/api/user/projects/"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            print("response",response.json().get('projects', []))
            return response.json().get('projects', [])
        else:
            print("false")
            st.error("Failed to fetch projects")
            return []
    else:
        st.error("No token found!")
        return []

# Main function to render the Streamlit app
def project_list():    
    st.title("User Projects")
    projects = fetch_user_projects()
    col_names = ["Name", "Description"]
    if projects:
        for project in projects:
            # Create a button for each project name
            if st.button(project['name']):
                view_project_details(project['name'])  # Navigate to the project details function
            st.write(project['description']) # Navigate to the project details function

    else:
        st.write("No projects found.")
        



def view_project_details():
    pass








def login_page():
    # get_query_params()
    st.title("Login with Google")

    # Check if the user is already authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        st.success("You are logged in!")
        if st.button("Logout"):
            # Call the Django logout endpoint
            logout_url = "http://localhost:8000/auth/logout/"
            response = requests.get(logout_url)
            if response.status_code == 200:
                st.session_state.authenticated = False
                st.success("Successfully logged out!")
            else:
                st.error("Logout failed!")
    else:
        if st.button("Login with Google"):
            login_url = "http://localhost:8000/google-auth/"
            # response = requests.get(login_url)
            response = st.write(f"[Login with Google]({login_url})")
            print("Response ",response)
        
        st.write("Or log in with your username and password:")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            login_url = "http://localhost:8000/google-auth/"
            response = requests.post(login_url, data={'username': username, 'password': password})
            if response.status_code == 200:
                st.session_state.authenticated = True
                st.success("Successfully authenticated!")
            else:
                st.error("Authentication failed!")

if __name__ == "__main__":
    get_query_params()


