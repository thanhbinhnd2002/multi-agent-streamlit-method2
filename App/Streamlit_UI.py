# ✅ Streamlit_UI.py — UI Streamlit cải tiến: hỗ trợ vẽ mạng, xóa tệp tạm sau khi chạy

import sys
import os
import shutil
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Simulate.Simulate_Model_Method_2 import import_network, simulate
from functions.Compare import match_with_oncokb_pubmed

# UI Title
st.set_page_config(page_title="Cancer Gene Simulation", layout="wide")
st.title("🔬 Multi-agent Outside Competitive Dynamics Model")

# Sidebar - Upload + Parameters
st.sidebar.header("⚙️ Simulation Settings")
uploaded_file = st.sidebar.file_uploader("Upload a .txt network file", type=["txt"])
EPSILON = st.sidebar.slider("Epsilon", 0.05, 1.0, 0.1, step=0.01)
DELTA = st.sidebar.slider("Delta", 0.01, 1.0, 0.2, step=0.01)
MAX_ITER = st.sidebar.number_input("Max Iterations", 10, 200, 50)
TOL = st.sidebar.number_input("Tolerance", 1e-6, 1e-2, 1e-4, format="%e")
N_BETA = st.sidebar.slider("Number of Beta per group", 1, 10, 2)

run_sim = st.sidebar.button("🚀 Run Simulation", disabled=(uploaded_file is None))
draw_network = st.sidebar.button("🖼️ Draw Network", disabled=(uploaded_file is None))

# Prepare file path and state
if uploaded_file:
    os.makedirs("Temp_Upload", exist_ok=True)
    temp_path = os.path.join("Temp_Upload", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    G = import_network(temp_path)
    st.write(f"✅ Network loaded with **{len(G.nodes())} nodes** and **{len(G.edges())} edges**.")
    st.session_state["temp_path"] = temp_path
else:
    st.warning("⚠️ Please upload a network file.")

# ✅ Draw network
if draw_network and "temp_path" in st.session_state:
    G = import_network(st.session_state["temp_path"])
    fig, ax = plt.subplots(figsize=(6, 5))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, node_size=20, edge_color="gray", ax=ax, with_labels=False)
    st.pyplot(fig)

# ✅ Run simulation
if run_sim and "temp_path" in st.session_state:
    with st.spinner("Running simulation..."):
        df = simulate(
            file_path=st.session_state["temp_path"],
            EPSILON=EPSILON,
            DELTA=DELTA,
            MAX_ITER=MAX_ITER,
            TOL=TOL,
            N_BETA=N_BETA
        )
        st.session_state["result_df"] = df
        shutil.rmtree("Temp_Upload")  # ❌ Xóa tạm sau khi dùng

# ✅ Hiển thị kết quả nếu có
if "result_df" in st.session_state:
    df = st.session_state["result_df"]
    st.success("✅ Simulation completed.")
    st.subheader("📊 Simulation Result:")
    st.dataframe(df.sort_values("Total_Support", ascending=False))
    st.download_button(
        "⬇️ Download Result CSV",
        data=df.to_csv(index=False),
        file_name="simulation_result.csv",
        mime="text/csv"
    )

    if st.button("🔍 Match with OncoKB and PubMed"):
        matched_df = match_with_oncokb_pubmed(df)
        st.session_state["matched_df"] = matched_df.sort_values("Total_Support", ascending=False)

# ✅ Hiển thị đối chiếu nếu có
if "matched_df" in st.session_state:
    matched_df = st.session_state["matched_df"]
    st.subheader("🧬 Matched Genes (OncoKB / PubMed)")
    st.dataframe(matched_df)
    st.download_button(
        "📅 Download Matched Results",
        data=matched_df.to_csv(index=False),
        file_name="matched_result.csv",
        mime="text/csv"
    )
