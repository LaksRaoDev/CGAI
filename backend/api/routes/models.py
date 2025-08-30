# Model Management API Routes
# File: backend/api/routes/models.py

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from services.model_manager import get_model_manager

# Create blueprint
models_bp = Blueprint('models', __name__)

# Get model manager instance
model_manager = get_model_manager()

@models_bp.route('/list', methods=['GET'])
def list_models():
    """Get list of all available AI models"""
    try:
        models_data = model_manager.get_available_models()
        
        return jsonify({
            'success': True,
            'data': models_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to list models: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/current', methods=['GET'])
def get_current_model():
    """Get information about the currently active model"""
    try:
        model_info = model_manager.get_current_model_info()
        
        return jsonify({
            'success': True,
            'data': model_info,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to get current model: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/switch', methods=['POST'])
def switch_model():
    """Switch to a different AI model"""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({
                'success': False,
                'error': 'Model name is required',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        model_name = data['model']
        result = model_manager.switch_model(model_name)
        
        status_code = 200 if result['success'] else 400
        
        return jsonify({
            **result,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code
        
    except Exception as e:
        logging.error(f"❌ Failed to switch model: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/recommendations', methods=['POST'])
def get_model_recommendations():
    """Get model recommendations for specific content type and requirements"""
    try:
        data = request.get_json()
        content_type = data.get('content_type', 'general')
        requirements = data.get('requirements', {})
        
        recommendations = model_manager.get_model_recommendations(content_type, requirements)
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to get recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/comparison', methods=['GET'])
def get_model_comparison():
    """Get detailed comparison of all models"""
    try:
        comparison = model_manager.get_model_comparison()
        
        return jsonify({
            'success': True,
            'data': comparison,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to get model comparison: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get overall system and model status"""
    try:
        status = model_manager.get_system_status()
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to get system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/test', methods=['POST'])
def test_model():
    """Test a specific model or all models"""
    try:
        data = request.get_json() or {}
        model_name = data.get('model')
        
        if model_name:
            # Test specific model
            original_model = model_manager.current_model
            switch_result = model_manager.switch_model(model_name)
            
            if not switch_result['success']:
                return jsonify({
                    'success': False,
                    'error': switch_result['error'],
                    'timestamp': datetime.utcnow().isoformat()
                }), 400
            
            # Test with sample prompt
            test_prompt = "Write a brief product description for wireless earbuds."
            test_settings = {'max_length': 100, 'temperature': 0.7}
            
            result = model_manager.generate_content(test_prompt, 'product', test_settings)
            
            # Restore original model
            model_manager.switch_model(original_model)
            
            return jsonify({
                'success': True,
                'data': {
                    'model': model_name,
                    'test_result': result
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        else:
            # Test all models
            results = model_manager.test_all_models()
            
            return jsonify({
                'success': True,
                'data': results,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
    except Exception as e:
        logging.error(f"❌ Model test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/generate', methods=['POST'])
def generate_with_model():
    """Generate content using the current model"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        prompt = data.get('prompt')
        content_type = data.get('content_type', 'general')
        settings = data.get('settings', {})
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Generate content
        result = model_manager.generate_content(prompt, content_type, settings)
        
        status_code = 200 if result['success'] else 500
        
        return jsonify({
            **result,
            'timestamp': datetime.utcnow().isoformat()
        }), status_code
        
    except Exception as e:
        logging.error(f"❌ Content generation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@models_bp.route('/stats', methods=['GET'])
def get_model_stats():
    """Get model usage statistics"""
    try:
        stats = model_manager.model_stats
        
        # Calculate additional statistics
        total_uses = sum(stat.get('uses', 0) for stat in stats.values())
        avg_success_rate = sum(stat.get('success_rate', 0) for stat in stats.values()) / max(len(stats), 1)
        
        return jsonify({
            'success': True,
            'data': {
                'model_stats': stats,
                'summary': {
                    'total_uses': total_uses,
                    'average_success_rate': round(avg_success_rate, 1),
                    'most_used_model': max(stats.keys(), key=lambda x: stats[x].get('uses', 0)) if stats else None,
                    'models_tested': len(stats)
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"❌ Failed to get stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
