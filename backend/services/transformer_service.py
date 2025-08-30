# Hugging Face Transformers and GPT-2 Service
# File: backend/services/transformer_service.py

import torch
from transformers import (
    GPT2LMHeadModel, GPT2Tokenizer,
    T5ForConditionalGeneration, T5Tokenizer,
    BartForConditionalGeneration, BartTokenizer,
    AutoTokenizer, AutoModelForCausalLM
)
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import gc

class TransformerService:
    """Service class for Hugging Face Transformers integration"""
    
    def __init__(self):
        """Initialize transformer models"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.tokenizers = {}
        self.current_model = None
        
        # Available models
        self.available_models = {
            'gpt2': {
                'name': 'GPT-2',
                'description': 'OpenAI GPT-2 - Great for creative text generation',
                'model_class': GPT2LMHeadModel,
                'tokenizer_class': GPT2Tokenizer,
                'model_name': 'gpt2',
                'max_length': 1024,
                'use_case': 'general'
            },
            'gpt2-medium': {
                'name': 'GPT-2 Medium',
                'description': 'GPT-2 Medium - Better quality, slower generation',
                'model_class': GPT2LMHeadModel,
                'tokenizer_class': GPT2Tokenizer,
                'model_name': 'gpt2-medium',
                'max_length': 1024,
                'use_case': 'quality'
            },
            'distilgpt2': {
                'name': 'DistilGPT-2',
                'description': 'Distilled GPT-2 - Fast and lightweight',
                'model_class': GPT2LMHeadModel,
                'tokenizer_class': GPT2Tokenizer,
                'model_name': 'distilgpt2',
                'max_length': 1024,
                'use_case': 'fast'
            },
            't5-small': {
                'name': 'T5 Small',
                'description': 'T5 Small - Good for text-to-text tasks',
                'model_class': T5ForConditionalGeneration,
                'tokenizer_class': T5Tokenizer,
                'model_name': 't5-small',
                'max_length': 512,
                'use_case': 'summarization'
            },
            'bart-base': {
                'name': 'BART Base',
                'description': 'BART - Excellent for summarization and text generation',
                'model_class': BartForConditionalGeneration,
                'tokenizer_class': BartTokenizer,
                'model_name': 'facebook/bart-base',
                'max_length': 1024,
                'use_case': 'summarization'
            }
        }
        
        # Load default model (GPT-2)
        self.load_model('gpt2')
        
        logging.info(f"✅ TransformerService initialized with {len(self.available_models)} available models")

    def load_model(self, model_key: str) -> Dict[str, Any]:
        """Load a specific model"""
        try:
            if model_key not in self.available_models:
                raise ValueError(f"Unknown model: {model_key}")
            
            model_config = self.available_models[model_key]
            
            # Clear previous model from memory if different
            if self.current_model and self.current_model != model_key:
                self.unload_current_model()
            
            # Load model if not already loaded
            if model_key not in self.models:
                logging.info(f"🔄 Loading {model_config['name']}...")
                start_time = time.time()
                
                # Load tokenizer
                tokenizer = model_config['tokenizer_class'].from_pretrained(
                    model_config['model_name'],
                    padding_side='left'
                )
                
                # Add padding token if it doesn't exist
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                # Load model
                model = model_config['model_class'].from_pretrained(
                    model_config['model_name'],
                    torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32
                ).to(self.device)
                
                # Enable evaluation mode
                model.eval()
                
                self.models[model_key] = model
                self.tokenizers[model_key] = tokenizer
                
                load_time = time.time() - start_time
                logging.info(f"✅ {model_config['name']} loaded in {load_time:.2f}s")
            
            self.current_model = model_key
            
            return {
                'success': True,
                'model': model_key,
                'name': model_config['name'],
                'description': model_config['description'],
                'device': str(self.device)
            }
            
        except Exception as e:
            logging.error(f"❌ Failed to load model {model_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def unload_current_model(self):
        """Unload current model to free memory"""
        if self.current_model and self.current_model in self.models:
            del self.models[self.current_model]
            del self.tokenizers[self.current_model]
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            gc.collect()
            logging.info(f"🗑️ Unloaded {self.current_model}")

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return {
            'models': [
                {
                    'key': key,
                    'name': config['name'],
                    'description': config['description'],
                    'use_case': config['use_case'],
                    'max_length': config['max_length'],
                    'loaded': key in self.models
                }
                for key, config in self.available_models.items()
            ],
            'current_model': self.current_model,
            'device': str(self.device)
        }

    def generate_text(self, prompt: str, settings: Dict[str, Any], content_type: str = 'general') -> Dict[str, Any]:
        """Generate text using current transformer model"""
        try:
            if not self.current_model:
                raise Exception("No model loaded")
            
            model = self.models[self.current_model]
            tokenizer = self.tokenizers[self.current_model]
            
            # Build enhanced prompt based on content type
            enhanced_prompt = self._build_enhanced_prompt(prompt, content_type, settings)
            
            # Tokenize input
            inputs = tokenizer.encode(
                enhanced_prompt,
                return_tensors='pt',
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # Generation parameters
            max_length = min(
                settings.get('max_length', 200) + len(inputs[0]),
                self.available_models[self.current_model]['max_length']
            )
            
            temperature = settings.get('temperature', 0.7)
            top_p = settings.get('top_p', 0.9)
            top_k = settings.get('top_k', 50)
            repetition_penalty = settings.get('repetition_penalty', 1.1)
            
            # Generate text
            start_time = time.time()
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    min_length=len(inputs[0]) + 20,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repetition_penalty=repetition_penalty,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,
                    early_stopping=True
                )
            
            generation_time = time.time() - start_time
            
            # Decode generated text
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (remove prompt)
            generated_content = generated_text[len(enhanced_prompt):].strip()
            
            # Post-process based on content type
            final_content = self._post_process_content(generated_content, content_type, settings)
            
            return {
                'success': True,
                'content': final_content,
                'word_count': len(final_content.split()),
                'character_count': len(final_content),
                'generation_time': round(generation_time, 2),
                'model_used': self.available_models[self.current_model]['name'],
                'model_key': self.current_model,
                'settings_applied': {
                    'temperature': temperature,
                    'top_p': top_p,
                    'top_k': top_k,
                    'repetition_penalty': repetition_penalty
                }
            }
            
        except Exception as e:
            logging.error(f"❌ Text generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': self.current_model
            }

    def _build_enhanced_prompt(self, user_prompt: str, content_type: str, settings: Dict[str, Any]) -> str:
        """Build enhanced prompt based on content type"""
        
        prompts = {
            'product': {
                'prefix': 'Write a compelling product description for:',
                'context': 'Focus on benefits, features, and why customers should buy this product.',
                'format': 'Use persuasive language and include a call-to-action.'
            },
            'social': {
                'prefix': 'Create an engaging social media post about:',
                'context': 'Make it shareable, include relevant hashtags, and encourage interaction.',
                'format': 'Keep it concise and platform-appropriate.'
            },
            'blog': {
                'prefix': 'Write informative blog content about:',
                'context': 'Provide valuable insights and actionable information.',
                'format': 'Use clear structure with headings and bullet points where appropriate.'
            },
            'marketing': {
                'prefix': 'Create high-converting marketing copy for:',
                'context': 'Focus on benefits, address pain points, and drive action.',
                'format': 'Use persuasive language and strong call-to-action.'
            },
            'general': {
                'prefix': 'Write creative content about:',
                'context': 'Be engaging and informative.',
                'format': 'Use clear, compelling language.'
            }
        }
        
        prompt_config = prompts.get(content_type, prompts['general'])
        
        enhanced_prompt = f"{prompt_config['prefix']} {user_prompt}\n\n"
        enhanced_prompt += f"{prompt_config['context']} {prompt_config['format']}\n\n"
        
        # Add specific requirements
        tone = settings.get('tone', 'professional')
        if tone:
            enhanced_prompt += f"Tone: {tone.title()}\n"
        
        audience = settings.get('audience', 'general')
        if audience and audience != 'general':
            enhanced_prompt += f"Target audience: {audience}\n"
        
        enhanced_prompt += "\n"
        
        return enhanced_prompt

    def _post_process_content(self, content: str, content_type: str, settings: Dict[str, Any]) -> str:
        """Post-process generated content"""
        
        # Basic cleanup
        content = content.strip()
        
        # Remove incomplete sentences at the end
        sentences = content.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            content = '.'.join(sentences[:-1]) + '.'
        
        # Content type specific processing
        if content_type == 'social':
            # Ensure it's not too long for social media
            if len(content) > 280:  # Twitter limit
                content = content[:277] + '...'
        
        elif content_type == 'product':
            # Ensure it ends with a call-to-action if requested
            if settings.get('includeCTA', False) and not any(word in content.lower() for word in ['buy', 'order', 'purchase', 'get']):
                content += " Order now and experience the difference!"
        
        elif content_type == 'marketing':
            # Ensure strong ending
            if not content.endswith(('!', '?', '.')):
                content += '!'
        
        return content

    def switch_model(self, model_key: str) -> Dict[str, Any]:
        """Switch to a different model"""
        return self.load_model(model_key)

    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        if not self.current_model:
            return {'loaded': False}
        
        model_config = self.available_models[self.current_model]
        
        return {
            'loaded': True,
            'current_model': self.current_model,
            'model_name': model_config['name'],
            'description': model_config['description'],
            'device': str(self.device),
            'memory_usage': self._get_memory_usage()
        }

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        if torch.cuda.is_available():
            return {
                'gpu_allocated': f"{torch.cuda.memory_allocated() / 1024**2:.1f} MB",
                'gpu_reserved': f"{torch.cuda.memory_reserved() / 1024**2:.1f} MB",
                'device': 'CUDA'
            }
        else:
            return {
                'device': 'CPU',
                'message': 'Running on CPU - consider using GPU for better performance'
            }

    def generate_product_description(self, product_info: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product description using transformer model"""
        return self.generate_text(product_info, settings, 'product')

    def generate_social_post(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media post using transformer model"""
        return self.generate_text(topic, settings, 'social')

    def generate_marketing_copy(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing copy using transformer model"""
        return self.generate_text(topic, settings, 'marketing')

    def generate_blog_content(self, topic: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blog content using transformer model"""
        return self.generate_text(topic, settings, 'blog')

# Singleton instance
_transformer_service = None

def get_transformer_service() -> TransformerService:
    """Get singleton instance of transformer service"""
    global _transformer_service
    if _transformer_service is None:
        _transformer_service = TransformerService()
    return _transformer_service
