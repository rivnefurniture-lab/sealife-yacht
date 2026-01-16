"""
Sea Life Yacht School - Main Application
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sealife-yacht-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sealife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Telegram settings
app.config['TG_CHANNEL'] = 'sealife_yachtschool'  # Telegram channel for news/updates
app.config['TG_CONTACT'] = 'a_liudvichuk'          # Telegram contact for direct messages/requests

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============== MODELS ==============

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_uk = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_uk = db.Column(db.Text)
    description_en = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Integer, default=0)
    discount_until = db.Column(db.Date)
    location_uk = db.Column(db.String(200))
    location_en = db.Column(db.String(200))
    trip_type = db.Column(db.String(50))  # course, trip, expedition
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    max_participants = db.Column(db.Integer, default=10)
    image = db.Column(db.String(300))
    highlights_uk = db.Column(db.Text)  # JSON array
    highlights_en = db.Column(db.Text)  # JSON array
    included_uk = db.Column(db.Text)  # What's included
    included_en = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_current_price(self):
        if self.discount_percent and self.discount_until:
            if date.today() <= self.discount_until:
                return self.price * (1 - self.discount_percent / 100)
        return self.price
    
    def has_active_discount(self):
        if self.discount_percent and self.discount_until:
            return date.today() <= self.discount_until
        return False

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_uk = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    excerpt_uk = db.Column(db.Text)
    excerpt_en = db.Column(db.Text)
    content_uk = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300))
    tags = db.Column(db.String(500))  # Comma-separated
    meta_description_uk = db.Column(db.String(300))
    meta_description_en = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300), nullable=False)
    caption_uk = db.Column(db.String(300))
    caption_en = db.Column(db.String(300))
    category = db.Column(db.String(50))  # trips, courses, lifestyle
    is_featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    message = db.Column(db.Text)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============== LOGIN ==============

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ============== CONTEXT PROCESSOR ==============

@app.context_processor
def inject_globals():
    lang = request.args.get('lang', session.get('lang', 'uk'))
    session['lang'] = lang
    return {
        'lang': lang,
        'current_year': datetime.now().year
    }

# ============== PUBLIC ROUTES ==============

@app.route('/')
def home():
    lang = session.get('lang', 'uk')
    trips = Trip.query.filter_by(is_active=True).order_by(Trip.start_date).limit(6).all()
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    gallery = GalleryItem.query.filter_by(is_featured=True).order_by(GalleryItem.order).limit(8).all()
    return render_template('pages/home.html', trips=trips, posts=posts, gallery=gallery)

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/trips')
def trips():
    trip_type = request.args.get('type', 'all')
    if trip_type == 'all':
        trips = Trip.query.filter_by(is_active=True).order_by(Trip.start_date).all()
    else:
        trips = Trip.query.filter_by(is_active=True, trip_type=trip_type).order_by(Trip.start_date).all()
    return render_template('pages/trips.html', trips=trips, current_type=trip_type)

@app.route('/trip/<int:trip_id>')
def trip_detail(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    related = Trip.query.filter(Trip.id != trip_id, Trip.is_active == True).limit(3).all()
    return render_template('pages/trip_detail.html', trip=trip, related=related)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag')
    if tag:
        posts = BlogPost.query.filter(BlogPost.is_published == True, BlogPost.tags.contains(tag)).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9)
    else:
        posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('pages/blog.html', posts=posts, current_tag=tag)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.views += 1
    db.session.commit()
    related = BlogPost.query.filter(BlogPost.id != post.id, BlogPost.is_published == True).limit(3).all()
    return render_template('pages/blog_post.html', post=post, related=related)

@app.route('/gallery')
def gallery():
    category = request.args.get('category', 'all')
    if category == 'all':
        items = GalleryItem.query.order_by(GalleryItem.order, GalleryItem.created_at.desc()).all()
    else:
        items = GalleryItem.query.filter_by(category=category).order_by(GalleryItem.order).all()
    return render_template('pages/gallery.html', items=items, current_category=category)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contact = ContactRequest(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            message=request.form.get('message'),
            trip_id=request.form.get('trip_id') or None
        )
        db.session.add(contact)
        db.session.commit()
        flash('Дякуємо! Ми зв\'яжемося з вами найближчим часом.' if session.get('lang') == 'uk' else 'Thank you! We will contact you soon.', 'success')
        return redirect(url_for('contact'))
    trips = Trip.query.filter_by(is_active=True).all()
    return render_template('pages/contact.html', trips=trips)

@app.route('/set-lang/<lang>')
def set_lang(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

# ============== ADMIN ROUTES ==============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        password = request.form.get('password')
        admin = Admin.query.first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Невірний пароль', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'trips': Trip.query.count(),
        'posts': BlogPost.query.count(),
        'gallery': GalleryItem.query.count(),
        'contacts': ContactRequest.query.filter_by(is_read=False).count()
    }
    recent_contacts = ContactRequest.query.order_by(ContactRequest.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, contacts=recent_contacts)

# Admin - Trips
@app.route('/admin/trips')
@login_required
def admin_trips():
    trips = Trip.query.order_by(Trip.start_date.desc()).all()
    return render_template('admin/trips.html', trips=trips)

@app.route('/admin/trips/add', methods=['GET', 'POST'])
@login_required
def admin_trip_add():
    if request.method == 'POST':
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"trip_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        trip = Trip(
            title_uk=request.form.get('title_uk'),
            title_en=request.form.get('title_en'),
            description_uk=request.form.get('description_uk'),
            description_en=request.form.get('description_en'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            price=float(request.form.get('price')),
            discount_percent=int(request.form.get('discount_percent') or 0),
            discount_until=datetime.strptime(request.form.get('discount_until'), '%Y-%m-%d').date() if request.form.get('discount_until') else None,
            location_uk=request.form.get('location_uk'),
            location_en=request.form.get('location_en'),
            trip_type=request.form.get('trip_type'),
            difficulty=request.form.get('difficulty'),
            max_participants=int(request.form.get('max_participants') or 10),
            image=image,
            highlights_uk=request.form.get('highlights_uk'),
            highlights_en=request.form.get('highlights_en'),
            included_uk=request.form.get('included_uk'),
            included_en=request.form.get('included_en'),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(trip)
        db.session.commit()
        flash('Подорож додано!', 'success')
        return redirect(url_for('admin_trips'))
    return render_template('admin/trip_form.html', trip=None)

@app.route('/admin/trips/edit/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def admin_trip_edit(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"trip_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                trip.image = filename
        
        trip.title_uk = request.form.get('title_uk')
        trip.title_en = request.form.get('title_en')
        trip.description_uk = request.form.get('description_uk')
        trip.description_en = request.form.get('description_en')
        trip.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trip.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trip.price = float(request.form.get('price'))
        trip.discount_percent = int(request.form.get('discount_percent') or 0)
        trip.discount_until = datetime.strptime(request.form.get('discount_until'), '%Y-%m-%d').date() if request.form.get('discount_until') else None
        trip.location_uk = request.form.get('location_uk')
        trip.location_en = request.form.get('location_en')
        trip.trip_type = request.form.get('trip_type')
        trip.difficulty = request.form.get('difficulty')
        trip.max_participants = int(request.form.get('max_participants') or 10)
        trip.highlights_uk = request.form.get('highlights_uk')
        trip.highlights_en = request.form.get('highlights_en')
        trip.included_uk = request.form.get('included_uk')
        trip.included_en = request.form.get('included_en')
        trip.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Подорож оновлено!', 'success')
        return redirect(url_for('admin_trips'))
    return render_template('admin/trip_form.html', trip=trip)

@app.route('/admin/trips/delete/<int:trip_id>', methods=['POST'])
@login_required
def admin_trip_delete(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    flash('Подорож видалено!', 'success')
    return redirect(url_for('admin_trips'))

# Admin - Blog
@app.route('/admin/blog')
@login_required
def admin_blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@login_required
def admin_blog_add():
    if request.method == 'POST':
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"blog_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        # Generate slug
        slug = request.form.get('title_en', '').lower()
        slug = ''.join(c if c.isalnum() else '-' for c in slug)
        slug = '-'.join(filter(None, slug.split('-')))
        
        post = BlogPost(
            title_uk=request.form.get('title_uk'),
            title_en=request.form.get('title_en'),
            slug=slug,
            excerpt_uk=request.form.get('excerpt_uk'),
            excerpt_en=request.form.get('excerpt_en'),
            content_uk=request.form.get('content_uk'),
            content_en=request.form.get('content_en'),
            image=image,
            tags=request.form.get('tags'),
            meta_description_uk=request.form.get('meta_description_uk'),
            meta_description_en=request.form.get('meta_description_en'),
            meta_keywords=request.form.get('meta_keywords'),
            is_published=request.form.get('is_published') == 'on'
        )
        db.session.add(post)
        db.session.commit()
        flash('Статтю додано!', 'success')
        return redirect(url_for('admin_blog'))
    return render_template('admin/blog_form.html', post=None)

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def admin_blog_edit(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"blog_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image = filename
        
        post.title_uk = request.form.get('title_uk')
        post.title_en = request.form.get('title_en')
        post.excerpt_uk = request.form.get('excerpt_uk')
        post.excerpt_en = request.form.get('excerpt_en')
        post.content_uk = request.form.get('content_uk')
        post.content_en = request.form.get('content_en')
        post.tags = request.form.get('tags')
        post.meta_description_uk = request.form.get('meta_description_uk')
        post.meta_description_en = request.form.get('meta_description_en')
        post.meta_keywords = request.form.get('meta_keywords')
        post.is_published = request.form.get('is_published') == 'on'
        
        db.session.commit()
        flash('Статтю оновлено!', 'success')
        return redirect(url_for('admin_blog'))
    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@login_required
def admin_blog_delete(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Статтю видалено!', 'success')
    return redirect(url_for('admin_blog'))

# Admin - Gallery
@app.route('/admin/gallery')
@login_required
def admin_gallery():
    items = GalleryItem.query.order_by(GalleryItem.order, GalleryItem.created_at.desc()).all()
    return render_template('admin/gallery.html', items=items)

@app.route('/admin/gallery/add', methods=['GET', 'POST'])
@login_required
def admin_gallery_add():
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"gallery_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                item = GalleryItem(
                    image=filename,
                    caption_uk=request.form.get('caption_uk'),
                    caption_en=request.form.get('caption_en'),
                    category=request.form.get('category'),
                    is_featured=request.form.get('is_featured') == 'on',
                    order=int(request.form.get('order') or 0)
                )
                db.session.add(item)
                db.session.commit()
                flash('Фото додано!', 'success')
        return redirect(url_for('admin_gallery'))
    return render_template('admin/gallery_form.html', item=None)

@app.route('/admin/gallery/delete/<int:item_id>', methods=['POST'])
@login_required
def admin_gallery_delete(item_id):
    item = GalleryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Фото видалено!', 'success')
    return redirect(url_for('admin_gallery'))

# Admin - Contacts
@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = ContactRequest.query.order_by(ContactRequest.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/contacts/mark-read/<int:contact_id>', methods=['POST'])
@login_required
def admin_contact_mark_read(contact_id):
    contact = ContactRequest.query.get_or_404(contact_id)
    contact.is_read = True
    db.session.commit()
    return jsonify({'success': True})

# ============== INIT ==============

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        if not Admin.query.first():
            admin = Admin(username='admin')
            admin.set_password('greece')
            db.session.add(admin)
            db.session.commit()
            print("Admin created with password: greece")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)

