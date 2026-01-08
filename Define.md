# Định nghĩa các thư viện Python

## 1. subprocess
Thư viện `subprocess` cho phép tạo và quản lý các tiến trình con (child processes) từ Python. Nó cho phép:
- Chạy các lệnh shell hoặc chương trình bên ngoài
- Tương tác với stdin, stdout, stderr của các tiến trình
- Kiểm soát đầu vào và đầu ra của các lệnh hệ thống
- Thay thế cho các module cũ như `os.system()`, `os.spawn*()`

**Ví dụ sử dụng:**
```python
import subprocess
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(result.stdout)
```

## 2. argparse
Thư viện `argparse` cung cấp cách dễ dàng để phân tích các đối số dòng lệnh (command-line arguments). Nó giúp:
- Định nghĩa các tham số mà script nhận vào từ terminal
- Tự động tạo thông báo trợ giúp (help message)
- Xác thực kiểu dữ liệu của đối số
- Hỗ trợ các loại đối số: positional, optional, flags

**Ví dụ sử dụng:**
```python
import argparse
parser = argparse.ArgumentParser(description='Mô tả chương trình')
parser.add_argument('--input', help='File đầu vào')
args = parser.parse_args()
```

## 3. json
Thư viện `json` cung cấp các công cụ để làm việc với dữ liệu JSON (JavaScript Object Notation). Nó cho phép:
- Chuyển đổi đối tượng Python thành chuỗi JSON (serialization)
- Chuyển đổi chuỗi JSON thành đối tượng Python (deserialization)
- Đọc và ghi file JSON
- Xử lý dữ liệu có cấu trúc dạng key-value

**Ví dụ sử dụng:**
```python
import json
data = {'name': 'Python', 'version': 3.9}
json_string = json.dumps(data)
parsed_data = json.loads(json_string)
```

## 4. os
Thư viện `os` cung cấp giao diện để tương tác với hệ điều hành. Nó cho phép:
- Truy cập các biến môi trường
- Thực hiện các thao tác với file và thư mục
- Quản lý đường dẫn (path operations)
- Chạy lệnh hệ thống (deprecated, nên dùng subprocess)
- Lấy thông tin về hệ thống

**Ví dụ sử dụng:**
```python
import os
current_dir = os.getcwd()
os.chdir('/path/to/directory')
env_var = os.environ.get('HOME')
```
