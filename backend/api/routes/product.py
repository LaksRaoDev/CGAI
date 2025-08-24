"""
Product Description API Routes
File: backend/api/routes/product.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random

# Create blueprint
product_bp = Blueprint('product', __name__)

# Mock templates for product descriptions
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
    """Generate product description based on input"""
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
        
        # Simulate processing time
        time.sleep(random.uniform(1, 3))
        
        # Generate description
        description = generate_description(product_info, tone, length, settings)
        
        # Return response
        return jsonify({
            'success': True,
            'data': {
                'description': description,
                'word_count': len(description.split()),
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
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_description(product_info, tone, length, settings):
    """Generate product description using templates"""
    
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
    """Get available product description templates"""
    return jsonify({
        'success': True,
        'data': {
            'tones': list(PRODUCT_TEMPLATES.keys()),
            'lengths': ['short', 'medium', 'long'],
            'categories': [
                'electronics', 'fashion', 'home', 'beauty', 
                'sports', 'books', 'automotive', 'food'
            ],
            'audiences': [
                'general', 'professionals', 'tech', 'young', 
                'families', 'seniors'
            ]
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
        
        if not product_info:
            errors.append("Product information is required")
        elif len(product_info) < 10:
            errors.append("Product information must be at least 10 characters")
        elif len(product_info) > 500:
            errors.append("Product information must be less than 500 characters")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': ['Invalid input format'],
            'timestamp': datetime.utcnow().isoformat()
        }), 400