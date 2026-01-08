# Định nghĩa các thư viện Python

## 1. subprocess
Thư viện `subprocess` cho phép tạo và quản lý các tiến trình con (child processes) từ Python. Nó cho phép:
- Chạy các lệnh shell hoặc chương trình bên ngoài
- Tương tác với stdin, stdout, stderr của các tiến trình
- Kiểm soát đầu vào và đầu ra của các lệnh hệ thống
- Thay thế cho các module cũ như `os.system()`, `os.spawn*()`

## 2. argparse
Thư viện `argparse` cung cấp cách dễ dàng để phân tích các đối số dòng lệnh (command-line arguments). Nó giúp:
- Định nghĩa các tham số mà script nhận vào từ terminal
- Tự động tạo thông báo trợ giúp (help message)
- Xác thực kiểu dữ liệu của đối số
- Hỗ trợ các loại đối số: positional, optional, flags

## 3. json
Thư viện `json` cung cấp các công cụ để làm việc với dữ liệu JSON (JavaScript Object Notation). Nó cho phép:
- Chuyển đổi đối tượng Python thành chuỗi JSON (serialization)
- Chuyển đổi chuỗi JSON thành đối tượng Python (deserialization)
- Đọc và ghi file JSON
- Xử lý dữ liệu có cấu trúc dạng key-value

## 4. os
Thư viện `os` cung cấp giao diện để tương tác với hệ điều hành. Nó cho phép:
- Truy cập các biến môi trường
- Thực hiện các thao tác với file và thư mục
- Quản lý đường dẫn (path operations)
- Chạy lệnh hệ thống (deprecated, nên dùng subprocess)
- Lấy thông tin về hệ thống

---

# Định nghĩa các tham số Nmap

## -sS (SYN Scan / Stealth Scan)
Tham số `-sS` thực hiện SYN scan (còn gọi là half-open scan hoặc stealth scan):
- Gửi các gói SYN đến các cổng mục tiêu
- Nếu cổng mở, máy đích sẽ trả về SYN-ACK
- Nmap sẽ gửi RST để đóng kết nối mà không hoàn tất handshake
- Ưu điểm: Nhanh, ít để lại log, khó phát hiện hơn TCP connect scan
- Yêu cầu quyền root/administrator để sử dụng
- Đây là kiểu scan mặc định khi chạy với quyền root

**Ví dụ sử dụng:**
```bash
nmap -sS 192.168.1.1
```

## -sV (Version Detection)
Tham số `-sV` kích hoạt chế độ phát hiện phiên bản dịch vụ:
- Xác định các dịch vụ và phiên bản đang chạy trên các cổng mở
- Gửi các probe packets đặc biệt để khớp với signature của các dịch vụ
- Phân tích phản hồi để xác định tên và phiên bản dịch vụ
- Hữu ích để tìm lỗ hổng bảo mật cụ thể theo phiên bản
- Có thể mất nhiều thời gian hơn so với port scan thông thường

**Ví dụ sử dụng:**
```bash
nmap -sV 192.168.1.1
```

## -O (OS Detection)
Tham số `-O` kích hoạt chế độ phát hiện hệ điều hành:
- Phân tích các đặc điểm của network stack để xác định OS
- Gửi các probe packets và phân tích TCP/IP fingerprint
- So sánh với database các OS fingerprints
- Yêu cầu quyền root/administrator
- Kết hợp với `-sV` để có thông tin đầy đủ về mục tiêu
- Kết quả có thể không chính xác 100%, đặc biệt với các OS mới

**Ví dụ sử dụng:**
```bash
nmap -O 192.168.1.1
```

## Output XML hoặc Grepable
Nmap cung cấp các định dạng đầu ra khác nhau để xử lý và phân tích:

### XML Output (-oX)
- Định dạng XML chuẩn, dễ parse bằng các công cụ tự động
- Chứa đầy đủ thông tin chi tiết về scan
- Hỗ trợ tốt cho việc xử lý bằng script và tích hợp với các tool khác
- Có thể dùng với `-oX filename.xml` hoặc `-oX -` để xuất ra stdout

**Ví dụ sử dụng:**
```bash
nmap -sS -sV -O -oX output.xml 192.168.1.1
```

### Grepable Output (-oG)
- Định dạng một dòng cho mỗi host, dễ xử lý bằng grep, awk, sed
- Tất cả thông tin trên một dòng, ngăn cách bởi tab
- Thuận tiện cho việc lọc và tìm kiếm nhanh
- Ít chi tiết hơn XML nhưng dễ đọc và xử lý hơn
- Có thể dùng với `-oG filename.txt` hoặc `-oG -` để xuất ra stdout

**Ví dụ sử dụng:**
```bash
nmap -sS -sV -oG output.txt 192.168.1.1
grep "80/open" output.txt
```
