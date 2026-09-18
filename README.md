# Smart Parking – Smart Mall Parking Reservation System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

> **BSc Computer Science Final Year Project**  
> A full-stack, production-grade 3D interactive mall parking reservation web platform with real-time slot availability, procedural WebGL 3D rendering, multi-mode simulated payments (UPI, Card, QR), dynamic QR code parking entry pass generation, and an administrative control panel with live traffic simulation.

---

## 🌟 Key Features

### 1. Interactive 3D WebGL Parking Environment (Three.js)
- **Real-Time 3D Floor Layout**: Renders epoxy floor grids, road lanes, directional arrows, concrete pillars, hazard stripes, and entry/exit gates.
- **Dynamic Procedural 3D Cars**: Renders sleek procedural 3D car meshes inside occupied parking slots.
- **Interactive Raycasting**: Hover animations and mouse click selection with smooth camera tweening (lerp) to selected slots.
- **Visual Status Markers**:
  - 🟢 **Available**: Neon Green visual + LED status indicator
  - 🟡 **Reserved**: Neon Yellow / Orange visual
  - 🔴 **Occupied**: Neon Red visual + 3D parked car model
  - 🔵 **Disabled / EV**: Neon Blue / Cyan visual with EV charging station props
- **Camera View Presets**: One-click switching between Top 2D View, 3D Perspective View, and Reset Camera.

### 2. Multi-City & 25+ Smart Malls Catalog
- **5 Cities**: Chennai, Madurai, Tirunelveli, Coimbatore, Trichy.
- **5 Malls Per City (25+ Malls Total)**: Each mall features full descriptions, opening/closing hours, ratings, addresses, image fallbacks (`onerror="this.src='/static/images/default-mall.jpg'"`), and multi-tier 3D basement floors.

### 3. Smart Slot Recommendation & Search
- **Smart Slot Recommender**: Recommends the optimal available slot based on selected vehicle type (Car, Bike, SUV, EV) and preference:
  - Nearest to Entrance
  - Nearest to Exit
  - EV Charging Station
  - Accessible Disability Parking
- **Real-time Live Polling**: Automatic API polling (every 3 seconds) updates slot colors and counters without refreshing the page.

### 4. Multi-Method Payment Gateway (UPI, Card, QR)
- **UPI Payment**: UPI ID input (`username@upi`), generated payment QR code, and "Pay with UPI" button.
- **Card Payment**: Simulated credit/debit card form without storing sensitive credentials.
- **Dynamic QR Payment**: Dynamic QR code containing Booking ID (`SP-XXXXXXXX`), Amount, Mall, Slot, Date, Time.
- **Payment Processing Animation**: Professional loading state ("Processing Payment... ✓ Payment Successful") with double-booking prevention validation right before payment confirmation.

### 5. Digital Parking Pass & Entry QR Code
- **Instant Pass Generation**: Generates unique booking reference IDs (`SP-XXXXXXXX`).
- **Dynamic Entry QR Code**: Rendered via `qrcode.js` containing pass verification data.
- **Print & Text Pass Download**: Ready for gate scanner verification.

### 6. Admin Panel & DEMO MODE Traffic Simulator
- **Payment Audit Report**: Comprehensive record table logging Booking ID (`SP-XXXXXXXX`), User, Mall, Slot, Amount, Payment Method (`UPI`, `CARD`, `QR`), Payment Status (`SUCCESS`, `FAILED`, `REFUNDED`), and Date.
- **Analytics Dashboard**: Real-time stats and Chart.js graphs for daily bookings, slot breakdown, and revenue.
- **Live 3D Admin Control Map**: Click any slot to manually override status to Available, Reserved, Occupied, or Disabled.
- **⚡ DEMO MODE Simulator**: Simulates real-time parking activity by randomly parking/unparking cars for project evaluation demonstrations!

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Three.js (r128), OrbitControls, Bootstrap 5.3, FontAwesome 6, QRCode.js |
| **Backend** | Python 3.10+, Flask 3.0.3, Werkzeug (Password Hashing), REST API |
| **Database** | MySQL (via `mysql-connector-python` & `PyMySQL`) / SQLite (Out-of-the-box fallback) via SQLAlchemy ORM |
| **Configuration** | Environment variables via `python-dotenv` |

---

## 📁 Project Architecture

```
park3d/
├── app.py                  # Main Flask Application Entry Point
├── config.py               # Environment & Database Configuration
├── requirements.txt        # Python Dependencies
├── database.sql            # MySQL Database Schema & Seed Script (25 Malls)
├── .env.example            # Environment Template
├── .env                    # Local Configuration
├── models/
│   ├── db.py               # SQLAlchemy Database Instance
│   └── models.py           # User, City, Mall, Slot, Booking, Payment Models
├── routes/
│   ├── auth.py             # Authentication APIs (Register/Login/Logout)
│   ├── api.py              # Parking, Booking, Payment, & Recommendation APIs
│   ├── admin.py            # Admin Dashboard, CRUD, & DEMO Mode Simulator APIs
│   └── views.py            # Page Template Renders
├── services/
│   ├── parking_service.py  # 3D Coordinates Generator & Occupancy Math
│   └── booking_service.py  # Booking Validation & Payment Logic
├── templates/
│   ├── base.html           # Master Layout with Smart Parking Logo
│   ├── index.html          # Home Page with Hero & Quick Search
│   ├── login.html          # Login Page
│   ├── register.html       # User Registration
│   ├── malls.html          # City & Mall Browsing ("Parking in City")
│   ├── parking.html        # Interactive 3D Parking Map View
│   ├── booking.html        # Slot Booking & Pricing
│   ├── payment.html        # Simulated Payment Gateway (UPI, Card, QR)
│   ├── confirmation.html   # Digital Entry Pass & QR Code
│   ├── bookings.html       # User Reservation History
│   └── admin/              # Admin Suite Templates (Dashboard, Live Map, Malls, Slots, Bookings)
└── static/
    ├── css/                # Glassmorphism & Admin CSS
    ├── images/             # Local Fallback Images (default-mall.jpg)
    └── js/                 # Three.js 3D Engine, Admin Charts, Booking Logic
```

---

## 🚀 Setup & Execution Guide

### Step 1: Navigate to Project Directory
```bash
cd C:\Users\acer\.gemini\antigravity\scratch\park3d
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🔐 Default Credentials

| Account Role | Email | Password |
|---|---|---|
| **System Admin** | `admin@park3d.com` | `admin123` |
| **Demo User** | `user@park3d.com` | `user123` |
