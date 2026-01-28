"""
AI Insight Generator for Incident Quality Report.
Calls LLM API to generate actionable insights for each analysis dimension.
Includes JSON-based LRU caching with expiry to avoid redundant API calls.
Supports bilingual output (English and Chinese).
"""
import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Initialize OpenAI client with DeepSeek endpoint
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL')
)

MODEL = os.getenv('OPENAI_MODEL', 'deepseek-chat')

# Cache configuration
CACHE_FILE = os.path.join(os.path.dirname(__file__), '.insights_cache.json')
MAX_CACHE_ENTRIES = 200
CACHE_EXPIRY_DAYS = 30


# ============================================
# CACHE MANAGEMENT
# ============================================

def clear_cache() -> None:
    """Clear the insights cache file."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)


def _is_cache_entry_expired(entry: dict) -> bool:
    """Check if a cache entry has expired."""
    if 'last_used' not in entry:
        return True  # No timestamp = expired

    try:
        last_used = datetime.fromisoformat(entry['last_used'])
        expiry_date = datetime.now() - timedelta(days=CACHE_EXPIRY_DAYS)
        return last_used < expiry_date
    except (ValueError, TypeError):
        return True  # Invalid timestamp = expired


def _load_cache() -> dict:
    """Load cache from JSON file and remove expired entries."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            # Remove expired entries
            valid_cache = {
                key: value for key, value in cache.items()
                if not _is_cache_entry_expired(value)
            }

            # Save cleaned cache if entries were removed
            if len(valid_cache) < len(cache):
                _save_cache(valid_cache)

            return valid_cache
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    """Save cache to JSON file with LRU cleanup."""
    # Cleanup if exceeds max entries
    if len(cache) > MAX_CACHE_ENTRIES:
        # Sort by last_used, keep newest entries
        sorted_items = sorted(
            cache.items(),
            key=lambda x: x[1].get('last_used', ''),
            reverse=True
        )
        cache = dict(sorted_items[:MAX_CACHE_ENTRIES])
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _get_cache_key(dimension: str, context: str, language: str = 'en') -> str:
    """Generate MD5 hash key from dimension, context, and language."""
    content = f"{dimension}|{context}|{language}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def _get_cached_insight(cache_key: str) -> str | None:
    """Get insight from cache if exists, update last_used timestamp."""
    cache = _load_cache()
    if cache_key in cache:
        # Update last_used timestamp
        cache[cache_key]['last_used'] = datetime.now().isoformat()
        _save_cache(cache)
        return cache[cache_key]['insight']
    return None


def _save_to_cache(cache_key: str, insight: str) -> None:
    """Save new insight to cache."""
    cache = _load_cache()
    cache[cache_key] = {
        'insight': insight,
        'last_used': datetime.now().isoformat()
    }
    _save_cache(cache)


# ============================================
# INSIGHT GENERATION
# ============================================

def generate_insights(results: dict, language: str = 'en') -> dict:
    """Generate AI insights for each analysis dimension with language support."""
    insights = {}
    cache_hits = 0

    # 1. Executive Summary Insight
    context = _build_summary_context(results.get('summary', {}))
    insight, hit = _generate_insight_with_cache("Executive Summary", context, language)
    insights['summary'] = insight
    cache_hits += hit

    # 2. SLA Analysis Insight
    context = _build_sla_context(results.get('sla', {}))
    insight, hit = _generate_insight_with_cache("SLA Analysis", context, language)
    insights['sla'] = insight
    cache_hits += hit

    # 3. Priority Analysis Insight
    context = _build_priority_context(results.get('priority', {}))
    insight, hit = _generate_insight_with_cache("Priority Analysis", context, language)
    insights['priority'] = insight
    cache_hits += hit

    # 4. Personnel Analysis Insight
    context = _build_personnel_context(results.get('personnel', {}))
    insight, hit = _generate_insight_with_cache("Personnel Analysis", context, language)
    insights['personnel'] = insight
    cache_hits += hit

    # 5. Category Analysis Insight
    context = _build_category_context(results.get('category', {}))
    insight, hit = _generate_insight_with_cache("Category Analysis", context, language)
    insights['category'] = insight
    cache_hits += hit

    # 6. Time Analysis Insight
    context = _build_time_context(results.get('time', {}))
    insight, hit = _generate_insight_with_cache("Time Analysis", context, language)
    insights['time'] = insight
    cache_hits += hit

    # Log cache stats
    total = len(insights)
    print(f"   📦 Cache: {cache_hits}/{total} hits, {total - cache_hits} API calls")

    return insights


def _generate_insight_with_cache(dimension: str, context: str, language: str = 'en') -> tuple[str, int]:
    """Generate insight with cache lookup. Returns (insight, cache_hit_flag)."""
    cache_key = _get_cache_key(dimension, context, language)

    # Try cache first
    cached = _get_cached_insight(cache_key)
    if cached:
        return cached, 1  # Cache hit

    # Cache miss - call LLM
    insight = _call_llm(dimension, context, language)
    _save_to_cache(cache_key, insight)
    return insight, 0  # Cache miss


def _call_llm(dimension: str, context: str, language: str = 'en') -> str:
    """Call LLM API to generate insight with language support and retry logic."""
    # Build prompt based on language
    if language == 'zh':
        prompt = f"""你是一位资深运维总监，正在分析事件数据。

基于以下{dimension}数据：
{context}

请提供 3-5 句简洁、可操作的洞察，面向高管受众：
- 关注"意义何在"和业务影响
- 突出关键风险或机会
- 如适当，建议具体的下一步行动
- 不要简单重复数据点
- 使用专业的商务中文写作"""
    else:
        prompt = f"""You are a Senior Operations Director analyzing incident data.

Based on the following {dimension} data:
{context}

Provide 3-5 concise, actionable sentences of insight for an executive audience.
- Focus on the "so what" and business impact
- Highlight key risks or opportunities
- Suggest concrete next steps if appropriate
- Do NOT simply repeat the data points
- Write in professional business English"""

    system_msg = "你是一位资深运维分析师，提供高管洞察。" if language == 'zh' else "You are a senior operations analyst providing executive insights."

    # Retry logic with exponential backoff
    max_retries = 3
    base_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                timeout=30.0  # 30 second timeout
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            error_type = type(e).__name__
            is_last_attempt = (attempt == max_retries - 1)

            if is_last_attempt:
                # Final failure - return error message
                error_msg = f"洞察生成失败 ({error_type}): {str(e)}" if language == 'zh' else f"Insight generation failed ({error_type}): {str(e)}"
                print(f"   ⚠️  API call failed for {dimension} after {max_retries} attempts: {error_type}")
                return f"[{error_msg}]"
            else:
                # Retry with exponential backoff
                delay = base_delay * (2 ** attempt)
                print(f"   ⚠️  API call attempt {attempt + 1} failed for {dimension}, retrying in {delay}s...")
                time.sleep(delay)


# ============================================
# CONTEXT BUILDERS
# ============================================

def _build_summary_context(summary: dict) -> str:
    """Build context string for executive summary."""
    if not summary:
        return "No data available."
    
    return f"""- Total Tickets: {summary.get('total', 'N/A')}
- SLA Compliance Rate: {summary.get('sla_rate', 0):.1f}%
- Average MTTR: {summary.get('avg_mttr', 0):.1f} hours
- P1 Incidents: {summary.get('p1_count', 0)}
- P2 Incidents: {summary.get('p2_count', 0)}
- Volume Trend (vs previous period): {summary.get('vol_trend', 0):.1f}%
- MTTR Trend (vs previous period): {summary.get('mttr_trend', 0):.1f}%
- Key Anomalies: {', '.join(summary.get('anomalies', [])) or 'None'}"""


def _build_sla_context(sla: dict) -> str:
    """Build context string for SLA analysis."""
    if not sla:
        return "No SLA data available."
    
    violations_by_person = sla.get('violations_by_person', {})
    top_violators = list(violations_by_person.head(3).items()) if hasattr(violations_by_person, 'head') else []
    
    violations_by_category = sla.get('violations_by_category', {})
    top_categories = list(violations_by_category.head(3).items()) if hasattr(violations_by_category, 'head') else []
    
    return f"""- Overall SLA Rate: {sla.get('overall_rate', 0):.1f}%
- Total Violations: {sla.get('total_violations', 0)}
- Top Violating Personnel: {', '.join([f'{p}: {c}' for p, c in top_violators]) or 'N/A'}
- Top Violating Categories: {', '.join([f'{c}: {n}' for c, n in top_categories]) or 'N/A'}
- Severity Distribution: Minor (<1h): {sla.get('severity_distribution', {}).get('Minor (<1h)', 0)}, Moderate (1-4h): {sla.get('severity_distribution', {}).get('Moderate (1-4h)', 0)}, Severe (>4h): {sla.get('severity_distribution', {}).get('Severe (>4h)', 0)}"""


def _build_priority_context(priority: dict) -> str:
    """Build context string for priority analysis."""
    if not priority:
        return "No priority data available."
    
    dist = priority.get('distribution', {})
    dist_str = ', '.join([f'{p}: {c}' for p, c in dist.items()]) if hasattr(dist, 'items') else 'N/A'
    
    mttr_data = priority.get('mttr_by_priority', None)
    mttr_str = 'N/A'
    if mttr_data is not None and hasattr(mttr_data, 'index'):
        mttr_str = ', '.join([f"{idx}: {mttr_data.loc[idx, 'mean']:.1f}h mean" for idx in mttr_data.index])
    
    p1_cases = priority.get('p1_cases', [])
    p1_summary = f"{len(p1_cases)} P1 cases" if p1_cases else "No P1 cases"
    
    p1_avg = 'N/A'
    if p1_cases:
        total_hours = sum(c.get('Resolution_Hours', 0) for c in p1_cases)
        p1_avg = f"{total_hours / len(p1_cases):.1f}h" if p1_cases else 'N/A'
    
    return f"""- Priority Distribution: {dist_str}
- MTTR by Priority: {mttr_str}
- P1 Cases: {p1_summary}
- P1 Average Resolution Time: {p1_avg}"""


def _build_personnel_context(personnel: dict) -> str:
    """Build context string for personnel analysis."""
    if not personnel:
        return "No personnel data available."
    
    top_performers = personnel.get('top_performers', None)
    top_str = 'N/A'
    if top_performers is not None:
        if hasattr(top_performers, 'head'):
            top_str = ', '.join([str(x) for x in top_performers.head(3).index.tolist()])
        elif isinstance(top_performers, list):
            top_str = ', '.join([str(p.get('Resolver', 'N/A')) for p in top_performers[:3]]) or 'N/A'
    
    unassigned = personnel.get('unassigned', {})
    
    return f"""- Total Resolvers: {personnel.get('total_resolvers', 'N/A')}
- Top Performers (by efficiency score): {top_str}
- Unassigned Tickets: {unassigned.get('count', 0)} ({unassigned.get('percentage', 0):.1f}%)
- Average Volume per Person: {personnel.get('avg_volume', 'N/A')}"""


def _build_category_context(category: dict) -> str:
    """Build context string for category analysis."""
    if not category:
        return "No category data available."
    
    dist = category.get('distribution', {})
    top_categories = list(dist.head(3).items()) if hasattr(dist, 'head') else []
    dist_str = ', '.join([f'{c}: {n}' for c, n in top_categories]) or 'N/A'
    
    fastest_growing = category.get('fastest_growing', [])
    growth_str = ', '.join([f'{name}: +{change:.1f}%' for name, change in fastest_growing[:3]]) or 'None'
    
    keywords = category.get('keywords', [])
    keyword_str = ', '.join([w for w, _ in keywords[:5]]) if keywords else 'N/A'
    
    return f"""- Top Categories by Volume: {dist_str}
- Fastest Growing Categories: {growth_str}
- Top Keywords in Ticket Titles: {keyword_str}"""


def _build_time_context(time_data: dict) -> str:
    """Build context string for time analysis."""
    if not time_data:
        return "No time data available."
    
    long_tail = time_data.get('long_tail', {})
    
    return f"""- Peak Hour: {time_data.get('peak_hour', 'N/A')}
- Peak Day: {time_data.get('peak_day', 'N/A')}
- Valley Hour: {time_data.get('valley_hour', 'N/A')}
- Long-tail Tickets (>48h): {long_tail.get('count', 0)} ({long_tail.get('percentage', 0):.1f}%)
- Long-tail Average Duration: {long_tail.get('avg_hours', 0):.1f}h"""
