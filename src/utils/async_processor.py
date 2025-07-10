"""Asynchronous processing utilities for improved performance."""
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass
from loguru import logger
import time


@dataclass
class ProcessingResult:
    """Result of processing a single item."""
    item_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class AsyncPaperProcessor:
    """Process multiple papers concurrently."""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def process_papers_batch(
        self,
        papers: List[Dict],
        process_func: Callable[[Dict], bool],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """Process multiple papers in parallel."""
        results = []
        total = len(papers)
        completed = 0
        
        # Submit all tasks
        future_to_paper = {
            self.executor.submit(self._process_single, paper, process_func): paper
            for paper in papers
        }
        
        # Process completed tasks
        for future in as_completed(future_to_paper):
            paper = future_to_paper[future]
            result = future.result()
            results.append(result)
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
            
            logger.info(
                f"Processed {completed}/{total}: {paper.get('name', 'Unknown')} "
                f"({'Success' if result.success else 'Failed'})"
            )
        
        return results
    
    def _process_single(self, paper: Dict, process_func: Callable) -> ProcessingResult:
        """Process a single paper with timing."""
        start_time = time.time()
        paper_id = paper.get('id', 'unknown')
        
        try:
            result = process_func(paper)
            return ProcessingResult(
                item_id=paper_id,
                success=bool(result),
                result=result,
                processing_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error processing paper {paper_id}: {e}")
            return ProcessingResult(
                item_id=paper_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)


class BatchProcessor:
    """Process items in configurable batches."""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
    
    def process_in_batches(
        self,
        items: List[Any],
        process_func: Callable[[List[Any]], List[Any]],
        delay_between_batches: float = 0.0
    ) -> List[Any]:
        """Process items in batches with optional delay."""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            logger.debug(f"Processing batch {i//self.batch_size + 1} with {len(batch)} items")
            
            batch_results = process_func(batch)
            results.extend(batch_results)
            
            if delay_between_batches > 0 and i + self.batch_size < len(items):
                time.sleep(delay_between_batches)
        
        return results


class CacheManager:
    """Simple in-memory cache for API responses."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl_seconds:
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                # Expired
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"Cached value for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")