"""
Google Gemini AI Service
File: backend/services/gemini_service.py
"""
import google.generativeai as genai
import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class GeminiService:
    """Service class for Google Gemini AI integration"""
    
    def __init__(self):
        """Initialize Gemini service"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and efficient
            logging.info("✅ Gemini service initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize Gemini model: {str(e)}")
            raise

    def generate_product_description(self, product_info: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product description using Gemini AI"""
        try:
            # Extract settings
            tone = settings.get('tone', 'professional')
            length = settings.get('length', 'medium')
            audience = settings.get('audience', 'general')
            category = settings.get('category', 'general')
            
            # Build comprehensive prompt
            prompt = self._build_product_prompt(product_info, tone, length, audience, category, settings)
            
            # Generate content
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Creative but controlled
                    max_output_tokens=800,  # Reasonable length
                    top_p=0.9,
                    top_k=40
                )
            )
            
            generation_time = time.time() - start_time
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            # Clean up response
            description = response.text.strip()
            
            return {
                'success': True,
                'description': description,
                'word_count': len(description.split()),
                'generation_time': round(generation_time, 2),
                'model_used': 'gemini-1.5-flash',
                'settings_applied': {
                    'tone': tone,
                    'length': length,
                    'audience': audience,
                    'category': category
                }
            }
            
        except Exception as e:
            logging.error(f"❌ Gemini generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback': self._get_fallback_description(product_info, settings)
            }

    def _build_product_prompt(self, product_info: str, tone: str, length: str, 
                            audience: str, category: str, settings: Dict[str, Any]) -> str:
        """Build comprehensive prompt for product description generation"""
        
        # Length guidelines
        length_guide = {
            'short': '50-100 words, concise and punchy',
            'medium': '100-200 words, balanced detail',
            'long': '200-300 words, comprehensive',
            'detailed': '300+ words, very thorough'
        }
        
        # Tone guidelines
        tone_guide = {
            'professional': 'formal, authoritative, business-focused',
            'casual': 'friendly, conversational, approachable',
            'luxury': 'premium, sophisticated, exclusive',
            'technical': 'detailed, specification-focused, precise',
            'enthusiastic': 'energetic, exciting, dynamic'
        }
        
        # Audience guidelines
        audience_guide = {
            'general': 'broad appeal, easy to understand',
            'professionals': 'industry-focused, technical benefits',
            'tech': 'feature-rich, innovation-focused',
            'young': 'trendy, lifestyle-focused',
            'families': 'practical, safety-focused',
            'seniors': 'clear benefits, easy-to-understand'
        }
        
        # Build prompt
        prompt = f"""You are an expert copywriter specializing in product descriptions. 

PRODUCT INFORMATION:
{product_info}

REQUIREMENTS:
- Tone: {tone_guide.get(tone, 'professional')}
- Length: {length_guide.get(length, 'balanced detail')}
- Target Audience: {audience_guide.get(audience, 'broad appeal')}
- Category: {category}

ADDITIONAL REQUIREMENTS:"""
        
        if settings.get('includeCTA', False):
            prompt += "\n- Include a compelling call-to-action"
        
        if settings.get('includeSpecs', False):
            prompt += "\n- Include key features/specifications section"
            
        if settings.get('seoKeywords', False):
            prompt += "\n- Naturally include relevant SEO keywords"
            
        if settings.get('seoMeta', False):
            prompt += "\n- Add a meta description at the end"

        prompt += f"""

INSTRUCTIONS:
1. Create a compelling product description that converts browsers into buyers
2. Focus on benefits, not just features
3. Use emotional triggers appropriate for the {audience} audience
4. Maintain {tone} tone throughout
5. Target word count: {length_guide.get(length, 'balanced detail')}
6. Make it scannable with good structure
7. Highlight what makes this product unique
8. Address potential customer concerns

Generate the product description now:"""
        
        return prompt

    def _get_fallback_description(self, product_info: str, settings: Dict[str, Any]) -> str:
        """Provide fallback description if AI fails"""
        tone = settings.get('tone', 'professional')
        
        fallback_templates = {
            'professional': f"Professional-grade {product_info} designed for discerning customers. This carefully crafted product delivers reliable performance and exceptional value.",
            'casual': f"Meet your new favorite {product_info}! This awesome product is packed with cool features that'll make your life easier and more enjoyable.",
            'luxury': f"Experience the ultimate in luxury with our exclusive {product_info}. Meticulously crafted from premium materials for the most discerning clientele."
        }
        
        base = fallback_templates.get(tone, fallback_templates['professional'])
        
        if settings.get('includeCTA', False):
            base += " Get yours today and experience the difference!"
            
        return base

    def generate_social_post(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media post using Gemini AI"""
        try:
            platform = settings.get('platform', 'general')
            tone = settings.get('tone', 'engaging')
            goal = settings.get('goal', 'engagement')
            
            prompt = self._build_social_prompt(topic, platform, tone, goal, settings)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,  # More creative for social content
                    max_output_tokens=300,
                    top_p=0.9
                )
            )
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            content = response.text.strip()
            
            return {
                'success': True,
                'content': content,
                'character_count': len(content),
                'platform': platform,
                'hashtags_included': '#' in content,
                'model_used': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            logging.error(f"❌ Social post generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_social_prompt(self, topic: str, platform: str, tone: str, 
                           goal: str, settings: Dict[str, Any]) -> str:
        """Build prompt for social media content"""
        
        platform_specs = {
            'twitter': 'Twitter (280 characters max, use hashtags, engaging)',
            'instagram': 'Instagram (catchy, visual-focused, hashtags)',
            'linkedin': 'LinkedIn (professional, business-focused, thought leadership)',
            'facebook': 'Facebook (conversational, community-focused)',
            'tiktok': 'TikTok (trendy, youth-focused, viral potential)'
        }
        
        prompt = f"""Create a {tone} social media post for {platform_specs.get(platform, 'social media')}.

TOPIC: {topic}
GOAL: {goal}
TONE: {tone}

Requirements:
- Platform-appropriate length and style
- Include relevant hashtags
- Engage the audience
- Clear call-to-action if needed
- Authentic and shareable content

Generate the social media post:"""
        
        return prompt

    def generate_marketing_copy(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing copy using Gemini AI"""
        try:
            copy_type = settings.get('copyType', 'email')
            tone = settings.get('tone', 'persuasive')
            goal = settings.get('goal', 'conversion')
            audience = settings.get('audience', 'business')
            
            prompt = self._build_marketing_prompt(topic, copy_type, tone, goal, audience, settings)
            
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,  # More creative for marketing
                    max_output_tokens=1000,
                    top_p=0.9
                )
            )
            
            generation_time = time.time() - start_time
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            content = response.text.strip()
            
            return {
                'success': True,
                'content': content,
                'word_count': len(content.split()),
                'generation_time': round(generation_time, 2),
                'model_used': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            logging.error(f"❌ Marketing copy generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_marketing_prompt(self, topic: str, copy_type: str, tone: str, 
                              goal: str, audience: str, settings: Dict[str, Any]) -> str:
        """Build prompt for marketing copy generation"""
        
        copy_specs = {
            'email': 'Email marketing campaign with subject line and body',
            'landing': 'Landing page copy with headlines and sections',
            'ad': 'Short advertisement copy (under 100 words)',
            'sales': 'Long-form sales page with multiple sections'
        }
        
        tone_guide = {
            'persuasive': 'compelling and convincing language',
            'urgent': 'time-sensitive and action-driven',
            'friendly': 'warm and approachable tone',
            'professional': 'business-focused and formal',
            'exciting': 'enthusiastic and energetic',
            'trustworthy': 'reliable and credible',
            'authoritative': 'expert and confident'
        }
        
        prompt = f"""You are an expert copywriter specializing in high-converting marketing content.

TOPIC: {topic}
COPY TYPE: {copy_specs.get(copy_type, 'Marketing copy')}
TONE: {tone_guide.get(tone, 'professional')}
GOAL: {goal}
AUDIENCE: {audience}

REQUIREMENTS:
- Focus on benefits over features
- Include compelling headlines
- Use emotional triggers
- Create urgency when appropriate
- Include clear call-to-action
- Write for {audience} audience
- Optimize for {goal}"""
        
        if copy_type == 'email':
            prompt += "\n- Include engaging subject line\n- Structure: Subject + Body"
        elif copy_type == 'landing':
            prompt += "\n- Include multiple sections with headers\n- Add social proof elements"
        elif copy_type == 'ad':
            prompt += "\n- Keep under 100 words\n- Focus on one key benefit"
        elif copy_type == 'sales':
            prompt += "\n- Create long-form content (300+ words)\n- Include guarantee and testimonials"
        
        if settings.get('includeUrgency', False):
            prompt += "\n- Add time-sensitive elements"
        if settings.get('includeGuarantee', False):
            prompt += "\n- Include money-back guarantee"
        if settings.get('includeSocialProof', False):
            prompt += "\n- Add customer testimonials or statistics"
        
        prompt += "\n\nGenerate the marketing copy now:"
        
        return prompt

    def generate_blog_content(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blog content using Gemini AI"""
        try:
            content_type = settings.get('contentType', 'article')
            style = settings.get('style', 'informative')
            word_count = int(settings.get('wordCount', 500))
            audience = settings.get('audience', 'general')
            
            prompt = self._build_blog_prompt(topic, content_type, style, word_count, audience, settings)
            
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Balanced creativity
                    max_output_tokens=1500,  # Longer for blog content
                    top_p=0.9
                )
            )
            
            generation_time = time.time() - start_time
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            content = response.text.strip()
            
            return {
                'success': True,
                'content': content,
                'word_count': len(content.split()),
                'generation_time': round(generation_time, 2),
                'model_used': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            logging.error(f"❌ Blog content generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_blog_prompt(self, topic: str, content_type: str, style: str, 
                         word_count: int, audience: str, settings: Dict[str, Any]) -> str:
        """Build prompt for blog content generation"""
        
        content_specs = {
            'article': 'Complete blog article with introduction, body sections, and conclusion',
            'summary': 'Concise summary with key points and takeaways',
            'outline': 'Structured outline with main points and subpoints',
            'intro': 'Engaging introduction that hooks readers and sets up the topic'
        }
        
        style_guide = {
            'informative': 'educational, factual, and well-researched',
            'conversational': 'friendly, approachable, and personal',
            'professional': 'business-focused, formal, and authoritative',
            'creative': 'engaging, imaginative, and unique',
            'technical': 'detailed, precise, and specification-focused',
            'storytelling': 'narrative-driven with compelling stories'
        }
        
        prompt = f"""You are an expert blog writer and content creator.

TOPIC: {topic}
CONTENT TYPE: {content_specs.get(content_type, 'Blog content')}
WRITING STYLE: {style_guide.get(style, 'informative')}
TARGET LENGTH: {word_count} words
AUDIENCE: {audience}

REQUIREMENTS:
- Create engaging, valuable content
- Use clear headings and structure
- Include actionable insights
- Write for {audience} audience
- Target approximately {word_count} words
- Use {style_guide.get(style, 'informative')} style"""
        
        if content_type == 'article':
            prompt += "\n- Include multiple sections with H2/H3 headings\n- Add introduction and conclusion"
        elif content_type == 'summary':
            prompt += "\n- Focus on key points and takeaways\n- Use bullet points for clarity"
        elif content_type == 'outline':
            prompt += "\n- Create hierarchical structure\n- Include main points and subpoints"
        elif content_type == 'intro':
            prompt += "\n- Hook readers from the first sentence\n- Preview what they'll learn"
        
        if settings.get('metaDescription', False):
            prompt += "\n- Include SEO meta description at the end"
        if settings.get('includeKeywords', False):
            prompt += "\n- Naturally incorporate relevant keywords"
        if settings.get('includeCTA', False):
            prompt += "\n- End with compelling call-to-action"
        
        prompt += "\n\nGenerate the blog content now:"
        
        return prompt

    def test_connection(self) -> Dict[str, Any]:
        """Test Gemini API connection"""
        try:
            response = self.model.generate_content("Test connection: say 'Hello from Gemini!'")
            return {
                'connected': True,
                'response': response.text if response else None,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get singleton instance of Gemini service"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
