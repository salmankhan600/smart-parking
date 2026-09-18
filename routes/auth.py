from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db
from models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email and password are required.'}), 400
        
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
        
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        phone=phone,
        role='user'
    )
    
    db.session.add(user)
    db.session.commit()
    
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_email'] = user.email
    session['user_role'] = user.role
    
    return jsonify({
        'success': True,
        'message': 'Registration successful!',
        'user': user.to_dict()
    })

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_email'] = user.email
    session['user_role'] = user.role
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': user.to_dict()
    })

@auth_bp.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    return redirect(url_for('views.index'))

@auth_bp.route('/api/user/me', methods=['GET'])
def api_user_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False}), 200
        
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({'logged_in': False}), 200
        
    return jsonify({
        'logged_in': True,
        'user': user.to_dict()
    })
