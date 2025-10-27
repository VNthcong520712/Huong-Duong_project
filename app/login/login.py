import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# --- Cài đặt ban đầu ---
app = Flask(__name__)
# Kích hoạt CORS để cho phép tệp HTML (từ domain khác) gọi đến API này
CORS(app)

# Cấu hình cơ sở dữ liệu (sử dụng SQLite cho đơn giản)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Định nghĩa Model (Bảng) cho Người dùng ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<User {self.phone}>'

# --- Cấu hình Admin ---
# Định nghĩa 3 tài khoản admin bạn muốn tạo
ADMIN_ACCOUNTS = {
    "100000001": "Hradmin42", # SĐT admin 1 và mật khẩu
    "100000002": "Bkadmin92", # SĐT admin 2 và mật khẩu
    "100000003": "Jeadmin32"  # SĐT admin 3 và mật khẩu
}

def initialize_admins():
    """Kiểm tra và tạo các tài khoản admin nếu chúng chưa tồn tại."""
    # Cần app_context để thao tác với DB bên ngoài một request
    with app.app_context():
        try:
            for phone, password in ADMIN_ACCOUNTS.items():
                admin_user = db.session.query(User).filter_by(phone=phone).first()
                if not admin_user:
                    print(f"[Admin Setup] Tạo tài khoản admin: {phone}")
                    hashed_password = generate_password_hash(password)
                    new_admin = User(phone=phone, password_hash=hashed_password)
                    db.session.add(new_admin)
                else:
                    print(f"[Admin Setup] Tài khoản admin {phone} đã tồn tại.")
            
            # Commit tất cả thay đổi (nếu có)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi khởi tạo admin: {e}")

# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    """Endpoint để đăng ký người dùng mới."""
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({"message": "Thiếu số điện thoại hoặc mật khẩu"}), 400

    # Kiểm tra xem SĐT đã tồn tại chưa
    # SỬA LỖI: Dùng filter_by(phone=phone) thay vì .get()
    existing_user = db.session.query(User).filter_by(phone=phone).first()
    if existing_user:
        return jsonify({"message": "Số điện thoại đã tồn tại"}), 400

    # Mã hóa mật khẩu
    hashed_password = generate_password_hash(password)
    
    # Tạo người dùng mới và lưu vào DB
    new_user = User(phone=phone, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Đăng ký thành công!"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Endpoint để đăng nhập."""
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({"message": "Thiếu số điện thoại hoặc mật khẩu"}), 400

    # Tìm người dùng
    # SỬA LỖI: Dùng filter_by(phone=phone) thay vì .get()
    user = db.session.query(User).filter_by(phone=phone).first()

    # Kiểm tra người dùng và mật khẩu
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Sai số điện thoại hoặc mật khẩu"}), 401

    # Đăng nhập thành công (Trong ứng dụng thực tế, bạn sẽ tạo một JWT token ở đây)
    return jsonify({"message": "Đăng nhập thành công!"}), 200

@app.route('/main-page')
def main_page():
    """Trang chính sau khi đăng nhập thành công."""
    # Sử dụng render_template_string để trả về HTML đơn giản
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <title>Trang Chính</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 flex items-center justify-center h-screen">
            <div class="text-center p-10 bg-white rounded-lg shadow-lg">
                <h1 class="text-3xl font-bold text-indigo-600">Chào mừng bạn đã trở lại!</h1>
                <p class="text-gray-700 mt-4">Bạn đã đăng nhập thành công vào trang chính.</p>
                <a href="#" onclick="alert('Đã đăng xuất!');" 
                   class="mt-6 inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
                   Đăng xuất (Giả lập)
                </a>
            </div>
        </body>
        </html>
    ''')

# --- Chạy ứng dụng ---
if __name__ == '__main__':
    # Tạo cơ sở dữ liệu nếu chưa tồn tại
    with app.app_context():
        db.create_all()

    # Khởi tạo các tài khoản admin (chạy sau khi db.create_all())
    initialize_admins()

    # Chạy máy chủ Flask
    # debug=True sẽ tự động khởi động lại máy chủ khi có thay đổi
    app.run(debug=True, port=5000)

