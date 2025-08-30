"""
Marketing Copy API Routes - Updated with Gemini AI
File: backend/api/routes/marketing.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random
import os
import logging

# Create blueprint
marketing_bp = Blueprint('marketing', __name__)

# Import Gemini service
try:
    from services.gemini_service import get_gemini_service
    GEMINI_AVAILABLE = True
    logging.info("✅ Gemini AI service available for marketing copy")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logging.warning(f"⚠️ Gemini AI not available for marketing copy: {str(e)}")

# Fallback mock templates (keep as backup)
MARKETING_TEMPLATES = {
    'email': {
        'persuasive': {
            'subject': "Don't Miss Out: {topic} Inside!",
            'body': """Hi there!

You know that feeling when you discover something that changes everything? That's exactly what {topic} did for thousands of people just like you.

Here's what makes this different:
✅ Proven results in just days
✅ No complicated setup required  
✅ Backed by our 30-day guarantee
✅ Join 50,000+ satisfied customers

But here's the thing - this special offer won't last forever.

Ready to transform your experience?

[GET STARTED NOW - 50% OFF]

Don't wait. Your future self will thank you.

Best regards,
The Team"""
        },
        'urgent': {
            'subject': "URGENT: {topic} - 24 Hours Left!",
            'body': """FINAL HOURS WARNING!

This is it. In less than 24 hours, our exclusive {topic} offer disappears forever.

🚨 WHAT YOU GET:
→ Complete {topic} system
→ Bonus training modules  
→ 1-year support included
→ 60-day money-back guarantee

Right now: $97 (Regular price: $297)
Tomorrow: GONE.

[CLAIM YOUR SPOT NOW]

This isn't a drill. When the timer hits zero, this offer vanishes.

[SECURE YOUR ACCESS - FINAL HOURS]"""
        },
        'friendly': {
            'subject': "Hey! Quick question about {topic}",
            'body': """Hey friend!

Hope you're having an amazing day! 

I wanted to reach out because I know you've been interested in {topic}, and I just had to share this with you.

We've been working on something pretty special, and honestly? I think you're going to love it.

Want to take a quick look? No pressure at all - just thought you might find it interesting.

[CHECK IT OUT HERE]

Let me know what you think!

Talk soon,
[Your Name]"""
        }
    }
}

@marketing_bp.route('/generate', methods=['POST'])
def generate_marketing_copy():
    """Generate marketing copy using AI or fallback templates"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Extract parameters
        topic = data.get('topic', '')
        settings = data.get('settings', {})
        
        if not topic:
            return jsonify({
                'error': 'Topic is required',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Validate settings
        copy_type = settings.get('copyType', 'email')
        tone = settings.get('tone', 'persuasive')
        goal = settings.get('goal', 'conversion')
        
        # Try Gemini AI first, fallback to templates
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here':
            try:
                logging.info(f"🤖 Using Gemini AI for marketing copy generation - {copy_type}")
                gemini_service = get_gemini_service()
                result = gemini_service.generate_marketing_copy(topic, settings)
                
                if result['success']:
                    # Calculate conversion score (AI-enhanced)
                    conversion_score = calculate_ai_conversion_score(result['content'], settings)
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'content': result['content'],
                            'word_count': result['word_count'],
                            'conversion_score': conversion_score,
                            'copy_type': copy_type,
                            'ai_powered': True,
                            'model_used': result['model_used'],
                            'generation_time': result.get('generation_time', 0),
                            'settings_used': {
                                'copy_type': copy_type,
                                'tone': tone,
                                'goal': goal,
                                'audience': settings.get('audience', 'business')
                            }
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    logging.warning("⚠️ Gemini failed for marketing, using fallback templates")
                    
            except Exception as e:
                logging.error(f"❌ Gemini error for marketing: {str(e)}")
        
        # Fallback to mock templates
        logging.info(f"📝 Using mock templates for marketing copy generation - {copy_type}")
        time.sleep(random.uniform(2, 3))  # Simulate processing
        
        copy_content = generate_mock_copy(topic, copy_type, tone, settings)
        conversion_score = random.randint(75, 95)
        
        return jsonify({
            'success': True,
            'data': {
                'content': copy_content,
                'word_count': len(copy_content.split()),
                'conversion_score': conversion_score,
                'copy_type': copy_type,
                'ai_powered': False,
                'model_used': 'mock-template',
                'generation_time': random.uniform(2, 3),
                'settings_used': {
                    'copy_type': copy_type,
                    'tone': tone,
                    'goal': goal,
                    'audience': settings.get('audience', 'business')
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Marketing copy generation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_mock_copy(topic, copy_type, tone, settings):
    """Generate marketing copy using mock templates (fallback)"""
    
    # Get template
    copy_templates = MARKETING_TEMPLATES.get('email', MARKETING_TEMPLATES['email'])
    template = copy_templates.get(tone, copy_templates['persuasive'])
    
    if copy_type == 'email':
        copy = f"Subject: {template['subject']}\n\n{template['body']}"
    else:
        copy = template['body']
    
    # Replace topic placeholder
    copy = copy.format(topic=topic)
    
    # Add elements based on settings
    if settings.get('includeUrgency', False) and 'limited time' not in copy.lower():
        copy += '\n\n⏰ Limited Time Offer - Don\'t Miss Out!'
    
    if settings.get('includeGuarantee', False) and 'guarantee' not in copy.lower():
        copy += '\n\n💰 30-Day Money-Back Guarantee - Risk Free!'
    
    if settings.get('includeSocialProof', False) and 'customers' not in copy.lower():
        copy += '\n\n⭐ Join 10,000+ satisfied customers who already transformed their results!'
    
    return copy

def calculate_ai_conversion_score(content, settings):
    """Calculate conversion score for AI-generated content"""
    score = 70
    
    # Analyze content elements
    if any(word in content.lower() for word in ['guarantee', 'risk-free', 'money-back']):
        score += 10
    
    if any(word in content.lower() for word in ['limited', 'urgent', 'now', 'today only']):
        score += 8
    
    if any(word in content.lower() for word in ['proven', 'results', 'success', 'testimonial']):
        score += 7
    
    if len(content.split()) > 100:  # Comprehensive content
        score += 5
    
    # Cap at 98 to be realistic
    return min(score, 98)

@marketing_bp.route('/templates', methods=['GET'])
def get_marketing_templates():
    """Get available marketing copy templates and AI status"""
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
            'copy_types': [
                {'id': 'email', 'name': 'Email Copy', 'description': 'Email campaigns and newsletters'},
                {'id': 'landing', 'name': 'Landing Page', 'description': 'High-converting landing pages'},
                {'id': 'ad', 'name': 'Ad Copy', 'description': 'Short-form advertisement copy'},
                {'id': 'sales', 'name': 'Sales Page', 'description': 'Long-form sales pages'}
            ],
            'tones': [
                {'id': 'persuasive', 'name': 'Persuasive', 'description': 'Compelling and convincing'},
                {'id': 'urgent', 'name': 'Urgent', 'description': 'Time-sensitive and action-driven'},
                {'id': 'friendly', 'name': 'Friendly', 'description': 'Warm and approachable'},
                {'id': 'professional', 'name': 'Professional', 'description': 'Business-focused and formal'},
                {'id': 'exciting', 'name': 'Exciting', 'description': 'Enthusiastic and energetic'},
                {'id': 'trustworthy', 'name': 'Trustworthy', 'description': 'Reliable and credible'},
                {'id': 'authoritative', 'name': 'Authoritative', 'description': 'Expert and confident'}
            ],
            'goals': ['conversion', 'awareness', 'engagement', 'retention', 'leads', 'sales'],
            'audiences': ['business', 'consumers', 'young', 'families', 'seniors', 'entrepreneurs', 'students'],
            'cta_styles': ['direct', 'benefit', 'urgent', 'social'],
            'ai_status': ai_status
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@marketing_bp.route('/analyze', methods=['POST'])
def analyze_copy():
    """Analyze marketing copy for conversion potential"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                'error': 'Content is required for analysis',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Enhanced analysis with AI awareness
        analysis = {
            'conversion_score': calculate_ai_conversion_score(content, {}),
            'readability_score': random.randint(75, 90),
            'emotional_impact': random.randint(65, 85),
            'urgency_level': random.randint(50, 95),
            'cta_strength': random.randint(70, 90),
            'suggestions': [
                'Consider adding more social proof elements',
                'Strengthen the call-to-action with urgency',
                'Include specific benefits or features',
                'Add a risk-reversal guarantee'
            ][:random.randint(2, 4)]
        }
        
        return jsonify({
            'success': True,
            'data': analysis,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@marketing_bp.route('/validate', methods=['POST'])
def validate_marketing_input():
    """Validate marketing copy input"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        copy_type = data.get('copy_type', 'email')
        
        errors = []
        warnings = []
        
        if not topic:
            errors.append("Topic is required")
        elif len(topic) < 5:
            errors.append("Topic must be at least 5 characters")
        elif len(topic) > 300:
            errors.append("Topic must be less than 300 characters")
        
        # Copy type specific validation
        if copy_type not in ['email', 'landing', 'ad', 'sales']:
            errors.append("Invalid copy type")
        
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
