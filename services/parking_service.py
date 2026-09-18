from models.db import db
from models.models import City, Mall, ParkingFloor, ParkingSlot, User
from werkzeug.security import generate_password_hash

def seed_default_data():
    """Seed cities, 5+ malls per city, floors, admin user, and dynamic 3D slots if database is fresh."""
    if City.query.count() >= 5 and Mall.query.count() >= 25:
        return

    # Seed Admin & Demo Users
    if User.query.count() == 0:
        admin_user = User(
            name='System Admin',
            email='admin@park3d.com',
            password_hash=generate_password_hash('admin123'),
            phone='9876543210',
            role='admin'
        )
        demo_user = User(
            name='Demo User',
            email='user@park3d.com',
            password_hash=generate_password_hash('user123'),
            phone='9876543211',
            role='user'
        )
        db.session.add_all([admin_user, demo_user])
        db.session.commit()

    # Cities Data
    cities_data = [
        {'name': 'Chennai', 'state': 'Tamil Nadu', 'image_url': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80'},
        {'name': 'Madurai', 'state': 'Tamil Nadu', 'image_url': 'https://images.unsplash.com/photo-1609946782912-6738b556b6b5?auto=format&fit=crop&w=800&q=80'},
        {'name': 'Tirunelveli', 'state': 'Tamil Nadu', 'image_url': 'https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=800&q=80'},
        {'name': 'Coimbatore', 'state': 'Tamil Nadu', 'image_url': 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80'},
        {'name': 'Trichy', 'state': 'Tamil Nadu', 'image_url': 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=800&q=80'}
    ]

    city_objs = {}
    for c_data in cities_data:
        city = City.query.filter_by(name=c_data['name']).first()
        if not city:
            city = City(name=c_data['name'], state=c_data['state'], image_url=c_data['image_url'])
            db.session.add(city)
            db.session.commit()
        city_objs[c_data['name']] = city

    # 5 Malls per City (25 Malls Total) with local images
    malls_catalog = [
        # CHENNAI MALLS (5)
        {'city': 'Chennai', 'name': 'Phoenix Marketcity', 'address': 'Velachery Main Rd, Chennai', 'img': '/static/images/malls/phoenix-mall.jpg', 'desc': 'Premier multi-level shopping destination with smart EV parking bays.'},
        {'city': 'Chennai', 'name': 'Express Avenue', 'address': 'Whites Road, Royapettah, Chennai', 'img': '/static/images/malls/express-avenue.jpg', 'desc': 'Central retail hub with multi-floor basement parking and automated guidance.'},
        {'city': 'Chennai', 'name': 'Forum Vijaya Mall', 'address': 'NSK Salai, Arcot Rd, Vadapalani, Chennai', 'img': '/static/images/malls/forum-vijaya.jpg', 'desc': 'Modern shopping center featuring automated 3D slot tracking.'},
        {'city': 'Chennai', 'name': 'VR Chennai', 'address': 'Inner Ring Rd, Anna Nagar West, Chennai', 'img': '/static/images/malls/vr-chennai.jpg', 'desc': 'Flagship lifestyle destination with premium reserved parking spaces.'},
        {'city': 'Chennai', 'name': 'The Marina Mall', 'address': 'Old Mahabalipuram Rd, Egatoor, Chennai', 'img': '/static/images/malls/marina-mall.jpg', 'desc': 'Spacious IT corridor mall equipped with high-speed EV charging slots.'},

        # MADURAI MALLS (5)
        {'city': 'Madurai', 'name': 'Vishaal De Mal', 'address': 'Gokhale Road, Tallakulam, Madurai', 'img': '/static/images/malls/vishaal-mall.jpg', 'desc': 'Madurai premier shopping destination featuring multi-level basement parking.'},
        {'city': 'Madurai', 'name': 'Madurai City Centre', 'address': 'KK Nagar, Madurai', 'img': '/static/images/malls/madurai-mart.jpg', 'desc': 'Modern commercial hub with dedicated two-wheeler and four-wheeler slots.'},
        {'city': 'Madurai', 'name': 'Milan\'em Shopping Mall', 'address': 'Club Road, Madurai', 'img': '/static/images/malls/milanem-mall.jpg', 'desc': 'Popular family entertainment center with smart sensor parking.'},
        {'city': 'Madurai', 'name': 'VNS Plaza Madurai', 'address': 'Bye Pass Road, Madurai', 'img': '/static/images/malls/madurai-mall-4.jpg', 'desc': 'Convenient retail plaza with accessible disability-friendly parking.'},
        {'city': 'Madurai', 'name': 'Grand Plaza Madurai', 'address': 'Anna Nagar, Madurai', 'img': '/static/images/malls/madurai-mall-5.jpg', 'desc': 'High-density commercial complex with live availability counters.'},

        # TIRUNELVELI MALLS (5)
        {'city': 'Tirunelveli', 'name': 'VNS Mall', 'address': 'Palayamkottai, Tirunelveli', 'img': '/static/images/malls/vns-mall.jpg', 'desc': 'Premier Tirunelveli retail destination with automated ground level parking.'},
        {'city': 'Tirunelveli', 'name': 'High Ground Mall', 'address': 'High Ground Rd, Tirunelveli', 'img': '/static/images/malls/high-ground.jpg', 'desc': 'Spacious shopping arcade with 3D smart parking management.'},
        {'city': 'Tirunelveli', 'name': 'Tirunelveli Plaza', 'address': 'Vannarpettai, Tirunelveli', 'img': '/static/images/malls/tirunelveli-plaza.jpg', 'desc': 'Central business center offering fast-track parking reservation.'},
        {'city': 'Tirunelveli', 'name': 'Palayam Central Mall', 'address': 'Palayamkottai Main Rd, Tirunelveli', 'img': '/static/images/malls/palayam-central.jpg', 'desc': 'Modern multi-brand retail mall with EV charging infrastructure.'},
        {'city': 'Tirunelveli', 'name': 'City Centre Tirunelveli', 'address': 'Trivandrum Rd, Tirunelveli', 'img': '/static/images/malls/city-centre-tirunelveli.jpg', 'desc': 'High-capacity parking lot with live reservation updates.'},

        # COIMBATORE MALLS (5)
        {'city': 'Coimbatore', 'name': 'Brookefields Mall', 'address': 'Krishnaswamy Road, Coimbatore', 'img': '/static/images/malls/brookefields.jpg', 'desc': 'Iconic Coimbatore shopping mall with smart multi-tier basement parking.'},
        {'city': 'Coimbatore', 'name': 'Fun Republic Mall', 'address': 'Avinashi Road, Peelamedu, Coimbatore', 'img': '/static/images/malls/fun-republic.jpg', 'desc': 'Bustling retail center with real-time slot occupancy sensors.'},
        {'city': 'Coimbatore', 'name': 'Prozone Mall', 'address': 'Sathy Road, Saravanampatti, Coimbatore', 'img': '/static/images/malls/prozone.jpg', 'desc': 'Large-scale horizontal shopping center with extensive 3D parking layout.'},
        {'city': 'Coimbatore', 'name': 'Crosscut Shopping Centre', 'address': 'Cross Cut Rd, Gandhipuram, Coimbatore', 'img': '/static/images/malls/crosscut.jpg', 'desc': 'Commercial shopping complex with quick reservation capabilities.'},
        {'city': 'Coimbatore', 'name': 'Covai City Mall', 'address': 'DB Road, RS Puram, Coimbatore', 'img': '/static/images/malls/covai-city.jpg', 'desc': 'Exclusive lifestyle mall offering VIP reserved parking slots.'},

        # TRICHY MALLS (5)
        {'city': 'Trichy', 'name': 'Femina Shopping Mall', 'address': 'Williams Road, Cantonment, Trichy', 'img': '/static/images/malls/femina.jpg', 'desc': 'Trichy landmark commercial complex with organized parking bays.'},
        {'city': 'Trichy', 'name': 'Manghalam Towers', 'address': 'Thillai Nagar, Trichy', 'img': '/static/images/malls/manghalam.jpg', 'desc': 'Busy business center featuring automated parking guidance.'},
        {'city': 'Trichy', 'name': 'Chinthamani Plaza', 'address': 'Chatram Bus Stand Rd, Trichy', 'img': '/static/images/malls/chinthamani.jpg', 'desc': 'Central retail hub with dedicated EV and accessible parking.'},
        {'city': 'Trichy', 'name': 'Trichy Central Mall', 'address': 'Salai Road, Thillai Nagar, Trichy', 'img': '/static/images/malls/trichy-central.jpg', 'desc': 'Modern shopping destination with live 3D basement monitoring.'},
        {'city': 'Trichy', 'name': 'Rockfort Shopping Complex', 'address': 'NSB Road, Teppakulam, Trichy', 'img': '/static/images/malls/rockfort.jpg', 'desc': 'Heritage shopping arcade with online parking slot pre-booking.'}
    ]

    for m_data in malls_catalog:
        city = city_objs.get(m_data['city'])
        if not city:
            continue
            
        existing_mall = Mall.query.filter_by(city_id=city.id, name=m_data['name']).first()
        if not existing_mall:
            mall = Mall(
                city_id=city.id,
                name=m_data['name'],
                address=m_data['address'],
                image_url=m_data['img'],
                description=m_data['desc'],
                opening_time='09:00 AM',
                closing_time='10:00 PM',
                rating=4.5,
                total_floors=2
            )
            db.session.add(mall)
            db.session.commit()

            f1 = ParkingFloor(mall_id=mall.id, floor_name='Basement 1 - North Wing', level_code='B1')
            f2 = ParkingFloor(mall_id=mall.id, floor_name='Basement 2 - South Wing', level_code='B2')
            db.session.add_all([f1, f2])
            db.session.commit()

            generate_floor_slots(mall.id, f1.id)
            generate_floor_slots(mall.id, f2.id)

def generate_floor_slots(mall_id, floor_id):
    """Generate 30 structured 3D parking slots (Rows A, B, C) with 3D x, y, z positions."""
    slots = []
    rows = [
        ('A', -10.0),
        ('B', 0.0),
        ('C', 10.0)
    ]
    
    for row_letter, z_pos in rows:
        for i in range(1, 11):
            slot_num = f"{row_letter}-{i:02d}"
            x_pos = (i - 5.5) * 5.0
            
            if i in [1, 2] and row_letter == 'A':
                slot_type = 'ev'
                v_type = 'ev'
                price = 50.0
            elif i in [1, 2] and row_letter == 'B':
                slot_type = 'accessible'
                v_type = 'car'
                price = 30.0
            elif i in [1, 2] and row_letter == 'C':
                slot_type = 'premium'
                v_type = 'suv'
                price = 60.0
            else:
                slot_type = 'standard'
                v_type = 'car' if i % 2 == 0 else 'bike'
                price = 30.0 if v_type == 'car' else 20.0

            if i == 3 and row_letter == 'A':
                status = 'occupied'
            elif i == 5 and row_letter == 'B':
                status = 'reserved'
            elif i == 8 and row_letter == 'C':
                status = 'disabled'
            else:
                status = 'available'

            dist_entrance = round(((x_pos - (-28))**2 + (z_pos - 0)**2)**0.5, 1)
            dist_exit = round(((x_pos - (28))**2 + (z_pos - 0)**2)**0.5, 1)

            slot = ParkingSlot(
                mall_id=mall_id,
                floor_id=floor_id,
                slot_number=slot_num,
                slot_type=slot_type,
                vehicle_type=v_type,
                status=status,
                price_per_hour=price,
                x_position=x_pos,
                y_position=0.0,
                z_position=z_pos,
                distance_to_entrance=dist_entrance,
                distance_to_exit=dist_exit
            )
            slots.append(slot)

    db.session.add_all(slots)
    db.session.commit()

def get_floor_occupancy_metrics(floor_id):
    """Calculate availability metrics for a given floor."""
    slots = ParkingSlot.query.filter_by(floor_id=floor_id).all()
    total = len(slots)
    available = sum(1 for s in slots if s.status == 'available')
    occupied = sum(1 for s in slots if s.status == 'occupied')
    reserved = sum(1 for s in slots if s.status == 'reserved')
    disabled = sum(1 for s in slots if s.status == 'disabled')
    
    occupancy_pct = round(((total - available) / total * 100), 1) if total > 0 else 0
    
    return {
        'total': total,
        'available': available,
        'occupied': occupied,
        'reserved': reserved,
        'disabled': disabled,
        'occupancy_pct': occupancy_pct
    }
