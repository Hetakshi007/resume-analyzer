import streamlit as st

st.title("🔍 Debugging Streamlit Secrets")
st.write("Checking if secrets are accessible...")

try:
    huggingface_api_key = st.secrets["HUGGINGFACE_API_KEY"]
    st.success("✅ Secrets loaded successfully!")
except KeyError as e:
    st.error(f"❌ Secret not found: {e}")
