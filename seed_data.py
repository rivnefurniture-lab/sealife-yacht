"""
Seed sample data for Sea Life Yacht School
"""
from app import app, db, Trip, BlogPost, GalleryItem, Admin
from datetime import datetime, date, timedelta
import os
import urllib.request

def download_image(url, filename):
    """Download image from URL"""
    filepath = os.path.join('static/uploads', filename)
    if not os.path.exists(filepath):
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
    return filename

def seed_data():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin if not exists
        if not Admin.query.first():
            admin = Admin(username='admin')
            admin.set_password('greece')
            db.session.add(admin)
            print("Admin created with password: greece")
        
        # Clear existing data
        Trip.query.delete()
        BlogPost.query.delete()
        GalleryItem.query.delete()
        
        # Sample trips
        trips_data = [
            {
                'title_uk': 'Bareboat Skipper — Квітень',
                'title_en': 'Bareboat Skipper — April',
                'description_uk': '<p>Курс Bareboat Skipper — це ваш перший крок до самостійного керування яхтою. За 7 днів інтенсивного навчання ви отримаєте всі необхідні навички та міжнародну ліцензію IYT.</p><p>Курс включає теоретичну підготовку та практичні заняття на воді. Ви навчитеся керувати яхтою, швартуватися, працювати з вітрилами та навігаційним обладнанням.</p>',
                'description_en': '<p>The Bareboat Skipper course is your first step to independent yacht management. In 7 days of intensive training, you will gain all the necessary skills and an international IYT license.</p><p>The course includes theoretical preparation and practical training on the water. You will learn to operate a yacht, moor, work with sails and navigation equipment.</p>',
                'start_date': date(2026, 4, 12),
                'end_date': date(2026, 4, 19),
                'price': 1500,
                'discount_percent': 15,
                'discount_until': date(2026, 3, 15),
                'location_uk': 'Греція, Афіни',
                'location_en': 'Greece, Athens',
                'trip_type': 'course',
                'difficulty': 'beginner',
                'max_participants': 6,
                'highlights_uk': '• Міжнародна ліцензія IYT Bareboat Skipper\n• 7 днів практики на воді\n• Досвідчений сертифікований інструктор\n• Сучасна яхта Bavaria 40',
                'highlights_en': '• International IYT Bareboat Skipper license\n• 7 days of practice on the water\n• Experienced certified instructor\n• Modern Bavaria 40 yacht',
                'included_uk': '• Навчання та сертифікація\n• Проживання на яхті\n• Паливо та стоянки\n• Страхування',
                'included_en': '• Training and certification\n• Accommodation on yacht\n• Fuel and marina fees\n• Insurance',
                'is_active': True
            },
            {
                'title_uk': 'Подорож Кіклади — Травень',
                'title_en': 'Cyclades Trip — May',
                'description_uk': '<p>Незабутня морська подорож по найкрасивіших островах Греції. Санторіні, Міконос, Наксос, Парос — кожен острів унікальний та неповторний.</p><p>Це ідеальна можливість поєднати відпочинок з навчанням яхтингу. Ви будете активним учасником команди та отримаєте практичний досвід керування яхтою.</p>',
                'description_en': '<p>An unforgettable sea voyage through the most beautiful islands of Greece. Santorini, Mykonos, Naxos, Paros — each island is unique.</p><p>This is the perfect opportunity to combine relaxation with yacht training. You will be an active team member and gain practical yacht management experience.</p>',
                'start_date': date(2026, 5, 10),
                'end_date': date(2026, 5, 17),
                'price': 1200,
                'discount_percent': 0,
                'location_uk': 'Греція, Кіклади',
                'location_en': 'Greece, Cyclades',
                'trip_type': 'trip',
                'difficulty': 'beginner',
                'max_participants': 8,
                'highlights_uk': '• 5+ островів за тиждень\n• Санторіні та Міконос\n• Купання в кришталево чистих водах\n• Грецька кухня та вино',
                'highlights_en': '• 5+ islands in a week\n• Santorini and Mykonos\n• Swimming in crystal clear waters\n• Greek cuisine and wine',
                'included_uk': '• Місце на яхті\n• Досвідчений капітан\n• Паливо та стоянки\n• Страхування',
                'included_en': '• Place on yacht\n• Experienced captain\n• Fuel and marina fees\n• Insurance',
                'is_active': True
            },
            {
                'title_uk': 'Day Skipper — Червень',
                'title_en': 'Day Skipper — June',
                'description_uk': '<p>Курс Day Skipper — наступний рівень після Bareboat Skipper. Ви навчитеся планувати маршрути, працювати з картами та керувати яхтою в різних погодних умовах.</p>',
                'description_en': '<p>The Day Skipper course is the next level after Bareboat Skipper. You will learn to plan routes, work with charts and operate a yacht in various weather conditions.</p>',
                'start_date': date(2026, 6, 7),
                'end_date': date(2026, 6, 14),
                'price': 1800,
                'discount_percent': 10,
                'discount_until': date(2026, 5, 1),
                'location_uk': 'Греція, Саронічна затока',
                'location_en': 'Greece, Saronic Gulf',
                'trip_type': 'course',
                'difficulty': 'intermediate',
                'max_participants': 6,
                'is_active': True
            },
            {
                'title_uk': 'Експедиція Іонічні острови',
                'title_en': 'Ionian Islands Expedition',
                'description_uk': '<p>Двотижнева експедиція по Іонічних островах. Корфу, Лефкада, Кефалонія, Закінтос — найзеленіші острови Греції з бірюзовими водами.</p>',
                'description_en': '<p>Two-week expedition through the Ionian Islands. Corfu, Lefkada, Kefalonia, Zakynthos — the greenest islands of Greece with turquoise waters.</p>',
                'start_date': date(2026, 7, 5),
                'end_date': date(2026, 7, 19),
                'price': 2200,
                'discount_percent': 0,
                'location_uk': 'Греція, Іонічні острови',
                'location_en': 'Greece, Ionian Islands',
                'trip_type': 'expedition',
                'difficulty': 'intermediate',
                'max_participants': 8,
                'is_active': True
            },
        ]
        
        for trip_data in trips_data:
            trip = Trip(**trip_data)
            db.session.add(trip)
        
        # Sample blog posts
        posts_data = [
            {
                'title_uk': 'Як обрати перший курс яхтингу',
                'title_en': 'How to Choose Your First Sailing Course',
                'slug': 'how-to-choose-first-sailing-course',
                'excerpt_uk': 'Поради для тих, хто тільки починає свій шлях у яхтингу. Розбираємося в типах ліцензій та курсів.',
                'excerpt_en': 'Tips for those who are just starting their sailing journey. Understanding license types and courses.',
                'content_uk': '<p>Яхтинг — це не просто хобі, це спосіб життя. І перший крок на цьому шляху — обрати правильний курс навчання.</p><h3>Типи ліцензій</h3><p><strong>Bareboat Skipper</strong> — базова ліцензія, яка дозволяє орендувати яхту та керувати нею в денний час при хорошій погоді.</p><p><strong>Day Skipper</strong> — наступний рівень, що включає навігацію та планування маршрутів.</p><p><strong>Coastal Skipper</strong> — для тих, хто хоче керувати яхтою вночі та в складніших умовах.</p><h3>Як обрати?</h3><p>Якщо ви новачок — починайте з Bareboat Skipper. Цей курс дасть вам базові навички та впевненість на воді.</p>',
                'content_en': '<p>Yachting is not just a hobby, it\'s a lifestyle. And the first step on this path is choosing the right training course.</p><h3>License Types</h3><p><strong>Bareboat Skipper</strong> — a basic license that allows you to rent and operate a yacht during the day in good weather.</p><p><strong>Day Skipper</strong> — the next level, including navigation and route planning.</p><p><strong>Coastal Skipper</strong> — for those who want to operate a yacht at night and in more challenging conditions.</p><h3>How to Choose?</h3><p>If you\'re a beginner — start with Bareboat Skipper. This course will give you basic skills and confidence on the water.</p>',
                'tags': 'яхтинг, навчання, ліцензія, bareboat skipper',
                'meta_description_uk': 'Як обрати перший курс яхтингу. Поради для початківців від Sea Life Yacht School.',
                'meta_description_en': 'How to choose your first sailing course. Tips for beginners from Sea Life Yacht School.',
                'is_published': True
            },
            {
                'title_uk': '5 причин навчитися яхтингу в Греції',
                'title_en': '5 Reasons to Learn Sailing in Greece',
                'slug': '5-reasons-learn-sailing-greece',
                'excerpt_uk': 'Чому Греція — ідеальне місце для навчання яхтингу. Погода, острови та інфраструктура.',
                'excerpt_en': 'Why Greece is the perfect place to learn sailing. Weather, islands and infrastructure.',
                'content_uk': '<p>Греція — одне з найкращих місць у світі для навчання яхтингу. Ось 5 головних причин:</p><h3>1. Ідеальна погода</h3><p>300+ сонячних днів на рік та стабільні вітри створюють ідеальні умови для навчання.</p><h3>2. Тисячі островів</h3><p>Більше 6000 островів означають нескінченні можливості для подорожей та практики.</p><h3>3. Розвинена інфраструктура</h3><p>Сотні марин, чартерних компаній та яхт-клубів.</p><h3>4. Доступні ціни</h3><p>Порівняно з Карибами чи Хорватією, Греція пропонує відмінне співвідношення ціни та якості.</p><h3>5. Культура та історія</h3><p>Кожен острів — це нова історія, нова кухня та нові враження.</p>',
                'content_en': '<p>Greece is one of the best places in the world to learn sailing. Here are 5 main reasons:</p><h3>1. Perfect Weather</h3><p>300+ sunny days per year and stable winds create ideal learning conditions.</p><h3>2. Thousands of Islands</h3><p>More than 6000 islands mean endless opportunities for travel and practice.</p><h3>3. Developed Infrastructure</h3><p>Hundreds of marinas, charter companies and yacht clubs.</p><h3>4. Affordable Prices</h3><p>Compared to the Caribbean or Croatia, Greece offers excellent value for money.</p><h3>5. Culture and History</h3><p>Each island is a new story, new cuisine and new experiences.</p>',
                'tags': 'греція, яхтинг, острови, подорожі',
                'meta_description_uk': '5 причин навчитися яхтингу в Греції. Погода, острови та доступні ціни.',
                'meta_description_en': '5 reasons to learn sailing in Greece. Weather, islands and affordable prices.',
                'is_published': True
            },
            {
                'title_uk': 'Що взяти з собою на яхту',
                'title_en': 'What to Pack for a Yacht Trip',
                'slug': 'what-to-pack-yacht-trip',
                'excerpt_uk': 'Повний список речей для комфортної подорожі на яхті. Одяг, взуття та необхідні аксесуари.',
                'excerpt_en': 'Complete packing list for a comfortable yacht trip. Clothes, shoes and essential accessories.',
                'content_uk': '<p>Правильно зібрана сумка — запорука комфортної подорожі на яхті. Ось що обов\'язково потрібно взяти:</p><h3>Одяг</h3><ul><li>Легкий одяг для спекотних днів</li><li>Флісова кофта для прохолодних вечорів</li><li>Непромокаюча куртка</li><li>Купальники (2-3 шт)</li></ul><h3>Взуття</h3><ul><li>Яхтові мокасини з білою підошвою</li><li>Сандалі або шльопанці</li></ul><h3>Аксесуари</h3><ul><li>Сонцезахисні окуляри</li><li>Кепка або панама</li><li>Сонцезахисний крем SPF 50+</li></ul>',
                'content_en': '<p>A properly packed bag is the key to a comfortable yacht trip. Here\'s what you must take:</p><h3>Clothing</h3><ul><li>Light clothes for hot days</li><li>Fleece jacket for cool evenings</li><li>Waterproof jacket</li><li>Swimsuits (2-3 pcs)</li></ul><h3>Footwear</h3><ul><li>Yacht moccasins with white sole</li><li>Sandals or flip-flops</li></ul><h3>Accessories</h3><ul><li>Sunglasses</li><li>Cap or panama hat</li><li>Sunscreen SPF 50+</li></ul>',
                'tags': 'поради, подорожі, пакування',
                'is_published': True
            },
        ]
        
        for post_data in posts_data:
            post = BlogPost(**post_data)
            db.session.add(post)
        
        db.session.commit()
        print("Sample data seeded successfully!")
        print(f"Created {len(trips_data)} trips")
        print(f"Created {len(posts_data)} blog posts")

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs('static/uploads', exist_ok=True)
    seed_data()

