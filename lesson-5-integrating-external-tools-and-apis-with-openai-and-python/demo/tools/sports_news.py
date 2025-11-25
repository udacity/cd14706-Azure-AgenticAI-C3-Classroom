# tools/sports_news.py
from semantic_kernel.functions import kernel_function
import requests
import logging
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import feedparser

logger = logging.getLogger(__name__)

class SportsNewsTools:
    """Tools for sports news aggregation using external APIs"""
    
    def __init__(self):
        # Using NewsAPI for sports news (free tier available)
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.newsapi_base = "https://newsapi.org/v2"
        
        # RSS feeds as fallback
        self.rss_feeds = {
            "NBA": "https://www.espn.com/espn/rss/nba/news",
            "NFL": "https://www.espn.com/espn/rss/nfl/news",
            "MLB": "https://www.espn.com/espn/rss/mlb/news",
            "NHL": "https://www.espn.com/espn/rss/nhl/news"
        }
    
    def _get_news_from_rss(self, league: str, team: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get news from RSS feed as fallback"""
        articles = []
        feed_url = self.rss_feeds.get(league.upper())
        
        if not feed_url:
            return articles
        
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:limit * 2]:  # Get more to filter by team
                if team:
                    if team.lower() not in entry.title.lower() and team.lower() not in entry.get("summary", "").lower():
                        continue
                
                article = {
                    "title": entry.title,
                    "summary": entry.get("summary", entry.get("description", ""))[:200],
                    "content": entry.get("summary", entry.get("description", "")),
                    "author": entry.get("author", "ESPN"),
                    "source": "ESPN",
                    "published_date": entry.get("published", ""),
                    "url": entry.link,
                    "tags": [league, team] if team else [league]
                }
                articles.append(article)
                
                if len(articles) >= limit:
                    break
        except Exception as e:
            logger.warning(f"RSS feed parsing failed: {e}")
        
        return articles
    
    @kernel_function(name="get_latest_news", description="Get latest sports news using external news API")
    def get_latest_news(self, league: str = "NBA", team: str = None, limit: int = 5) -> Dict[str, Any]:
        """
        Get latest sports news using NewsAPI or RSS feeds.
        
        Args:
            league: Sports league (NBA, NFL, MLB, NHL, etc.)
            team: Specific team to get news for (optional)
            limit: Maximum number of articles to return
            
        Returns:
            Dictionary containing sports news information
        """
        try:
            logger.info(f"Getting latest sports news from real API for league: {league}, team: {team}")
            
            articles = []
            
            # Try NewsAPI first if key is available
            if self.newsapi_key:
                try:
                    search_query = f"{league} {team}" if team else league
                    newsapi_url = f"{self.newsapi_base}/everything"
                    params = {
                        "q": search_query,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": limit,
                        "apiKey": self.newsapi_key
                    }
                    
                    resp = requests.get(newsapi_url, params=params, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    if data.get("status") == "ok" and data.get("articles"):
                        for article in data["articles"][:limit]:
                            articles.append({
                                "title": article.get("title", ""),
                                "summary": article.get("description", "")[:200],
                                "content": article.get("content", article.get("description", "")),
                                "author": article.get("author", article.get("source", {}).get("name", "Unknown")),
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "published_date": article.get("publishedAt", ""),
                                "url": article.get("url", ""),
                                "image_url": article.get("urlToImage", ""),
                                "tags": [league, team] if team else [league]
                            })
                except Exception as e:
                    logger.warning(f"NewsAPI request failed: {e}, falling back to RSS")
            
            # Fallback to RSS feeds if NewsAPI fails or no key
            if not articles:
                articles = self._get_news_from_rss(league, team, limit)
            
            if not articles:
                # Return empty result with helpful message
                return {
                    "api_source": "NewsAPI / RSS Feeds",
                    "news_data": {
                        "total_articles": 0,
                        "articles": [],
                        "message": f"No news found for {league}" + (f" and {team}" if team else "")
                    }
                }
            
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "news_data": {
                    "total_articles": len(articles),
                    "articles": articles[:limit],
                    "league": league,
                    "team": team
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get sports news: {e}")
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "news_data": {
                    "league": league,
                    "team": team,
                    "error": f"API call failed: {e}",
                    "articles": []
                }
            }
    
    @kernel_function(name="get_breaking_news", description="Get breaking sports news using external API")
    def get_breaking_news(self, league: str = "NBA") -> Dict[str, Any]:
        """
        Get breaking sports news using external API.
        
        Args:
            league: Sports league to get breaking news for
            
        Returns:
            Dictionary containing breaking news information
        """
        try:
            logger.info(f"Getting breaking sports news from real API for league: {league}")
            
            # Get latest news and filter for breaking/urgent items
            latest_news = self.get_latest_news(league, limit=10)
            articles = latest_news.get("news_data", {}).get("articles", [])
            
            # Filter for breaking news (recent articles, typically within last hour)
            breaking_articles = []
            cutoff_time = datetime.now() - timedelta(hours=2)
            
            for article in articles:
                try:
                    pub_date_str = article.get("published_date", "")
                    if pub_date_str:
                        # Try to parse various date formats
                        pub_date = None
                        for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S %Z"]:
                            try:
                                pub_date = datetime.strptime(pub_date_str, fmt)
                                break
                            except:
                                continue
                        
                        if pub_date and pub_date >= cutoff_time:
                            breaking_articles.append({
                                "title": article.get("title", ""),
                                "summary": article.get("summary", ""),
                                "priority": "high",
                                "published_date": pub_date_str,
                                "source": article.get("source", ""),
                                "url": article.get("url", "")
                            })
                except:
                    # If date parsing fails, include it anyway (might be recent)
                    breaking_articles.append({
                        "title": article.get("title", ""),
                        "summary": article.get("summary", ""),
                        "priority": "high",
                        "published_date": article.get("published_date", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", "")
                    })
            
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "breaking_news": {
                    "urgent_articles": breaking_articles[:5],
                    "alert_level": "high" if breaking_articles else "normal",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get breaking sports news: {e}")
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "breaking_news": {
                    "league": league,
                    "error": f"API call failed: {e}",
                    "urgent_articles": []
                }
            }
    
    @kernel_function(name="search_news", description="Search sports news using external API")
    def search_news(self, query: str, league: str = "NBA", days_back: int = 7) -> Dict[str, Any]:
        """
        Search sports news using external API.
        
        Args:
            query: Search query
            league: Sports league to search in
            days_back: Number of days back to search
            
        Returns:
            Dictionary containing search results
        """
        try:
            logger.info(f"Searching sports news from real API for query: {query}, league: {league}")
            
            articles = []
            
            # Try NewsAPI first if key is available
            if self.newsapi_key:
                try:
                    search_query = f"{query} {league}"
                    newsapi_url = f"{self.newsapi_base}/everything"
                    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                    
                    params = {
                        "q": search_query,
                        "language": "en",
                        "sortBy": "relevancy",
                        "pageSize": 10,
                        "from": from_date,
                        "apiKey": self.newsapi_key
                    }
                    
                    resp = requests.get(newsapi_url, params=params, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    if data.get("status") == "ok" and data.get("articles"):
                        for article in data["articles"]:
                            articles.append({
                                "title": article.get("title", ""),
                                "summary": article.get("description", "")[:200],
                                "relevance_score": 0.9,  # NewsAPI sorts by relevance
                                "published_date": article.get("publishedAt", ""),
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "url": article.get("url", "")
                            })
                except Exception as e:
                    logger.warning(f"NewsAPI search failed: {e}, falling back to RSS")
            
            # Fallback: search RSS feed articles
            if not articles:
                rss_articles = self._get_news_from_rss(league, limit=20)
                query_lower = query.lower()
                for article in rss_articles:
                    if query_lower in article.get("title", "").lower() or query_lower in article.get("summary", "").lower():
                        articles.append({
                            "title": article.get("title", ""),
                            "summary": article.get("summary", ""),
                            "relevance_score": 0.7,
                            "published_date": article.get("published_date", ""),
                            "source": article.get("source", ""),
                            "url": article.get("url", "")
                        })
            
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "search_results": {
                    "total_results": len(articles),
                    "articles": articles[:10],
                    "query": query,
                    "league": league
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to search sports news: {e}")
            return {
                "api_source": "NewsAPI / RSS Feeds",
                "search_results": {
                    "query": query,
                    "error": f"API call failed: {e}",
                    "articles": []
                }
            }
