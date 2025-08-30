"""
Authentication API Routes
File: backend/api/routes/auth.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.database import db, User, UserSession
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Name, email and password are required'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 409
        
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Create session
        session = UserSession(
            user_id=new_user.id,
            session_token=UserSession.generate_token(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'token': session.session_token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Login user"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is disabled'
            }), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Deactivate old sessions
        UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})
        
        # Create new session
        session = UserSession(
            user_id=user.id,
            session_token=UserSession.generate_token(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'token': session.session_token
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Logout user"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'No session token provided'
            }), 400
        
        # Find and deactivate session
        session = UserSession.query.filter_by(session_token=token, is_active=True).first()
        
        if session:
            session.is_active = False
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@auth_bp.route('/verify', methods=['GET', 'OPTIONS'])
def verify_session():
    """Verify if session is valid"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'No session token provided'
            }), 401
        
        # Find active session
        session = UserSession.query.filter_by(
            session_token=token,
            is_active=True
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session'
            }), 401
        
        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            db.session.commit()
            return jsonify({
                'success': False,
                'message': 'Session expired'
            }), 401
        
        # Get user info
        user = session.user
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Verification failed: {str(e)}'
        }), 500

@auth_bp.route('/user/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    """Get user information"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        # Verify authentication
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        session = UserSession.query.filter_by(
            session_token=token,
            is_active=True
        ).first()
        
        if not session or session.user_id != user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user: {str(e)}'
        }), 500
