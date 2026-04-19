"""
Optimization utilities for AI Hedge Fund
==========================================
Improvements:
- Added logging module
- Enhanced error handling
- Added type hints
- Performance optimization
"""

import logging
import json
from typing import Dict, Any, Optional, List
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache for API responses."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                del self._cache[key]
                logger.debug(f"Cache expired: {key}")
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        self._cache[key] = (value, datetime.now())
        logger.debug(f"Cache set: {key}")
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        logger.info("Cache cleared")


# Global cache instance
_cache = CacheManager()


def get_cached_data(key: str) -> Optional[Any]:
    """Get cached data by key."""
    return _cache.get(key)


def set_cached_data(key: str, value: Any) -> None:
    """Set cached data with key."""
    _cache.set(key, value)


def clear_cache() -> None:
    """Clear the global cache."""
    _cache.clear()


def optimize_json_parsing(response: str) -> Optional[Dict[str, Any]]:
    """
    Enhanced JSON parsing with better error handling.
    
    Improvements:
    - More detailed error messages
    - Logging for debugging
    - Support for trailing commas and common JSON issues
    """
    try:
        # First try standard JSON parsing
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}")
        # Try to fix common issues
        fixed = response.replace(',}', '}').replace(',]', ']')
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON after fix attempt: {response[:200]}...")
            return None
    except TypeError as e:
        logger.error(f"Invalid response type: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return None


def validate_tickers(tickers: List[str]) -> List[str]:
    """
    Validate and clean ticker symbols.
    
    Improvements:
    - Uppercase normalization
    - Remove duplicates
    - Filter invalid symbols
    """
    seen = set()
    valid_tickers = []
    
    for ticker in tickers:
        cleaned = ticker.upper().strip()
        if cleaned and cleaned not in seen:
            if cleaned.isalpha() or '.' in cleaned:  # Allow symbols like BRK.B
                seen.add(cleaned)
                valid_tickers.append(cleaned)
                logger.debug(f"Valid ticker: {cleaned}")
            else:
                logger.warning(f"Invalid ticker filtered: {ticker}")
    
    return valid_tickers


def format_decision_output(decision: Dict[str, Any]) -> str:
    """
    Format trading decision for display.
    
    Improvements:
    - Pretty print JSON
    - Add timestamp
    - Color coding placeholder
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "decision": decision
    }
    return json.dumps(output, indent=2)
