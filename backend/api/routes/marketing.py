"""
Marketing Copy API Routes
File: backend/api/routes/marketing.py
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import random

# Create blueprint
marketing_bp = Blueprint('marketing', __name__)

# Marketing copy templates
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
The Team

P.S. Still thinking about it? Check out what Sarah M. said: "This completely changed my approach to {topic}. I wish I'd started sooner!\""""
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

🚨 WHAT YOU MISS IF YOU WAIT:
→ Paying 3x more later
→ Missing the bonus content
→ Staying stuck with old methods

Right now: $97 (Regular price: $297)
Tomorrow: GONE.

[CLAIM YOUR SPOT NOW]

This isn't a drill. When the timer hits zero, this offer vanishes.

Act now or regret later.

[SECURE YOUR ACCESS - FINAL HOURS]"""
        },
        'friendly': {
            'subject': "Hey! Quick question about {topic}",
            'body': """Hey friend!

Hope you're having an amazing day! 

I wanted to reach out because I know you've been interested in {topic}, and I just had to share this with you.

We've been working on something pretty special, and honestly? I think you're going to love it.

It's all about making {topic} simple, effective, and actually enjoyable. (Yes, really!)

Here's what caught my attention:
• Real results in the first week
• Super easy to get started
• Works even if you're a complete beginner
• Costs less than your monthly coffee budget

Want to take a quick look? No pressure at all - just thought you might find it interesting.

[CHECK IT OUT HERE]

Let me know what you think!

Talk soon,
[Your Name]

P.S. There's a small bonus if you check it out today, but no worries if you can't. It'll still be awesome tomorrow!"""
        }
    },
    'landing': {
        'persuasive': """# Finally! The Complete {topic} Solution You've Been Searching For

## Struggling with {topic}? You're Not Alone.

Thousands of people just like you have been frustrated by complicated, expensive, and ineffective solutions. But what if there was a better way?

## Introducing the Revolutionary {topic} System

Our breakthrough approach has helped over 10,000 people achieve remarkable results in just weeks, not months.

### ✅ What You Get:
- Complete step-by-step system
- Video tutorials and guides  
- 24/7 support community
- 30-day money-back guarantee
- Exclusive bonus materials worth $297

### ✅ What You'll Achieve:
- Master {topic} in record time
- Save hours every week
- See results from day one
- Gain confidence and expertise

## Don't Just Take Our Word For It

*"This system completely transformed my approach to {topic}. I went from struggling beginner to confident expert in just 30 days!"* - Sarah M.

## Limited Time: Special Launch Price

~~Regular Price: $297~~
**Today Only: $97** (Save $200!)

### 🎁 BONUS: Order in the next 20 minutes and get:
- Advanced techniques course ($97 value)
- Private community access ($47 value)  
- 1-on-1 consultation ($197 value)

**Total Value: $638 - Your Price: Just $97**

[GET INSTANT ACCESS NOW - $97]

*30-day money-back guarantee. No questions asked.*""",

        'urgent': """# 🚨 URGENT: {topic} Solution - Only 24 Hours Left!

## This Offer DISAPPEARS at Midnight Tonight!

You've been thinking about mastering {topic} for months. Maybe even years.

How much longer will you wait?

## What Happens When You Keep Waiting:
❌ Prices go up (next week it's $297)
❌ You miss the bonus materials (worth $341)
❌ You stay frustrated with current methods
❌ Others get ahead while you fall behind

## What Happens When You Act TODAY:
✅ Lock in the lowest price ever ($97 vs $297)
✅ Get $341 in bonus materials FREE
✅ Start seeing results within 48 hours
✅ Join 10,000+ success stories

## ⏰ COUNTDOWN TIMER: [23:47:32]

Every second you wait, you're choosing to stay where you are.

Don't let this moment slip away.

[SECURE YOUR COPY NOW - FINAL HOURS]

*Warning: When this timer hits zero, this offer is gone forever. No exceptions. No extensions.*

## Still Hesitating? Here's What Others Say:

*"I almost didn't buy because I thought I'd wait. Thank God I didn't! This changed everything for me."* - Mike T.

[CLAIM YOUR SPOT BEFORE MIDNIGHT]"""
    },
    'ad': {
        'persuasive': """Tired of struggling with {topic}?

Our proven system has helped 10,000+ people master {topic} in just weeks.

✓ Easy to follow
✓ Guaranteed results  
✓ 30-day money back

Limited time: 50% off

[Start Your Transformation Today]""",

        'urgent': """LAST CHANCE: {topic} Solution

24 HOURS LEFT!

Don't miss out on the system that's changing lives.

Regular price: $297
TODAY ONLY: $97

[Secure Your Copy Now]

Timer: ⏰ 23:58:42""",

        'exciting': """🔥 BREAKTHROUGH: {topic} Just Got 10x Easier!

This is HUGE! 

The {topic} method everyone's talking about is finally here.

✨ 10,000+ success stories
✨ Works in just days
✨ No prior experience needed

Ready to be next?

[Join the Revolution]"""
    },
    'sales': """# The Ultimate {topic} Transformation System

## Your Current Situation (And Why It's Not Your Fault)

You've tried everything. Books, courses, YouTube videos, expensive consultations. Yet you're still struggling with {topic}.

Here's the truth: It's not because you're not smart enough or dedicated enough. It's because you've been using outdated, incomplete methods.

## The Solution That Changes Everything

After 5 years of research and testing with over 10,000 students, we've cracked the code on {topic}.

### The {topic} Master System includes:

**Module 1: Foundation Mastery** ($97 value)
- Core principles that 99% of people get wrong
- The 3-step framework for instant results
- Common mistakes that sabotage success

**Module 2: Advanced Strategies** ($197 value)
- Professional-level techniques
- Case studies from real success stories
- Troubleshooting guide for any situation

**Module 3: Implementation Blueprint** ($147 value)
- Step-by-step action plans
- Templates and checklists
- 90-day roadmap to mastery

**BONUS 1: Private Community Access** ($97 value)
- Connect with 10,000+ members
- Weekly Q&A sessions
- Peer support and accountability

**BONUS 2: 1-on-1 Strategy Session** ($297 value)
- Personal consultation with expert
- Customized action plan
- Direct access for questions

### Total Value: $835
### Your Investment Today: Just $197

## Why This Price Won't Last

We're keeping this introductory price for the first 500 students only. After that, it goes to the full price of $497.

## Our Iron-Clad Guarantee

Try the {topic} Master System for 60 days. If you don't see dramatic improvement, we'll refund every penny. No questions asked.

## What Our Students Say

*"I've spent thousands on {topic} training. This $197 system taught me more in 30 days than everything else combined."* - Jennifer L.

*"Skeptical at first, but the results speak for themselves. Worth every penny and more."* - David R.

## Ready to Transform Your {topic} Skills?

Don't let another day pass wondering "what if."

[ENROLL NOW - $197]

Questions? Email us at support@example.com or call 1-800-XXX-XXXX"""
}

@marketing_bp.route('/generate', methods=['POST'])
def generate_marketing_copy():
    """Generate marketing copy based on input"""
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
        
        # Simulate processing time
        time.sleep(random.uniform(2, 3))
        
        # Generate copy
        copy_content = generate_copy(topic, copy_type, tone, settings)
        
        # Calculate conversion score (mock)
        conversion_score = random.randint(75, 95)
        
        return jsonify({
            'success': True,
            'data': {
                'content': copy_content,
                'word_count': len(copy_content.split()),
                'conversion_score': conversion_score,
                'copy_type': copy_type,
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
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def generate_copy(topic, copy_type, tone, settings):
    """Generate marketing copy using templates"""
    
    # Get template
    copy_templates = MARKETING_TEMPLATES.get(copy_type, MARKETING_TEMPLATES['email'])
    
    if copy_type == 'email':
        template = copy_templates.get(tone, copy_templates['persuasive'])
        copy = f"Subject: {template['subject']}\n\n{template['body']}"
    elif copy_type in ['landing', 'sales']:
        template = copy_templates.get(tone, copy_templates['persuasive'] if copy_type == 'landing' else copy_templates)
        copy = template
    else:  # ad
        template = copy_templates.get(tone, copy_templates['persuasive'])
        copy = template
    
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

@marketing_bp.route('/templates', methods=['GET'])
def get_marketing_templates():
    """Get available marketing copy templates and options"""
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
            'cta_styles': ['direct', 'benefit', 'urgent', 'social']
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
        
        # Mock analysis (in real app, use ML models)
        analysis = {
            'conversion_score': random.randint(70, 95),
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
        
        if not topic:
            errors.append("Topic is required")
        elif len(topic) < 5:
            errors.append("Topic must be at least 5 characters")
        elif len(topic) > 300:
            errors.append("Topic must be less than 300 characters")
        
        # Copy type specific validation
        if copy_type not in ['email', 'landing', 'ad', 'sales']:
            errors.append("Invalid copy type")
        
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