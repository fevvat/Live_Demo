import os
# from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar'  # Güvenli anahtar önerilir

basedir = os.path.abspath(os.path.dirname(__file__))

# Veritabanı ayarı aynı kaldı
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'veritabani.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Resimlerin kaydedileceği klasörü statik klasör içindeki resimler olarak ayarla
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'resimler')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MODELLER
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(80), nullable=False)
    marka = db.Column(db.String(80), nullable=False)
    yil = db.Column(db.Integer)
    fiyat_gunluk = db.Column(db.Float)
    reservations = db.relationship('Reservation', backref='car', lazy=True)
    image_filename = db.Column(db.String(255))

    def __repr__(self):
        return f"<Araba {self.marka} {self.model}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    profile_image_url = db.Column(db.String(255), nullable=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    role = db.Column(db.String(5), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Kullanıcı {self.username}>"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    baslangic_tarihi = db.Column(db.DateTime, nullable=False)
    bitis_tarihi = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Rezervasyon {self.id} - Kullanıcı: {self.user_id}, Araç: {self.car_id}>"

# VERİTABANI OLUŞTUR
with app.app_context():
    db.create_all()

# ROUTELAR

@app.route('/')
def anasayfa():
    return render_template('index.html')

@app.route('/index')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return render_template('karsilama.html', username=user.username)
    flash('Lütfen giriş yapın.', 'warning')
    return redirect(url_for('kullanici_girisi'))

@app.route('/arabalarimiz')
def arabalarimiz():
    arabalar = Car.query.all()
    return render_template('arabalarimiz.html', arabalar=arabalar)


@app.route('/rezervasyonlarim')
def rezervasyonlarim():
    if 'user_id' not in session:
        flash('Lütfen giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))
    user = User.query.get(session['user_id'])
    rezervasyonlar = user.reservations
    return render_template('rezervasyonlarim.html', rezervasyonlar=rezervasyonlar)

@app.route('/iletisim')
def iletisim_sayfasi():
    return render_template('iletisim.html')

@app.route('/giris', methods=['GET', 'POST'])
def kullanici_girisi():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Lütfen e-posta ve şifre giriniz.', 'error')
            return render_template('giris.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['username'] = user.username
            session['role'] = user.role
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Giriş başarısız. E-posta veya şifre hatalı.', 'error')

    return render_template('giris.html')

@app.route('/cikis')
def kullanici_cikisi():
    session.clear()
    flash('Çıkış yapıldı.', 'success')
    return redirect(url_for('anasayfa'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_girisi():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.role == 'admin':
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = 'admin'
            flash('Admin girişi başarılı!', 'success')
            return redirect(url_for('admin_paneli'))
        else:
            flash('Admin girişi başarısız. Kullanıcı adı veya şifre hatalı.', 'error')
    return render_template('admin_giris.html')

@app.route('/admin/panel')
def admin_paneli():
    if 'user_id' in session and session.get('role') == 'admin':
        return render_template('admin_paneli.html')
    else:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('anasayfa'))

@app.route('/admin/araclar')
def admin_arac_listesi():
    if 'user_id' in session and session.get('role') == 'admin':
        araclar = Car.query.all()
        return render_template('admin_arac_listesi.html', araclar=araclar)
    else:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('anasayfa'))

@app.route('/admin/arac/ekle', methods=['GET', 'POST'])
def arac_ekleme_formu():
    if 'user_id' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            marka = request.form.get('marka')
            model = request.form.get('model')
            yil = request.form.get('yil')
            fiyat_gunluk = request.form.get('fiyat_gunluk')

            try:
                yil = int(yil)
                fiyat_gunluk = float(fiyat_gunluk)
            except:
                flash('Yıl ve fiyat alanları sayısal olmalıdır.', 'error')
                return redirect(url_for('arac_ekleme_formu'))

            image_filename = None
            if 'resim' in request.files:
                resim = request.files['resim']
                if resim and allowed_file(resim.filename):
                    filename = secure_filename(resim.filename)
                    resim.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
                else:
                    flash('Geçersiz dosya türü veya dosya yok.', 'error')
                    return redirect(url_for('arac_ekleme_formu'))

            yeni_araba = Car(marka=marka, model=model, yil=yil, fiyat_gunluk=fiyat_gunluk, image_filename=image_filename)
            db.session.add(yeni_araba)
            db.session.commit()
            flash('Araç başarıyla eklendi!', 'success')
            return redirect(url_for('admin_arac_listesi'))

        return render_template('arac_ekle.html')
    else:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('anasayfa'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_id' not in session:
        flash('Lütfen giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.city = request.form.get('city')
        user.district = request.form.get('district')
        user.address = request.form.get('address')

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_image_url = filename

        db.session.commit()
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('profil'))

    return render_template('profil.html', user=user)

@app.route('/kayit', methods=['GET', 'POST'])
def kayit_sayfasi():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')

        if not username or not email or not password:
            flash('Lütfen tüm zorunlu alanları doldurun.', 'error')
            return render_template('kayit.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Bu kullanıcı adı veya e-posta zaten kayıtlı.', 'error')
            return render_template('kayit.html')

        yeni_user = User(username=username, email=email, full_name=full_name)
        yeni_user.set_password(password)

        db.session.add(yeni_user)
        db.session.commit()
        flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
        return redirect(url_for('kullanici_girisi'))

    return render_template('kayit.html')

@app.route('/profil_detay', methods=['GET', 'POST'])
def profil_detay():
    user = get_current_user()
    if not user:
        flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.city = request.form.get('city')
        user.district = request.form.get('district')
        user.address = request.form.get('address')
        db.session.commit()
        flash('Profiliniz güncellendi.', 'success')
        return redirect(url_for('profil_detay'))

    return render_template('profil-detay.html', user=user)

def add_static_cars():
    # Örnek arabalar, sen statik HTML'deki arabalarına göre burayı düzenle
    cars_data = [
        {
            'marka': 'Citroen',
            'model': 'C3',
            'yil': 2020,
            'fiyat_gunluk': 300,
            'image_filename': 'f-citroen-c3.png'
        },
        {
            'marka': 'Fiat',
            'model': 'Egea',
            'yil': 2021,
            'fiyat_gunluk': 350,
            'image_filename': 'n-fiat-egea.png'
        },
        {
            'marka': 'Renault',
            'model': 'Clio',
            'yil': 2022,
            'fiyat_gunluk': 400,
            'image_filename': 'f-renault-clio.jpg'
        },
        {
            'marka': 'Volkswagen',
            'model': 'Golf',
            'yil': 2023,
            'fiyat_gunluk': 500,
            'image_filename': 'polo.png'
        },
        {
            'marka': 'BMW',
            'model': '3 Serisi',
            'yil': 2023,
            'fiyat_gunluk': 1000,
            'image_filename': 'bmw.png'
        },
        {
            'marka': 'Mercedes',
            'model': 'C Serisi',
            'yil': 2023,
            'fiyat_gunluk': 1200,
            'image_filename': 'c200.jpg'
        },
        {
            'marka': 'Audi',
            'model': 'A4',
            'yil': 2023,
            'fiyat_gunluk': 1100,
            'image_filename': 'audia6.png'
        },
        {
            'marka': 'Ford',
            'model': 'Focus',
            'yil': 2022,
            'fiyat_gunluk': 450,
            'image_filename': 'o-ford-focus.png'
        },
        {
            'marka': 'Hyundai',
            'model': 'i20',
            'yil': 2021,
            'fiyat_gunluk': 400,
            'image_filename': 'n-hyundai-i20.png'
        }
    ]

    for car_data in cars_data:
        existing_car = Car.query.filter_by(marka=car_data['marka'], model=car_data['model']).first()
        if not existing_car:
            yeni_araba = Car(**car_data)
            db.session.add(yeni_araba)
    db.session.commit()
    print("Statik arabalar veritabanına eklendi.")


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        add_static_cars()  # Statik arabaları ekle
    app.run(debug=True)

