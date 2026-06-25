import streamlit as st

st.set_page_config(page_title="Verba Latina Test", layout="centered")

st.title("🧪 Test App")
st.success("✅ If you see this message, the app is running successfully!")

st.write("GROK_API_KEY present in secrets:", "GROK_API_KEY" in st.secrets)

st.info("If this loads, we can gradually add your real code back.")
