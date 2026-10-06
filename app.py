import streamlit as st

st.title("My First Streamlit App")

name = st.text_input("Enter your name")
button = st.button("Click me")

if name:
    st.write(f"Hello, {name}!")

if button:
    st.success("Button clicked!")