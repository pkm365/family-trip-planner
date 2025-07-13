"""
Translation Cache Model

Stores translations to avoid repeated API calls and improve performance.
Uses content hashing for efficient lookups and caching.
"""

import hashlib
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime

from .base import BaseModel


class TranslationCache(BaseModel):
    """
    Cache for translated content to avoid repeated API calls.
    
    Uses source text hash for efficient lookups while supporting
    different source and target language combinations.
    """

    __tablename__ = "translation_cache"

    id = Column(Integer, primary_key=True, index=True)

    # Source content identification
    source_text_hash = Column(String(64), nullable=False, index=True)
    source_language = Column(String(5), nullable=False, default="en")
    target_language = Column(String(5), nullable=False, default="zh")
    
    # Original and translated content
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Translation metadata
    translation_service = Column(String(50), nullable=True)  # 'openai', 'google', etc.
    translation_model = Column(String(50), nullable=True)  # 'gpt-4', 'gpt-3.5-turbo', etc.
    translation_quality_score = Column(Integer, nullable=True)  # Quality assessment if available
    
    # Usage tracking
    usage_count = Column(Integer, default=1)  # How many times this translation was used
    last_used_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Create composite index for efficient lookups
    __table_args__ = (
        Index('ix_translation_lookup', 'source_text_hash', 'source_language', 'target_language'),
    )

    def __repr__(self):
        return f"<TranslationCache(hash='{self.source_text_hash[:8]}...', {self.source_language}->{self.target_language})>"

    @staticmethod
    def generate_content_hash(text: str) -> str:
        """
        Generate a SHA-256 hash for the source text.
        
        Args:
            text: Source text to hash
            
        Returns:
            Hexadecimal hash string
        """
        if not text:
            return ""
        
        # Normalize text (strip whitespace, lowercase) for consistent hashing
        normalized_text = text.strip().lower()
        return hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()

    @classmethod
    def get_cached_translation(
        cls, 
        db, 
        source_text: str, 
        source_lang: str = "en", 
        target_lang: str = "zh"
    ) -> str:
        """
        Retrieve cached translation if available.
        
        Args:
            db: Database session
            source_text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Cached translation or None if not found
        """
        if not source_text or not source_text.strip():
            return None
            
        content_hash = cls.generate_content_hash(source_text)
        
        cached = db.query(cls).filter(
            cls.source_text_hash == content_hash,
            cls.source_language == source_lang,
            cls.target_language == target_lang
        ).first()
        
        if cached:
            # Update usage tracking
            cached.usage_count += 1
            cached.last_used_at = datetime.utcnow()
            db.commit()
            return cached.translated_text
            
        return None

    @classmethod
    def cache_translation(
        cls,
        db,
        source_text: str,
        translated_text: str,
        source_lang: str = "en",
        target_lang: str = "zh",
        service: str = None,
        model: str = None
    ) -> 'TranslationCache':
        """
        Cache a new translation.
        
        Args:
            db: Database session
            source_text: Original text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
            service: Translation service used
            model: Translation model used
            
        Returns:
            Created or updated cache entry
        """
        if not source_text or not translated_text:
            raise ValueError("Both source and translated text are required")
            
        content_hash = cls.generate_content_hash(source_text)
        
        # Check if already exists
        existing = db.query(cls).filter(
            cls.source_text_hash == content_hash,
            cls.source_language == source_lang,
            cls.target_language == target_lang
        ).first()
        
        if existing:
            # Update existing entry
            existing.translated_text = translated_text
            existing.translation_service = service
            existing.translation_model = model
            existing.updated_at = datetime.utcnow()
            db.commit()
            return existing
        
        # Create new cache entry
        cache_entry = cls(
            source_text_hash=content_hash,
            source_language=source_lang,
            target_language=target_lang,
            source_text=source_text,
            translated_text=translated_text,
            translation_service=service,
            translation_model=model
        )
        
        db.add(cache_entry)
        db.commit()
        db.refresh(cache_entry)
        
        return cache_entry

    @property
    def cache_age_days(self) -> int:
        """Get the age of this cache entry in days."""
        return (datetime.utcnow() - self.created_at).days

    def is_stale(self, max_age_days: int = 30) -> bool:
        """
        Check if this cache entry is stale and should be refreshed.
        
        Args:
            max_age_days: Maximum age before considering stale
            
        Returns:
            True if the cache entry is older than max_age_days
        """
        return self.cache_age_days > max_age_days