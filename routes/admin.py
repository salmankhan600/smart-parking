import os
import random
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from models.db import db
from models.models import User, City, Mall, ParkingFloor, ParkingSlot, Booking, Payment
from services.parking_service import generate_floor_slots

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_admin_auth():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return False
    return True

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard_data():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Admin authorization required.'}), 403
        
    total_malls = Mall.query.count()
    total_cities = City.query.count()
    total_slots = ParkingSlot.query.count()
    available_slots = ParkingSlot.query.filter_by(status='available').count()
    occupied_slots = ParkingSlot.query.filter_by(status='occupied').count()
    reserved_slots = ParkingSlot.query.filter_by(status='reserved').count()
    disabled_slots = ParkingSlot.query.filter_by(status='disabled').count()
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    today_bookings = Booking.query.filter(Booking.created_at >= today_start).count()
    
    today_payments = db.session.query(db.func.sum(Payment.amount)).filter(Payment.paid_at >= today_start).scalar() or 0.0
    total_revenue = db.session.query(db.func.sum(Payment.amount)).scalar() or 0.0
    
    # 7-day booking analytics
    daily_stats = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        count = Booking.query.filter(Booking.created_at >= day_start, Booking.created_at <= day_end).count()
        rev = db.session.query(db.func.sum(Payment.amount)).filter(Payment.paid_at >= day_start, Payment.paid_at <= day_end).scalar() or 0.0
        
        daily_stats.append({
            'date': day.strftime('%b %d'),
            'bookings': count,
            'revenue': float(rev)
        })

    # Payment Methods Breakdown (UPI, CARD, QR)
    upi_count = Payment.query.filter_by(payment_method='UPI').count()
    card_count = Payment.query.filter_by(payment_method='CARD').count()
    qr_count = Payment.query.filter_by(payment_method='QR').count()

    return jsonify({
        'success': True,
        'metrics': {
            'total_malls': total_malls,
            'total_cities': total_cities,
            'total_slots': total_slots,
            'available_slots': available_slots,
            'occupied_slots': occupied_slots,
            'reserved_slots': reserved_slots,
            'disabled_slots': disabled_slots,
            'today_bookings': today_bookings,
            'today_revenue': float(today_payments),
            'total_revenue': float(total_revenue),
            'payment_methods': {
                'upi': upi_count,
                'card': card_count,
                'qr': qr_count
            }
        },
        'daily_stats': daily_stats
    })

# --- CITY CRUD ---
@admin_bp.route('/api/admin/cities', methods=['POST'])
def add_city():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    state = data.get('state', 'Tamil Nadu').strip()
    image_url = data.get('image_url', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'City name required.'}), 400
        
    city = City(name=name, state=state, image_url=image_url or '/static/images/malls/default-mall.jpg')
    db.session.add(city)
    db.session.commit()
    return jsonify({'success': True, 'city': city.to_dict()})

@admin_bp.route('/api/admin/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
    city = City.query.get(city_id)
    if not city:
        return jsonify({'success': False, 'message': 'City not found.'}), 404
    db.session.delete(city)
    db.session.commit()
    return jsonify({'success': True, 'message': 'City deleted.'})

# --- MALL CRUD & IMAGE UPLOAD ---
@admin_bp.route('/api/admin/malls', methods=['POST'])
def add_mall():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
    data = request.get_json() or {}
    city_id = data.get('city_id')
    name = data.get('name', '').strip()
    address = data.get('address', '').strip()
    image_url = data.get('image_url', '').strip()
    description = data.get('description', '').strip()
    total_floors = data.get('total_floors', 2)
    
    if not city_id or not name or not address:
        return jsonify({'success': False, 'message': 'City ID, Mall Name, and Address are required.'}), 400
        
    mall = Mall(
        city_id=city_id,
        name=name,
        address=address,
        image_url=image_url or '/static/images/malls/default-mall.jpg',
        description=description or 'Modern smart shopping complex with multi-floor 3D parking.',
        opening_time='09:00 AM',
        closing_time='10:00 PM',
        rating=4.5,
        total_floors=total_floors
    )
    db.session.add(mall)
    db.session.commit()
    
    f1 = ParkingFloor(mall_id=mall.id, floor_name='Basement 1', level_code='B1')
    f2 = ParkingFloor(mall_id=mall.id, floor_name='Basement 2', level_code='B2')
    db.session.add_all([f1, f2])
    db.session.commit()
    generate_floor_slots(mall.id, f1.id)
    generate_floor_slots(mall.id, f2.id)
    
    return jsonify({'success': True, 'mall': mall.to_dict()})

@admin_bp.route('/api/admin/malls/<int:mall_id>/upload-image', methods=['POST'])
def upload_mall_image(mall_id):
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
        
    mall = Mall.query.get(mall_id)
    if not mall:
        return jsonify({'success': False, 'message': 'Mall not found.'}), 404
        
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided.'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file.'}), 400
        
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"mall_{mall.id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'malls')
        os.makedirs(upload_dir, exist_ok=True)
        
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)
        
        # Save relative image URL
        mall.image_url = f"/static/uploads/malls/{filename}"
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mall image uploaded successfully!',
            'image_url': mall.image_url,
            'mall': mall.to_dict()
        })
        
    return jsonify({'success': False, 'message': 'Invalid image format. Allowed: JPG, JPEG, PNG, WEBP.'}), 400

@admin_bp.route('/api/admin/malls/<int:mall_id>', methods=['DELETE'])
def delete_mall(mall_id):
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
    mall = Mall.query.get(mall_id)
    if not mall:
        return jsonify({'success': False, 'message': 'Mall not found.'}), 404
    db.session.delete(mall)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Mall deleted.'})

# --- SLOT MANUAL STATUS OVERRIDE ---
@admin_bp.route('/api/admin/slots/<int:slot_id>/status', methods=['POST'])
def update_slot_status(slot_id):
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ['available', 'reserved', 'occupied', 'disabled']:
        return jsonify({'success': False, 'message': 'Invalid status choice.'}), 400
        
    slot = ParkingSlot.query.get(slot_id)
    if not slot:
        return jsonify({'success': False, 'message': 'Slot not found.'}), 404
        
    slot.status = new_status
    db.session.commit()
    return jsonify({'success': True, 'slot': slot.to_dict()})

# --- DEMO MODE TRAFFIC SIMULATOR ---
@admin_bp.route('/api/admin/demo-simulate', methods=['POST'])
def demo_simulate_parking():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
        
    slots = ParkingSlot.query.filter(ParkingSlot.status != 'disabled').all()
    if not slots:
        return jsonify({'success': False, 'message': 'No slots available for simulation.'}), 400
        
    changed_count = random.randint(3, 6)
    target_slots = random.sample(slots, min(changed_count, len(slots)))
    
    updates = []
    for slot in target_slots:
        old_status = slot.status
        if old_status == 'available':
            slot.status = random.choice(['occupied', 'reserved'])
        elif old_status in ['occupied', 'reserved']:
            slot.status = 'available'
            
        updates.append({'slot_number': slot.slot_number, 'from': old_status, 'to': slot.status})
        
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'Simulated live traffic activity on {len(updates)} slots.',
        'updates': updates
    })
