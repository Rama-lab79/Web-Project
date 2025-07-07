from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeSerializer
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

# Hash
s = URLSafeSerializer("SECRET_KEY")
id_hashed = s.dumps(123)
print(id_hashed)
id_asli = s.loads(id_hashed)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'message': self.message,
            'date': self.date
        }


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='user')  # ⬅️ Tambahan role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PaketUmroh(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    durasi = db.Column(db.Integer, nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Inisialisasi DB & Admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='khodimulharamain').first():
        admin = User(username='khodimulharamain',
                     role='admin')  # ⬅️ role=admin
        admin.set_password('khodimulharamain123')
        db.session.add(admin)
        db.session.commit()

# Routes Publik


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/produk')
def produk():
    paket_umroh = PaketUmroh.query.all()
    return render_template('produk.html', paket_umroh=paket_umroh)


@app.route('/tentang')
def tentang():
    return render_template('tentang.html')


@app.route('/galeri-jamaah')
def galeri_jamaah():
    foto_list = []
    img_dir = os.path.join(app.static_folder, 'img')
    if os.path.exists(img_dir):
        foto_list = sorted(
            [f for f in os.listdir(img_dir) if f.startswith(
                'd') and f.endswith('.jpg')],
            key=lambda x: os.path.getctime(os.path.join(img_dir, x)),
            reverse=True
        )
    return render_template('galeri-jamaah.html', foto_list=foto_list)


@app.route('/testimoni')
def testimoni():
    try:
        all_testimonials = Testimonial.query.all()
        sorted_testimonials = sorted(all_testimonials, key=lambda x: datetime.strptime(
            x.date, '%d %B %Y'), reverse=True)
    except Exception as e:
        print(f"Error sorting testimonials: {e}")
        sorted_testimonials = Testimonial.query.all()

    return render_template('testimoni.html', testimonials=sorted_testimonials)

# Login / Logout


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_paket'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_paket'))
        flash('Username atau password salah', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin Area


@app.route('/admin/paket')
@login_required
def admin_paket():
    paket_umroh = PaketUmroh.query.all()
    return render_template('admin/paket.html', paket_umroh=paket_umroh)


@app.route('/admin/galeri')
@login_required
def admin_galeri():
    foto_list = []
    img_dir = os.path.join(app.static_folder, 'img')
    if os.path.exists(img_dir):
        foto_list = [f for f in os.listdir(
            img_dir) if f.startswith('d') and f.endswith('.jpg')]
    return render_template('admin/galeri.html', foto_list=foto_list)


@app.route('/admin/tambah_paket', methods=['POST'])
@login_required
def tambah_paket():
    nama = request.form.get('nama')
    durasi = request.form.get('durasi')
    deskripsi = request.form.get('deskripsi')
    harga = request.form.get('harga')
    file = request.files.get('file')

    filename = None
    if file:
        img_dir = os.path.join(app.static_folder, 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        filename = f"paket_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        file.save(os.path.join(img_dir, filename))

    paket = PaketUmroh(
        nama=nama,
        durasi=int(durasi),
        deskripsi=deskripsi,
        harga=int(harga),
        image=filename or 'default.jpg'
    )
    db.session.add(paket)
    db.session.commit()

    return jsonify({'status': 'success'})


@app.route('/admin/upload_foto', methods=['POST'])
@login_required
def upload_foto():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})

    if file:
        img_dir = os.path.join(app.static_folder, 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        existing_files = [f for f in os.listdir(
            img_dir) if f.startswith('d') and f.endswith('.jpg')]
        next_num = len(existing_files) + 1
        filename = f"d{next_num}.jpg"

        file.save(os.path.join(img_dir, filename))
        return jsonify({'status': 'success', 'filename': filename})


@app.route('/admin/hapus_foto', methods=['POST'])
@login_required
def hapus_foto():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({'status': 'error', 'message': 'Nama file tidak diberikan'}), 400

    filepath = os.path.join(app.static_folder, 'img', filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Gagal menghapus file: {e}'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'File tidak ditemukan'}), 404

# API Testimoni


@app.route('/submit_testimonial', methods=['POST'])
def submit_testimonial():
    data = request.json

    bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
             'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    now = datetime.now()
    date_str = f"{now.day} {bulan[now.month - 1]} {now.year}"

    new_testimonial = Testimonial(
        name=data['name'],
        title=data['title'],
        message=data['message'],
        date=date_str
    )
    db.session.add(new_testimonial)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Testimonial berhasil dikirim!', 'testimonial': new_testimonial.to_dict()})


@app.route('/delete_testimonial/<int:id>', methods=['DELETE'])
@login_required
def delete_testimonial(id):
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Hanya admin yang boleh menghapus'}), 403

    testimonial = Testimonial.query.get_or_404(id)
    db.session.delete(testimonial)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Testimonial berhasil dihapus'})


@app.route('/update_testimonial/<int:id>', methods=['PUT'])
def update_testimonial(id):
    data = request.json
    testimonial = Testimonial.query.get_or_404(id)
    testimonial.name = data['name']
    testimonial.title = data['title']
    testimonial.message = data['message']
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Testimonial berhasil diperbarui', 'testimonial': testimonial.to_dict()})


@app.route("/user/<token>")
def user_profile(token):
    try:
        user_id = s.loads(token)
        return f"User ID: {user_id}"
    except:
        return "Invalid link", 400

if __name__ == '__main__':
    app.run(debug=True)
