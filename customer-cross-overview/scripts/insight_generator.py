"""
AI Insight Generator for Comprehensive Report.

Generates AI-powered insights for each ITIL process area.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Load .env before importing config
from dotenv import load_dotenv
_SCRIPT_DIR = Path(__file__).parent
_ENV_PATH = _SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, SCRIPT_DIR
from analyzer import ComprehensiveResult


CACHE_FILE = SCRIPT_DIR / ".insights_cache.json"
CACHE_EXPIRY_DAYS = 30


class InsightGenerator:
    """AI-powered insight generator with caching."""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.client = None
        self.cache = self._load_cache()
        
        api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
            )
    
    def _load_cache(self) -> Dict:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _get_cache_key(self, context: str) -> str:
        content = f"{context}_{self.language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[str]:
        entry = self.cache.get(key)
        if entry:
            try:
                cached_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if (datetime.now() - cached_time).days < CACHE_EXPIRY_DAYS:
                    return entry.get("insight")
            except:
                pass
        return None
    
    def _cache_insight(self, key: str, insight: str) -> None:
        self.cache[key] = {
            "insight": insight,
            "timestamp": datetime.now().isoformat(),
            "language": self.language
        }
        self._save_cache()
    
    def _call_ai(self, prompt: str) -> str:
        if not self.client:
            return self._fallback()
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL or "deepseek-chat",
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI API error: {e}")
            return self._fallback()
    
    def _system_prompt(self) -> str:
        if self.language == "zh":
            return """你是一位资深IT运维管理顾问。请基于数据提供简洁、专业的分析洞察。
要求：2-3句话，聚焦关键发现和建议，适合管理层阅读。"""
        return """You are a senior IT operations consultant. Provide concise, professional insights.
Requirements: 2-3 sentences, focus on key findings and recommendations, executive-level language."""
    
    def _fallback(self) -> str:
        if self.language == "zh":
            return "AI 洞察暂时不可用。请检查 API 配置。"
        return "AI insights temporarily unavailable. Please check API configuration."
    
    # =========================================================================
    # INDIVIDUAL INSIGHT GENERATORS
    # =========================================================================
    
    def generate_executive_summary(self, result: ComprehensiveResult) -> str:
        """Generate executive summary insight."""
        context = f"""
Health Score: {result.health_score:.0f}/100 ({result.health_grade})
Total Incidents: {result.total_incidents}
Total Changes: {result.total_changes}
Total Requests: {result.total_requests}
Total Problems: {result.total_problems}
Top Risks: {len(result.top_risks)}
"""
        key = self._get_cache_key(f"exec_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下服务健康数据，给出整体评估（一句话）和最关键的改进建议：\n{context}"
        else:
            prompt = f"Based on this service health data, provide overall assessment (one sentence) and the most critical improvement recommendation:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_incident_insight(self, result: ComprehensiveResult) -> str:
        """Generate incident management insight."""
        if not result.incident_summary:
            return ""
        
        kpis = result.incident_summary.kpis
        sla = kpis.get("sla_rate")
        mttr = kpis.get("avg_mttr")
        p1_p2 = kpis.get("p1_p2_count")
        
        sla_val = f"{sla.current_value:.1%}" if sla else "N/A"
        mttr_val = f"{mttr.current_value:.1f}h" if mttr else "N/A"
        p1p2_val = str(int(p1_p2.current_value)) if p1_p2 else "N/A"
        major_count = len(result.major_incidents) if result.major_incidents else 0
        
        context = f"""
Incident SLA Rate: {sla_val}
Average MTTR: {mttr_val}
P1/P2 Incidents: {p1p2_val}
Total Incidents: {result.total_incidents}
Major Incidents: {major_count}
"""
        key = self._get_cache_key(f"incident_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下事件管理数据，分析SLA达成情况和MTTR趋势，给出改进建议：\n{context}"
        else:
            prompt = f"Based on this incident data, analyze SLA compliance and MTTR trends, provide improvement recommendations:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_change_insight(self, result: ComprehensiveResult) -> str:
        """Generate change management insight."""
        if not result.change_summary:
            return ""
        
        kpis = result.change_summary.kpis
        success = kpis.get("change_success_rate")
        incident_rate = kpis.get("change_incident_rate")
        
        success_val = f"{success.current_value:.1%}" if success else "N/A"
        incident_rate_val = f"{incident_rate.current_value:.1%}" if incident_rate else "N/A"
        failed_count = len(result.failed_changes) if result.failed_changes else 0
        
        context = f"""
Change Success Rate: {success_val}
Change-Induced Incident Rate: {incident_rate_val}
Total Changes: {result.total_changes}
Failed Changes: {failed_count}
"""
        key = self._get_cache_key(f"change_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下变更管理数据，分析变更成功率和失败原因，给出改进建议：\n{context}"
        else:
            prompt = f"Based on this change data, analyze success rate and failure patterns, provide recommendations:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_request_insight(self, result: ComprehensiveResult) -> str:
        """Generate service request insight."""
        if not result.request_summary:
            return ""
        
        kpis = result.request_summary.kpis
        csat = kpis.get("request_csat")
        sla = kpis.get("request_sla_rate")
        csat_val = f"{csat.current_value:.2f}/5" if csat else "N/A"
        sla_val = f"{sla.current_value:.1%}" if sla else "N/A"
        
        context = f"""
Customer Satisfaction (CSAT): {csat_val}
Request SLA Rate: {sla_val}
Total Requests: {result.total_requests}
"""
        key = self._get_cache_key(f"request_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下服务请求数据，分析客户满意度和SLA达成情况，给出提升建议：\n{context}"
        else:
            prompt = f"Based on this service request data, analyze CSAT and SLA compliance, provide improvement suggestions:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_problem_insight(self, result: ComprehensiveResult) -> str:
        """Generate problem management insight."""
        if not result.problem_summary:
            return ""
        
        kpis = result.problem_summary.kpis
        closure = kpis.get("problem_closure_rate")
        rca = kpis.get("rca_rate")
        closure_val = f"{closure.current_value:.1%}" if closure else "N/A"
        rca_val = f"{rca.current_value:.1%}" if rca else "N/A"
        open_count = len(result.open_problems) if result.open_problems else 0
        
        context = f"""
Problem Closure Rate: {closure_val}
RCA Completion Rate: {rca_val}
Total Problems: {result.total_problems}
Open Problems: {open_count}
"""
        key = self._get_cache_key(f"problem_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下问题管理数据，分析问题关闭率和RCA完成情况，给出改进建议：\n{context}"
        else:
            prompt = f"Based on this problem data, analyze closure rate and RCA completion, provide recommendations:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_risk_insight(self, result: ComprehensiveResult) -> str:
        """Generate risk analysis insight."""
        if not result.top_risks:
            if self.language == "zh":
                return "未发现显著风险，当前服务状态良好。建议继续保持监控。"
            return "No significant risks identified. Current service status is healthy. Continue monitoring."
        
        risk_desc = "\n".join([
            f"- [{r.priority}] {r.message}" for r in result.top_risks[:5]
        ])
        
        context = f"Top Risks:\n{risk_desc}"
        key = self._get_cache_key(f"risk_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下风险列表，指出最需要优先处理的风险和建议的缓解措施：\n{risk_desc}"
        else:
            prompt = f"Based on these risks, identify the highest priority risk and recommended mitigation:\n{risk_desc}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_action_insight(self, result: ComprehensiveResult) -> str:
        """Generate recommended actions insight."""
        if not result.actions:
            if self.language == "zh":
                return "当前无紧急改进事项。建议关注持续优化和预防性维护。"
            return "No urgent improvements needed. Focus on continuous optimization and preventive maintenance."
        
        action_desc = "\n".join([
            f"- [{a.priority}] {a.action}" for a in result.actions[:5]
        ])
        
        context = f"Recommended Actions:\n{action_desc}"
        key = self._get_cache_key(f"action_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下改进建议，说明最紧急的行动项和预期效果：\n{action_desc}"
        else:
            prompt = f"Based on these recommended actions, explain the most urgent item and expected impact:\n{action_desc}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    def generate_trend_insight(self, result: ComprehensiveResult) -> str:
        """Generate trend analysis insight."""
        context = f"""
Health Score: {result.health_score:.0f}/100
Week-over-Week Comparison: {'Available' if result.can_compare_wow else 'Not available'}
Month-over-Month Comparison: {'Available' if result.can_compare_mom else 'Not available'}
"""
        key = self._get_cache_key(f"trend_{context}")
        cached = self._get_cached(key)
        if cached:
            return cached
        
        if self.language == "zh":
            prompt = f"基于以下趋势数据，分析健康评分走势和未来预测：\n{context}"
        else:
            prompt = f"Based on this trend data, analyze health score direction and future outlook:\n{context}"
        
        insight = self._call_ai(prompt)
        self._cache_insight(key, insight)
        return insight
    
    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================
    
    def generate_all_insights(self, result: ComprehensiveResult) -> Dict[str, str]:
        """Generate all insights for comprehensive report."""
        print(f"    Generating insights...")
        
        insights = {
            "executive_summary": self.generate_executive_summary(result),
            "incident_insight": self.generate_incident_insight(result),
            "change_insight": self.generate_change_insight(result),
            "request_insight": self.generate_request_insight(result),
            "problem_insight": self.generate_problem_insight(result),
            "risk_insight": self.generate_risk_insight(result),
            "action_insight": self.generate_action_insight(result),
            "trend_insight": self.generate_trend_insight(result),
        }
        
        # Filter out empty insights
        insights = {k: v for k, v in insights.items() if v}
        
        return insights
