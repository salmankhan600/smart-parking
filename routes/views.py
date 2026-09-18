from flask import Blueprint, render_template, session, redirect, url_for, request
from models.models import City, Mall, ParkingFloor, ParkingSlot, Booking

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    cities = City.query.order_by(City.name).all()
    malls = Mall.query.order_by(Mall.name).limit(6).all()
    
    total_slots = ParkingSlot.query.count()
    available_slots = ParkingSlot.query.filter_by(status='available').count()
    occupied_slots = ParkingSlot.query.filter_by(status='occupied').count()
    reserved_slots = ParkingSlot.query.filter_by(status='reserved').count()
    
    return render_template('index.html',
                           cities=cities,
                           malls=malls,
                           total_slots=total_slots,
                           available_slots=available_slots,
                           occupied_slots=occupied_slots,
                           reserved_slots=reserved_slots)

@views_bp.route('/login')
def login_page():
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('login.html')

@views_bp.route('/register')
def register_page():
    if session.get('user_id'):
        return redirect(url_for('views.index'))
    return render_template('register.html')

@views_bp.route('/malls')
def malls_page():
    city_id = request.args.get('city_id', type=int)
    search_q = request.args.get('q', '').strip()
    
    cities = City.query.order_by(City.name).all()
    
    query = Mall.query
    if city_id:
        query = query.filter_by(city_id=city_id)
    if search_q:
        query = query.filter(Mall.name.ilike(f'%{search_q}%') | Mall.address.ilike(f'%{search_q}%'))
        
    malls = query.order_by(Mall.name).all()
    selected_city = City.query.get(city_id) if city_id else None
    
    return render_template('malls.html',
                           cities=cities,
                           malls=malls,
                           selected_city=selected_city,
                           search_q=search_q)

@views_bp.route('/parking')
def parking_page():
    mall_id = request.args.get('mall_id', type=int)
    floor_id = request.args.get('floor_id', type=int)
    
    if not mall_id:
        first_mall = Mall.query.first()
        if first_mall:
            mall_id = first_mall.id
        else:
            return redirect(url_for('views.malls_page'))
            
    mall = Mall.query.get_or_404(mall_id)
    floors = ParkingFloor.query.filter_by(mall_id=mall.id).order_by(ParkingFloor.level_code).all()
    
    if not floor_id and floors:
        floor_id = floors[0].id
        
    current_floor = ParkingFloor.query.get(floor_id) if floor_id else None
    
    return render_template('parking.html',
                           mall=mall,
                           floors=floors,
                           current_floor=current_floor)

@views_bp.route('/booking')
def booking_page():
    if not session.get('user_id'):
        return redirect(url_for('views.login_page'))
        
    slot_id = request.args.get('slot_id', type=int)
    if not slot_id:
        return redirect(url_for('views.parking_page'))
        
    slot = ParkingSlot.query.get_or_404(slot_id)
    return render_template('booking.html', slot=slot)

@views_bp.route('/payment')
def payment_page():
    if not session.get('user_id'):
        return redirect(url_for('views.login_page'))
        
    booking_id = request.args.get('booking_id', type=int)
    if not booking_id:
        return redirect(url_for('views.parking_page'))
        
    booking = Booking.query.get_or_404(booking_id)
    return render_template('payment.html', booking=booking)

@views_bp.route('/confirmation')
def confirmation_page():
    if not session.get('user_id'):
        return redirect(url_for('views.login_page'))
        
    booking_id = request.args.get('booking_id', type=int)
    if not booking_id:
        return redirect(url_for('views.bookings_page'))
        
    booking = Booking.query.get_or_404(booking_id)
    return render_template('confirmation.html', booking=booking)

@views_bp.route('/bookings')
def bookings_page():
    if not session.get('user_id'):
        return redirect(url_for('views.login_page'))
        
    return render_template('bookings.html')

# --- ADMIN VIEWS ---
@views_bp.route('/admin')
def admin_dashboard():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return redirect(url_for('views.login_page'))
    return render_template('admin/dashboard.html')

@views_bp.route('/admin/live-map')
def admin_live_map():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return redirect(url_for('views.login_page'))
    malls = Mall.query.order_by(Mall.name).all()
    return render_template('admin/live_map.html', malls=malls)

@views_bp.route('/admin/malls')
def admin_malls():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return redirect(url_for('views.login_page'))
    cities = City.query.order_by(City.name).all()
    malls = Mall.query.order_by(Mall.name).all()
    return render_template('admin/malls.html', cities=cities, malls=malls)

@views_bp.route('/admin/slots')
def admin_slots():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return redirect(url_for('views.login_page'))
    malls = Mall.query.order_by(Mall.name).all()
    return render_template('admin/slots.html', malls=malls)

@views_bp.route('/admin/bookings')
def admin_bookings():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        return redirect(url_for('views.login_page'))
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)
