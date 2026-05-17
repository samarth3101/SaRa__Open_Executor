from typing import List, Optional, Tuple
import requests

from app.core.config import get_settings
from app.modules.news.schemas import NewsArticle, NewsSummaryResult


TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
EVERYTHING_URL = "https://newsapi.org/v2/everything"


def _extract_topic_and_query(text: str) -> Tuple[str, Optional[str], str]:
    value = text.lower().strip()

    if any(word in value for word in ["geopolitics", "world politics", "international relations", "diplomacy"]):
        return (
            "geopolitics",
            '("foreign policy" OR diplomacy OR sanctions OR conflict OR "international relations" OR war) '
            'AND NOT (sports OR entertainment OR celebrity OR television OR children)',
            "everything",
        )

    if any(word in value for word in ["ai", "artificial intelligence", "machine learning"]):
        return (
            "ai",
            '("artificial intelligence" OR AI OR "machine learning" OR OpenAI OR Anthropic OR Google DeepMind) '
            'AND NOT (gaming OR movie OR entertainment)',
            "everything",
        )

    if any(word in value for word in ["startup", "funding", "venture capital"]):
        return (
            "startups",
            '("startup" OR funding OR "venture capital" OR acquisition) '
            'AND NOT (sports OR entertainment)',
            "everything",
        )

    if any(word in value for word in ["india", "indian"]):
        return (
            "india",
            '(India OR Indian) AND NOT (sports OR entertainment)',
            "everything",
        )

    if any(word in value for word in ["technology", "tech"]):
        return ("technology", "technology", "everything")

    if any(word in value for word in ["business", "market", "finance"]):
        return ("business", "business OR markets OR finance", "everything")

    if "sports" in value:
        return ("sports", None, "top-headlines")

    if "health" in value:
        return ("health", None, "top-headlines")

    return ("general", None, "top-headlines")


def _is_relevant_article(article: NewsArticle, topic: str) -> bool:
    haystack = f"{article.title or ''} {article.description or ''}".lower()

    topic_keywords = {
        "ai": [
            "ai",
            "artificial intelligence",
            "machine learning",
            "openai",
            "anthropic",
            "deepmind",
            "llm",
            "model",
        ],
        "geopolitics": [
            "diplomacy",
            "sanction",
            "war",
            "conflict",
            "foreign policy",
            "government",
            "military",
            "international",
        ],
        "startups": [
            "startup",
            "funding",
            "venture capital",
            "acquisition",
            "seed",
            "series a",
            "series b",
        ],
        "india": [
            "india",
            "indian",
            "new delhi",
            "mumbai",
            "bengaluru",
            "bangalore",
        ],
    }

    if topic not in topic_keywords:
        return True

    return any(keyword in haystack for keyword in topic_keywords[topic])


def _dedupe_and_filter_articles(raw_articles: list, topic: str) -> List[NewsArticle]:
    articles: List[NewsArticle] = []
    seen_titles = set()
    seen_sources = {}

    for item in raw_articles:
        title = item.get("title")
        url = item.get("url")

        if not title or not url:
            continue

        article = NewsArticle(
            title=title.strip(),
            source=(item.get("source") or {}).get("name", "Unknown"),
            url=url,
            published_at=item.get("publishedAt"),
            description=item.get("description"),
        )

        normalized_title = article.title.lower().strip()
        if normalized_title in seen_titles:
            continue

        if not _is_relevant_article(article, topic):
            continue

        source_count = seen_sources.get(article.source, 0)
        if source_count >= 2:
            continue

        seen_titles.add(normalized_title)
        seen_sources[article.source] = source_count + 1
        articles.append(article)

        if len(articles) == 5:
            break

    return articles


def _fetch_articles(api_key: str, topic: str, query: Optional[str], mode: str) -> List[NewsArticle]:
    headers = {"X-Api-Key": api_key}

    if mode == "everything" and query:
        params = {
            "q": query,
            "language": "en",
            "pageSize": 8,
            "sortBy": "relevancy",
            "searchIn": "title,description",
        }
        response = requests.get(EVERYTHING_URL, headers=headers, params=params, timeout=15)
    else:
        params = {
            "language": "en",
            "pageSize": 8,
        }

        if topic in {"technology", "business", "sports", "health"}:
            params["category"] = topic
        else:
            params["country"] = "us"

        response = requests.get(TOP_HEADLINES_URL, headers=headers, params=params, timeout=15)

    response.raise_for_status()
    data = response.json()
    raw_articles = data.get("articles", []) or []

    return _dedupe_and_filter_articles(raw_articles, topic)


def _build_summary(articles: List[NewsArticle], topic: str) -> str:
    if not articles:
        return f"No major {topic} news was found right now."

    unique_sources = []
    for article in articles:
        if article.source not in unique_sources:
            unique_sources.append(article.source)

    lead_sources = ", ".join(unique_sources[:3])
    return f"Here are the top {topic} updates right now. Key coverage is coming from {lead_sources}."


def get_news_summary(command_text: str) -> NewsSummaryResult:
    api_key = get_settings().news_api_key

    if not api_key:
        return NewsSummaryResult(
            ok=False,
            source="news",
            summary="News API key is missing on the backend.",
            articles=[],
            suggested_action="add_news_api_key",
            estimated_time="1m",
            topic=None,
        )

    topic, query, mode = _extract_topic_and_query(command_text)

    articles = _fetch_articles(
        api_key=api_key,
        topic=topic,
        query=query,
        mode=mode,
    )

    summary = _build_summary(articles, topic)

    return NewsSummaryResult(
        ok=True,
        source="newsapi",
        summary=summary,
        articles=articles,
        suggested_action="read_top_story" if articles else "try_another_topic",
        estimated_time="5s",
        topic=topic,
    )
