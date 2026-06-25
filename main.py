import streamlit as st

st.set_page_config(page_title="Verba Latina", layout="centered")

st.title("Verba Latina")
st.success("✅ The app is now running on Streamlit Cloud!")

st.info("GROK_API_KEY in secrets: " + str("GROK_API_KEY" in st.secrets))

st.write("If you see this, the deployment works. We can add your full code back.")
