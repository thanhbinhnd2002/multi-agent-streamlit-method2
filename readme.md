# 🧬 Multi-agent Outside Competitive Dynamics Model — Method 2

This repository provides an interactive simulation interface for the **Outside Competitive Dynamics Model** (Multi-agent version), using **Streamlit** for visualization and analysis of cancer gene networks.

## 📌 Key Features
- Upload your custom gene regulatory network in `.txt` format.
- Configure simulation parameters: epsilon, delta, number of betas, etc.
- Run simulations using the multi-agent competitive dynamics model.
- Match top predicted genes with **OncoKB** and **PubMed** datasets.
- Download results and matched gene data.
- Visualize network structure interactively.

---

## 📁 Folder Structure
```
App/
├── Streamlit_UI.py             # Streamlit-based web interface
├── Temp_Upload/                # Temporary files (auto-deleted after each run)
Simulate/
├── Simulate_Model_Method_2.py # Core model implementation (multi-agent dynamics)
functions/
├── Compare.py                  # Matching results with OncoKB & PubMed
...
```

---

## ⚙️ Installation
```bash
# Clone the repository
https://github.com/thanhbinhnd2002/multi-agent-streamlit-method2.git
cd multi-agent-streamlit-method2

# Recommended: create virtual environment
conda create -n multi_beta_env python=3.8
conda activate multi_beta_env

# Install dependencies
pip install -r requirements.txt
```

> **Note**: You may need to install `joblib`, `networkx`, `matplotlib`, `streamlit`, `pandas`, `openpyxl` manually if not included.

---

## 🚀 Usage
```bash
cd App
streamlit run Streamlit_UI.py
```

Then open your browser at: [http://localhost:8501](http://localhost:8501)

### Step-by-step Workflow
1. **Upload** a `.txt` file containing the gene regulatory network (see format below).
2. **Adjust** parameters (epsilon, delta, N_BETA, tolerance).
3. Click **Run Simulation**.
4. View the result table and download if needed.
5. Click **Match with OncoKB / PubMed** for validation.
6. Click **Draw Network** to visualize the uploaded graph.

---

## 📄 Input Format
Each line in the input `.txt` network file (excluding header) should follow:
```
source_node\ttarget_node\tdirection\tweight
```
- `direction = 1`: one-way edge from source to target
- `direction = 0`: bidirectional edge

**Example:**
```
from	target	direction	weight
A	B	1	0.7
B	C	0	1.0
```

---

## 🧹 Cleanup
- All uploaded files are saved temporarily in `Temp_Upload/`.
- This folder is automatically deleted after each simulation for safety.

---

## 📬 Contact & Credits
Developed by [Phạm Thành Bình](https://github.com/thanhbinhnd2002) at HUST — supervised by **Thầy Phạm Văn Hải**.

For feedback or contributions, feel free to open an issue or pull request.
