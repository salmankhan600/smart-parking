import uuid
from datetime import datetime, timedelta
from models.db import db
from models.models import Booking, ParkingSlot, Payment

def calculate_booking_price(slot_id, duration_hours):
    slot = ParkingSlot.query.get(slot_id)
    if not slot:
        return 0.0
    
    base_price = slot.price_per_hour
    if duration_hours == 1:
        total = base_price
    elif duration_hours == 2:
        total = base_price * 1.8
    elif duration_hours == 3:
        total = base_price * 2.5
    elif duration_hours == 4:
        total = base_price * 3.2
    else:
        total = base_price * (duration_hours * 0.75)
        
    return round(total, 2)

def create_booking(user_id, slot_id, vehicle_type, vehicle_number, start_time_str, duration_hours):
    """
    Atomic creation of booking with slot locking & double-booking prevention.
    """
    slot = ParkingSlot.query.with_for_update().get(slot_id) if db.engine.name == 'mysql' else ParkingSlot.query.get(slot_id)
    
    if not slot:
        return None, "Selected parking slot does not exist."
        
    if slot.status != 'available':
        return None, f"Sorry, slot {slot.slot_number} was just booked by another user. Please select another slot."
        
    try:
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M') if 'T' in start_time_str else datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
    except ValueError:
        start_time = datetime.utcnow()
        
    end_time = start_time + timedelta(hours=duration_hours)
    total_amount = calculate_booking_price(slot_id, duration_hours)
    
    # Generate unique booking code prefixed with SP-XXXXXXXX
    booking_code = f"SP-{uuid.uuid4().hex[:8].upper()}"
    
    booking = Booking(
        booking_code=booking_code,
        user_id=user_id,
        slot_id=slot_id,
        vehicle_type=vehicle_type,
        vehicle_number=vehicle_number.upper(),
        start_time=start_time,
        end_time=end_time,
        duration_hours=duration_hours,
        total_amount=total_amount,
        payment_status='PENDING',
        booking_status='upcoming'
    )
    
    # Mark slot as reserved temporarily during payment
    slot.status = 'reserved'
    
    db.session.add(booking)
    db.session.commit()
    
    return booking, None

def process_payment(booking_id, payment_method):
    booking = Booking.query.get(booking_id)
    if not booking:
        return None, "Booking record not found."
        
    slot = ParkingSlot.query.get(booking.slot_id)
    if not slot:
        return None, "Associated parking slot not found."

    # Verify slot hasn't been cancelled or modified inappropriately
    if booking.booking_status == 'cancelled':
        return None, "Cannot process payment for a cancelled booking."
        
    transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
    
    # Normalize payment method display to UPI, CARD, or QR
    method_clean = payment_method.upper()
    if method_clean not in ['UPI', 'CARD', 'QR']:
        method_clean = 'UPI'

    payment = Payment(
        booking_id=booking.id,
        transaction_id=transaction_id,
        payment_method=method_clean,
        amount=booking.total_amount,
        status='SUCCESS',
        paid_at=datetime.utcnow()
    )
    
    # Update booking and slot status
    booking.payment_status = 'COMPLETED'
    booking.booking_status = 'active'
    
    # Update slot to occupied
    slot.status = 'occupied'
        
    db.session.add(payment)
    db.session.commit()
    
    return payment, None

def cancel_booking(booking_id, user_id, is_admin=False):
    booking = Booking.query.get(booking_id)
    if not booking:
        return False, "Booking not found."
        
    if not is_admin and booking.user_id != user_id:
        return False, "Unauthorized to cancel this booking."
        
    if booking.booking_status == 'cancelled':
        return False, "Booking is already cancelled."
        
    booking.booking_status = 'cancelled'
    booking.payment_status = 'REFUNDED'
    
    # Reset parking slot to available
    slot = ParkingSlot.query.get(booking.slot_id)
    if slot and slot.status in ['occupied', 'reserved']:
        slot.status = 'available'
        
    db.session.commit()
    return True, "Booking cancelled successfully. Parking slot is now available."
