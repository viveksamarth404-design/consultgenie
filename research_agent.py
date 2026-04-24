import os
from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient

_client = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise EnvironmentError("TAVILY_API_KEY not found. Check your .env file.")
        _client = TavilyClient(api_key=api_key)
    return _client


def search_one(query: str, max_results: int = 5) -> list[dict]:
    try:
        client = _get_client()
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
        )
        return response.get("results", [])
    except Exception as e:
        print(f"[research_agent] Tavily error for query '{query}': {e}")
        return []


def filter_results(results: list[dict]) -> list[dict]:
    filtered = []
    seen_urls = set()
    for r in results:
        url = r.get("url", "")
        content = r.get("content", "").strip()
        title = r.get("title", "").strip()
        if url in seen_urls or len(content) < 80 or not title:
            continue
        seen_urls.add(url)
        filtered.append(r)
    return filtered


def summarize_results(query: str, results: list[dict]) -> str:
    if not results:
        return f"No useful results found for: {query}\n"

    lines = [f"### Research: {query}\n"]
    for i, r in enumerate(results[:3], 1):
        title = r.get("title", "Untitled")
        content = r.get("content", "")[:400]
        url = r.get("url", "")
        lines.append(f"**{i}. {title}**\n{content}…\n[Source]({url})\n")

    return "\n".join(lines)


def run_research(queries: list[str]) -> str:
    if not queries:
        return ""

    all_summaries = []
    for query in queries:
        raw = search_one(query)
        filtered = filter_results(raw)
        summary = summarize_results(query, filtered)
        all_summaries.append(summary)

    return "\n---\n".join(all_summaries)
