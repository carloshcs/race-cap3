# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 15:26:24 2024

@author: carlo
"""


import streamlit as st

# Title of the app
st.title("Streamlit Test App")

# Simple text
st.write("Hello! This is a test app to ensure Streamlit is working correctly on PythonAnywhere.")

# Button to count clicks
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Click me!"):
    st.session_state.count += 1

st.write(f"Button clicked {st.session_state.count} times.")
