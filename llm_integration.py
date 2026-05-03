"""
LLM Integration Module for Dataset Curator
Handles AI-powered recommendations and description generation
"""

import os
import json
from typing import List, Dict, Optional
import logging

# Try importing different LLM providers
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from huggingface_hub import InferenceClient
    HAS_HF = True
except ImportError:
    HAS_HF = False

logger = logging.getLogger(__name__)


class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self):
        pass
    
    def generate_recommendation(self, user_problem: str, datasets: List[Dict]) -> Dict:
        """Generate recommendations based on user problem"""
        raise NotImplementedError
    
    def generate_description(self, dataset: Dict) -> str:
        """Generate human-readable description for a dataset"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
    
    def generate_recommendation(self, user_problem: str, datasets: List[Dict]) -> Dict:
        """Generate personalized dataset recommendations"""
        
        dataset_info = json.dumps(datasets, indent=2)
        
        prompt = f"""You are a helpful ML expert assistant. A user has described their dataset needs.
        
User's Problem: {user_problem}

Available Datasets:
{dataset_info}

Based on the user's problem and available datasets, provide:
1. Top 3 recommended datasets (list by name)
2. Why each is a good fit (2-3 sentences max per dataset)
3. Any preprocessing or preparation tips

Format your response as JSON with keys: "top_recommendations", "reasoning", "tips"
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert ML dataset curator. Provide concise, practical recommendations in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            return {
                "top_recommendations": [],
                "reasoning": response.choices[0].message.content,
                "tips": "Unable to parse structured response"
            }
    
    def generate_description(self, dataset: Dict) -> str:
        """Generate a human-readable description for a dataset"""
        
        prompt = f"""Generate a concise, engaging description (2-3 sentences) for this dataset:

Dataset Name: {dataset.get('name', 'Unknown')}
Domain: {dataset.get('domain', 'Unknown')}
Task: {dataset.get('task', 'Unknown')}
Samples: {dataset.get('samples', 'Unknown')}
Labels: {dataset.get('labels', 'Unknown')}
Model Types: {', '.join(dataset.get('model_types', []))}

Make it suitable for someone choosing a dataset for their ML project. Be specific about what this dataset is good for."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at writing clear, concise dataset descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-haiku-20240307"
    
    def generate_recommendation(self, user_problem: str, datasets: List[Dict]) -> Dict:
        """Generate personalized dataset recommendations"""
        
        dataset_info = json.dumps(datasets, indent=2)
        
        prompt = f"""You are a helpful ML expert assistant. A user has described their dataset needs.
        
User's Problem: {user_problem}

Available Datasets:
{dataset_info}

Based on the user's problem and available datasets, provide:
1. Top 3 recommended datasets (list by name)
2. Why each is a good fit (2-3 sentences max per dataset)
3. Any preprocessing or preparation tips

Format your response as JSON with keys: "top_recommendations", "reasoning", "tips"
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system="You are an expert ML dataset curator. Provide concise, practical recommendations in JSON format.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            result = json.loads(message.content[0].text)
            return result
        except json.JSONDecodeError:
            return {
                "top_recommendations": [],
                "reasoning": message.content[0].text,
                "tips": "Unable to parse structured response"
            }
    
    def generate_description(self, dataset: Dict) -> str:
        """Generate a human-readable description for a dataset"""
        
        prompt = f"""Generate a concise, engaging description (2-3 sentences) for this dataset:

Dataset Name: {dataset.get('name', 'Unknown')}
Domain: {dataset.get('domain', 'Unknown')}
Task: {dataset.get('task', 'Unknown')}
Samples: {dataset.get('samples', 'Unknown')}
Labels: {dataset.get('labels', 'Unknown')}
Model Types: {', '.join(dataset.get('model_types', []))}

Make it suitable for someone choosing a dataset for their ML project. Be specific about what this dataset is good for."""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=150,
            system="You are an expert at writing clear, concise dataset descriptions.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text.strip()


class HuggingFaceProvider(LLMProvider):
    """Hugging Face Inference API provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("HF_API_KEY")
        if not self.api_key:
            raise ValueError("Hugging Face API key not found. Set HF_API_KEY environment variable.")
        self.client = InferenceClient(api_key=self.api_key)
        self.model = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def generate_recommendation(self, user_problem: str, datasets: List[Dict]) -> Dict:
        """Generate personalized dataset recommendations"""
        
        dataset_info = json.dumps(datasets, indent=2)
        
        prompt = f"""You are a helpful ML expert assistant. A user has described their dataset needs.
        
User's Problem: {user_problem}

Available Datasets:
{dataset_info}

Based on the user's problem and available datasets, provide:
1. Top 3 recommended datasets (list by name)
2. Why each is a good fit
3. Any preprocessing tips

Respond in JSON format."""
        
        response = self.client.text_generation(
            prompt,
            max_new_tokens=500,
            temperature=0.7
        )
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {
                "top_recommendations": [],
                "reasoning": response,
                "tips": "Unable to parse structured response"
            }
    
    def generate_description(self, dataset: Dict) -> str:
        """Generate a human-readable description for a dataset"""
        
        prompt = f"""Generate a concise description (2-3 sentences) for this ML dataset:
Name: {dataset.get('name', 'Unknown')}, Domain: {dataset.get('domain', 'Unknown')}, Task: {dataset.get('task', 'Unknown')}"""
        
        response = self.client.text_generation(
            prompt,
            max_new_tokens=150,
            temperature=0.7
        )
        
        return response.strip()


class FallbackProvider(LLMProvider):
    """Fallback provider with template-based recommendations (no API needed)"""
    
    def generate_recommendation(self, user_problem: str, datasets: List[Dict]) -> Dict:
        """Generate template-based recommendations"""
        
        # Simple heuristic-based recommendations
        recommendations = {
            "top_recommendations": [d['name'] for d in datasets[:3]],
            "reasoning": f"Based on your requirement: '{user_problem}', we recommend these datasets for your use case.",
            "tips": "Consider checking dataset documentation for preprocessing requirements and checking sample sizes for your needs."
        }
        return recommendations
    
    def generate_description(self, dataset: Dict) -> str:
        """Generate template-based description"""
        
        return f"{dataset.get('name')} is a {dataset.get('domain')} dataset suitable for {dataset.get('task')} tasks with {dataset.get('samples')} samples and {dataset.get('labels')} labels."


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Get an LLM provider instance
    
    Args:
        provider_name: Specific provider to use ('openai', 'anthropic', 'huggingface', 'fallback')
                       If None, tries providers in order of availability
    
    Returns:
        LLMProvider instance
    """
    
    if provider_name:
        if provider_name.lower() == "openai" and HAS_OPENAI:
            return OpenAIProvider()
        elif provider_name.lower() == "anthropic" and HAS_ANTHROPIC:
            return AnthropicProvider()
        elif provider_name.lower() == "huggingface" and HAS_HF:
            return HuggingFaceProvider()
        elif provider_name.lower() == "fallback":
            return FallbackProvider()
        else:
            logger.warning(f"Provider {provider_name} not available, using fallback")
            return FallbackProvider()
    
    # Try providers in order of preference
    if HAS_OPENAI:
        try:
            return OpenAIProvider()
        except ValueError as e:
            logger.warning(f"OpenAI provider not available: {e}")
    
    if HAS_ANTHROPIC:
        try:
            return AnthropicProvider()
        except ValueError as e:
            logger.warning(f"Anthropic provider not available: {e}")
    
    if HAS_HF:
        try:
            return HuggingFaceProvider()
        except ValueError as e:
            logger.warning(f"Hugging Face provider not available: {e}")
    
    logger.info("Using fallback provider")
    return FallbackProvider()


# Cache for generated descriptions
_description_cache: Dict[str, str] = {}


def get_dataset_description(dataset: Dict, use_cache: bool = True, provider: Optional[str] = None) -> str:
    """
    Get an AI-generated description for a dataset
    
    Args:
        dataset: Dataset dictionary
        use_cache: Whether to use cached descriptions
        provider: Specific LLM provider to use
    
    Returns:
        Description string
    """
    
    cache_key = dataset.get('name', '')
    
    if use_cache and cache_key in _description_cache:
        return _description_cache[cache_key]
    
    try:
        llm = get_llm_provider(provider)
        description = llm.generate_description(dataset)
        
        if use_cache:
            _description_cache[cache_key] = description
        
        return description
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        return f"{dataset.get('name')} is a {dataset.get('domain')} dataset for {dataset.get('task')} tasks."


def get_smart_recommendations(user_problem: str, datasets: List[Dict], provider: Optional[str] = None) -> Dict:
    """
    Get AI-powered dataset recommendations based on user's problem description
    
    Args:
        user_problem: User's description of their ML problem
        datasets: List of available datasets
        provider: Specific LLM provider to use
    
    Returns:
        Dictionary with recommendations, reasoning, and tips
    """
    
    if not user_problem or not user_problem.strip():
        return {
            "error": "Please describe your ML problem",
            "top_recommendations": [],
            "reasoning": "",
            "tips": ""
        }
    
    try:
        llm = get_llm_provider(provider)
        recommendations = llm.generate_recommendation(user_problem, datasets)
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "error": f"Error generating recommendations: {str(e)}",
            "top_recommendations": [d['name'] for d in datasets[:3]],
            "reasoning": "Fallback to basic recommendations",
            "tips": "Please check dataset documentation"
        }
