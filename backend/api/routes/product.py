"""
Product Description API Routes - Updated with Gemini AI
File: backend/api/routes/product.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random
import os
import logging

# Create blueprint
product_bp = Blueprint('product', __name__)

# Import Gemini service
try:
    from services.gemini_service import get_gemini_service
    GEMINI_AVAILABLE = True
    logging.info("✅ Gemini AI service available")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logging.warning(f"⚠️ Gemini AI not available: {str(e)}")

# Fallback mock templates (keep as backup)
PRODUCT_TEMPLATES = {
    'professional': {
        'short': "Professional-grade {product} designed for discerning customers. Features premium build quality and reliable performance.",
        'medium': "Discover the superior quality of our {product}. This professionally engineered product combines cutting-edge technology with premium materials to deliver exceptional performance.",
        'long': "Experience unparalleled excellence with our {product}. This premium product represents the pinnacle of engineering and design, crafted for those who refuse to compromise on quality."
    },
    'casual': {
        'short': "Meet your new favorite {product}! Super easy to use and packed with cool features.",
        'medium': "Hey there! Looking for an awesome {product}? You've found it! This little gem is packed with amazing features that'll make your day so much better.",
        'long': "Alright, let's talk about this amazing {product} that's about to become your new best friend! This isn't just another product - it's like having a personal assistant."
    },
    'luxury': {
        'short': "Exquisite {product} crafted for the discerning connoisseur. Premium materials and sophisticated design.",
        'medium': "Indulge in the ultimate luxury with our exclusive {product}. Meticulously crafted from the finest materials and designed with sophisticated elegance.",
        'long': "Experience the epitome of luxury with our exquisite {product}, a masterpiece of craftsmanship and design that defines sophistication."
    }
}

@product_bp.route('/generate', methods=['POST'])
def generate_product_description():
    """Generate product description using AI or fallback templates"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Extract parameters
        product_info = data.get('product_info', '')
        settings = data.get('settings', {})
        
        if not product_info:
            return jsonify({
                'error': 'Product information is required',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Validate settings
        tone = settings.get('tone', 'professional')
        length = settings.get('length', 'medium')
        audience = settings.get('audience', 'general')
        category = settings.get('category', 'electronics')
        
        # Try Gemini AI first, fallback to templates
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here':
            try:
                logging.info("🤖 Using Gemini AI for product description generation")
                gemini_service = get_gemini_service()
                result = gemini_service.generate_product_description(product_info, settings)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'data': {
                            'description': result['description'],
                            'word_count': result['word_count'],
                            'generation_time': result['generation_time'],
                            'model_used': result['model_used'],
                            'ai_powered': True,
                            'settings_used': {
                                'tone': tone,
                                'length': length,
                                'audience': audience,
                                'category': category
                            }
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    logging.warning("⚠️ Gemini failed, using fallback templates")
                    
            except Exception as e:
                logging.error(f"❌ Gemini error: {str(e)}")
        
        # Fallback to mock templates
        logging.info("📝 Using mock templates for product description generation")
        time.sleep(random.uniform(1, 2))  # Simulate processing
        
        description = generate_mock_description(product_info, tone, length, settings)
        
        return jsonify({
            'success': True,
            'data': {
                'description': description,
                'word_count': len(description.split()),
                'generation_time': random.uniform(1, 2),
                'model_used': 'mock-template',
                'ai_powered': False,
                'settings_used': {
                    'tone': tone,
                    'length': length,
                    'audience': audience,
                    'category': category
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Product generation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_mock_description(product_info, tone, length, settings):
    """Generate product description using mock templates (fallback)"""
    
    # Get template
    template = PRODUCT_TEMPLATES.get(tone, PRODUCT_TEMPLATES['professional'])
    base_description = template.get(length, template['medium'])
    
    # Replace placeholder
    description = base_description.format(product=product_info)
    
    # Add elements based on settings
    if settings.get('includeCTA', False):
        ctas = [
            "Order now and experience the difference!",
            "Get yours today - limited stock available!",
            "Don't wait - transform your experience today!"
        ]
        description += "\n\n" + random.choice(ctas)
    
    if settings.get('includeSpecs', False):
        description += "\n\nKey Features:\n• Premium materials and construction\n• Advanced performance capabilities\n• Quality tested and certified"
    
    if settings.get('seoKeywords', False):
        keywords = f"\n\nKeywords: {product_info}, premium, quality, reliable, professional"
        description += keywords
    
    return description

@product_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get available product description templates and AI status"""
    ai_status = {
        'available': GEMINI_AVAILABLE,
        'model': 'gemini-1.5-flash' if GEMINI_AVAILABLE else None,
        'api_key_set': bool(os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here')
    }
    
    # Test connection if available
    if GEMINI_AVAILABLE and ai_status['api_key_set']:
        try:
            gemini_service = get_gemini_service()
            connection_test = gemini_service.test_connection()
            ai_status['connected'] = connection_test['connected']
        except Exception:
            ai_status['connected'] = False
    else:
        ai_status['connected'] = False
    
    return jsonify({
        'success': True,
        'data': {
            'tones': list(PRODUCT_TEMPLATES.keys()) + ['technical', 'enthusiastic'] if GEMINI_AVAILABLE else list(PRODUCT_TEMPLATES.keys()),
            'lengths': ['short', 'medium', 'long', 'detailed'] if GEMINI_AVAILABLE else ['short', 'medium', 'long'],
            'categories': [
                'electronics', 'fashion', 'home', 'beauty', 
                'sports', 'books', 'automotive', 'food',
                'technology', 'health', 'business', 'entertainment'
            ],
            'audiences': [
                'general', 'professionals', 'tech', 'young', 
                'families', 'seniors'
            ],
            'ai_status': ai_status
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@product_bp.route('/validate', methods=['POST'])
def validate_input():
    """Validate product description input"""
    try:
        data = request.get_json()
        product_info = data.get('product_info', '')
        
        errors = []
        warnings = []
        
        if not product_info:
            errors.append("Product information is required")
        elif len(product_info) < 10:
            errors.append("Product information must be at least 10 characters")
        elif len(product_info) > 500:
            errors.append("Product information must be less than 500 characters")
        
        # Check AI availability
        if not GEMINI_AVAILABLE or not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
            warnings.append("AI service not configured. Using mock templates.")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': ['Invalid input format'],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat()
        }), 400

@product_bp.route('/ai-status', methods=['GET'])
def get_ai_status():
    """Get current AI service status"""
    try:
        status = {
            'gemini_available': GEMINI_AVAILABLE,
            'api_key_configured': bool(os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here'),
            'service_status': 'offline',
            'model': None,
            'last_tested': datetime.utcnow().isoformat()
        }
        
        if GEMINI_AVAILABLE and status['api_key_configured']:
            try:
                gemini_service = get_gemini_service()
                test_result = gemini_service.test_connection()
                
                status['service_status'] = 'online' if test_result['connected'] else 'error'
                status['model'] = 'gemini-1.5-flash'
                status['test_response'] = test_result.get('response')
                
            except Exception as e:
                status['service_status'] = 'error'
                status['error'] = str(e)
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
