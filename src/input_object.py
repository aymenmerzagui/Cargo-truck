import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from src.cao import * 
from streamlit_stl import stl_from_file 
import tempfile
import os


def run():
    if "selected_box" not in st.session_state:
        st.session_state.selected_box = None 
    st.set_page_config(
        page_title="Cargo Planner", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    with open("src/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    with st.sidebar:

        st.markdown("""
        <div class="main-header">
            <h1>🚚 Easy Cargo Planner</h1>
            <p>Optimize your cargo loading with 3D visualization and smart planning</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h3>📁 File Upload</h3></div>', unsafe_allow_html=True)
        with st.form("my-form", clear_on_submit=True):
            uploaded_file = st.file_uploader(
            "", 
            type=["stp", "step"],
            help="Upload STEP or STP files for 3D cargo analysis",
            key="file_uploader"
        )
            submitted = st.form_submit_button("UPLOAD")
       
        
        
        if "boxes" not in st.session_state:
            st.session_state.boxes = []

    main_col, details_col = st.columns([2, 2], gap="large")

    with details_col:
        st.markdown('<div class="section-header"><h3>🎯 3D Visualization</h3></div>', unsafe_allow_html=True)
        
        if submitted:
            try:
                with st.spinner("Processing 3D model..."):
                    suffix = ".stp" if uploaded_file.name.endswith(".stp") else ".step"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                        stl_file = convert_step_to_stl(tmp_file_path)
                        length, width, height = get_bounding_box_dimensions(tmp_file_path)
                        
                        if not any(b["File"] == uploaded_file.name for b in st.session_state.boxes):
                            st.session_state.boxes.append({
                                "select": False,
                                "File": uploaded_file.name,
                                "Length": round(length, 2),
                                "Width": round(width, 2),
                                "Height": round(height, 2),
                                "quantity": 1,
                                "path": tmp_file_path,
                            })
                
                success = stl_from_file(
                    file_path=stl_file,
                    color="#FF9900",
                    material='material',
                    auto_rotate=True,
                    opacity=1,
                    cam_v_angle=60,
                    cam_h_angle=-90,
                    cam_distance=0,
                    height=400,
                    max_view_distance=1000,
                    key=f"stl_{uploaded_file.name}"
                )
                
                st.markdown('<div class="section-header"><h4>📏 Box Dimensions</h4></div>', unsafe_allow_html=True)
                
                dim_col1, dim_col2, dim_col3 = st.columns(3)
                with dim_col1:
                    st.metric("Length", f"{length:.1f}", delta=None)
                with dim_col2:
                    st.metric("Width", f"{width:.1f}", delta=None)
                with dim_col3:
                    st.metric("Height", f"{height:.1f}", delta=None)

                uploaded_file.seek(0)
                os.remove(tmp_file_path)
                os.remove(stl_file)                
            except Exception as e:
                st.error(f"Error processing file: {e}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;">
                <h4 style="color: #6c757d;">📦 No 3D Model Loaded</h4>
                <p style="color: #6c757d;">Upload a STEP or STP file to visualize your cargo</p>
            </div>
            """, unsafe_allow_html=True)

    with main_col:
        st.markdown('<div class="section-header"><h3>📋 Cargo Inventory</h3></div>', unsafe_allow_html=True)
        
        if st.session_state.boxes: 
            display_columns = [ "select","File", "Length", "Width", "Height", "quantity"]
            edited_boxes = st.data_editor(
                pd.DataFrame(st.session_state.boxes)[display_columns],
                num_rows="static",
                width="stretch",
                hide_index=True,
                column_config={
                    "File": st.column_config.TextColumn("📁 File Name", width="small"),
                    "Length": st.column_config.NumberColumn("Length", format="%.1f"),
                    "Width": st.column_config.NumberColumn("Width", format="%.1f"),
                    "Height": st.column_config.NumberColumn("Height", format="%.1f"),
                    "quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1)
                }
            )

            # Update session state with edited data
            st.session_state.boxes = edited_boxes.to_dict("records")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state.boxes = []
                    st.rerun()
            with col2:
                if st.button("📊 Calculate Load", use_container_width=True):
                    st.info("Load calculation feature coming soon!")
                    
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px;">
                <h5 style="color: #6c757d;">📦 No Boxes Added</h5>
                <p style="color: #6c757d;">Upload CAO files to start building your cargo inventory</p>
            </div>
            """, unsafe_allow_html=True)


