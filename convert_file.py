import csv
import json
import os

def csv_to_json(csv_file, json_file):
    # Kiểm tra xem file JSON đã tồn tại hay chưa, nếu có thì xóa
    if os.path.exists(json_file):
        os.remove(json_file)
    
    # Đọc file CSV
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        data = {}
        account_count = 1
        
        # Bỏ qua header (nếu có)
        next(reader, None)
        
        # Đọc từng dòng trong file CSV
        for row in reader:
            account_key = f"account_{account_count}"
            data[account_key] = {
                "url1": row[0],
                "url2": row[1],
                "username": row[2],
                "password": row[3]
            }
            account_count += 1
        
        # Ghi dữ liệu vào file JSON
        with open(json_file, mode='w', encoding='utf-8') as jsonf:
            json.dump(data, jsonf, indent=4, ensure_ascii=False)

# Ví dụ sử dụng hàm
csv_to_json('data_page.csv', 'account.json')
