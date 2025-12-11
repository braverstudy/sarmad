"""
X API v2 Mock Layer
Simulates Twitter/X API v2 endpoints for testing.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class APIResponse:
    """Standard API response wrapper."""
    data: Any
    meta: Dict[str, Any]
    includes: Optional[Dict[str, Any]] = None


class MockXAPI:
    """
    Simulated X API v2 interface.
    Matches the structure of real X API v2 responses.
    """
    
    def __init__(self, dataset: List[Dict[str, Any]]):
        """Initialize with synthetic dataset."""
        self.dataset = dataset
        self._index_by_id = {t["id"]: t for t in dataset}
        self._index_by_conversation = {}
        
        for tweet in dataset:
            conv_id = tweet.get("conversation_id")
            if conv_id:
                if conv_id not in self._index_by_conversation:
                    self._index_by_conversation[conv_id] = []
                self._index_by_conversation[conv_id].append(tweet)
    
    def search_recent(
        self,
        query: str,
        start_time: datetime = None,
        end_time: datetime = None,
        max_results: int = 100
    ) -> APIResponse:
        """
        GET /2/tweets/search/recent
        
        Search for tweets matching query within time range.
        """
        results = []
        
        for tweet in self.dataset:
            # Time filter
            tweet_time = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
            
            if start_time and tweet_time < start_time:
                continue
            if end_time and tweet_time > end_time:
                continue
            
            # Query filter (simple keyword matching)
            text = tweet.get("text", "")
            if query.lower() in text.lower():
                results.append(tweet)
            
            if len(results) >= max_results:
                break
        
        return APIResponse(
            data=results,
            meta={
                "result_count": len(results),
                "newest_id": results[0]["id"] if results else None,
                "oldest_id": results[-1]["id"] if results else None
            }
        )
    
    def get_tweet(self, tweet_id: str) -> APIResponse:
        """
        GET /2/tweets/:id
        
        Get a single tweet by ID.
        """
        tweet = self._index_by_id.get(tweet_id)
        
        if not tweet:
            return APIResponse(
                data=None,
                meta={"error": "Tweet not found"}
            )
        
        return APIResponse(
            data=tweet,
            meta={}
        )
    
    def get_conversation(
        self, 
        conversation_id: str,
        max_results: int = 100
    ) -> APIResponse:
        """
        GET /2/tweets/search/recent?conversation_id=
        
        Get all tweets in a conversation thread.
        """
        tweets = self._index_by_conversation.get(conversation_id, [])
        tweets = tweets[:max_results]
        
        return APIResponse(
            data=tweets,
            meta={
                "result_count": len(tweets)
            }
        )
    
    def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 100
    ) -> APIResponse:
        """
        GET /2/users/:id/tweets
        
        Get tweets by a specific user.
        """
        tweets = [
            t for t in self.dataset 
            if t.get("author_id") == user_id
        ][:max_results]
        
        return APIResponse(
            data=tweets,
            meta={
                "result_count": len(tweets)
            }
        )
    
    def count_tweets(
        self,
        query: str,
        start_time: datetime = None,
        end_time: datetime = None,
        granularity: str = "hour"
    ) -> APIResponse:
        """
        GET /2/tweets/counts/recent
        
        Count tweets matching query, grouped by time.
        """
        counts = {}
        
        for tweet in self.dataset:
            text = tweet.get("text", "")
            if query.lower() not in text.lower():
                continue
            
            tweet_time = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
            
            if start_time and tweet_time < start_time:
                continue
            if end_time and tweet_time > end_time:
                continue
            
            if granularity == "hour":
                key = tweet_time.strftime("%Y-%m-%dT%H:00:00Z")
            elif granularity == "minute":
                key = tweet_time.strftime("%Y-%m-%dT%H:%M:00Z")
            else:
                key = tweet_time.strftime("%Y-%m-%dT00:00:00Z")
            
            counts[key] = counts.get(key, 0) + 1
        
        data = [
            {"start": k, "end": k, "tweet_count": v}
            for k, v in sorted(counts.items())
        ]
        
        return APIResponse(
            data=data,
            meta={
                "total_tweet_count": sum(counts.values())
            }
        )


def create_mock_api(dataset: List[Dict[str, Any]]) -> MockXAPI:
    """Factory function to create mock API instance."""
    return MockXAPI(dataset)


if __name__ == "__main__":
    # Test X API mock
    from data_generator import generate_synthetic_dataset
    
    tweets = generate_synthetic_dataset()
    api = create_mock_api(tweets)
    
    print("🐦 Testing X API v2 Mock\n")
    
    # Test search
    result = api.search_recent("مضاربة", max_results=5)
    print(f"Search 'مضاربة': {result.meta['result_count']} results")
    
    # Test get tweet
    if tweets:
        tweet_id = tweets[0]["id"]
        result = api.get_tweet(tweet_id)
        print(f"Get tweet {tweet_id[:10]}...: {result.data is not None}")
    
    # Test counts
    result = api.count_tweets("مضاربة", granularity="hour")
    print(f"Tweet counts by hour: {len(result.data)} buckets")
    print(f"Total tweets: {result.meta['total_tweet_count']}")
