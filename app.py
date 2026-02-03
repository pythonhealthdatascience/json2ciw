import streamlit as st
import numpy as np
from PIL import Image

st.title("Sketch to DES simulation model")

st.write("Upload an image of your patient pathway to convert to a simulation model 👁️") 

tab1, tab2 = st.tabs(["Pathway sketch", "Description"])

with tab1:
    uploaded_file = st.file_uploader("Upload a sketch of your pathway", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)

    else:
        image = None

    if image:
        st.image(image, width="stretch")
