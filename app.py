# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import pyodbc
# import os
# from werkzeug.utils import secure_filename
# import time

# app = Flask(__name__)
# CORS(app) 

# UPLOAD_FOLDER = 'static/uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB_CONNECTION_STRING = (
#     r'DRIVER={ODBC Driver 17 for SQL Server};'
#     r'SERVER=LAPTOP-2M82QJRG;' 
#     r'DATABASE=TonyDzungHouseDB;'
#     r'UID=sa;'
#     r'PWD=123;'
# )

# def get_db_connection():
#     return pyodbc.connect(DB_CONNECTION_STRING)

# # 1. LẤY danh sách phòng VÀ toàn bộ ảnh của phòng đó
# @app.route('/api/rooms', methods=['GET'])
# def get_rooms():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Lấy tất cả phòng
#         cursor.execute('SELECT * FROM Rooms ORDER BY Id DESC')
#         room_columns = [column[0] for column in cursor.description]
#         rooms = [dict(zip(room_columns, row)) for row in cursor.fetchall()]
        
#         # Lấy tất cả ảnh
#         cursor.execute('SELECT * FROM RoomImages')
#         img_columns = [column[0] for column in cursor.description]
#         images = [dict(zip(img_columns, row)) for row in cursor.fetchall()]
        
#         # Ghép ảnh vào đúng phòng
#         for room in rooms:
#             # Tạo một mảng 'Images' chứa các ảnh có RoomId trùng khớp
#             room['Images'] = [img for img in images if img['RoomId'] == room['Id']]

#         conn.close()
#         return jsonify(rooms)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 2. THÊM phòng mới
# @app.route('/api/rooms', methods=['POST'])
# def add_room():
#     try:
#         data = request.form 
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Bước 1: Thêm phòng và lấy ID của phòng vừa tạo
#         sql_room = '''INSERT INTO Rooms (Title, Price, Area, District, Address, Bedrooms, Features, Status)
#                       OUTPUT INSERTED.Id
#                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
#         cursor.execute(sql_room, (data['Title'], data['Price'], data['Area'], data['District'], 
#                                   data['Address'], data['Bedrooms'], data['Features'], data['Status']))
        
#         new_room_id = cursor.fetchone()[0] # Lấy ID
        
#         # Bước 2: Lưu các file ảnh và Insert vào bảng RoomImages
#         if 'imageFiles' in request.files:
#             files = request.files.getlist('imageFiles')
#             for index, file in enumerate(files):
#                 if file.filename != '':
#                     filename = str(int(time.time())) + '_' + secure_filename(file.filename)
#                     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                     img_url = f"http://localhost:5000/static/uploads/{filename}"
                    
#                     # Ảnh đầu tiên là ảnh chính (IsPrimary = 1)
#                     is_primary = 1 if index == 0 else 0 
                    
#                     sql_img = 'INSERT INTO RoomImages (RoomId, ImageUrl, IsPrimary) VALUES (?, ?, ?)'
#                     cursor.execute(sql_img, (new_room_id, img_url, is_primary))
#                     time.sleep(0.1)

#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Thêm phòng thành công!"}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 3. CẬP NHẬT phòng
# @app.route('/api/rooms/<int:id>', methods=['PUT'])
# def update_room(id):
#     try:
#         data = request.form
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Cập nhật thông tin phòng
#         sql = '''UPDATE Rooms SET Title=?, Price=?, Area=?, District=?, Address=?, 
#                  Bedrooms=?, Features=?, Status=? WHERE Id=?'''
#         cursor.execute(sql, (data['Title'], data['Price'], data['Area'], data['District'], 
#                              data['Address'], data['Bedrooms'], data['Features'], data['Status'], id))
        
#         # Nếu có upload ảnh mới, ta sẽ XÓA các link ảnh cũ trong DB và Thêm ảnh mới vào
#         if 'imageFiles' in request.files and request.files.getlist('imageFiles')[0].filename != '':
#             cursor.execute('DELETE FROM RoomImages WHERE RoomId=?', (id,))
            
#             files = request.files.getlist('imageFiles')
#             for index, file in enumerate(files):
#                 if file.filename != '':
#                     filename = str(int(time.time())) + '_' + secure_filename(file.filename)
#                     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                     img_url = f"http://localhost:5000/static/uploads/{filename}"
#                     is_primary = 1 if index == 0 else 0 
                    
#                     sql_img = 'INSERT INTO RoomImages (RoomId, ImageUrl, IsPrimary) VALUES (?, ?, ?)'
#                     cursor.execute(sql_img, (id, img_url, is_primary))
#                     time.sleep(0.1)

#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Cập nhật thành công!"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 4. XÓA phòng 
# @app.route('/api/rooms/<int:id>', methods=['DELETE'])
# def delete_room(id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         # Vì bạn đã dùng ON DELETE CASCADE trong DB, xóa phòng sẽ tự xóa ảnh trong bảng RoomImages
#         cursor.execute('DELETE FROM Rooms WHERE Id=?', (id,))
#         conn.commit()
#         conn.close()
#         return jsonify({"message": "Xóa thành công!"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# # API Đăng nhập cho Admin
# @app.route('/api/login', methods=['POST'])
# def login():
#     try:
#         data = request.json
#         username = data.get('username')
#         password = data.get('password')
        
#         # Tài khoản và mật khẩu mặc định (Bạn có thể đổi tùy ý)
#         if username == 'admin' and password == '123456':
#             # Trả về một mã token (chìa khóa) bí mật
#             return jsonify({"token": "tonydzung_secret_token_888", "message": "Đăng nhập thành công"}), 200
#         else:
#             return jsonify({"error": "Sai tài khoản hoặc mật khẩu!"}), 401
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import secrets



app = Flask(__name__)
CORS(app) 

app.secret_key = secrets.token_hex(16) # Tạo chìa khóa bảo mật cho Session
# ==========================================
# 1. CẤU HÌNH CLOUDINARY (LƯU ẢNH LÊN ĐÁM MÂY)
# ==========================================
cloudinary.config( 
  cloud_name = "dlrfr3l2u", 
  api_key = "244357886668169", 
  api_secret = "w8q3WzGcMw0AbrYxWY7McmXZJcQ" 
)

# ==========================================
# 2. CẤU HÌNH MYSQL 
# ==========================================
# DB_CONFIG = {
#     'host': 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
#     'user': 'root',
#     'password': '', 
#     'database': 'TonyDzungHouseDB'
# }
# DB_CONFIG = {
#     'host': 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
#     'port': 4000, 
#     'user': '2sPr4a2fvv6hnJs.root',
#     'password': 'ZDUpibQEnxtgdbh8',
#     'database': 'test' # TiDB mặc định tên database là 'test'
# }

# def get_db_connection():
#     return mysql.connector.connect(**DB_CONFIG)
# ==========================================
# 2. CẤU HÌNH MYSQL VỚI CONNECTION POOL (SIÊU TỐC)
# ==========================================
dbconfig = {
    'host': 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
    'port': 4000, 
    'user': '2sPr4a2fvv6hnJs.root',
    'password': 'ZDUpibQEnxtgdbh8',
    'database': 'test'
}

# Tạo sẵn một "hồ bơi" chứa 5 kết nối luôn mở tới Singapore
db_pool = pooling.MySQLConnectionPool(
    pool_name="tonydzung_pool",
    pool_size=5,
    pool_reset_session=True,
    **dbconfig
)

def get_db_connection():
    # Thay vì kết nối mới, ta chỉ việc rút 1 kết nối có sẵn từ hồ bơi ra xài (tốn 0.001 giây)
    return db_pool.get_connection()

# ==========================================
# 3. CÁC API XỬ LÝ (KHÔNG CẦN FOLDER STATIC NỮA)
# ==========================================

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        
        cursor.execute('SELECT * FROM Rooms ORDER BY Id DESC')
        rooms = cursor.fetchall()
        
        cursor.execute('SELECT * FROM RoomImages')
        images = cursor.fetchall()
        
        for room in rooms:
            room['Images'] = [img for img in images if img['RoomId'] == room['Id']]

        conn.close()
        return jsonify(rooms)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rooms', methods=['POST'])
def add_room():
    try:
        data = request.form 
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_room = '''INSERT INTO Rooms (Title, Price, Area, District, Address, Bedrooms, Features, Status)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(sql_room, (data['Title'], data['Price'], data['Area'], data['District'], 
                                  data['Address'], data['Bedrooms'], data['Features'], data['Status']))
        
        new_room_id = cursor.lastrowid 
        
        # --- ĐOẠN XỬ LÝ ẢNH MỚI: BẮN LÊN CLOUDINARY ---
        if 'imageFiles' in request.files:
            files = request.files.getlist('imageFiles')
            for index, file in enumerate(files):
                if file.filename != '':
                    # Đẩy ảnh lên Cloudinary
                    upload_result = cloudinary.uploader.upload(file, folder="tonydzung_rooms")
                    
                    # Nhận lại link ảnh xịn từ Cloudinary
                    img_url = upload_result.get('secure_url')
                    
                    is_primary = True if index == 0 else False 
                    
                    # Lưu cái link đó vào CSDL MySQL
                    sql_img = 'INSERT INTO RoomImages (RoomId, ImageUrl, IsPrimary) VALUES (%s, %s, %s)'
                    cursor.execute(sql_img, (new_room_id, img_url, is_primary))

        conn.commit()
        conn.close()
        return jsonify({"message": "Thêm phòng thành công!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rooms/<int:id>', methods=['PUT'])
def update_room(id):
    try:
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = '''UPDATE Rooms SET Title=%s, Price=%s, Area=%s, District=%s, Address=%s, 
                 Bedrooms=%s, Features=%s, Status=%s WHERE Id=%s'''
        cursor.execute(sql, (data['Title'], data['Price'], data['Area'], data['District'], 
                             data['Address'], data['Bedrooms'], data['Features'], data['Status'], id))
        
        if 'imageFiles' in request.files and request.files.getlist('imageFiles')[0].filename != '':
            cursor_dict = conn.cursor(dictionary=True)
            cursor_dict.execute('SELECT ImageUrl FROM RoomImages WHERE RoomId=%s', (id,))
            old_images = cursor_dict.fetchall()
            
            for img in old_images:
                try:
                    url = img['ImageUrl']
                    parts = url.split('/')
                    public_id = f"{parts[-2]}/{parts[-1].split('.')[0]}"
                    cloudinary.uploader.destroy(public_id) # Tiêu hủy ảnh cũ
                except:
                    pass
            cursor.execute('DELETE FROM RoomImages WHERE RoomId=%s', (id,))
            
            files = request.files.getlist('imageFiles')
            for index, file in enumerate(files):
                if file.filename != '':
                    upload_result = cloudinary.uploader.upload(file, folder="tonydzung_rooms")
                    img_url = upload_result.get('secure_url')
                    is_primary = True if index == 0 else False 
                    
                    sql_img = 'INSERT INTO RoomImages (RoomId, ImageUrl, IsPrimary) VALUES (%s, %s, %s)'
                    cursor.execute(sql_img, (id, img_url, is_primary))

        conn.commit()
        conn.close()
        return jsonify({"message": "Cập nhật thành công!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rooms/<int:id>', methods=['DELETE'])
def delete_room(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        
        # TÌM VÀ XÓA ẢNH TRÊN CLOUDINARY TRƯỚC
        cursor.execute('SELECT ImageUrl FROM RoomImages WHERE RoomId=%s', (id,))
        old_images = cursor.fetchall()
        
        for img in old_images:
            try:
                url = img['ImageUrl']
                # Cắt URL để lấy public_id 
                parts = url.split('/')
                folder = parts[-2] # Lấy tên thư mục
                filename = parts[-1].split('.')[0] # Lấy tên file bỏ đuôi .jpg
                public_id = f"{folder}/{filename}"
                
                # Gọi Cloudinary xóa file gốc
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print("Lỗi khi xóa ảnh Cloudinary:", e) # Bỏ qua nếu lỗi để DB vẫn được xóa

        # SAU ĐÓ XÓA TRONG DATABASE (MySQL)
        cursor = conn.cursor() # Đổi lại cursor bình thường
        cursor.execute('DELETE FROM Rooms WHERE Id=%s', (id,))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Đã xóa phòng và dọn sạch ảnh trên Cloudinary!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/api/login', methods=['POST'])
# def login():
#     try:
#         data = request.json
#         username = data.get('username')
#         password = data.get('password')
        
#         if username == 'admin' and password == '123456':
#             return jsonify({"token": "tonydzung_secret_token_888", "message": "Đăng nhập thành công"}), 200
#         else:
#             return jsonify({"error": "Sai tài khoản hoặc mật khẩu!"}), 401
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
# --- API ĐĂNG NHẬP (ĐÃ NÂNG CẤP ĐỂ ĐỌC MẬT KHẨU MÃ HÓA) ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Users WHERE Username = %s', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Kiểm tra: Nếu là pass mã hóa thì dùng hàm check, nếu là pass cũ thì so sánh bằng
        is_valid = False
        if user['Password'].startswith('scrypt:') or user['Password'].startswith('pbkdf2:'):
            is_valid = check_password_hash(user['Password'], password)
        else:
            is_valid = (user['Password'] == password) # Dành cho pass 'temp_password' ban đầu

        if is_valid:
            return jsonify({"message": "Đăng nhập thành công", "token": "login_success_secure"}), 200
    
    return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401


# --- API ĐỔI MẬT KHẨU MỚI ---
@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Users WHERE Username = %s', (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "Không tìm thấy tài khoản!"}), 404

    # 1. Kiểm tra mật khẩu cũ có đúng không
    is_valid = False
    if user['Password'].startswith('scrypt:') or user['Password'].startswith('pbkdf2:'):
        is_valid = check_password_hash(user['Password'], old_password)
    else:
        is_valid = (user['Password'] == old_password)

    if not is_valid:
        conn.close()
        return jsonify({"error": "Mật khẩu cũ không chính xác!"}), 401

    # 2. Mã hóa mật khẩu mới
    hashed_new_password = generate_password_hash(new_password)

    # 3. Lưu vào Database
    cursor.execute('UPDATE Users SET Password = %s WHERE Username = %s', (hashed_new_password, username))
    conn.commit()
    conn.close()

    return jsonify({"message": "Đổi mật khẩu thành công!"}), 200
if __name__ == '__main__':
    app.run(debug=True, port=5000)

