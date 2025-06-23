# ✅ app.py — UI đơn giản, chạy song song, giữ trạng thái sau khi tải và đối chiếu OncoKB / PubMed + lưu kết quả đối chiếu

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
import pandas as pd
from Simulate.Simulate_Model_Method_2 import import_network, simulate
from functions.Compare import match_with_oncokb_pubmed  # ✅ Giả sử file compare.py có hàm này

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
start = st.sidebar.button("🚀 Run Simulation", disabled=(uploaded_file is None))

# Prepare file path and state
temp_path = None
if uploaded_file:
    st.code(uploaded_file.name)
    os.makedirs("Temp_Upload", exist_ok=True)
    temp_path = os.path.join("Temp_Upload", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    G = import_network(temp_path)
    st.write(f"✅ Network loaded with **{len(G.nodes())} nodes** and **{len(G.edges())} edges**.")
    st.session_state["temp_path"] = temp_path
else:
    st.warning("⚠️ Please upload a network file.")

# Run simulation
if start and "temp_path" in st.session_state:
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

# Show result if available
if "result_df" in st.session_state:
    st.success("✅ Simulation completed.")
    st.subheader("📊 Simulation Result:")
    df = st.session_state["result_df"]
    st.dataframe(df.sort_values("Total_Support", ascending=True))
    st.download_button(
        "⬇️ Download Result CSV",
        data=df.to_csv(index=False),
        file_name="simulation_result.csv",
        mime="text/csv"
    )

    # ✅ Nút đối chiếu kết quả với dữ liệu OncoKB / PubMed
    if st.button("🔍 Match with OncoKB and PubMed"):
        matched_df = match_with_oncokb_pubmed(df)
        st.session_state["matched_df"] = matched_df

# ✅ Hiển thị bảng đối chiếu nếu có
if "matched_df" in st.session_state:
    st.subheader("🧬 Matched Genes (OncoKB / PubMed)")
    matched_df = st.session_state["matched_df"]
    st.dataframe(matched_df)
    st.download_button(
        "💾 Download Matched Results",
        data=matched_df.to_csv(index=False),
        file_name="matched_result.csv",
        mime="text/csv"
    )
