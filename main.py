import streamlit as st
from src import input_object, truck_3d_view

PAGES = {
    "Input Objects": input_object,
    "3D Truck View": truck_3d_view
}


with st.spinner(f"Loading ..."):
    input_object.run()