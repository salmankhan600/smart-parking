import os
from datetime import datetime
from .db import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    state = db.Column(db.String(100), default='Tamil Nadu')
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    malls = db.relationship('Mall', backref='city', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'image_url': self.image_url or '/static/images/malls/default-mall.jpg',
            'malls_count': len(self.malls) if self.malls else 0
        }

class Mall(db.Model):
    __tablename__ = 'malls'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    opening_time = db.Column(db.String(20), default='09:00 AM')
    closing_time = db.Column(db.String(20), default='10:00 PM')
    rating = db.Column(db.Float, default=4.5)
    total_floors = db.Column(db.Integer, default=2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    floors = db.relationship('ParkingFloor', backref='mall', lazy=True, cascade='all, delete-orphan')
    slots = db.relationship('ParkingSlot', backref='mall', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        total_slots = sum(len(f.slots) for f in self.floors) if self.floors else len(self.slots)
        avail_slots = sum(sum(1 for s in f.slots if s.status == 'available') for f in self.floors) if self.floors else sum(1 for s in self.slots if s.status == 'available')
        
        # Backend normalization of image_url
        img = (self.image_url or '').strip()
        if not img:
            normalized_img = '/static/images/malls/default-mall.jpg'
            img_status = 'missing'
        elif img.startswith('http://') or img.startswith('https://') or img.startswith('/static/'):
            normalized_img = img
            img_status = 'available'
        else:
            normalized_img = f'/static/images/malls/{img}'
            img_status = 'available'

        return {
            'id': self.id,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else '',
            'name': self.name,
            'address': self.address,
            'image_url': normalized_img,
            'image_status': img_status,
            'description': self.description or 'Premier smart shopping destination featuring multi-level 3D parking guidance.',
            'opening_time': self.opening_time or '09:00 AM',
            'closing_time': self.closing_time or '10:00 PM',
            'rating': self.rating or 4.5,
            'total_floors': self.total_floors,
            'floors_count': len(self.floors) if self.floors else 0,
            'total_slots': total_slots,
            'available_slots': avail_slots
        }

class ParkingFloor(db.Model):
    __tablename__ = 'parking_floors'
    
    id = db.Column(db.Integer, primary_key=True)
    mall_id = db.Column(db.Integer, db.ForeignKey('malls.id'), nullable=False)
    floor_name = db.Column(db.String(50), nullable=False)
    level_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    slots = db.relationship('ParkingSlot', backref='floor', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'mall_id': self.mall_id,
            'floor_name': self.floor_name,
            'level_code': self.level_code,
            'total_slots': len(self.slots) if self.slots else 0,
            'available_slots': sum(1 for s in self.slots if s.status == 'available') if self.slots else 0
        }

class ParkingSlot(db.Model):
    __tablename__ = 'parking_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    mall_id = db.Column(db.Integer, db.ForeignKey('malls.id'), nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('parking_floors.id'), nullable=False)
    slot_number = db.Column(db.String(20), nullable=False)
    slot_type = db.Column(db.String(20), default='standard')
    vehicle_type = db.Column(db.String(20), default='car')
    status = db.Column(db.String(20), default='available')
    price_per_hour = db.Column(db.Float, default=30.0)
    x_position = db.Column(db.Float, default=0.0)
    y_position = db.Column(db.Float, default=0.0)
    z_position = db.Column(db.Float, default=0.0)
    distance_to_entrance = db.Column(db.Float, default=10.0)
    distance_to_exit = db.Column(db.Float, default=15.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='slot', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'mall_id': self.mall_id,
            'floor_id': self.floor_id,
            'slot_number': self.slot_number,
            'slot_type': self.slot_type,
            'vehicle_type': self.vehicle_type,
            'status': self.status,
            'price_per_hour': self.price_per_hour,
            'x_position': self.x_position,
            'y_position': self.y_position,
            'z_position': self.z_position,
            'distance_to_entrance': self.distance_to_entrance,
            'distance_to_exit': getattr(self, 'distance_to_exit', 15.0),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slots.id'), nullable=False)
    vehicle_type = db.Column(db.String(20), default='car')
    vehicle_number = db.Column(db.String(30), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='COMPLETED')
    booking_status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    payments = db.relationship('Payment', backref='booking', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'booking_code': self.booking_code,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else '',
            'user_email': self.user.email if self.user else '',
            'slot_id': self.slot_id,
            'slot_number': self.slot.slot_number if self.slot else '',
            'city_name': self.slot.mall.city.name if self.slot and self.slot.mall and self.slot.mall.city else '',
            'mall_name': self.slot.mall.name if self.slot and self.slot.mall else '',
            'floor_name': self.slot.floor.floor_name if self.slot and self.slot.floor else '',
            'floor_level': self.slot.floor.level_code if self.slot and self.slot.floor else '',
            'price_per_hour': self.slot.price_per_hour if self.slot else 30.0,
            'vehicle_type': self.vehicle_type,
            'vehicle_number': self.vehicle_number,
            'start_time': self.start_time.strftime('%Y-%m-%d %I:%M %p') if self.start_time else '',
            'end_time': self.end_time.strftime('%Y-%m-%d %I:%M %p') if self.end_time else '',
            'booking_date': self.start_time.strftime('%d-%m-%Y') if self.start_time else '',
            'duration_hours': self.duration_hours,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'booking_status': self.booking_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    payment_method = db.Column(db.String(20), default='UPI')
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='SUCCESS')
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'transaction_id': self.transaction_id,
            'payment_method': self.payment_method,
            'amount': self.amount,
            'status': self.status,
            'paid_at': self.paid_at.strftime('%Y-%m-%d %H:%M:%S') if self.paid_at else ''
        }
