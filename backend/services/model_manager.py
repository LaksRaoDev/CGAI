# AI Model Manager - Handles switching between different AI models
# File: backend/services/model_manager.py

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .gemini_service import get_gemini_service, GeminiService
from .transformer_service import get_transformer_service, TransformerService
import asyncio
import time

class ModelManager:
    """Centralized manager for all AI models"""
    
    def __init__(self):
        """Initialize model manager"""
        self.current_model = 'gemini'  # Default to Gemini
        self.models = {}
        self.model_stats = {}
        
        # Available model providers
        self.available_providers = {
            'gemini': {
                'name': 'Google Gemini',
                'description': 'Google\'s most capable AI model - Fast, accurate, and versatile',
                'strengths': ['Speed', 'Quality', 'Versatility', 'Context Understanding'],
                'best_for': ['All content types', 'Complex queries', 'Creative writing'],
                'cost': 'Low',
                'speed': 'Fast',
                'quality': 'Excellent'
            },
            'gpt2': {
                'name': 'GPT-2',
                'description': 'OpenAI GPT-2 - Reliable open-source model for text generation',
                'strengths': ['Free', 'Offline', 'Customizable', 'Privacy-focused'],
                'best_for': ['Basic content', 'Offline usage', 'Custom fine-tuning'],
                'cost': 'Free',
                'speed': 'Medium',
                'quality': 'Good'
            },
            'gpt2-medium': {
                'name': 'GPT-2 Medium',
                'description': 'Larger GPT-2 model - Better quality but slower generation',
                'strengths': ['Better quality', 'More coherent', 'Free'],
                'best_for': ['Higher quality content', 'Longer texts'],
                'cost': 'Free',
                'speed': 'Slower',
                'quality': 'Very Good'
            },
            'distilgpt2': {
                'name': 'DistilGPT-2',
                'description': 'Lightweight GPT-2 variant - Fast and efficient',
                'strengths': ['Very fast', 'Lightweight', 'Low memory'],
                'best_for': ['Quick generation', 'Limited resources'],
                'cost': 'Free',
                'speed': 'Very Fast',
                'quality': 'Fair'
            },
            't5-small': {
                'name': 'T5 Small',
                'description': 'Google T5 - Excellent for text-to-text tasks',
                'strengths': ['Text-to-text', 'Summarization', 'Translation'],
                'best_for': ['Summarization', 'Text transformation'],
                'cost': 'Free',
                'speed': 'Fast',
                'quality': 'Good'
            },
            'bart-base': {
                'name': 'BART',
                'description': 'Facebook BART - Great for summarization and generation',
                'strengths': ['Summarization', 'Text generation', 'Paraphrasing'],
                'best_for': ['Blog summaries', 'Content rewriting'],
                'cost': 'Free',
                'speed': 'Medium',
                'quality': 'Very Good'
            }
        }
        
        self.initialize_services()
        
        logging.info("🤖 ModelManager initialized with all AI model providers")

    def initialize_services(self):
        """Initialize all AI services"""
        try:
            # Initialize Gemini service
            self.models['gemini'] = get_gemini_service()
            logging.info("✅ Gemini service initialized")
        except Exception as e:
            logging.warning(f"⚠️ Gemini service failed to initialize: {str(e)}")
            self.models['gemini'] = None
        
        try:
            # Initialize Transformer service
            transformer_service = get_transformer_service()
            self.models['gpt2'] = transformer_service
            self.models['gpt2-medium'] = transformer_service
            self.models['distilgpt2'] = transformer_service
            self.models['t5-small'] = transformer_service
            self.models['bart-base'] = transformer_service
            logging.info("✅ Transformer services initialized")
        except Exception as e:
            logging.warning(f"⚠️ Transformer services failed to initialize: {str(e)}")

    def switch_model(self, model_name: str) -> Dict[str, Any]:
        """Switch to a different AI model"""
        try:
            if model_name not in self.available_providers:
                return {
                    'success': False,
                    'error': f'Unknown model: {model_name}',
                    'available_models': list(self.available_providers.keys())
                }
            
            # Handle Gemini model
            if model_name == 'gemini':
                if self.models.get('gemini') is None:
                    return {
                        'success': False,
                        'error': 'Gemini service not available. Please check API key configuration.'
                    }
                self.current_model = model_name
                
                return {
                    'success': True,
                    'current_model': model_name,
                    'model_info': self.available_providers[model_name],
                    'message': f'Switched to {self.available_providers[model_name]["name"]}'
                }
            
            # Handle transformer models
            else:
                transformer_service = self.models.get('gpt2')  # All transformer models use the same service
                if transformer_service is None:
                    return {
                        'success': False,
                        'error': 'Transformer service not available'
                    }
                
                # Switch the transformer model
                result = transformer_service.switch_model(model_name)
                if result['success']:
                    self.current_model = model_name
                    result['model_info'] = self.available_providers[model_name]
                    result['message'] = f'Switched to {self.available_providers[model_name]["name"]}'
                
                return result
                
        except Exception as e:
            logging.error(f"❌ Failed to switch model to {model_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_content(self, prompt: str, content_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using the current model"""
        try:
            start_time = time.time()
            
            # Route to appropriate service based on current model
            if self.current_model == 'gemini':
                result = self._generate_with_gemini(prompt, content_type, settings)
            else:
                result = self._generate_with_transformer(prompt, content_type, settings)
            
            # Add model manager metadata
            result['model_manager'] = {
                'current_model': self.current_model,
                'model_name': self.available_providers[self.current_model]['name'],
                'total_generation_time': round(time.time() - start_time, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Update statistics
            self._update_stats(self.current_model, result['success'])
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Content generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'current_model': self.current_model
            }

    def _generate_with_gemini(self, prompt: str, content_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using Gemini AI"""
        gemini_service = self.models['gemini']
        
        if content_type == 'product':
            return gemini_service.generate_product_description(prompt, settings)
        elif content_type == 'social':
            return gemini_service.generate_social_post(prompt, settings)
        elif content_type == 'blog':
            return gemini_service.generate_blog_content(prompt, settings)
        elif content_type == 'marketing':
            return gemini_service.generate_marketing_copy(prompt, settings)
        else:
            return gemini_service.generate_product_description(prompt, settings)

    def _generate_with_transformer(self, prompt: str, content_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using Transformer models"""
        transformer_service = self.models['gpt2']  # All use the same service instance
        
        if content_type == 'product':
            return transformer_service.generate_product_description(prompt, settings)
        elif content_type == 'social':
            return transformer_service.generate_social_post(prompt, settings)
        elif content_type == 'blog':
            return transformer_service.generate_blog_content(prompt, settings)
        elif content_type == 'marketing':
            return transformer_service.generate_marketing_copy(prompt, settings)
        else:
            return transformer_service.generate_text(prompt, settings, content_type)

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of all available models with their details"""
        models_list = []
        
        for model_key, model_info in self.available_providers.items():
            # Check if model is actually available
            is_available = self._check_model_availability(model_key)
            
            models_list.append({
                'key': model_key,
                'name': model_info['name'],
                'description': model_info['description'],
                'strengths': model_info['strengths'],
                'best_for': model_info['best_for'],
                'cost': model_info['cost'],
                'speed': model_info['speed'],
                'quality': model_info['quality'],
                'available': is_available,
                'current': model_key == self.current_model,
                'stats': self.model_stats.get(model_key, {'uses': 0, 'success_rate': 100})
            })
        
        return {
            'models': models_list,
            'current_model': self.current_model,
            'total_models': len(models_list),
            'available_models': sum(1 for m in models_list if m['available'])
        }

    def _check_model_availability(self, model_key: str) -> bool:
        """Check if a specific model is available"""
        if model_key == 'gemini':
            return self.models.get('gemini') is not None
        else:
            return self.models.get('gpt2') is not None

    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if self.current_model not in self.available_providers:
            return {'error': 'No model currently selected'}
        
        model_info = self.available_providers[self.current_model].copy()
        model_info['key'] = self.current_model
        model_info['stats'] = self.model_stats.get(self.current_model, {'uses': 0, 'success_rate': 100})
        
        # Add service-specific status
        if self.current_model == 'gemini':
            service = self.models.get('gemini')
            if service:
                model_info['status'] = 'Ready'
            else:
                model_info['status'] = 'Not Available'
        else:
            transformer_service = self.models.get('gpt2')
            if transformer_service:
                status = transformer_service.get_model_status()
                model_info['status'] = 'Ready' if status.get('loaded') else 'Loading'
                model_info['device'] = status.get('device', 'Unknown')
                if 'memory_usage' in status:
                    model_info['memory_usage'] = status['memory_usage']
        
        return model_info

    def get_model_recommendations(self, content_type: str, requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get model recommendations based on content type and requirements"""
        if requirements is None:
            requirements = {}
        
        priority_speed = requirements.get('priority_speed', False)
        priority_quality = requirements.get('priority_quality', False)
        priority_cost = requirements.get('priority_cost', False)
        
        recommendations = []
        
        # Content type specific recommendations
        if content_type == 'product':
            recommendations = [
                {'model': 'gemini', 'score': 95, 'reason': 'Excellent for persuasive product descriptions'},
                {'model': 'gpt2-medium', 'score': 85, 'reason': 'Good quality, free alternative'},
                {'model': 'gpt2', 'score': 75, 'reason': 'Solid choice for basic product descriptions'}
            ]
        
        elif content_type == 'social':
            recommendations = [
                {'model': 'gemini', 'score': 98, 'reason': 'Perfect for engaging social content'},
                {'model': 'distilgpt2', 'score': 80, 'reason': 'Fast generation for social media'},
                {'model': 'gpt2', 'score': 70, 'reason': 'Decent for basic social posts'}
            ]
        
        elif content_type == 'blog':
            recommendations = [
                {'model': 'gemini', 'score': 92, 'reason': 'Best for comprehensive blog content'},
                {'model': 'bart-base', 'score': 88, 'reason': 'Excellent for structured content'},
                {'model': 'gpt2-medium', 'score': 82, 'reason': 'Good for longer articles'}
            ]
        
        elif content_type == 'marketing':
            recommendations = [
                {'model': 'gemini', 'score': 96, 'reason': 'Superior persuasive writing abilities'},
                {'model': 'gpt2-medium', 'score': 78, 'reason': 'Decent marketing copy generation'},
                {'model': 'gpt2', 'score': 68, 'reason': 'Basic marketing content'}
            ]
        
        # Apply user preferences
        if priority_speed:
            speed_bonus = {'distilgpt2': 15, 'gemini': 10, 'gpt2': 5}
            for rec in recommendations:
                rec['score'] += speed_bonus.get(rec['model'], 0)
        
        if priority_quality:
            quality_bonus = {'gemini': 20, 'gpt2-medium': 10, 'bart-base': 10}
            for rec in recommendations:
                rec['score'] += quality_bonus.get(rec['model'], 0)
        
        if priority_cost:
            cost_bonus = {'gpt2': 15, 'gpt2-medium': 15, 'distilgpt2': 15, 't5-small': 15, 'bart-base': 15}
            for rec in recommendations:
                rec['score'] += cost_bonus.get(rec['model'], 0)
        
        # Sort by score and filter available models
        available_recommendations = [
            rec for rec in recommendations 
            if self._check_model_availability(rec['model'])
        ]
        available_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'content_type': content_type,
            'recommendations': available_recommendations[:3],  # Top 3
            'current_model': self.current_model,
            'requirements_applied': requirements
        }

    def _update_stats(self, model_name: str, success: bool):
        """Update model usage statistics"""
        if model_name not in self.model_stats:
            self.model_stats[model_name] = {'uses': 0, 'successes': 0, 'success_rate': 100}
        
        stats = self.model_stats[model_name]
        stats['uses'] += 1
        if success:
            stats['successes'] = stats.get('successes', 0) + 1
        
        stats['success_rate'] = round((stats.get('successes', 0) / stats['uses']) * 100, 1)

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            'model_manager': {
                'status': 'operational',
                'current_model': self.current_model,
                'initialized_models': len([k for k, v in self.models.items() if v is not None])
            },
            'services': {},
            'statistics': self.model_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check Gemini service
        if self.models.get('gemini'):
            try:
                gemini_test = self.models['gemini'].test_connection()
                status['services']['gemini'] = {
                    'status': 'operational' if gemini_test['connected'] else 'error',
                    'details': gemini_test
                }
            except Exception as e:
                status['services']['gemini'] = {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            status['services']['gemini'] = {
                'status': 'not_configured',
                'message': 'Gemini API key not provided'
            }
        
        # Check Transformer service
        if self.models.get('gpt2'):
            try:
                transformer_status = self.models['gpt2'].get_model_status()
                status['services']['transformers'] = {
                    'status': 'operational' if transformer_status.get('loaded') else 'loading',
                    'details': transformer_status
                }
            except Exception as e:
                status['services']['transformers'] = {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            status['services']['transformers'] = {
                'status': 'error',
                'message': 'Transformer service not initialized'
            }
        
        return status

# Singleton instance
_model_manager = None

def get_model_manager() -> ModelManager:
    """Get singleton instance of model manager"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
