from flask import Blueprint, request, jsonify, session
from models.models import City, Mall, ParkingFloor, ParkingSlot, Booking, Payment
from services.parking_service import get_floor_occupancy_metrics
from services.booking_service import calculate_booking_price, create_booking, process_payment, cancel_booking

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/cities', methods=['GET'])
def get_cities():
    cities = City.query.order_by(City.name).all()
    return jsonify({
        'success': True,
        'cities': [c.to_dict() for c in cities]
    })

@api_bp.route('/api/malls/<int:city_id>', methods=['GET'])
def get_malls(city_id):
    malls = Mall.query.filter_by(city_id=city_id).order_by(Mall.name).all()
    return jsonify({
        'success': True,
        'malls': [m.to_dict() for m in malls]
    })

@api_bp.route('/api/floors/<int:mall_id>', methods=['GET'])
def get_floors(mall_id):
    floors = ParkingFloor.query.filter_by(mall_id=mall_id).order_by(ParkingFloor.level_code).all()
    return jsonify({
        'success': True,
        'floors': [f.to_dict() for f in floors]
    })

@api_bp.route('/api/parking/<int:mall_id>/<int:floor_id>', methods=['GET'])
def get_parking_map(mall_id, floor_id):
    floor = ParkingFloor.query.filter_by(id=floor_id, mall_id=mall_id).first()
    if not floor:
        return jsonify({'success': False, 'message': 'Floor not found.'}), 404
        
    slots = ParkingSlot.query.filter_by(mall_id=mall_id, floor_id=floor_id).order_by(ParkingSlot.slot_number).all()
    metrics = get_floor_occupancy_metrics(floor_id)
    
    return jsonify({
        'success': True,
        'floor': floor.to_dict(),
        'metrics': metrics,
        'slots': [s.to_dict() for s in slots]
    })

@api_bp.route('/api/recommend-slot', methods=['GET'])
def recommend_slot():
    floor_id = request.args.get('floor_id', type=int)
    vehicle_type = request.args.get('vehicle_type', 'car').lower()
    preference = request.args.get('preference', 'entrance').lower()
    
    if not floor_id:
        return jsonify({'success': False, 'message': 'floor_id is required.'}), 400
        
    query = ParkingSlot.query.filter_by(floor_id=floor_id, status='available')
    
    if preference == 'ev' or vehicle_type == 'ev':
        query = query.filter_by(slot_type='ev')
    elif preference == 'accessible':
        query = query.filter_by(slot_type='accessible')
        
    if preference == 'exit':
        available_slots = query.order_by(ParkingSlot.distance_to_exit).all()
        reason = "Nearest available slot to Exit gate"
    else:
        available_slots = query.order_by(ParkingSlot.distance_to_entrance).all()
        reason = "Nearest available slot to Entrance gate"
    
    if not available_slots:
        # Fallback to any available slot sorted by entrance
        available_slots = ParkingSlot.query.filter_by(floor_id=floor_id, status='available').order_by(ParkingSlot.distance_to_entrance).all()
        reason = "Best available slot on this floor"
        
    if not available_slots:
        return jsonify({'success': False, 'message': 'No parking slots are currently available on this floor.'}), 404
        
    recommended = available_slots[0]
    dist = recommended.distance_to_exit if preference == 'exit' else recommended.distance_to_entrance
    
    return jsonify({
        'success': True,
        'slot': recommended.to_dict(),
        'reason': f"{reason} ({dist}m)"
    })

@api_bp.route('/api/book', methods=['POST'])
def book_slot():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Session expired. Please login to reserve a parking slot.'}), 401
        
    data = request.get_json() or {}
    slot_id = data.get('slot_id')
    vehicle_type = data.get('vehicle_type', 'car')
    vehicle_number = data.get('vehicle_number', '')
    start_time = data.get('start_time')
    duration = data.get('duration', 1)
    
    if not slot_id or not vehicle_number or not start_time:
        return jsonify({'success': False, 'message': 'Slot ID, vehicle registration number, and start time are required.'}), 400
        
    try:
        duration = int(duration)
    except ValueError:
        duration = 1
        
    booking, error = create_booking(
        user_id=session['user_id'],
        slot_id=slot_id,
        vehicle_type=vehicle_type,
        vehicle_number=vehicle_number,
        start_time_str=start_time,
        duration_hours=duration
    )
    
    if error:
        return jsonify({'success': False, 'message': error}), 400
        
    return jsonify({
        'success': True,
        'message': 'Slot reserved! Proceed to payment.',
        'booking': booking.to_dict()
    })

@api_bp.route('/api/payment', methods=['POST'])
def make_payment():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 401
        
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    payment_method = data.get('payment_method', 'UPI')
    
    if not booking_id:
        return jsonify({'success': False, 'message': 'Booking ID required.'}), 400
        
    payment, error = process_payment(booking_id, payment_method)
    if error:
        return jsonify({'success': False, 'message': error}), 400
        
    booking = Booking.query.get(booking_id)
    return jsonify({
        'success': True,
        'message': 'Payment Successful!',
        'payment': payment.to_dict(),
        'booking': booking.to_dict()
    })

@api_bp.route('/api/bookings', methods=['GET'])
def get_user_bookings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 401
        
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return jsonify({
        'success': True,
        'bookings': [b.to_dict() for b in bookings]
    })

@api_bp.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking_detail(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 401
        
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found.'}), 404
        
    if booking.user_id != user_id and session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Forbidden.'}), 403
        
    return jsonify({
        'success': True,
        'booking': booking.to_dict()
    })

@api_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_user_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 401
        
    is_admin = (session.get('user_role') == 'admin')
    success, message = cancel_booking(booking_id, user_id, is_admin)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400
        
    return jsonify({
        'success': True,
        'message': message
    })
