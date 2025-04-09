import streamlit as st
import streamlit_oauth

def authenticate_google():
    """Handles Google OAuth authentication and returns user info."""
    # --- Google OAuth Configuration ---
    # Load credentials from secrets
    try:
        client_id = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
        redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
    except KeyError:
        st.error("Google OAuth credentials not found in secrets.toml.")
        st.info("Please create a `.streamlit/secrets.toml` file with your Google Client ID, Client Secret, and Redirect URI.")
        st.stop()
    except FileNotFoundError:
         st.error("Secrets file not found.")
         st.info("Please create a `.streamlit/secrets.toml` file in your project root.")
         st.stop()

    # --- Authentication Function ---
    user_info = streamlit_oauth.google_oauth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        authorize_button_text="Login with Google",
        scope="openid email profile",
        pkce=True # Recommended for security
    )
    return user_info 