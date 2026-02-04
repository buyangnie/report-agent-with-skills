"""
AI Insight Generator for BO Workload Performance Report.

Uses DeepSeek API to generate contextual insights with caching.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    SCRIPT_DIR
)
from analyzer import (
    AnalysisResult,
    ResolverProfile,
    CategoryRisk,
    WorkloadBalanceResult,
    KnowledgeSilo
)
from i18n import get_text


# Cache file path
CACHE_FILE = SCRIPT_DIR / ".insights_cache.json"
CACHE_EXPIRY_DAYS = 30
CACHE_MAX_ENTRIES = 200


class InsightGenerator:
    """
    AI-powered insight generator with caching.
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize insight generator.
        
        Args:
            language: Output language ("en" or "zh")
        """
        self.language = language
        self.client = None
        self.cache = self._load_cache()
        
        # Initialize OpenAI client if API key is available
        api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
            )
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        # Clean expired entries
        now = datetime.now()
        cleaned_cache = {}
        for key, entry in self.cache.items():
            try:
                cached_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if (now - cached_time).days < CACHE_EXPIRY_DAYS:
                    cleaned_cache[key] = entry
            except:
                pass
        
        # Limit cache size
        if len(cleaned_cache) > CACHE_MAX_ENTRIES:
            # Keep most recent entries
            sorted_entries = sorted(
                cleaned_cache.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )
            cleaned_cache = dict(sorted_entries[:CACHE_MAX_ENTRIES])
        
        self.cache = cleaned_cache
        
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _get_cache_key(self, context: str) -> str:
        """Generate cache key from context."""
        content = f"{context}_{self.language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_insight(self, cache_key: str) -> Optional[str]:
        """Get cached insight if available."""
        entry = self.cache.get(cache_key)
        if entry:
            try:
                cached_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if (datetime.now() - cached_time).days < CACHE_EXPIRY_DAYS:
                    return entry.get("insight")
            except:
                pass
        return None
    
    def _cache_insight(self, cache_key: str, insight: str) -> None:
        """Cache an insight."""
        self.cache[cache_key] = {
            "insight": insight,
            "timestamp": datetime.now().isoformat(),
            "language": self.language
        }
        self._save_cache()
    
    def _call_ai(self, prompt: str) -> str:
        """
        Call AI API to generate insight.
        
        Args:
            prompt: Prompt text
        
        Returns:
            Generated insight text
        """
        if not self.client:
            return self._get_fallback_insight()
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL or os.getenv("OPENAI_MODEL", "deepseek-chat"),
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI API error: {e}")
            return self._get_fallback_insight()
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on language."""
        if self.language == "zh":
            return """你是一位资深的运维管理专家，专注于团队效能分析和瓶颈识别。
请基于提供的数据分析结果，给出专业、可操作的洞察和建议。
输出要求：
1. 结构清晰，使用标题和要点
2. 聚焦于最关键的发现和风险
3. 提供具体、可执行的改进建议
4. 语言简洁专业"""
        else:
            return """You are a senior operations management expert specializing in team performance analysis and bottleneck identification.
Based on the provided analysis data, give professional and actionable insights and recommendations.
Output requirements:
1. Clear structure with headings and bullet points
2. Focus on the most critical findings and risks
3. Provide specific, actionable improvement suggestions
4. Concise and professional language"""
    
    def _get_fallback_insight(self) -> str:
        """Get fallback insight when AI is unavailable."""
        if self.language == "zh":
            return "AI 洞察生成暂时不可用。请检查 API 配置。"
        return "AI insights temporarily unavailable. Please check API configuration."
    
    def generate_executive_summary_insight(self, result: AnalysisResult) -> str:
        """
        Generate executive summary insight with priority distribution context.
        
        Args:
            result: Analysis result
        
        Returns:
            Generated insight text
        """
        # Calculate total P1/P2 vs P3/P4 ratio for context
        total_p1_p2 = sum(p.p1_count + p.p2_count for p in result.resolver_profiles)
        total_p3_p4 = sum(p.p3_count + p.p4_count for p in result.resolver_profiles)
        total = total_p1_p2 + total_p3_p4
        high_priority_ratio = total_p1_p2 / total * 100 if total > 0 else 0
        
        # Find top contributors by weighted workload
        sorted_by_weighted = sorted(result.resolver_profiles, key=lambda x: x.weighted_workload, reverse=True)[:5]
        top_weighted_info = []
        for p in sorted_by_weighted:
            top_weighted_info.append(f"- {p.name}: Weighted={p.weighted_workload:.0f}, P1/P2={p.priority_index*100:.0f}%")
        
        # Build context
        context = f"""
Total Resolvers: {result.total_resolvers}
BO Resolvers (Tier 2+3): {result.total_bo_resolvers}
Total Tickets: {result.total_tickets}
BO Tickets: {result.total_bo_tickets}
Global Avg MTTR: {result.global_avg_mttr:.1f} hours
Global SLA Rate: {result.global_sla_rate:.1%}
High Risk Items: {result.high_risk_count}
Bottleneck Count: {result.bottleneck_count}
Tier Distribution: {result.tier_counts}

Priority Analysis:
- High Priority (P1/P2) Tickets: {total_p1_p2} ({high_priority_ratio:.1f}%)
- Standard Priority (P3/P4) Tickets: {total_p3_p4} ({100-high_priority_ratio:.1f}%)

Top Contributors by Weighted Workload:
""" + "\n".join(top_weighted_info)
        
        cache_key = self._get_cache_key(f"exec_summary_v2_{context}")
        cached = self._get_cached_insight(cache_key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"""请基于以下 BO 负载分析数据，生成执行摘要洞察：

{context}

请包含：
1. 整体健康度评估
2. 优先级分布分析（P1/P2 高优先级工单的处理情况）
3. 最关键的风险点（2-3个）
4. 识别处理高优先级工单的关键人员及其价值
5. 需要立即关注的事项"""
        else:
            prompt = f"""Based on the following BO workload analysis data, generate an executive summary insight:

{context}

Please include:
1. Overall health assessment
2. Priority distribution analysis (P1/P2 high-priority ticket handling)
3. Most critical risk points (2-3)
4. Identify key contributors handling high-priority tickets and their value
5. Items requiring immediate attention"""
        
        insight = self._call_ai(prompt)
        self._cache_insight(cache_key, insight)
        return insight
    
    def generate_bottleneck_insight(
        self,
        top_bottlenecks: List[ResolverProfile],
        result: AnalysisResult
    ) -> str:
        """
        Generate bottleneck analysis insight.
        
        Args:
            top_bottlenecks: Top bottleneck profiles
            result: Full analysis result
        
        Returns:
            Generated insight text
        """
        # Build context
        bottleneck_details = []
        for p in top_bottlenecks[:5]:
            bottleneck_details.append(
                f"- {p.name}: Score={p.bottleneck_score:.2f}, "
                f"Backlog={p.current_backlog}, MTTR={p.avg_mttr_hours:.1f}h, "
                f"Causes={', '.join(p.bottleneck_root_causes)}"
            )
        
        context = f"""
Top Bottleneck Experts:
{chr(10).join(bottleneck_details)}

Total BO Experts: {result.total_bo_resolvers}
Global Avg MTTR: {result.global_avg_mttr:.1f}h
"""
        
        cache_key = self._get_cache_key(f"bottleneck_{context}")
        cached = self._get_cached_insight(cache_key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"""请基于以下瓶颈分析数据，生成改进建议：

{context}

请包含：
1. 瓶颈根因诊断
2. 短期缓解措施（1-2周内可执行）
3. 中长期优化建议"""
        else:
            prompt = f"""Based on the following bottleneck analysis data, generate improvement recommendations:

{context}

Please include:
1. Root cause diagnosis
2. Short-term mitigation measures (within 1-2 weeks)
3. Medium and long-term optimization suggestions"""
        
        insight = self._call_ai(prompt)
        self._cache_insight(cache_key, insight)
        return insight
    
    def generate_dependency_insight(
        self,
        high_risk_categories: List[CategoryRisk],
        knowledge_silos: List[KnowledgeSilo]
    ) -> str:
        """
        Generate single-point dependency insight.
        
        Args:
            high_risk_categories: High-risk category list
            knowledge_silos: Knowledge silo list
        
        Returns:
            Generated insight text
        """
        # Build context
        risk_details = []
        for r in high_risk_categories[:10]:
            risk_details.append(
                f"- {r.category}: {r.resolver_count} resolver(s), "
                f"{r.ticket_count} tickets, Experts: {', '.join(r.resolvers[:3])}"
            )
        
        silo_details = []
        for s in knowledge_silos[:5]:
            silo_details.append(
                f"- {s.category}: {', '.join(s.sole_experts)}, "
                f"{s.ticket_count} tickets, Priority: {s.priority}"
            )
        
        context = f"""
High-Risk Categories (Single-Point Dependency):
{chr(10).join(risk_details) if risk_details else "None"}

Knowledge Silos:
{chr(10).join(silo_details) if silo_details else "None"}
"""
        
        cache_key = self._get_cache_key(f"dependency_{context}")
        cached = self._get_cached_insight(cache_key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"""请基于以下单点依赖风险数据，生成知识管理建议：

{context}

请包含：
1. 风险评估和潜在影响
2. 知识转移优先级建议
3. 文档化和备份人员培养计划"""
        else:
            prompt = f"""Based on the following single-point dependency risk data, generate knowledge management recommendations:

{context}

Please include:
1. Risk assessment and potential impact
2. Knowledge transfer priority recommendations
3. Documentation and backup personnel training plan"""
        
        insight = self._call_ai(prompt)
        self._cache_insight(cache_key, insight)
        return insight
    
    def generate_workload_balance_insight(self, balance: WorkloadBalanceResult) -> str:
        """
        Generate workload balance insight.
        
        Args:
            balance: Workload balance result
        
        Returns:
            Generated insight text
        """
        context = f"""
Gini Coefficient: {balance.gini_coefficient:.3f}
Interpretation: {balance.interpretation}
Average Workload: {balance.avg_workload:.1f} tickets
Std Deviation: {balance.std_workload:.1f}
Overloaded Experts: {', '.join(balance.overloaded_resolvers[:5]) if balance.overloaded_resolvers else 'None'}
Underloaded Experts: {', '.join(balance.underloaded_resolvers[:5]) if balance.underloaded_resolvers else 'None'}
"""
        
        cache_key = self._get_cache_key(f"balance_{context}")
        cached = self._get_cached_insight(cache_key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"""请基于以下负载均衡分析数据，生成优化建议：

{context}

请包含：
1. 负载分配健康度评估
2. 具体的重分配建议
3. 长期负载均衡策略"""
        else:
            prompt = f"""Based on the following workload balance analysis data, generate optimization recommendations:

{context}

Please include:
1. Workload distribution health assessment
2. Specific reallocation suggestions
3. Long-term load balancing strategy"""
        
        insight = self._call_ai(prompt)
        self._cache_insight(cache_key, insight)
        return insight
    
    def generate_all_insights(self, result: AnalysisResult) -> Dict[str, str]:
        """
        Generate all insights for the report.
        
        Args:
            result: Analysis result
        
        Returns:
            Dictionary of insight name to text
        """
        insights = {}
        
        # Executive summary
        insights["executive_summary"] = self.generate_executive_summary_insight(result)
        
        # Bottleneck insights
        top_bottlenecks = sorted(
            result.resolver_profiles,
            key=lambda x: x.bottleneck_score,
            reverse=True
        )[:5]
        insights["bottleneck"] = self.generate_bottleneck_insight(top_bottlenecks, result)
        
        # Dependency insights
        high_risk = [r for r in result.category_risks if r.risk_level == "High"]
        insights["dependency"] = self.generate_dependency_insight(
            high_risk,
            result.knowledge_silos
        )
        
        # Workload balance insights
        if result.workload_balance:
            insights["workload_balance"] = self.generate_workload_balance_insight(
                result.workload_balance
            )
        
        return insights
