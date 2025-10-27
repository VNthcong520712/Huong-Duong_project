import os
from flask import (
    Flask, request, jsonify, render_template, 
    Blueprint, redirect, url_for, session, g,
    send_from_directory, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import datetime 
import re 

# --- Cài đặt ban đầu ---
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'BnHHnB4389sn--Padfd***!@@#hhhahf'

# Cấu hình cơ sở dữ liệu
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CẤU HÌNH UPLOAD ---
PRODUCT_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
app.config['PRODUCT_UPLOAD_FOLDER'] = PRODUCT_UPLOAD_FOLDER
GALLERY_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'gallery')
app.config['GALLERY_UPLOAD_FOLDER'] = GALLERY_UPLOAD_FOLDER
PAYMENT_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'payment')
app.config['PAYMENT_UPLOAD_FOLDER'] = PAYMENT_UPLOAD_FOLDER
PROOF_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'proofs')
app.config['PROOF_UPLOAD_FOLDER'] = PROOF_UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# --- Định nghĩa Model (Bảng) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True) 
    image_filename = db.Column(db.String(200), nullable=True) 
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_info = db.Column(db.Text, nullable=True, default='Thông tin về dự án...')
    phone = db.Column(db.String(50), nullable=True, default='0123456789')
    email = db.Column(db.String(100), nullable=True, default='contact@example.com')
    facebook = db.Column(db.String(255), nullable=True, default='https://facebook.com')

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    
class PaymentInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    bank_name = db.Column(db.String(100), nullable=True, default='Tên Ngân Hàng')
    account_number = db.Column(db.String(50), nullable=True, default='Số tài khoản')
    account_holder = db.Column(db.String(100), nullable=True, default='Tên chủ tài khoản')
    qr_code_filename = db.Column(db.String(200), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='cash') 
    status = db.Column(db.String(50), nullable=False, default='pending') 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    payment_proof_filename = db.Column(db.String(200), nullable=True)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False) 
    
    product = db.relationship('Product', lazy=True)
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


ADMIN_ACCOUNTS = {
    "000000001": "admin_hoahuongduong_1",
    "000000002": "admin_hoadaquy_2",
    "000000003": "admin_hoacanxa_3"
}

def initialize_data():
    with app.app_context():
        try:
            for phone, password in ADMIN_ACCOUNTS.items():
                admin_user = db.session.query(User).filter_by(phone=phone).first()
                if not admin_user:
                    print(f"[Admin Setup] Tạo tài khoản admin: {phone}")
                    hashed_password = generate_password_hash(password)
                    new_admin = User(phone=phone, password_hash=hashed_password)
                    db.session.add(new_admin)
            
            info = db.session.query(ContactInfo).filter_by(id=1).first()
            if not info:
                print("[Setup] Tạo thông tin liên hệ mặc định.")
                default_info = ContactInfo(
                    id=1,
                    project_info="Đây là thông tin mặc định về dự án. Admin có thể thay đổi.",
                    phone="0987654321",
                    email="admin@shop.com",
                    facebook="https://www.facebook.com/profile.php?id=61581942372273"
                )
                db.session.add(default_info)

            payment_info = db.session.query(PaymentInfo).filter_by(id=1).first()
            if not payment_info:
                print("[Setup] Tạo thông tin thanh toán mặc định.")
                default_payment = PaymentInfo(id=1)
                db.session.add(default_payment)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi khởi tạo dữ liệu: {e}")

# --- CÁC HÀM VALIDATION MỚI (SERVER-SIDE) ---
def validate_phone(phone):
    return re.match(r'^0\d{9}$', phone)

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password): 
        return False
    if not re.search(r'\d', password): 
        return False
    return True

# ====================================================================
# --- BLUEPRINT CHO TRANG QUẢN TRỊ (ADMIN) ---
# ====================================================================
quanly_bp = Blueprint('quanlybanhang', __name__, 
                      template_folder='templates',
                      static_folder='static')

# --- HÀM BẢO VỆ (DECORATOR) CHO ADMIN ---
# *** ĐÃ SỬA LỖI ***
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            # --- START MODIFICATION ---
            # Nếu là yêu cầu API (mong đợi JSON), trả về lỗi JSON 401
            # Thay vì redirect về trang HTML
            if request.path.startswith('/quanlybanhang/api/'):
                return jsonify({"message": "Phiên đăng nhập đã hết hạn. Vui lòng tải lại trang và đăng nhập lại."}), 401
            # --- END MODIFICATION ---
            
            # Giữ nguyên hành vi cũ cho các trang bình thường
            flash("Bạn cần đăng nhập với tư cách quản trị viên để truy cập trang này.", "error")
            return redirect(url_for('quanlybanhang.show_login_page'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Bạn cần đăng nhập để xem trang này.", "error")
            return redirect(url_for('quanlybanhang.show_login_page'))
        if session.get('is_admin'):
            flash("Trang này chỉ dành cho khách hàng.", "error")
            return redirect(url_for('shop.show_shop_page')) 
        return f(*args, **kwargs)
    return decorated_function

# --- TUYẾN ĐƯỜNG ADMIN: Đăng nhập / Đăng xuất ---
@quanly_bp.route('/')
def show_login_page():
    return render_template('login.html')

@quanly_bp.route('/register', methods=['POST'])
def register_api():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({"message": "Thiếu số điện thoại hoặc mật khẩu"}), 400

    if not validate_phone(phone):
        return jsonify({"message": "SĐT phải bắt đầu bằng 0 và có 10 chữ số."}), 400
    
    if not validate_password(password):
        return jsonify({"message": "Mật khẩu phải ít nhất 8 ký tự, chứa cả chữ và số."}), 400

    existing_user = db.session.query(User).filter_by(phone=phone).first()
    if existing_user:
        return jsonify({"message": "Số điện thoại đã tồn tại"}), 400
        
    hashed_password = generate_password_hash(password)
    new_user = User(phone=phone, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Đăng ký thành công!"}), 201

@quanly_bp.route('/login', methods=['POST'])
def login_api():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    user = db.session.query(User).filter_by(phone=phone).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Sai số điện thoại hoặc mật khẩu"}), 401
    
    is_admin = phone in ADMIN_ACCOUNTS
    
    session['user_id'] = user.id
    session['user_phone'] = user.phone
    session['is_admin'] = is_admin
    
    if is_admin:
        session.pop('cart', None) 

    return jsonify({"message": "Đăng nhập thành công!", "is_admin": is_admin }), 200

@quanly_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('shop.show_shop_page')) 

@quanly_bp.route('/request-reset', methods=['POST'])
def request_reset_api():
    data = request.json
    phone = data.get('phone')
    
    if not validate_phone(phone):
         return jsonify({"message": "SĐT không hợp lệ."}), 400

    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        return jsonify({"message": "Số điện thoại này không tồn tại"}), 404
        
    return jsonify({"message": "Đã tìm thấy SĐT, vui lòng tạo mật khẩu mới."}), 200

@quanly_bp.route('/reset-password', methods=['POST'])
def reset_password_api():
    data = request.json
    phone = data.get('phone')
    new_password = data.get('new_password')
    
    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        return jsonify({"message": "Lỗi: Không tìm thấy người dùng"}), 404

    if not validate_password(new_password):
        return jsonify({"message": "Mật khẩu mới phải ít nhất 8 ký tự, chứa cả chữ và số."}), 400
        
    if check_password_hash(user.password_hash, new_password):
        return jsonify({"message": "Mật khẩu mới không được trùng với mật khẩu cũ."}), 400
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "Đã cập nhật mật khẩu thành công!"}), 200


# --- TUYẾN ĐƯỜNG ADMIN: Các trang được bảo vệ ---
@quanly_bp.route('/main-page')
@admin_required
def main_page():
    return render_template('main.html')

@quanly_bp.route('/transaction')
@admin_required
def transaction_page():
    try:
        orders = db.session.query(Order).options(
            db.joinedload(Order.items).joinedload(OrderItem.product)
        ).order_by(Order.created_at.desc()).all()
    except Exception as e:
        print(f"Lỗi truy vấn đơn hàng: {e}")
        orders = []
    return render_template('transaction.html', orders=orders)

# *** START: THÊM ROUTE THỐNG KÊ MỚI ***
@quanly_bp.route('/statistics')
@admin_required
def statistics_page():
    try:
        # Truy vấn để thống kê doanh thu theo sản phẩm
        # Chỉ tính các đơn hàng đã 'confirmed' (xác nhận), 'shipped' (đang giao), 'delivered' (đã giao)
        stats_query = db.session.query(
            Product.name,
            db.func.sum(OrderItem.quantity).label('total_quantity_sold'),
            db.func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
        ).join(
            OrderItem, OrderItem.product_id == Product.id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.status.in_(['confirmed', 'shipped', 'delivered'])
        ).group_by(
            Product.name
        ).order_by(
            db.desc('total_revenue') # Sắp xếp theo doanh thu giảm dần
        ).all()

        # Tính tổng cộng
        total_revenue_all = sum(item.total_revenue for item in stats_query)
        total_items_all = sum(item.total_quantity_sold for item in stats_query)

        return render_template(
            'statistic.html', 
            stats_data=stats_query,
            total_revenue_all=total_revenue_all,
            total_items_all=total_items_all
        )

    except Exception as e:
        print(f"Lỗi khi truy vấn thống kê: {e}")
        flash(f"Không thể tải thống kê: {str(e)}", "error")
        return render_template('statistic.html', stats_data=[], total_revenue_all=0, total_items_all=0)
# *** END: THÊM ROUTE THỐNG KÊ MỚI ***

@quanly_bp.route('/products')
@admin_required
def products_page():
    products = Product.query.all()
    return render_template('products.html', products=products)

@quanly_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings_page():
    info = db.session.get(ContactInfo, 1) 
    payment_info = db.session.get(PaymentInfo, 1)

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        try:
            if form_type == 'contact':
                info.project_info = request.form.get('project_info')
                info.phone = request.form.get('phone')
                info.email = request.form.get('email')
                info.facebook = request.form.get('facebook')
                flash("Cập nhật thông tin liên hệ thành công!", "success")
                
            elif form_type == 'payment':
                payment_info.bank_name = request.form.get('bank_name')
                payment_info.account_holder = request.form.get('account_holder')
                payment_info.account_number = request.form.get('account_number')
                
                if 'qr_image' in request.files:
                    file = request.files['qr_image']
                    if file and file.filename != '' and allowed_file(file.filename):
                        if payment_info.qr_code_filename:
                            old_path = os.path.join(app.config['PAYMENT_UPLOAD_FOLDER'], payment_info.qr_code_filename)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                                
                        filename = secure_filename(file.filename)
                        save_path = os.path.join(app.config['PAYMENT_UPLOAD_FOLDER'], filename)
                        file.save(save_path)
                        payment_info.qr_code_filename = filename
                        
                flash("Cập nhật thông tin thanh toán thành công!", "success")

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi cập nhật: {e}", "error")
        return redirect(url_for('quanlybanhang.settings_page'))
        
    return render_template('settings.html', info=info, payment_info=payment_info)

@quanly_bp.route('/gallery', methods=['GET'])
@admin_required
def gallery_page():
    images = GalleryImage.query.all()
    return render_template('gallery.html', images=images)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@quanly_bp.route('/messages')
@admin_required
def messages_page():
    try:
        messages = db.session.query(Message).order_by(Message.created_at.desc()).all()
    except Exception as e:
        print(f"Lỗi truy vấn tin nhắn: {e}")
        messages = []
    return render_template('messages.html', messages=messages)

# --- TUYẾN ĐƯỜNG ADMIN: API ---

# *** ĐÃ SỬA LỖI ***
# API này giờ sẽ trả về JSON thay vì redirect
@quanly_bp.route('/api/gallery/add', methods=['POST'])
@admin_required
def add_gallery_image_api():
    # Đổi tên 'image_file' thành 'image' để khớp với JS (nếu cần, nhưng file gốc là 'image')
    # Kiểm tra file gốc gallery.html...
    # <input type="file" id="image_file" name="image_file" ...>
    # FormData sẽ dùng name, vậy key là 'image_file'
    # Sửa lại 'image' thành 'image_file' cho khớp
    
    if 'image_file' not in request.files:
        return jsonify({"message": "Không có tệp nào được gửi lên"}), 400
        
    file = request.files['image_file']
    description = request.form.get('image_description', '') # Khớp với name 'image_description'

    if file.filename == '':
        return jsonify({"message": "Chưa chọn tệp nào"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['GALLERY_UPLOAD_FOLDER'], filename)
        
        # Chống ghi đè file
        count = 1
        original_filename = filename
        while os.path.exists(save_path):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{count}{ext}"
            save_path = os.path.join(app.config['GALLERY_UPLOAD_FOLDER'], filename)
            count += 1
            
        file.save(save_path)
        
        new_image = GalleryImage(filename=filename, description=description)
        db.session.add(new_image)
        db.session.commit()
        
        # Trả về JSON chứa thông tin ảnh mới để JS render
        return jsonify({
            "message": "Thêm ảnh vào thư viện thành công!",
            "image": {
                "id": new_image.id,
                "filename": new_image.filename,
                "description": new_image.description,
                "url": url_for('quanlybanhang.serve_gallery_upload', filename=new_image.filename)
            }
        }), 201 # 201 = Đã tạo mới
    else:
        return jsonify({"message": "Loại tệp không hợp lệ (Chỉ chấp nhận .png, .jpg, .jpeg, .gif)"}), 400


@quanly_bp.route('/api/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def delete_gallery_image_api(image_id):
    image = db.session.get(GalleryImage, image_id)
    if not image:
        return jsonify({"message": "Không tìm thấy ảnh"}), 404
    try:
        image_path = os.path.join(app.config['GALLERY_UPLOAD_FOLDER'], image.filename)
        if os.path.exists(image_path):
            os.remove(image_path)
            
        db.session.delete(image)
        db.session.commit()
        return jsonify({"message": "Xóa ảnh thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {e}"}), 500


# --- TUYẾN ĐƯỜNG ADMIN: API Sản phẩm (CRUD) (CẬP NHẬT) ---
@quanly_bp.route('/api/products/add', methods=['POST'])
@admin_required
def add_product_api():
    # Sửa keys để khớp với form 'products.html'
    name = request.form.get('product_name')
    price = request.form.get('product_price')
    description = request.form.get('product_description')
    stock_quantity = request.form.get('product_stock', 0)
    image_file = request.files.get('product_image')

    # Trả về lỗi JSON
    if not name or not price or not image_file or not description or not stock_quantity:
        return jsonify({"message": "Thiếu thông tin sản phẩm (Tên, Giá, Kho, Mô tả, Ảnh)"}), 400
    
    if image_file.filename == '':
        return jsonify({"message": "Không có file ảnh nào được chọn"}), 400

    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        
        # Chống ghi đè file (giống gallery)
        save_path = os.path.join(app.config['PRODUCT_UPLOAD_FOLDER'], filename)
        count = 1
        original_filename = filename
        while os.path.exists(save_path):
            name_part, ext = os.path.splitext(original_filename)
            filename = f"{name_part}_{count}{ext}"
            save_path = os.path.join(app.config['PRODUCT_UPLOAD_FOLDER'], filename)
            count += 1
            
        image_file.save(save_path)

        new_product = Product(
            name=name, 
            price=float(price), 
            description=description,
            image_filename=filename,
            stock_quantity=int(stock_quantity)
        )
        db.session.add(new_product)
        db.session.commit()
        
        # Trả về JSON chứa thông tin sản phẩm mới
        return jsonify({
            "message": "Thêm sản phẩm thành công!",
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price,
                "description": new_product.description,
                "stock_quantity": new_product.stock_quantity,
                "image_url": url_for('quanlybanhang.serve_product_upload', filename=new_product.image_filename)
            }
        }), 201
    else:
        # Trả về lỗi JSON
        return jsonify({"message": "Loại file không hợp lệ"}), 400

@quanly_bp.route('/api/products/update-price', methods=['POST'])
@admin_required
def update_product_price_api():
    data = request.json
    product_id = data.get('product_id')
    new_price = data.get('new_price')
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
    try:
        product.price = float(new_price)
        db.session.commit()
        return jsonify({"message": "Cập nhật giá thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {e}"}), 500

@quanly_bp.route('/api/products/update-stock', methods=['POST'])
@admin_required
def update_product_stock_api():
    data = request.json
    product_id = data.get('product_id')
    new_stock = data.get('new_stock')
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
    try:
        product.stock_quantity = int(new_stock)
        db.session.commit()
        return jsonify({"message": "Cập nhật số lượng thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {e}"}), 500

@quanly_bp.route('/api/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product_api(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
    try:
        if product.image_filename:
            image_path = os.path.join(app.config['PRODUCT_UPLOAD_FOLDER'], product.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Xóa sản phẩm thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {e}"}), 500

@quanly_bp.route('/api/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status_api(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Không tìm thấy đơn hàng"}), 404
        
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['pending', 'confirmed', 'shipped', 'delivered', 'rejected']:
        return jsonify({"message": "Trạng thái không hợp lệ"}), 400
        
    try:
        # --- START SỬA LỖI: LOGIC HOÀN KHO ---
        
        old_status = order.status
        
        # Chỉ hoàn kho NẾU:
        # 1. Trạng thái MỚI là 'rejected' (Hủy)
        # 2. Trạng thái CŨ CHƯA PHẢI là 'rejected' (Tránh hoàn kho nhiều lần)
        if new_status == 'rejected' and old_status != 'rejected':
            
            # Duyệt qua từng mặt hàng trong đơn hàng
            for item in order.items:
                # Tìm sản phẩm tương ứng
                # (Sử dụng item.product vì đã có relationship)
                product = item.product 
                if product:
                    # Cộng trả số lượng
                    product.stock_quantity += item.quantity
                    db.session.add(product) # Đánh dấu sản phẩm để cập nhật
                else:
                    # Ghi log nếu sản phẩm không còn tồn tại
                    print(f"Cảnh báo: Không tìm thấy Product ID {item.product_id} để hoàn kho.")
        
        # --- END SỬA LỖI ---
        
        # Cập nhật trạng thái của đơn hàng
        order.status = new_status
        db.session.add(order)
        
        # Commit tất cả thay đổi (cả hoàn kho và trạng thái đơn hàng)
        db.session.commit()
        
        return jsonify({"message": f"Đã cập nhật đơn hàng #{order_id} thành {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi: {e}"}), 500


@quanly_bp.route('/api/messages/read/<int:message_id>', methods=['POST'])
@admin_required
def mark_message_read_api(message_id):
    msg = db.session.get(Message, message_id)
    if not msg:
        abort(404)
    try:
        msg.is_read = True
        db.session.commit()
        return jsonify({"message": "Đã đánh dấu đã đọc"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@quanly_bp.route('/api/messages/delete/<int:message_id>', methods=['POST'])
@admin_required
def delete_message_api(message_id):
    msg = db.session.get(Message, message_id)
    if not msg:
        abort(404)
    try:
        db.session.delete(msg)
        db.session.commit()
        return jsonify({"message": "Đã xóa tin nhắn"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# Route phục vụ file ảnh (Dùng chung)
@quanly_bp.route('/uploads/products/<path:filename>')
def serve_product_upload(filename):
    return send_from_directory(app.config['PRODUCT_UPLOAD_FOLDER'], filename)

@quanly_bp.route('/uploads/gallery/<path:filename>')
def serve_gallery_upload(filename):
    return send_from_directory(app.config['GALLERY_UPLOAD_FOLDER'], filename)

@quanly_bp.route('/uploads/payment/<path:filename>')
def serve_payment_upload(filename):
    return send_from_directory(app.config['PAYMENT_UPLOAD_FOLDER'], filename)
@quanly_bp.route('/uploads/proofs/<path:filename>')
def serve_proof_upload(filename): 
    return send_from_directory(app.config['PROOF_UPLOAD_FOLDER'], filename)

# ====================================================================
# --- BLUEPRINT MỚI CHO CỬA HÀNG (CUSTOMER) ---
# ====================================================================
shop_bp = Blueprint('shop', __name__, template_folder='templates')

@shop_bp.context_processor
def inject_cart_info():
    cart = session.get('cart', {})
    cart_total_items = sum(int(q) for q in cart.values())
    return dict(cart_total_items=cart_total_items)

@shop_bp.route('/')
def show_shop_page():
    search_query = request.args.get('search', '')
    
    try:
        query = db.session.query(Product)
        
        if search_query:
            query = query.filter(Product.name.ilike(f'%{search_query}%'))
            
        products = query.order_by(Product.name).all()
        
    except Exception as e:
        print(f"Lỗi khi truy vấn sản phẩm: {e}")
        products = []
        
    return render_template('shop_main.html', 
                           products=products, 
                           search_query=search_query) 

@shop_bp.route('/product/<int:product_id>')
def show_product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return "Không tìm thấy sản phẩm", 404
    return render_template('shop_product_detail.html', product=product)

@shop_bp.route('/pages')
def pages_page():
    images = GalleryImage.query.all()
    return render_template('shop_pages.html', images=images)

@shop_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            subject = request.form.get('subject')
            content = request.form.get('content')
            
            if not name or not phone or not content:
                flash("Vui lòng điền Họ tên, SĐT và Nội dung tin nhắn.", "error")
            else:
                new_message = Message(
                    name=name,
                    phone=phone,
                    email=email,
                    subject=subject,
                    content=content
                )
                db.session.add(new_message)
                db.session.commit()
                flash("Gửi tin nhắn thành công! Chúng tôi sẽ liên hệ lại với bạn sớm.", "success")
                return redirect(url_for('shop.contact_page')) 

        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi gửi tin nhắn: {e}", "error")

    info = db.session.get(ContactInfo, 1) 
    return render_template('shop_contact.html', info=info)

@shop_bp.route('/cart')
def show_cart_page():
    cart = session.get('cart', {})
    if not cart:
        return render_template('cart.html', items=[], total=0)
    
    product_ids = [int(pid) for pid in cart.keys()]
    products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
    
    cart_items = []
    total_price = 0
    
    products_dict = {p.id: p for p in products}
    
    for product_id_str, quantity_in_cart in cart.items():
        product_id = int(product_id_str)
        product = products_dict.get(product_id)
        quantity = int(quantity_in_cart)
        
        if product:
            if quantity > product.stock_quantity:
                quantity = product.stock_quantity 
                cart[product_id_str] = quantity 
            
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'subtotal': subtotal,
                'image_filename': product.image_filename,
                'stock': product.stock_quantity 
            })
            
    session['cart'] = cart 
    return render_template('cart.html', items=cart_items, total=total_price)

@shop_bp.route('/checkout', methods=['GET', 'POST'])
def show_checkout_page():
    if request.method == 'GET':
        flash("Vui lòng chọn sản phẩm từ giỏ hàng để thanh toán.", "error")
        return redirect(url_for('shop.show_cart_page'))
        
    selected_ids = request.form.getlist('selected_items')
    if not selected_ids:
        flash("Bạn chưa chọn sản phẩm nào để thanh toán.", "error")
        return redirect(url_for('shop.show_cart_page'))

    cart = session.get('cart', {})
    
    items_to_checkout = []
    total_price = 0
    order_details_for_session = {} 
    
    product_ids = [int(pid) for pid in selected_ids]
    products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
    products_dict = {p.id: p for p in products}

    for product_id_str in selected_ids:
        product_id = int(product_id_str)
        product = products_dict.get(product_id)
        quantity = int(cart.get(product_id_str, 0))
        
        if product and quantity > 0:
            if quantity > product.stock_quantity:
                 flash(f"Sản phẩm '{product.name}' không đủ số lượng.", "error")
                 return redirect(url_for('shop.show_cart_page'))
                 
            subtotal = product.price * quantity
            total_price += subtotal
            items_to_checkout.append({
                'id': product.id,
                'name': product.name,
                'quantity': quantity,
                'subtotal': subtotal
            })
            order_details_for_session[product_id_str] = quantity

    session['checkout_order'] = order_details_for_session
            
    payment_info = db.session.get(PaymentInfo, 1)
            
    return render_template('checkout.html', 
                           items=items_to_checkout, 
                           total=total_price, 
                           payment_info=payment_info)

@shop_bp.route('/order-history')
@customer_required 
def order_history_page():
    customer_id = session.get('user_id')
    
    orders = db.session.query(Order).options(
        db.joinedload(Order.items).joinedload(OrderItem.product)
    ).filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    return render_template('order_history.html', orders=orders)


# --- API GIỎ HÀNG (CẬP NHẬT) ---
@shop_bp.route('/api/cart/add', methods=['POST'])
def add_to_cart_api():
    data = request.json
    product_id_str = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    if not product_id_str or quantity < 1:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400
    
    if session.get('is_admin'):
         return jsonify({"message": "Admin không thể thêm hàng vào giỏ."}), 403
    
    product = db.session.get(Product, int(product_id_str))
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
        
    if product.stock_quantity <= 0:
        return jsonify({"message": "Sản phẩm này đã hết hàng"}), 400

    cart = session.get('cart', {}) 
    current_in_cart = int(cart.get(product_id_str, 0))
    
    if (current_in_cart + quantity) > product.stock_quantity:
        return jsonify({
            "message": f"Trong kho chỉ còn {product.stock_quantity} sản phẩm. Bạn đã có {current_in_cart} trong giỏ."
        }), 400
    
    cart[product_id_str] = current_in_cart + quantity
    session['cart'] = cart
    
    cart_total_items = sum(int(q) for q in cart.values())

    return jsonify({
        "message": f"Đã thêm {quantity} sản phẩm vào giỏ!",
        "cart_total_items": cart_total_items
    }), 200

@shop_bp.route('/api/cart/update', methods=['POST'])
def update_cart_quantity_api():
    data = request.json
    product_id_str = str(data.get('product_id'))
    new_quantity = int(data.get('quantity', 1))
    
    cart = session.get('cart', {})
    if product_id_str not in cart:
        return jsonify({"message": "Sản phẩm không có trong giỏ hàng"}), 404
        
    product = db.session.get(Product, int(product_id_str))
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
        
    if new_quantity < 1:
        new_quantity = 1
    if new_quantity > product.stock_quantity:
        new_quantity = product.stock_quantity
        message = f"Trong kho chỉ còn {product.stock_quantity} sản phẩm."
    else:
        message = "Cập nhật số lượng thành công."

    cart[product_id_str] = new_quantity
    session['cart'] = cart
    
    subtotal = product.price * new_quantity
    cart_total_items = sum(int(q) for q in cart.values())

    return jsonify({
        "message": message,
        "new_quantity": new_quantity,
        "subtotal": subtotal,
        "cart_total_items": cart_total_items
    }), 200

@shop_bp.route('/api/cart/remove', methods=['POST'])
def remove_from_cart_api():
    data = request.json
    product_id_str = str(data.get('product_id'))
    
    cart = session.get('cart', {})
    if product_id_str in cart:
        cart.pop(product_id_str) 
    
    session['cart'] = cart
    
    cart_total_items = sum(int(q) for q in cart.values())
    
    product_ids = [int(pid) for pid in cart.keys()]
    products = db.session.query(Product).filter(Product.id.in_(product_ids)).all()
    products_dict = {p.id: p for p in products}
    total_price = 0
    for pid_str, qty in cart.items():
        product = products_dict.get(int(pid_str))
        if product:
            total_price += product.price * int(qty)

    return jsonify({
        "message": "Đã xóa sản phẩm khỏi giỏ hàng.",
        "cart_total_items": cart_total_items,
        "total_price": total_price
    }), 200

@shop_bp.route('/api/checkout/process', methods=['POST'])
def process_checkout_api():
    order_details = session.get('checkout_order', {})
    if not order_details:
        return jsonify({"message": "Không có đơn hàng nào để xử lý."}), 400
        
    customer_name = request.form.get('name')
    customer_phone = request.form.get('phone')
    customer_address = request.form.get('address')
    payment_method = request.form.get('payment_method')
    
    if not customer_name or not customer_phone or not customer_address or not payment_method:
        return jsonify({"message": "Thiếu thông tin khách hàng hoặc phương thức thanh toán."}), 400

    try:
        products_to_update = [] 
        items_for_order = [] 
        total_price = 0

        for pid_str, qty in order_details.items():
            product_id = int(pid_str)
            quantity_needed = int(qty)
            
            product = db.session.get(Product, product_id)
            
            if not product:
                raise Exception(f"Sản phẩm ID {product_id} không tồn tại.")
                
            if product.stock_quantity < quantity_needed:
                raise Exception(f"Sản phẩm '{product.name}' không đủ số lượng (cần {quantity_needed}, chỉ còn {product.stock_quantity}).")
                
            products_to_update.append((product, quantity_needed))
            items_for_order.append((product, quantity_needed))
            total_price += product.price * quantity_needed
        
        new_order = Order(
            customer_id=session.get('user_id') if not session.get('is_admin') else None, 
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_price=total_price,
            payment_method=payment_method,
            status='pending' 
        )
        db.session.add(new_order)
        db.session.flush() # Quan trọng: Lấy new_order.id TẠI ĐÂY
        
        if payment_method == 'bank_transfer' and 'payment_proof' in request.files:
            file = request.files['payment_proof']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Đổi tên tệp để đảm bảo tính duy nhất
                save_filename = f"proof_{new_order.id}_{filename}"
                save_path = os.path.join(app.config['PROOF_UPLOAD_FOLDER'], save_filename)
                file.save(save_path)
                new_order.payment_proof_filename = save_filename

        for product, quantity_needed in items_for_order:
            product.stock_quantity -= quantity_needed
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity_needed,
                price_at_purchase=product.price 
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        cart = session.get('cart', {})
        for pid_str in order_details.keys():
            cart.pop(pid_str, None) 
        session['cart'] = cart
        
        session.pop('checkout_order', None)
        
        flash("Đặt hàng thành công! Cảm ơn bạn đã mua hàng.", "success")
        
        cart_total_items = sum(int(q) for q in cart.values())
        return jsonify({
            "message": "Đặt hàng thành công!",
            "cart_total_items": cart_total_items
        }), 200
        
    except Exception as e:
        db.session.rollback() 
        return jsonify({"message": f"Lỗi khi đặt hàng: {str(e)}"}), 400

# --- ĐĂNG KÝ BLUEPRINTS VỚI APP CHÍNH ---
app.register_blueprint(quanly_bp, url_prefix='/quanlybanhang')
app.register_blueprint(shop_bp, url_prefix='/') 

@app.route('/')
def index_redirect():
    return redirect(url_for('shop.show_shop_page'))

# --- Chạy ứng dụng ---
if __name__ == '__main__':
    os.makedirs(app.config['PRODUCT_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GALLERY_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PAYMENT_UPLOAD_FOLDER'], exist_ok=True) 
    os.makedirs(app.config['PROOF_UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    initialize_data() 
    app.run(host='0.0.0.0', debug=True, port=5000)
