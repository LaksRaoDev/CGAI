"""
Content History API Routes
File: backend/api/routes/history.py
"""
from flask import Blueprint, request, jsonify
from models.database import db, ContentHistory, UserSession, User
from datetime import datetime
from functools import wraps

history_bp = Blueprint('history', __name__)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        session = UserSession.query.filter_by(
            session_token=token,
            is_active=True
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired session'
            }), 401
        
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            db.session.commit()
            return jsonify({
                'success': False,
                'message': 'Session expired'
            }), 401
        
        # Add user to kwargs
        kwargs['current_user'] = session.user
        return f(*args, **kwargs)
    
    return decorated_function

@history_bp.route('/save', methods=['POST', 'OPTIONS'])
@require_auth
def save_content(current_user=None):
    """Save generated content to history"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('content_type') or not data.get('prompt') or not data.get('generated_content'):
            return jsonify({
                'success': False,
                'message': 'Content type, prompt and generated content are required'
            }), 400
        
        # Create history entry
        history = ContentHistory(
            user_id=current_user.id,
            content_type=data['content_type'],
            prompt=data['prompt'],
            generated_content=data['generated_content'],
            model_used=data.get('model_used', 'gpt2'),
            parameters=data.get('parameters', {})
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Content saved successfully',
            'history_id': history.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to save content: {str(e)}'
        }), 500

@history_bp.route('/list', methods=['GET', 'OPTIONS'])
@require_auth
def get_history(current_user=None):
    """Get user's content history"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        content_type = request.args.get('content_type', None)
        search = request.args.get('search', None)
        
        # Build query
        query = ContentHistory.query.filter_by(
            user_id=current_user.id,
            is_deleted=False
        )
        
        # Apply filters
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        if search:
            query = query.filter(
                db.or_(
                    ContentHistory.prompt.contains(search),
                    ContentHistory.generated_content.contains(search)
                )
            )
        
        # Order by created_at descending
        query = query.order_by(ContentHistory.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Format response
        history_items = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'history': history_items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get history: {str(e)}'
        }), 500

@history_bp.route('/<int:history_id>', methods=['GET', 'OPTIONS'])
@require_auth
def get_history_item(history_id, current_user=None):
    """Get specific history item"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        history = ContentHistory.query.filter_by(
            id=history_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not history:
            return jsonify({
                'success': False,
                'message': 'History item not found'
            }), 404
        
        return jsonify({
            'success': True,
            'history': history.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get history item: {str(e)}'
        }), 500

@history_bp.route('/<int:history_id>', methods=['PUT', 'OPTIONS'])
@require_auth
def update_history(history_id, current_user=None):
    """Update history item"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        history = ContentHistory.query.filter_by(
            id=history_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not history:
            return jsonify({
                'success': False,
                'message': 'History item not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'prompt' in data:
            history.prompt = data['prompt']
        if 'generated_content' in data:
            history.generated_content = data['generated_content']
        if 'parameters' in data:
            history.parameters = data['parameters']
        
        history.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'History updated successfully',
            'history': history.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update history: {str(e)}'
        }), 500

@history_bp.route('/<int:history_id>', methods=['DELETE', 'OPTIONS'])
@require_auth
def delete_history(history_id, current_user=None):
    """Delete history item (soft delete)"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        history = ContentHistory.query.filter_by(
            id=history_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not history:
            return jsonify({
                'success': False,
                'message': 'History item not found'
            }), 404
        
        # Soft delete
        history.is_deleted = True
        history.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'History item deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete history: {str(e)}'
        }), 500

@history_bp.route('/stats', methods=['GET', 'OPTIONS'])
@require_auth
def get_stats(current_user=None):
    """Get user's content generation statistics"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    try:
        # Get total count by content type
        stats = db.session.query(
            ContentHistory.content_type,
            db.func.count(ContentHistory.id).label('count')
        ).filter_by(
            user_id=current_user.id,
            is_deleted=False
        ).group_by(ContentHistory.content_type).all()
        
        # Get total content generated
        total = ContentHistory.query.filter_by(
            user_id=current_user.id,
            is_deleted=False
        ).count()
        
        # Format stats
        content_stats = {}
        for stat in stats:
            content_stats[stat.content_type] = stat.count
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'by_type': content_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get stats: {str(e)}'
        }), 500