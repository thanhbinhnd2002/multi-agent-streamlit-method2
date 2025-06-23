# ✅ Simulate_Model_Method_2.py — Bổ sung song song bằng joblib cho mô hình cạnh tranh ngoài đa tác nhân

import os
import networkx as nx
import numpy as np
import pandas as pd
from joblib import Parallel, delayed  # ✅ thêm thư viện chạy song song

# ✅ B1: Đọc mạng từ file txt
def import_network(file_path):
    with open(file_path, "r") as f:
        data = f.readlines()[1:]
    G = nx.DiGraph()
    for line in data:
        from_node, to_node, direction, weight = line.strip().split("\t")
        direction = int(direction)
        weight = float(weight)
        G.add_edge(from_node, to_node, weight=weight)
        if direction == 0:
            G.add_edge(to_node, from_node, weight=weight)
    return G

# ✅ B2: Tạo ma trận kề và danh sách hàng xóm
def build_adjacency(G, node_order):
    n = len(node_order)
    node_index = {node: i for i, node in enumerate(node_order)}
    A = np.zeros((n, n))
    neighbors = {i: [] for i in range(n)}
    for u, v, data in G.edges(data=True):
        i, j = node_index[u], node_index[v]
        A[i, j] += data.get("weight", 1.0)
        neighbors[j].append(i)
    return A, neighbors, node_index

# ✅ B3: Cập nhật trạng thái
def update_states_multi_beta(x, A, neighbors, beta_indices, beta_weights, fixed_nodes, EPSILON, DELTA):
    n = len(x)
    x_new = x.copy()
    for u in range(n):
        if u in fixed_nodes:
            continue
        influence = EPSILON * sum(A[v, u] * (x[v] - x[u]) for v in neighbors[u])
        beta_influence = DELTA * sum(w * (x[b] - x[u]) for b, w in zip(beta_indices, beta_weights[u]))
        x_new[u] = x[u] + influence + beta_influence
    return np.clip(x_new, -1000, 1000)

# ✅ B4: Mô phỏng một lượt Beta lên target node
def simulate_beta_on_target(G, beta_nodes, target_node, x_prev, alpha_idx, node_order, EPSILON, DELTA, MAX_ITER, TOL):
    all_nodes = node_order + [f"Beta{i}" for i in range(len(beta_nodes))]
    A, neighbors, node_index = build_adjacency(G, all_nodes)
    n = len(all_nodes)

    if x_prev.shape[0] != n:
        x_prev = np.pad(x_prev, (0, n - x_prev.shape[0]), mode="constant")

    x = x_prev.copy()
    beta_indices = []
    fixed_nodes = set()
    beta_weights = [[0] * len(beta_nodes) for _ in range(n)]

    for i, beta in enumerate(beta_nodes):
        beta_name = f"Beta{i}"
        beta_idx = node_index[beta_name]
        A[beta_idx, node_index[target_node]] = 1.0
        neighbors[node_index[target_node]].append(beta_idx)
        x[beta_idx] = -1
        beta_indices.append(beta_idx)
        fixed_nodes.add(beta_idx)
        beta_weights[node_index[target_node]][i] = 1.0

    for _ in range(MAX_ITER):
        x_new = update_states_multi_beta(x, A, neighbors, beta_indices, beta_weights, fixed_nodes, EPSILON, DELTA)
        if np.linalg.norm(x_new - x) < TOL:
            break
        x = x_new

    return x[:len(node_order)]

# ✅ B5: Tổng hỗ trợ
def compute_total_support(x_state, alpha_idx):
    return sum(1 if x > 0 else -1 if x < 0 else 0 for i, x in enumerate(x_state) if i != alpha_idx)

# ✅ Tính ToS cho 1 node Alpha
def simulate_one_alpha(alpha_node, G, node_order, node_index, EPSILON, DELTA, MAX_ITER, TOL, N_BETA):
    alpha_idx = node_index[alpha_node]
    x_state = np.zeros(len(node_order))
    x_state[alpha_idx] = 1

    for i in range(0, len(node_order), N_BETA):
        beta_nodes = node_order[i:i + N_BETA]
        if alpha_node in beta_nodes:
            continue
        x_state = simulate_beta_on_target(G, beta_nodes, beta_nodes[0], x_state, alpha_idx, node_order, EPSILON, DELTA, MAX_ITER, TOL)

    support = compute_total_support(x_state, alpha_idx)
    return {"Alpha_Node": alpha_node, "Total_Support": support}

# ✅ Hàm simulate chính

def simulate(file_path, EPSILON, DELTA, MAX_ITER, TOL, N_BETA, output_folder=None):
    G = import_network(file_path)
    node_order = list(G.nodes())
    A, neighbors, node_index = build_adjacency(G, node_order)

    results = Parallel(n_jobs=-1)(
        delayed(simulate_one_alpha)(alpha, G, node_order, node_index, EPSILON, DELTA, MAX_ITER, TOL, N_BETA)
        for alpha in node_order
    )
    return pd.DataFrame(results)

# ✅ Dùng thử độc lập
if __name__ == "__main__":
    df = simulate("../example_data/HGRN.txt", 0.1, 0.2, 50, 1e-4, 2)
    print(df.head())
