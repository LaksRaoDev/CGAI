"""
Blog Content API Routes - Updated with Gemini AI
File: backend/api/routes/blog.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random
import os
import logging

# Create blueprint
blog_bp = Blueprint('blog', __name__)

# Import Gemini service
try:
    from services.gemini_service import get_gemini_service
    GEMINI_AVAILABLE = True
    logging.info("✅ Gemini AI service available for blog content")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logging.warning(f"⚠️ Gemini AI not available for blog content: {str(e)}")

# Fallback mock templates (keep as backup)
BLOG_TEMPLATES = {
    'article': {
        'informative': """# {topic}: A Comprehensive Guide

Understanding {topic} has become increasingly important in today's rapidly evolving landscape. This comprehensive guide explores the key concepts, benefits, and practical applications.

## What is {topic}?

{topic} represents a significant development that impacts various aspects of modern life. By examining the fundamentals, we can better understand its importance and potential applications.

## Key Benefits and Advantages

The implementation of {topic} offers numerous advantages:
- Enhanced efficiency and productivity
- Cost-effective solutions for businesses
- Improved user experience and satisfaction
- Scalable options for different needs

## Practical Implementation

When considering {topic}, it's essential to focus on practical steps that deliver real results. The most effective approach involves careful planning and gradual implementation.

## Future Outlook

As technology continues to advance, {topic} will likely play an even more significant role in shaping our future. Organizations that adapt early will be better positioned for success.

## Conclusion

{topic} represents both an opportunity and a necessity in our current environment. By understanding its potential and implementing it thoughtfully, we can achieve significant improvements in efficiency and outcomes.""",

        'conversational': """# Let's Talk About {topic}

Hey there! So you're curious about {topic}? That's awesome! This is one of those topics that seems complicated at first, but once you get the hang of it, everything starts to make sense.

## Why Should You Care About {topic}?

Look, I get it. Another thing to learn, right? But here's the thing - {topic} is actually pretty amazing when you see what it can do for you.

Think about it this way: remember when smartphones first came out and some people said "I don't need all that fancy stuff"? Well, {topic} is kind of like that, except it's happening right now.""",

        'professional': """# {topic}: Strategic Considerations and Implementation Framework

In today's competitive business environment, {topic} has emerged as a critical differentiator for organizations seeking sustainable growth and operational excellence.

## Executive Summary

This analysis examines the strategic implications of {topic} and provides a framework for successful implementation across diverse organizational contexts."""
    },
    'summary': """# {topic} - Key Points Summary

## Overview
{topic} represents a significant development in its field, offering numerous benefits and opportunities for implementation.

## Core Benefits
- Improved efficiency and productivity
- Cost-effective solutions
- Enhanced user experience
- Scalable implementation options""",
    
    'outline': """# {topic} - Comprehensive Outline

## I. Introduction
- Hook: Engaging opening statement about {topic}
- Background information and context
- Thesis statement and main objectives

## II. Understanding {topic}
- Definition and core concepts
- Current relevance and importance

## III. Key Benefits and Implementation
- Primary benefits and advantages
- Step-by-step implementation process""",
    
    'intro': """# Introduction: Understanding {topic}

In today's rapidly evolving landscape, {topic} has emerged as a pivotal element that shapes how we approach modern challenges and opportunities. Whether you're a seasoned professional or someone just beginning to explore this field, understanding {topic} is essential."""
}

@blog_bp.route('/generate', methods=['POST'])
def generate_blog_content():
    """Generate blog content using AI or fallback templates"""
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
        content_type = settings.get('contentType', 'article')
        style = settings.get('style', 'informative')
        word_count = int(settings.get('wordCount', 500))
        
        # Try Gemini AI first, fallback to templates
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here':
            try:
                logging.info(f"🤖 Using Gemini AI for blog content generation - {content_type}")
                gemini_service = get_gemini_service()
                result = gemini_service.generate_blog_content(topic, settings)
                
                if result['success']:
                    return jsonify({
                        'success': True,
                        'data': {
                            'content': result['content'],
                            'word_count': result['word_count'],
                            'content_type': content_type,
                            'ai_powered': True,
                            'model_used': result['model_used'],
                            'generation_time': result.get('generation_time', 0),
                            'settings_used': {
                                'content_type': content_type,
                                'style': style,
                                'word_count': word_count,
                                'audience': settings.get('audience', 'general')
                            }
                        },
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    logging.warning("⚠️ Gemini failed for blog, using fallback templates")
                    
            except Exception as e:
                logging.error(f"❌ Gemini error for blog: {str(e)}")
        
        # Fallback to mock templates
        logging.info(f"📝 Using mock templates for blog content generation - {content_type}")
        time.sleep(random.uniform(2, 4))  # Simulate processing
        
        content = generate_mock_content(topic, content_type, style, word_count, settings)
        
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'word_count': len(content.split()),
                'content_type': content_type,
                'ai_powered': False,
                'model_used': 'mock-template',
                'generation_time': random.uniform(2, 4),
                'settings_used': {
                    'content_type': content_type,
                    'style': style,
                    'word_count': word_count,
                    'audience': settings.get('audience', 'general')
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Blog content generation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_mock_content(topic, content_type, style, word_count, settings):
    """Generate blog content using mock templates (fallback)"""
    
    # Get template
    if content_type == 'article':
        template = BLOG_TEMPLATES['article'].get(style, BLOG_TEMPLATES['article']['informative'])
    else:
        template = BLOG_TEMPLATES.get(content_type, BLOG_TEMPLATES['summary'])
    
    # Generate base content
    content = template.format(topic=topic)
    
    # Adjust content length based on word count
    current_words = len(content.split())
    target_words = word_count
    
    if target_words < current_words * 0.7:
        # Shorten content
        paragraphs = content.split('\n\n')
        content = '\n\n'.join(paragraphs[:len(paragraphs)//2])
    elif target_words > current_words * 1.3:
        # Expand content
        content += f"""

## Additional Insights

Further exploration of {topic} reveals additional layers of complexity and opportunity. These advanced considerations provide deeper understanding for those ready to take their knowledge to the next level.

The interconnected nature of modern systems means that {topic} rarely exists in isolation. Understanding these relationships and dependencies is crucial for effective implementation and long-term success."""
    
    # Add SEO elements if enabled
    if settings.get('metaDescription', False):
        meta = f"**Meta Description:** Comprehensive guide to {topic} covering key concepts, benefits, implementation strategies, and best practices.\n\n"
        content = meta + content
    
    if settings.get('includeKeywords', False):
        content += f"\n\n**Target Keywords:** {topic}, implementation, benefits, strategy, guide, best practices"
    
    if settings.get('includeCTA', False):
        content += f"""

## Ready to Get Started?

Now that you understand the fundamentals of {topic}, it's time to take action. Start with small steps, apply what you've learned, and gradually build your expertise. Remember, every expert was once a beginner."""
    
    return content

@blog_bp.route('/templates', methods=['GET'])
def get_blog_templates():
    """Get available blog content templates and AI status"""
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
            'content_types': [
                {'id': 'article', 'name': 'Full Article', 'description': 'Complete blog article with sections'},
                {'id': 'summary', 'name': 'Summary', 'description': 'Brief overview with key points'},
                {'id': 'outline', 'name': 'Outline', 'description': 'Structured content outline'},
                {'id': 'intro', 'name': 'Introduction', 'description': 'Engaging article introduction'}
            ],
            'writing_styles': [
                {'id': 'informative', 'name': 'Informative', 'description': 'Educational and factual'},
                {'id': 'conversational', 'name': 'Conversational', 'description': 'Friendly and approachable'},
                {'id': 'professional', 'name': 'Professional', 'description': 'Business-focused and formal'},
                {'id': 'creative', 'name': 'Creative', 'description': 'Engaging and imaginative'},
                {'id': 'technical', 'name': 'Technical', 'description': 'Detailed and precise'},
                {'id': 'storytelling', 'name': 'Storytelling', 'description': 'Narrative-driven approach'}
            ],
            'word_counts': [300, 500, 800, 1000, 1500, 2000],
            'audiences': ['general', 'beginners', 'professionals', 'experts', 'students', 'entrepreneurs'],
            'categories': [
                'technology', 'business', 'lifestyle', 'health', 'education', 
                'travel', 'food', 'finance', 'marketing', 'personal'
            ],
            'ai_status': ai_status
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@blog_bp.route('/validate', methods=['POST'])
def validate_blog_input():
    """Validate blog content input"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        errors = []
        warnings = []
        
        if not topic:
            errors.append("Topic is required")
        elif len(topic) < 10:
            errors.append("Topic must be at least 10 characters")
        elif len(topic) > 200:
            errors.append("Topic must be less than 200 characters")
        
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
