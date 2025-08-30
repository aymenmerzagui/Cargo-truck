import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Simple 3D Visualization with Streamlit")

st.sidebar.header("3D Surface Parameters")
size = st.sidebar.slider("Grid Size", min_value=10, max_value=100, value=30)
amplitude = st.sidebar.slider("Amplitude", min_value=0.1, max_value=2.0, value=1.0)
freq = st.sidebar.slider("Frequency", min_value=0.1, max_value=2.0, value=1.0)

x = np.linspace(-5, 5, size)
y = np.linspace(-5, 5, size)
X, Y = np.meshgrid(x, y)
Z = amplitude * np.sin(freq * np.sqrt(X**2 + Y**2))

fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
fig.update_layout(title="3D Surface Plot", autosize=True,
                  margin=dict(l=40, r=40, b=40, t=40))

st.plotly_chart(fig, use_container_width=True)
