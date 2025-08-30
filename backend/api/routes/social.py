"""
Social Media API Routes - Updated with Gemini AI
File: backend/api/routes/social.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random
import os
import logging

# Create blueprint
social_bp = Blueprint('social', __name__)

# Import Gemini service
try:
    from services.gemini_service import get_gemini_service
    GEMINI_AVAILABLE = True
    logging.info("✅ Gemini AI service available for social media")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logging.warning(f"⚠️ Gemini AI not available for social media: {str(e)}")

# Fallback mock templates (keep as backup)
SOCIAL_TEMPLATES = {
    'facebook': {
        'promotional': {
            'friendly': "Check out our amazing {topic}! Perfect for anyone looking to upgrade their experience. What do you think?",
            'professional': "Introducing our latest {topic}. Designed with excellence in mind for professionals who demand quality.",
            'enthusiastic': "OMG! You HAVE to see our new {topic}! This is going to change everything! Who's excited?"
        },
        'educational': {
            'friendly': "Did you know {topic} can completely transform your daily routine? Here's what makes it special...",
            'professional': "Understanding {topic}: Key insights and benefits for informed decision-making."
        }
    },
    'instagram': {
        'promotional': {
            'friendly': "✨ New drop alert! Our {topic} is here and it's absolutely gorgeous! Swipe to see more 📸",
            'enthusiastic': "🔥 OBSESSED with our new {topic}! This is everything you've been waiting for! ✨",
            'casual': "Sunday vibes with our latest {topic} 🌟 Simple, beautiful, perfect."
        }
    },
    'twitter': {
        'promotional': {
            'professional': "Introducing {topic} - engineered for excellence. Available now.",
            'urgent': "🚨 LIVE NOW: Get {topic} before it's gone! Limited time only.",
            'casual': "New {topic} just dropped and it's pretty great tbh"
        }
    },
    'linkedin': {
        'promotional': {
            'professional': "Proud to announce our latest innovation: {topic}. A testament to our commitment to excellence and innovation in the industry."
        },
        'educational': {
            'professional': "Industry insight: How {topic} is reshaping the landscape and what it means for professionals in our field."
        }
    }
}

# Platform-specific hashtags
PLATFORM_HASHTAGS = {
    'facebook': ['#community', '#share', '#connect'],
    'instagram': ['#insta', '#photooftheday', '#instagood'],
    'twitter': ['#trending', '#tech', '#business'],
    'linkedin': ['#professional', '#business', '#leadership']
}

@social_bp.route('/generate', methods=['POST'])
def generate_social_post():
    """Generate social media post using AI or fallback templates"""
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
        platform = settings.get('platform', 'facebook')
        post_type = settings.get('postType', 'promotional')
        tone = settings.get('tone', 'friendly')
        
        # Try Gemini AI first, fallback to templates
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here':
            try:
                logging.info(f"🤖 Using Gemini AI for social media post generation - {platform}")
                gemini_service = get_gemini_service()
                result = gemini_service.generate_social_post(topic, settings)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'data': {
                            'content': result['content'],
                            'character_count': result['character_count'],
                            'platform': result['platform'],
                            'hashtags_included': result['hashtags_included'],
                            'ai_powered': True,
                            'model_used': result['model_used'],
                            'settings_used': {
                                'platform': platform,
                                'post_type': post_type,
                                'tone': tone,
                                'length': settings.get('length', 'medium')
                            }
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    logging.warning("⚠️ Gemini failed for social, using fallback templates")
                    
            except Exception as e:
                logging.error(f"❌ Gemini error for social: {str(e)}")
        
        # Fallback to mock templates
        logging.info(f"📝 Using mock templates for social media generation - {platform}")
        time.sleep(random.uniform(1, 2))  # Simulate processing
        
        post_content = generate_mock_post(topic, platform, post_type, tone, settings)
        
        return jsonify({
            'success': True,
            'data': {
                'content': post_content,
                'character_count': len(post_content),
                'platform': platform,
                'hashtags_included': '#' in post_content,
                'ai_powered': False,
                'model_used': 'mock-template',
                'settings_used': {
                    'platform': platform,
                    'post_type': post_type,
                    'tone': tone,
                    'length': settings.get('length', 'medium')
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Social media generation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_mock_post(topic, platform, post_type, tone, settings):
    """Generate social media post using mock templates (fallback)"""
    
    # Get template
    platform_templates = SOCIAL_TEMPLATES.get(platform, SOCIAL_TEMPLATES['facebook'])
    type_templates = platform_templates.get(post_type, platform_templates['promotional'])
    template = type_templates.get(tone, list(type_templates.values())[0])
    
    # Generate base post
    post = template.format(topic=topic)
    
    # Add emojis if enabled
    if settings.get('includeEmojis', False):
        emoji_sets = {
            'enthusiastic': ['🔥', '✨', '🚀', '💯', '🎉'],
            'friendly': ['😊', '👋', '💙', '🌟', '✨'],
            'professional': ['💼', '🎯', '📈', '⭐', '🏆']
        }
        emojis = emoji_sets.get(tone, emoji_sets['friendly'])
        if platform in ['instagram', 'facebook']:
            post += ' ' + ' '.join(emojis[:3])
        elif platform == 'twitter':
            post += ' ' + ' '.join(emojis[:2])
    
    # Add CTA if enabled
    if settings.get('includeCTA', False):
        ctas = {
            'facebook': "\n\nReady to experience the difference? Click the link in bio!",
            'instagram': "\n\nTap the link in bio to get yours! 👆",
            'twitter': "\n\nGet yours now 👇",
            'linkedin': "\n\nLearn more about how this can benefit your organization."
        }
        post += ctas.get(platform, ctas['facebook'])
    
    # Add engagement question if enabled
    if settings.get('includeQuestion', False):
        questions = [
            "\n\nWhat do you think? Let us know in the comments!",
            "\n\nHave you tried something like this before? Share your experience!",
            "\n\nWhich feature excites you the most? Tell us below!"
        ]
        post += random.choice(questions)
    
    # Add hashtags if enabled
    if settings.get('autoHashtags', False):
        base_hashtags = ['#innovation', '#quality', '#lifestyle', '#technology']
        platform_specific = PLATFORM_HASHTAGS.get(platform, [])
        
        hashtags = base_hashtags + platform_specific
        
        # Add custom hashtags if provided
        custom_hashtags = settings.get('customHashtags', '')
        if custom_hashtags:
            custom_tags = [tag.strip() if tag.strip().startswith('#') else f"#{tag.strip()}" 
                          for tag in custom_hashtags.split(',')]
            hashtags.extend(custom_tags)
        
        # Limit hashtags
        hashtag_count = int(settings.get('hashtagCount', 5))
        hashtags = hashtags[:hashtag_count]
        post += '\n\n' + ' '.join(hashtags)
    
    return post

@social_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get available social media platforms and their configurations"""
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
            'platforms': [
                {
                    'id': 'facebook',
                    'name': 'Facebook',
                    'character_limit': 63206,
                    'supports_hashtags': True,
                    'supports_emojis': True
                },
                {
                    'id': 'instagram',
                    'name': 'Instagram',
                    'character_limit': 2200,
                    'supports_hashtags': True,
                    'supports_emojis': True
                },
                {
                    'id': 'twitter',
                    'name': 'Twitter',
                    'character_limit': 280,
                    'supports_hashtags': True,
                    'supports_emojis': True
                },
                {
                    'id': 'linkedin',
                    'name': 'LinkedIn',
                    'character_limit': 3000,
                    'supports_hashtags': True,
                    'supports_emojis': False
                },
                {
                    'id': 'tiktok',
                    'name': 'TikTok',
                    'character_limit': 2200,
                    'supports_hashtags': True,
                    'supports_emojis': True
                }
            ],
            'post_types': ['promotional', 'educational', 'engagement', 'storytelling', 'announcement'],
            'tones': ['friendly', 'professional', 'casual', 'enthusiastic', 'inspiring', 'humorous', 'urgent'],
            'ai_status': ai_status
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@social_bp.route('/validate', methods=['POST'])
def validate_social_input():
    """Validate social media post input"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        platform = data.get('platform', 'facebook')
        
        errors = []
        warnings = []
        
        if not topic:
            errors.append("Topic is required")
        elif len(topic) < 5:
            errors.append("Topic must be at least 5 characters")
        
        # Platform-specific validation
        platform_limits = {
            'twitter': 280,
            'instagram': 2200,
            'facebook': 63206,
            'linkedin': 3000,
            'tiktok': 2200
        }
        
        limit = platform_limits.get(platform, 280)
        if len(topic) > limit // 2:  # Reserve space for template text
            errors.append(f"Topic too long for {platform} (max ~{limit//2} characters)")
        
        # Check AI availability
        if not GEMINI_AVAILABLE or not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
            warnings.append("AI service not configured. Using mock templates.")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'platform_limit': limit,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': ['Invalid input format'],
            'warnings': [],
            'timestamp': datetime.utcnow().isoformat()
        }), 400
