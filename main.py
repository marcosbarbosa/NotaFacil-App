import streamlit as st

st.set_page_config(page_title="My Streamlit App", page_icon="🚀", layout="wide")

st.title("Welcome to My Streamlit App")
st.write("This is your starting point. Edit `main.py` to build your app!")

col1, col2 = st.columns(2)

with col1:
    st.header("Getting Started")
    st.write("Streamlit makes it easy to create interactive web apps with Python.")
    name = st.text_input("What's your name?")
    if name:
        st.write(f"Hello, {name}!")

with col2:
    st.header("Features")
    st.write("Here are some things you can do:")
    st.markdown("""
    - **Charts & Graphs** - Visualize data with built-in chart support
    - **Widgets** - Add interactive controls like sliders, buttons, and more
    - **Data Display** - Show tables and dataframes easily
    - **Media** - Display images, audio, and video
    """)

st.divider()

st.subheader("Quick Demo")
slider_val = st.slider("Pick a number", 0, 100, 50)
st.write(f"You selected: **{slider_val}**")
st.progress(slider_val / 100)
