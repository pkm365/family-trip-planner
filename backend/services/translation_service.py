"""
Translation Service with OpenAI Integration and Intelligent Caching

Provides efficient translation capabilities for activity content with:
- OpenAI GPT-4 translation for high quality results
- Intelligent caching to minimize API costs
- Batch processing for multiple activities
- Cultural context-aware translations for Chinese travelers
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import aiohttp

from ..config import settings
from ..models.translation_cache import TranslationCache

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for translating activity content with OpenAI API and caching.
    
    Features:
    - High-quality OpenAI GPT-4 translations
    - Intelligent caching to reduce costs
    - Batch translation for efficiency
    - Cultural context for Chinese travelers
    - Fallback handling for API failures
    """

    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.max_batch_size = 10  # Limit batch size for API constraints
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def translate_activity_content(
        self,
        db: Session,
        activity_data: Dict[str, Any],
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> Dict[str, Any]:
        """
        Translate activity content with cultural context.
        
        Args:
            db: Database session
            activity_data: Activity data with content to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Activity data with translated content
        """
        try:
            # Fields to translate
            translation_fields = {
                'description': 'description_zh',
                'name': 'name_zh',  # Optional - might want to keep original name
            }
            
            translated_data = activity_data.copy()
            
            for source_field, target_field in translation_fields.items():
                if source_field in activity_data and activity_data[source_field]:
                    source_text = activity_data[source_field]
                    
                    # Check cache first
                    cached_translation = TranslationCache.get_cached_translation(
                        db, source_text, source_lang, target_lang
                    )
                    
                    if cached_translation:
                        translated_data[target_field] = cached_translation
                        logger.info(f"Used cached translation for {source_field}")
                    else:
                        # Translate with OpenAI
                        translation = await self._translate_with_openai(
                            source_text, source_lang, target_lang, 
                            context_type="travel_activity"
                        )
                        
                        if translation:
                            translated_data[target_field] = translation
                            
                            # Cache the translation
                            TranslationCache.cache_translation(
                                db, source_text, translation, 
                                source_lang, target_lang,
                                service="openai", model="gpt-4"
                            )
                            logger.info(f"Translated and cached {source_field}")
                        else:
                            logger.warning(f"Failed to translate {source_field}")
            
            # Generate cultural content for Chinese travelers
            if target_lang == "zh" and activity_data.get("name"):
                cultural_content = await self._generate_cultural_content(
                    db, activity_data["name"], activity_data.get("description", "")
                )
                if cultural_content:
                    translated_data["cultural_notes_zh"] = cultural_content.get("cultural_notes")
                    translated_data["tips_for_chinese_travelers"] = cultural_content.get("travel_tips")
                    
            return translated_data
            
        except Exception as e:
            logger.error(f"Error translating activity content: {e}")
            return activity_data  # Return original data if translation fails

    async def batch_translate_activities(
        self,
        db: Session,
        activities: List[Dict[str, Any]],
        source_lang: str = "en",
        target_lang: str = "zh"
    ) -> List[Dict[str, Any]]:
        """
        Efficiently translate multiple activities in batches.
        
        Args:
            db: Database session
            activities: List of activity data dictionaries
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of activities with translated content
        """
        if not activities:
            return activities
            
        # Initialize session if not in context manager
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
            )
        
        translated_activities = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(activities), self.max_batch_size):
            batch = activities[i:i + self.max_batch_size]
            logger.info(f"Translating batch {i//self.max_batch_size + 1} ({len(batch)} activities)")
            
            # Translate each activity in the batch
            batch_tasks = [
                self.translate_activity_content(db, activity, source_lang, target_lang)
                for activity in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch translation: {result}")
                    # Add original data if translation failed
                    translated_activities.append(batch[len(translated_activities) % len(batch)])
                else:
                    translated_activities.append(result)
            
            # Small delay between batches to be respectful to API
            if i + self.max_batch_size < len(activities):
                await asyncio.sleep(1)
                
        return translated_activities

    async def _translate_with_openai(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context_type: str = "general"
    ) -> Optional[str]:
        """
        Translate text using OpenAI API with cultural context.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context_type: Type of content for context-aware translation
            
        Returns:
            Translated text or None if failed
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured")
            return None
            
        try:
            # Create context-aware prompt
            prompt = self._create_translation_prompt(text, source_lang, target_lang, context_type)
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional translator specializing in travel content for Chinese tourists visiting Japan. Provide accurate, culturally-aware translations."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3  # Lower temperature for more consistent translations
            }
            
            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    translation = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"OpenAI translation successful: {text[:50]}... -> {translation[:50]}...")
                    return translation
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None

    async def _generate_cultural_content(
        self,
        db: Session,
        activity_name: str,
        description: str
    ) -> Optional[Dict[str, str]]:
        """
        Generate cultural notes and travel tips for Chinese travelers.
        
        Args:
            db: Database session
            activity_name: Name of the activity/location
            description: Activity description
            
        Returns:
            Dictionary with cultural_notes and travel_tips
        """
        # Check cache first
        cache_key = f"cultural_content_{activity_name}"
        cached = TranslationCache.get_cached_translation(db, cache_key, "en", "zh")
        
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                pass  # Fall through to generate new content
        
        try:
            prompt = f"""
            为中国游客生成关于日本景点"{activity_name}"的文化背景和实用建议。

            景点描述: {description}

            请提供:
            1. 文化背景 (cultural_notes): 这个地方的历史文化意义，为什么对中国游客有趣
            2. 实用建议 (travel_tips): 中国游客的实用提示（支付方式、语言、最佳参观时间等）

            请用JSON格式回复:
            {{
                "cultural_notes": "文化背景说明...",
                "travel_tips": "实用旅行建议..."
            }}
            """
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专门为中国游客提供日本旅行建议的文化专家。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            async with self.session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content_str = result["choices"][0]["message"]["content"].strip()
                    
                    # Try to parse JSON response
                    try:
                        content_json = json.loads(content_str)
                        
                        # Cache the result
                        TranslationCache.cache_translation(
                            db, cache_key, content_str, "en", "zh",
                            service="openai", model="gpt-4"
                        )
                        
                        return content_json
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse cultural content JSON: {content_str}")
                        return None
                else:
                    logger.error(f"OpenAI API error for cultural content: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating cultural content: {e}")
            return None

    def _create_translation_prompt(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context_type: str
    ) -> str:
        """
        Create context-aware translation prompt.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context_type: Type of content
            
        Returns:
            Formatted translation prompt
        """
        lang_names = {
            "en": "English",
            "zh": "Chinese",
            "ja": "Japanese"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        if context_type == "travel_activity":
            context_instruction = """
            This is a travel activity description for Chinese tourists visiting Japan. 
            Please translate it in a way that:
            1. Maintains the informative tone
            2. Uses terminology familiar to Chinese travelers
            3. Considers cultural context and preferences
            4. Keeps the translation natural and engaging
            """
        else:
            context_instruction = "Please provide an accurate and natural translation."
        
        return f"""
        {context_instruction}

        Please translate the following {source_name} text to {target_name}:

        "{text}"

        Provide only the translation without any additional explanation.
        """

    def calculate_quality_score(
        self,
        activity: Dict[str, Any],
        external_rating: Optional[float] = None,
        review_count: Optional[int] = None
    ) -> int:
        """
        Calculate quality score for activity filtering.
        
        Args:
            activity: Activity data
            external_rating: External rating (e.g., Google rating)
            review_count: Number of external reviews
            
        Returns:
            Quality score (0-100)
        """
        score = 0
        
        # External rating weight (40%)
        rating = external_rating or activity.get("external_rating", 0)
        if rating >= 4.5:
            score += 40
        elif rating >= 4.0:
            score += 30
        elif rating >= 3.5:
            score += 20
        elif rating >= 3.0:
            score += 10
        
        # Review count weight (20%)
        reviews = review_count or activity.get("external_review_count", 0)
        if reviews >= 1000:
            score += 20
        elif reviews >= 500:
            score += 15
        elif reviews >= 100:
            score += 10
        elif reviews >= 50:
            score += 5
        
        # Family-friendly weight (20%)
        types = activity.get("types", [])
        category = activity.get("category", "")
        if any(term in str(types).lower() for term in ["family", "child"]):
            score += 20
        elif "tourist_attraction" in str(types).lower():
            score += 15
        elif category in ["sightseeing", "food"]:
            score += 10
        
        # Completeness weight (20%)
        if activity.get("description"):
            score += 10
        if activity.get("primary_image_url"):
            score += 5
        if activity.get("address") or activity.get("location_name"):
            score += 5
        
        return min(score, 100)  # Cap at 100


# Global service instance
translation_service = TranslationService()