-- ========================================================
-- SMART PARKING - Smart Mall Parking Reservation System
-- Complete MySQL Schema & Expanded 25+ Mall Seed Database
-- ========================================================

CREATE DATABASE IF NOT EXISTS smart_parking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_parking_db;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CITIES TABLE
CREATE TABLE IF NOT EXISTS cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(100) DEFAULT 'Tamil Nadu',
    image_url VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. MALLS TABLE
CREATE TABLE IF NOT EXISTS malls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    image_url VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    opening_time VARCHAR(20) DEFAULT '09:00 AM',
    closing_time VARCHAR(20) DEFAULT '10:00 PM',
    rating FLOAT DEFAULT 4.5,
    total_floors INT DEFAULT 2,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

-- 4. PARKING FLOORS TABLE
CREATE TABLE IF NOT EXISTS parking_floors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mall_id INT NOT NULL,
    floor_name VARCHAR(50) NOT NULL,
    level_code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mall_id) REFERENCES malls(id) ON DELETE CASCADE
);

-- 5. PARKING SLOTS TABLE
CREATE TABLE IF NOT EXISTS parking_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mall_id INT NOT NULL,
    floor_id INT NOT NULL,
    slot_number VARCHAR(20) NOT NULL,
    slot_type ENUM('standard', 'ev', 'accessible', 'premium') DEFAULT 'standard',
    vehicle_type ENUM('car', 'bike', 'suv', 'ev') DEFAULT 'car',
    status ENUM('available', 'reserved', 'occupied', 'disabled') DEFAULT 'available',
    price_per_hour DECIMAL(8, 2) DEFAULT 30.00,
    x_position FLOAT DEFAULT 0.0,
    y_position FLOAT DEFAULT 0.0,
    z_position FLOAT DEFAULT 0.0,
    distance_to_entrance FLOAT DEFAULT 10.0,
    distance_to_exit FLOAT DEFAULT 15.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mall_id) REFERENCES malls(id) ON DELETE CASCADE,
    FOREIGN KEY (floor_id) REFERENCES parking_floors(id) ON DELETE CASCADE,
    UNIQUE KEY unique_floor_slot (floor_id, slot_number)
);

-- 6. BOOKINGS TABLE
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_code VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    slot_id INT NOT NULL,
    vehicle_type ENUM('car', 'bike', 'suv', 'ev') DEFAULT 'car',
    vehicle_number VARCHAR(30) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_hours INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED') DEFAULT 'COMPLETED',
    booking_status ENUM('upcoming', 'active', 'completed', 'cancelled') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id) ON DELETE CASCADE
);

-- 7. PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    payment_method ENUM('UPI', 'CARD', 'QR') DEFAULT 'UPI',
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'REFUNDED') DEFAULT 'SUCCESS',
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- INDEXES
CREATE INDEX idx_slot_status ON parking_slots(status);
CREATE INDEX idx_slot_floor ON parking_slots(floor_id);
CREATE INDEX idx_booking_user ON bookings(user_id);
CREATE INDEX idx_booking_status ON bookings(booking_status);

-- ========================================================
-- SEED DATA INSERTS
-- ========================================================

-- Users
INSERT INTO users (id, name, email, password_hash, phone, role) VALUES 
(1, 'System Admin', 'admin@park3d.com', 'pbkdf2:sha256:600000$5qKj5vR9$6e6e2329bdc56ec236b9e25010ec0d592982d6b38c22756d11fef67319989bca', '9876543210', 'admin'),
(2, 'Demo User', 'user@park3d.com', 'pbkdf2:sha256:600000$5qKj5vR9$6e6e2329bdc56ec236b9e25010ec0d592982d6b38c22756d11fef67319989bca', '9876543211', 'user')
ON DUPLICATE KEY UPDATE id=id;

-- Cities (5)
INSERT INTO cities (id, name, state, image_url) VALUES
(1, 'Chennai', 'Tamil Nadu', 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80'),
(2, 'Madurai', 'Tamil Nadu', 'https://images.unsplash.com/photo-1609946782912-6738b556b6b5?auto=format&fit=crop&w=800&q=80'),
(3, 'Tirunelveli', 'Tamil Nadu', 'https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=800&q=80'),
(4, 'Coimbatore', 'Tamil Nadu', 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80'),
(5, 'Trichy', 'Tamil Nadu', 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=800&q=80')
ON DUPLICATE KEY UPDATE id=id;

-- Malls (25 Malls - 5 per City)
INSERT INTO malls (id, city_id, name, address, image_url, description, total_floors) VALUES
-- CHENNAI
(1, 1, 'Phoenix Marketcity', 'Velachery Main Rd, Chennai', 'https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?auto=format&fit=crop&w=800&q=80', 'Premier multi-level shopping destination with smart EV parking bays.', 2),
(2, 1, 'Express Avenue', 'Whites Road, Royapettah, Chennai', 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80', 'Central retail hub with multi-floor basement parking.', 2),
(3, 1, 'Forum Vijaya Mall', 'Arcot Rd, Vadapalani, Chennai', 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80', 'Modern shopping center featuring automated 3D slot tracking.', 2),
(4, 1, 'VR Chennai', 'Anna Nagar West, Chennai', 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80', 'Flagship lifestyle destination with premium reserved parking.', 2),
(5, 1, 'The Marina Mall', 'OMR, Egatoor, Chennai', 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80', 'IT corridor mall equipped with EV charging slots.', 2),

-- MADURAI
(6, 2, 'Vishaal De Mal', 'Gokhale Road, Tallakulam, Madurai', 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80', 'Madurai premier shopping destination featuring multi-level basement parking.', 2),
(7, 2, 'Madurai City Centre', 'KK Nagar, Madurai', 'https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?auto=format&fit=crop&w=800&q=80', 'Modern commercial hub with dedicated two-wheeler and four-wheeler slots.', 2),
(8, 2, 'Milan\'em Shopping Mall', 'Club Road, Madurai', 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80', 'Popular family entertainment center with smart sensor parking.', 2),
(9, 2, 'VNS Plaza Madurai', 'Bye Pass Road, Madurai', 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80', 'Convenient retail plaza with accessible disability-friendly parking.', 2),
(10, 2, 'Grand Plaza Madurai', 'Anna Nagar, Madurai', 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80', 'High-density commercial complex with live availability counters.', 2),

-- TIRUNELVELI
(11, 3, 'VNS Mall', 'Palayamkottai, Tirunelveli', 'https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?auto=format&fit=crop&w=800&q=80', 'Premier Tirunelveli retail destination with ground level parking.', 2),
(12, 3, 'High Ground Mall', 'High Ground Rd, Tirunelveli', 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80', 'Spacious shopping arcade with 3D smart parking management.', 2),
(13, 3, 'Tirunelveli Plaza', 'Vannarpettai, Tirunelveli', 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80', 'Central business center offering fast-track parking reservation.', 2),
(14, 3, 'Palayam Central Mall', 'Palayamkottai Main Rd, Tirunelveli', 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80', 'Modern multi-brand retail mall with EV charging infrastructure.', 2),
(15, 3, 'City Centre Tirunelveli', 'Trivandrum Rd, Tirunelveli', 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80', 'High-capacity parking lot with live reservation updates.', 2),

-- COIMBATORE
(16, 4, 'Brookefields Mall', 'Krishnaswamy Road, Coimbatore', 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80', 'Iconic Coimbatore shopping mall with smart multi-tier basement parking.', 2),
(17, 4, 'Fun Republic Mall', 'Avinashi Road, Peelamedu, Coimbatore', 'https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?auto=format&fit=crop&w=800&q=80', 'Bustling retail center with real-time slot occupancy sensors.', 2),
(18, 4, 'Prozone Mall', 'Sathy Road, Saravanampatti, Coimbatore', 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80', 'Large-scale horizontal shopping center with extensive 3D parking layout.', 2),
(19, 4, 'Crosscut Shopping Centre', 'Cross Cut Rd, Gandhipuram, Coimbatore', 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80', 'Commercial shopping complex with quick reservation capabilities.', 2),
(20, 4, 'Covai City Mall', 'DB Road, RS Puram, Coimbatore', 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80', 'Exclusive lifestyle mall offering VIP reserved parking slots.', 2),

-- TRICHY
(21, 5, 'Femina Shopping Mall', 'Williams Road, Cantonment, Trichy', 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=800&q=80', 'Trichy landmark commercial complex with organized parking bays.', 2),
(22, 5, 'Manghalam Towers', 'Thillai Nagar, Trichy', 'https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?auto=format&fit=crop&w=800&q=80', 'Busy business center featuring automated parking guidance.', 2),
(23, 5, 'Chinthamani Plaza', 'Chatram Bus Stand Rd, Trichy', 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80', 'Central retail hub with dedicated EV and accessible parking.', 2),
(24, 5, 'Trichy Central Mall', 'Salai Road, Thillai Nagar, Trichy', 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&w=800&q=80', 'Modern shopping destination with live 3D basement monitoring.', 2),
(25, 5, 'Rockfort Shopping Complex', 'NSB Road, Teppakulam, Trichy', 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80', 'Heritage shopping arcade with online parking slot pre-booking.', 2)
ON DUPLICATE KEY UPDATE id=id;
