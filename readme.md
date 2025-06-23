# Hướng dẫn cài đặt môi trường chạy mô hình cạnh tranh ngoài đa tác nhân

Đồ án này triển khai mô hình động lực học cạnh tranh ngoài đa tác nhân trên mạng sinh học nhằm xác định các gene mục tiêu điều trị ung thư. Để đảm bảo có thể chạy đúng toàn bộ mã nguồn, vui lòng làm theo các bước dưới đây để thiết lập môi trường.

## Bước 1: Cài đặt Anaconda

Nếu bạn chưa cài đặt Anaconda, có thể tải tại: [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)

Cài đặt phiên bản phù hợp với hệ điều hành của bạn (Windows / Linux / macOS).

---

## Bước 2: Tạo môi trường ảo

Mở terminal (Linux/macOS) hoặc Anaconda Prompt (Windows), tạo một môi trường mới tên là `multi_beta_env` như sau:

```bash
conda create -n multi_beta_env python=3.10 -y
conda activate multi_beta_env
