"""
Data Analysis Engine for BO Workload Performance Report.

Provides deep analysis of second/third-line expert workload including:
- BO tier identification
- Expert profiling
- Single-point dependency detection
- Bottleneck scoring
- Workload balance analysis (Gini coefficient)
- Knowledge silo detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from config import (
    COMPLEXITY_INDEX_TIER2_THRESHOLD,
    COMPLEXITY_INDEX_TIER3_THRESHOLD,
    PRIORITY_INDEX_TIER2_THRESHOLD,
    PRIORITY_INDEX_TIER3_THRESHOLD,
    SPECIALIZATION_TIER2_THRESHOLD,
    SPECIALIZATION_TIER3_THRESHOLD,
    MIN_TICKETS_FOR_CLASSIFICATION,
    BOTTLENECK_WEIGHTS,
    BACKLOG_WARNING_THRESHOLD,
    BACKLOG_CRITICAL_THRESHOLD,
    MTTR_WARNING_THRESHOLD,
    MTTR_CRITICAL_THRESHOLD,
    SINGLE_POINT_RISK_THRESHOLD,
    GINI_GOOD_THRESHOLD,
    GINI_WARNING_THRESHOLD,
    OVERLOAD_MULTIPLIER,
    LONG_TAIL_HOURS,
    DEFAULT_SLA,
    EXCLUDED_RESOLVERS,
    PRIORITY_WEIGHTS
)
from utils import (
    load_excel_data,
    clean_data,
    calculate_gini_coefficient,
    calculate_herfindahl_index,
    safe_divide,
    get_date_range
)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ResolverProfile:
    """Profile of a single resolver."""
    name: str
    tier: str = "Tier 1"
    tier_justification: str = ""
    
    # Volume metrics
    total_tickets: int = 0
    p1_count: int = 0
    p2_count: int = 0
    p3_count: int = 0
    p4_count: int = 0
    
    # Priority-weighted workload (P1×4, P2×3, P3×2, P4×1)
    weighted_workload: float = 0.0
    priority_distribution: Dict[str, int] = field(default_factory=dict)  # {"P1": n, "P2": n, ...}
    
    # Efficiency metrics
    avg_mttr_hours: float = 0.0
    median_mttr_hours: float = 0.0
    sla_rate: float = 0.0
    long_tail_rate: float = 0.0  # % of tickets > 48h
    
    # Tier classification metrics
    complexity_index: float = 0.0
    priority_index: float = 0.0
    specialization: float = 0.0  # Herfindahl index
    
    # Category distribution
    category_distribution: Dict[str, int] = field(default_factory=dict)
    top_categories: List[str] = field(default_factory=list)
    
    # Bottleneck metrics
    current_backlog: int = 0
    replaceability_score: float = 0.0
    bottleneck_score: float = 0.0
    bottleneck_root_causes: List[str] = field(default_factory=list)
    
    # Hourly distribution
    hourly_distribution: Dict[int, int] = field(default_factory=dict)


@dataclass
class CategoryRisk:
    """Single-point dependency risk for a category."""
    category: str
    resolver_count: int = 0
    resolvers: List[str] = field(default_factory=list)
    ticket_count: int = 0
    risk_level: str = "Low"  # High, Medium, Low
    avg_mttr: float = 0.0


@dataclass
class WorkloadBalanceResult:
    """Result of workload balance analysis."""
    gini_coefficient: float = 0.0
    interpretation: str = ""
    overloaded_resolvers: List[str] = field(default_factory=list)
    underloaded_resolvers: List[str] = field(default_factory=list)
    avg_workload: float = 0.0
    std_workload: float = 0.0
    workload_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Weighted workload metrics (priority-adjusted)
    weighted_gini_coefficient: float = 0.0
    weighted_interpretation: str = ""
    weighted_avg_workload: float = 0.0
    weighted_overloaded_resolvers: List[str] = field(default_factory=list)
    weighted_workload_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class KnowledgeSilo:
    """Knowledge silo detection result."""
    category: str
    sole_experts: List[str] = field(default_factory=list)
    ticket_count: int = 0
    avg_mttr: float = 0.0
    priority: str = "Medium"  # High, Medium, Low


@dataclass
class TrendPeriod:
    """Metrics for a specific time period."""
    period_label: str
    start_date: str
    end_date: str
    ticket_count: int = 0
    avg_mttr_hours: float = 0.0
    sla_rate: float = 0.0
    p1_p2_count: int = 0


@dataclass
class TrendAnalysis:
    """Trend analysis result with adaptive time segmentation."""
    period_type: str  # "monthly", "bi-monthly", "quarterly"
    periods: List[TrendPeriod] = field(default_factory=list)
    mttr_trend: str = ""  # "improving", "stable", "deteriorating"
    sla_trend: str = ""   # "improving", "stable", "deteriorating"
    volume_trend: str = "" # "increasing", "stable", "decreasing"
    mttr_change_pct: float = 0.0
    sla_change_pct: float = 0.0
    volume_change_pct: float = 0.0


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    # Date range
    start_date: str = ""
    end_date: str = ""

    # Overview
    total_resolvers: int = 0
    total_bo_resolvers: int = 0
    total_tickets: int = 0
    total_bo_tickets: int = 0

    # Tier distribution
    tier_counts: Dict[str, int] = field(default_factory=dict)

    # Global metrics
    global_avg_mttr: float = 0.0
    global_sla_rate: float = 0.0

    # Detailed results
    resolver_profiles: List[ResolverProfile] = field(default_factory=list)
    category_risks: List[CategoryRisk] = field(default_factory=list)
    workload_balance: Optional[WorkloadBalanceResult] = None
    knowledge_silos: List[KnowledgeSilo] = field(default_factory=list)

    # Trend analysis
    trend_analysis: Optional[TrendAnalysis] = None

    # Summary counts
    high_risk_count: int = 0
    bottleneck_count: int = 0


# =============================================================================
# Main Analyzer Class
# =============================================================================

class BOWorkloadAnalyzer:
    """
    Analyzer for BO (second/third-line) workload performance.
    """
    
    def __init__(self, data_file: str):
        """
        Initialize analyzer with data file.
        
        Args:
            data_file: Path to Excel data file
        """
        self.data_file = data_file
        self.df: Optional[pd.DataFrame] = None
        self.sla_df: Optional[pd.DataFrame] = None
        self.sla_criteria: Dict[str, float] = {}
        
    def load_data(self) -> None:
        """Load and clean data from Excel file."""
        self.df, self.sla_df = load_excel_data(self.data_file)
        self.df = clean_data(self.df, EXCLUDED_RESOLVERS)
        
        # Build SLA criteria lookup
        if self.sla_df is not None:
            for _, row in self.sla_df.iterrows():
                priority = row.get("Priority", "")
                resolution_hours = row.get("Resolution (hours)", DEFAULT_SLA.get(priority, 24))
                self.sla_criteria[priority] = float(resolution_hours)
    
    def analyze(self) -> AnalysisResult:
        """
        Run complete analysis.
        
        Returns:
            AnalysisResult with all analysis data
        """
        if self.df is None:
            self.load_data()
        
        result = AnalysisResult()
        
        # Get date range
        start_date, end_date = get_date_range(self.df)
        result.start_date = start_date.strftime("%Y-%m-%d")
        result.end_date = end_date.strftime("%Y-%m-%d")
        
        # Calculate global metrics
        result.total_tickets = len(self.df)
        result.global_avg_mttr = self.df["Resolution_Hours"].mean() if "Resolution_Hours" in self.df.columns else 0
        result.global_sla_rate = self._calculate_global_sla_rate()
        
        # Get unique resolvers
        resolvers = self.df["Resolver"].unique()
        result.total_resolvers = len(resolvers)
        
        # Analyze each resolver
        resolver_profiles = []
        for resolver in resolvers:
            profile = self._analyze_resolver(resolver, result.global_avg_mttr)
            resolver_profiles.append(profile)
        
        # Classify tiers
        resolver_profiles = self._classify_tiers(resolver_profiles)
        
        # Count BO resolvers (Tier 2 + Tier 3)
        result.tier_counts = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0}
        for profile in resolver_profiles:
            result.tier_counts[profile.tier] = result.tier_counts.get(profile.tier, 0) + 1
        
        result.total_bo_resolvers = result.tier_counts.get("Tier 2", 0) + result.tier_counts.get("Tier 3", 0)
        
        # Calculate BO tickets
        bo_resolvers = [p.name for p in resolver_profiles if p.tier in ["Tier 2", "Tier 3"]]
        result.total_bo_tickets = len(self.df[self.df["Resolver"].isin(bo_resolvers)])
        
        # Analyze single-point dependency
        result.category_risks = self._analyze_dependency_risks()
        result.high_risk_count = len([r for r in result.category_risks if r.risk_level == "High"])
        
        # Calculate replaceability for each resolver
        resolver_profiles = self._calculate_replaceability(resolver_profiles, result.category_risks)
        
        # Calculate bottleneck scores
        resolver_profiles = self._calculate_bottleneck_scores(resolver_profiles)
        
        # Count bottlenecks (top 20% or score > 0.6)
        sorted_by_bottleneck = sorted(resolver_profiles, key=lambda x: x.bottleneck_score, reverse=True)
        threshold_idx = max(1, len(sorted_by_bottleneck) // 5)  # Top 20%
        result.bottleneck_count = len([p for p in sorted_by_bottleneck[:threshold_idx] if p.bottleneck_score > 0.4])
        
        result.resolver_profiles = resolver_profiles
        
        # Analyze workload balance
        result.workload_balance = self._analyze_workload_balance(resolver_profiles)
        
        # Detect knowledge silos
        result.knowledge_silos = self._detect_knowledge_silos()

        # Analyze trends with adaptive time segmentation
        result.trend_analysis = self._analyze_trends()

        return result
    
    def _calculate_global_sla_rate(self) -> float:
        """Calculate global SLA compliance rate."""
        if "Resolution_Hours" not in self.df.columns or "Priority" not in self.df.columns:
            return 0.0
        
        compliant = 0
        total = 0
        
        for _, row in self.df.iterrows():
            priority = row.get("Priority", "P4")
            resolution_hours = row.get("Resolution_Hours", 0)
            sla_threshold = self.sla_criteria.get(priority, DEFAULT_SLA.get(priority, 24))
            
            if pd.notna(resolution_hours):
                total += 1
                if resolution_hours <= sla_threshold:
                    compliant += 1
        
        return safe_divide(compliant, total, 0.0)
    
    def _analyze_resolver(self, resolver: str, global_avg_mttr: float) -> ResolverProfile:
        """
        Analyze a single resolver.
        
        Args:
            resolver: Resolver name
            global_avg_mttr: Global average MTTR for comparison
        
        Returns:
            ResolverProfile with analysis results
        """
        profile = ResolverProfile(name=resolver)
        
        # Filter data for this resolver
        resolver_df = self.df[self.df["Resolver"] == resolver]
        
        # Volume metrics
        profile.total_tickets = len(resolver_df)
        profile.p1_count = len(resolver_df[resolver_df["Priority"] == "P1"])
        profile.p2_count = len(resolver_df[resolver_df["Priority"] == "P2"])
        profile.p3_count = len(resolver_df[resolver_df["Priority"] == "P3"])
        profile.p4_count = len(resolver_df[resolver_df["Priority"] == "P4"])
        
        # Priority distribution and weighted workload
        profile.priority_distribution = {
            "P1": profile.p1_count,
            "P2": profile.p2_count,
            "P3": profile.p3_count,
            "P4": profile.p4_count
        }
        profile.weighted_workload = (
            profile.p1_count * PRIORITY_WEIGHTS.get("P1", 4) +
            profile.p2_count * PRIORITY_WEIGHTS.get("P2", 3) +
            profile.p3_count * PRIORITY_WEIGHTS.get("P3", 2) +
            profile.p4_count * PRIORITY_WEIGHTS.get("P4", 1)
        )
        
        # Efficiency metrics
        if "Resolution_Hours" in resolver_df.columns:
            mttr_series = resolver_df["Resolution_Hours"].dropna()
            if len(mttr_series) > 0:
                profile.avg_mttr_hours = mttr_series.mean()
                profile.median_mttr_hours = mttr_series.median()
                profile.long_tail_rate = safe_divide(
                    len(mttr_series[mttr_series > LONG_TAIL_HOURS]),
                    len(mttr_series),
                    0.0
                )
        
        # SLA rate
        profile.sla_rate = self._calculate_resolver_sla_rate(resolver_df)
        
        # Tier classification metrics
        profile.complexity_index = safe_divide(profile.avg_mttr_hours, global_avg_mttr, 1.0)
        profile.priority_index = safe_divide(
            profile.p1_count + profile.p2_count,
            profile.total_tickets,
            0.0
        )
        
        # Category distribution
        if "Category" in resolver_df.columns:
            category_counts = resolver_df["Category"].value_counts().to_dict()
            profile.category_distribution = category_counts
            profile.top_categories = list(category_counts.keys())[:5]
            
            # Specialization (Herfindahl index)
            if len(category_counts) > 0:
                counts = np.array(list(category_counts.values()))
                profile.specialization = calculate_herfindahl_index(counts)
        
        # Current backlog (open tickets)
        if "Order Status" in resolver_df.columns:
            open_statuses = ["Open", "In Progress", "Pending", "Assigned"]
            profile.current_backlog = len(resolver_df[resolver_df["Order Status"].isin(open_statuses)])
        
        # Hourly distribution
        if "Hour" in resolver_df.columns:
            hourly_counts = resolver_df["Hour"].value_counts().to_dict()
            profile.hourly_distribution = {int(k): v for k, v in hourly_counts.items()}
        
        return profile
    
    def _calculate_resolver_sla_rate(self, resolver_df: pd.DataFrame) -> float:
        """Calculate SLA compliance rate for a resolver."""
        if "Resolution_Hours" not in resolver_df.columns or "Priority" not in resolver_df.columns:
            return 0.0
        
        compliant = 0
        total = 0
        
        for _, row in resolver_df.iterrows():
            priority = row.get("Priority", "P4")
            resolution_hours = row.get("Resolution_Hours", 0)
            sla_threshold = self.sla_criteria.get(priority, DEFAULT_SLA.get(priority, 24))
            
            if pd.notna(resolution_hours):
                total += 1
                if resolution_hours <= sla_threshold:
                    compliant += 1
        
        return safe_divide(compliant, total, 0.0)
    
    def _classify_tiers(self, profiles: List[ResolverProfile]) -> List[ResolverProfile]:
        """
        Classify resolvers into tiers based on their metrics.
        
        Args:
            profiles: List of resolver profiles
        
        Returns:
            Updated profiles with tier classification
        """
        for profile in profiles:
            # Skip resolvers with too few tickets
            if profile.total_tickets < MIN_TICKETS_FOR_CLASSIFICATION:
                profile.tier = "Tier 1"
                profile.tier_justification = f"Insufficient data ({profile.total_tickets} tickets)"
                continue
            
            # Scoring for tier classification
            tier2_score = 0
            tier3_score = 0
            justifications = []
            
            # Complexity index
            if profile.complexity_index >= COMPLEXITY_INDEX_TIER3_THRESHOLD:
                tier3_score += 2
                justifications.append(f"High complexity ({profile.complexity_index:.2f}x avg)")
            elif profile.complexity_index >= COMPLEXITY_INDEX_TIER2_THRESHOLD:
                tier2_score += 1
                justifications.append(f"Moderate complexity ({profile.complexity_index:.2f}x avg)")
            
            # Priority index
            if profile.priority_index >= PRIORITY_INDEX_TIER3_THRESHOLD:
                tier3_score += 2
                justifications.append(f"High P1/P2 ratio ({profile.priority_index:.0%})")
            elif profile.priority_index >= PRIORITY_INDEX_TIER2_THRESHOLD:
                tier2_score += 1
                justifications.append(f"Moderate P1/P2 ratio ({profile.priority_index:.0%})")
            
            # Specialization
            if profile.specialization >= SPECIALIZATION_TIER3_THRESHOLD:
                tier3_score += 1
                justifications.append(f"Highly specialized (HHI: {profile.specialization:.2f})")
            elif profile.specialization >= SPECIALIZATION_TIER2_THRESHOLD:
                tier2_score += 1
                justifications.append(f"Moderately specialized (HHI: {profile.specialization:.2f})")
            
            # Determine tier
            if tier3_score >= 3:
                profile.tier = "Tier 3"
            elif tier3_score >= 2 or tier2_score >= 2:
                profile.tier = "Tier 2"
            else:
                profile.tier = "Tier 1"
            
            profile.tier_justification = "; ".join(justifications) if justifications else "General workload pattern"
        
        return profiles
    
    def _analyze_dependency_risks(self) -> List[CategoryRisk]:
        """
        Analyze single-point dependency risks by category.
        
        Returns:
            List of CategoryRisk objects
        """
        if "Category" not in self.df.columns:
            return []
        
        category_risks = []
        
        # Group by category
        for category, group in self.df.groupby("Category"):
            risk = CategoryRisk(category=category)
            
            # Count unique resolvers
            resolvers = group["Resolver"].unique().tolist()
            risk.resolver_count = len(resolvers)
            risk.resolvers = resolvers
            risk.ticket_count = len(group)
            
            # Calculate average MTTR
            if "Resolution_Hours" in group.columns:
                risk.avg_mttr = group["Resolution_Hours"].mean()
            
            # Determine risk level
            if risk.resolver_count <= 1:
                risk.risk_level = "High"
            elif risk.resolver_count <= SINGLE_POINT_RISK_THRESHOLD:
                risk.risk_level = "High"
            elif risk.resolver_count <= 4:
                risk.risk_level = "Medium"
            else:
                risk.risk_level = "Low"
            
            category_risks.append(risk)
        
        # Sort by risk (High first, then by ticket count)
        risk_order = {"High": 0, "Medium": 1, "Low": 2}
        category_risks.sort(key=lambda x: (risk_order.get(x.risk_level, 3), -x.ticket_count))
        
        return category_risks
    
    def _calculate_replaceability(
        self,
        profiles: List[ResolverProfile],
        category_risks: List[CategoryRisk]
    ) -> List[ResolverProfile]:
        """
        Calculate replaceability score for each resolver.
        
        Args:
            profiles: List of resolver profiles
            category_risks: List of category risks
        
        Returns:
            Updated profiles with replaceability scores
        """
        # Build category -> resolver count mapping
        category_resolver_counts = {r.category: r.resolver_count for r in category_risks}
        
        for profile in profiles:
            if not profile.category_distribution:
                profile.replaceability_score = 1.0
                continue
            
            # Weighted average replaceability based on ticket distribution
            total_weight = 0
            weighted_score = 0
            
            for category, count in profile.category_distribution.items():
                resolver_count = category_resolver_counts.get(category, 1)
                # More resolvers = higher replaceability
                score = min(1.0, (resolver_count - 1) / 5)  # Normalize: 1 resolver = 0, 6+ resolvers = 1
                weighted_score += score * count
                total_weight += count
            
            profile.replaceability_score = safe_divide(weighted_score, total_weight, 0.5)
        
        return profiles
    
    def _calculate_bottleneck_scores(self, profiles: List[ResolverProfile]) -> List[ResolverProfile]:
        """
        Calculate bottleneck scores for each resolver.

        Bottleneck score = weighted combination of:
        - Backlog (30%)
        - MTTR (25%)
        - Replaceability (25%)
        - SLA trend (20%)

        Args:
            profiles: List of resolver profiles

        Returns:
            Updated profiles with bottleneck scores
        """
        # Calculate statistical baselines for comparison
        all_mttrs = [p.avg_mttr_hours for p in profiles if p.avg_mttr_hours > 0]
        all_sla_rates = [p.sla_rate for p in profiles if p.sla_rate > 0]
        all_volumes = [p.total_tickets for p in profiles]

        avg_mttr = np.mean(all_mttrs) if all_mttrs else 24
        std_mttr = np.std(all_mttrs) if len(all_mttrs) > 1 else avg_mttr * 0.3
        avg_sla = np.mean(all_sla_rates) if all_sla_rates else 0.7
        avg_volume = np.mean(all_volumes) if all_volumes else 100

        # Calculate max values for normalization
        max_backlog = max((p.current_backlog for p in profiles), default=1) or 1
        max_mttr = max((p.avg_mttr_hours for p in profiles), default=1) or 1

        for profile in profiles:
            root_causes = []

            # Backlog score (0-1, higher = worse)
            backlog_score = min(1.0, profile.current_backlog / max(BACKLOG_CRITICAL_THRESHOLD, max_backlog))
            if profile.current_backlog >= BACKLOG_CRITICAL_THRESHOLD:
                root_causes.append(f"Critical backlog ({profile.current_backlog} open)")
            elif profile.current_backlog >= BACKLOG_WARNING_THRESHOLD:
                root_causes.append(f"High backlog ({profile.current_backlog} open)")

            # MTTR score - differentiate the actual issue
            mttr_score = min(1.0, profile.avg_mttr_hours / max(MTTR_CRITICAL_THRESHOLD, max_mttr))

            if profile.avg_mttr_hours > 0:
                # Compare to peers
                mttr_z_score = (profile.avg_mttr_hours - avg_mttr) / std_mttr if std_mttr > 0 else 0

                if profile.avg_mttr_hours >= MTTR_CRITICAL_THRESHOLD:
                    # Very slow - dig into why
                    if profile.priority_index > 0.25:
                        root_causes.append(f"Handles complex P1/P2 cases ({profile.priority_index:.0%})")
                    elif profile.specialization > 0.4:
                        root_causes.append(f"Deep specialist - fewer parallel cases")
                    else:
                        root_causes.append(f"MTTR {profile.avg_mttr_hours:.0f}h exceeds threshold")
                elif profile.avg_mttr_hours >= MTTR_WARNING_THRESHOLD:
                    if mttr_z_score > 1.5:
                        root_causes.append(f"MTTR {profile.avg_mttr_hours:.0f}h ({mttr_z_score:.1f}σ above avg)")
                    else:
                        root_causes.append(f"MTTR {profile.avg_mttr_hours:.0f}h above target")
                elif mttr_z_score > 1.0:
                    root_causes.append(f"MTTR above peer average (+{mttr_z_score:.1f}σ)")

            # Replaceability score (0-1, lower = worse, so invert)
            irreplaceability_score = 1.0 - profile.replaceability_score
            if profile.replaceability_score < 0.2:
                # Find which categories make them irreplaceable
                sole_categories = [cat for cat, count in profile.category_distribution.items()
                                   if count >= 5][:2]
                if sole_categories:
                    root_causes.append(f"Sole expert: {', '.join(sole_categories)}")
                else:
                    root_causes.append("Low replaceability across categories")
            elif profile.replaceability_score < 0.4:
                root_causes.append("Limited backup coverage")

            # SLA score - differentiate the pattern
            sla_score = 1.0 - profile.sla_rate

            if profile.sla_rate < avg_sla - 0.15:
                # Significantly below average
                if profile.long_tail_rate > 0.2:
                    root_causes.append(f"Long-tail cases ({profile.long_tail_rate:.0%} >48h)")
                elif profile.p1_count + profile.p2_count > profile.total_tickets * 0.3:
                    root_causes.append(f"Heavy P1/P2 load ({profile.p1_count + profile.p2_count} cases)")
                else:
                    root_causes.append(f"SLA {profile.sla_rate:.0%} below avg {avg_sla:.0%}")
            elif profile.sla_rate < 0.8:
                root_causes.append(f"SLA compliance {profile.sla_rate:.0%}")

            # Volume consideration
            if profile.total_tickets > avg_volume * 1.5:
                root_causes.append(f"High volume ({profile.total_tickets} tickets)")
            elif profile.total_tickets < avg_volume * 0.5 and profile.avg_mttr_hours > avg_mttr:
                root_causes.append("Low volume but high MTTR - may need training")

            # Calculate weighted bottleneck score
            profile.bottleneck_score = (
                BOTTLENECK_WEIGHTS["backlog"] * backlog_score +
                BOTTLENECK_WEIGHTS["mttr"] * mttr_score +
                BOTTLENECK_WEIGHTS["replaceability"] * irreplaceability_score +
                BOTTLENECK_WEIGHTS["sla_trend"] * sla_score
            )

            # If no specific root causes identified, provide a summary
            if not root_causes:
                if profile.bottleneck_score < 0.3:
                    root_causes.append("Performing within normal range")
                else:
                    root_causes.append("Minor efficiency gaps")

            profile.bottleneck_root_causes = root_causes

        return profiles
    
    def _analyze_workload_balance(self, profiles: List[ResolverProfile]) -> WorkloadBalanceResult:
        """
        Analyze workload balance across resolvers.
        
        Args:
            profiles: List of resolver profiles
        
        Returns:
            WorkloadBalanceResult with balance metrics (raw and weighted)
        """
        result = WorkloadBalanceResult()
        
        if not profiles:
            return result
        
        # Get raw workload distribution
        workloads = {p.name: p.total_tickets for p in profiles}
        result.workload_distribution = workloads
        
        workload_values = np.array(list(workloads.values()))
        
        # Calculate raw Gini coefficient
        result.gini_coefficient = calculate_gini_coefficient(workload_values)
        
        # Interpret raw Gini
        if result.gini_coefficient < GINI_GOOD_THRESHOLD:
            result.interpretation = "Well Balanced"
        elif result.gini_coefficient < GINI_WARNING_THRESHOLD:
            result.interpretation = "Moderate Imbalance"
        else:
            result.interpretation = "Severe Imbalance"
        
        # Calculate raw statistics
        result.avg_workload = float(np.mean(workload_values))
        result.std_workload = float(np.std(workload_values))
        
        # Identify overloaded and underloaded (raw)
        overload_threshold = result.avg_workload * OVERLOAD_MULTIPLIER
        underload_threshold = result.avg_workload * 0.5
        
        for name, workload in workloads.items():
            if workload > overload_threshold:
                result.overloaded_resolvers.append(name)
            elif workload < underload_threshold:
                result.underloaded_resolvers.append(name)
        
        # Calculate weighted workload distribution
        weighted_workloads = {p.name: p.weighted_workload for p in profiles}
        result.weighted_workload_distribution = weighted_workloads
        
        weighted_values = np.array(list(weighted_workloads.values()))
        
        if len(weighted_values) > 0 and weighted_values.sum() > 0:
            # Calculate weighted Gini coefficient
            result.weighted_gini_coefficient = calculate_gini_coefficient(weighted_values)
            
            # Interpret weighted Gini
            if result.weighted_gini_coefficient < GINI_GOOD_THRESHOLD:
                result.weighted_interpretation = "Well Balanced"
            elif result.weighted_gini_coefficient < GINI_WARNING_THRESHOLD:
                result.weighted_interpretation = "Moderate Imbalance"
            else:
                result.weighted_interpretation = "Severe Imbalance"
            
            # Calculate weighted statistics
            result.weighted_avg_workload = float(np.mean(weighted_values))
            
            # Identify overloaded (weighted)
            weighted_overload_threshold = result.weighted_avg_workload * OVERLOAD_MULTIPLIER
            for name, weighted_wl in weighted_workloads.items():
                if weighted_wl > weighted_overload_threshold:
                    result.weighted_overloaded_resolvers.append(name)
        
        return result
    
    def _detect_knowledge_silos(self) -> List[KnowledgeSilo]:
        """
        Detect knowledge silos (categories with only 1-2 experts).
        
        Returns:
            List of KnowledgeSilo objects
        """
        if "Category" not in self.df.columns:
            return []
        
        silos = []
        
        for category, group in self.df.groupby("Category"):
            resolvers = group["Resolver"].unique().tolist()
            
            # Only flag if 1-2 resolvers
            if len(resolvers) > 2:
                continue
            
            silo = KnowledgeSilo(
                category=category,
                sole_experts=resolvers,
                ticket_count=len(group)
            )
            
            # Calculate average MTTR
            if "Resolution_Hours" in group.columns:
                silo.avg_mttr = group["Resolution_Hours"].mean()
            
            # Determine priority based on ticket count and priority distribution
            p1_p2_count = len(group[group["Priority"].isin(["P1", "P2"])])
            p1_p2_ratio = safe_divide(p1_p2_count, len(group), 0)
            
            if len(resolvers) == 1 and (silo.ticket_count >= 10 or p1_p2_ratio > 0.2):
                silo.priority = "High"
            elif len(resolvers) == 1:
                silo.priority = "Medium"
            else:
                silo.priority = "Low"
            
            silos.append(silo)
        
        # Sort by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        silos.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.ticket_count))
        
        return silos
    
    def get_bo_resolvers(self) -> List[ResolverProfile]:
        """
        Get only Tier 2 and Tier 3 resolvers.
        
        Returns:
            List of BO resolver profiles
        """
        result = self.analyze()
        return [p for p in result.resolver_profiles if p.tier in ["Tier 2", "Tier 3"]]
    
    def get_top_bottlenecks(self, n: int = 5) -> List[ResolverProfile]:
        """
        Get top N bottleneck resolvers.
        
        Args:
            n: Number of bottlenecks to return
        
        Returns:
            List of top bottleneck profiles
        """
        result = self.analyze()
        sorted_profiles = sorted(
            result.resolver_profiles,
            key=lambda x: x.bottleneck_score,
            reverse=True
        )
        return sorted_profiles[:n]
    
    def get_high_risk_categories(self) -> List[CategoryRisk]:
        """
        Get high-risk categories only.

        Returns:
            List of high-risk CategoryRisk objects
        """
        result = self.analyze()
        return [r for r in result.category_risks if r.risk_level == "High"]

    def _analyze_trends(self) -> TrendAnalysis:
        """
        Analyze trends with adaptive time segmentation based on data span.

        Returns:
            TrendAnalysis with period metrics and trend indicators
        """
        if "Begin Date" not in self.df.columns:
            return TrendAnalysis(period_type="monthly", periods=[])

        # Get date range and determine period type
        start_date, end_date = get_date_range(self.df)
        total_days = (end_date - start_date).days

        # Adaptive segmentation: aim for 4-8 periods
        if total_days <= 90:  # <= 3 months: weekly
            period_type = "weekly"
            freq = "W"
        elif total_days <= 180:  # <= 6 months: bi-weekly
            period_type = "bi-weekly"
            freq = "2W"
        elif total_days <= 365:  # <= 1 year: monthly
            period_type = "monthly"
            freq = "M"
        elif total_days <= 730:  # <= 2 years: bi-monthly
            period_type = "bi-monthly"
            freq = "2M"
        else:  # > 2 years: quarterly
            period_type = "quarterly"
            freq = "Q"

        # Create period groups
        df_with_period = self.df.copy()
        df_with_period["Period"] = df_with_period["Begin Date"].dt.to_period(freq[0] if freq[0] != '2' else freq[1])

        if freq.startswith("2"):
            # Handle bi-weekly/bi-monthly by grouping adjacent periods
            periods_list = sorted(df_with_period["Period"].unique())
            period_mapping = {}
            for i, p in enumerate(periods_list):
                period_mapping[p] = periods_list[i // 2 * 2] if i // 2 * 2 < len(periods_list) else periods_list[-1]
            df_with_period["Period"] = df_with_period["Period"].map(period_mapping)

        # Calculate metrics per period
        periods = []
        for period, group in df_with_period.groupby("Period"):
            period_start = group["Begin Date"].min()
            period_end = group["Begin Date"].max()

            # Calculate SLA rate for this period
            compliant = 0
            total = 0
            for _, row in group.iterrows():
                priority = row.get("Priority", "P4")
                resolution_hours = row.get("Resolution_Hours", 0)
                sla_threshold = self.sla_criteria.get(priority, DEFAULT_SLA.get(priority, 24))

                if pd.notna(resolution_hours):
                    total += 1
                    if resolution_hours <= sla_threshold:
                        compliant += 1

            sla_rate = safe_divide(compliant, total, 0.0)

            trend_period = TrendPeriod(
                period_label=str(period),
                start_date=period_start.strftime("%Y-%m-%d") if pd.notna(period_start) else "",
                end_date=period_end.strftime("%Y-%m-%d") if pd.notna(period_end) else "",
                ticket_count=len(group),
                avg_mttr_hours=group["Resolution_Hours"].mean() if "Resolution_Hours" in group.columns else 0,
                sla_rate=sla_rate,
                p1_p2_count=len(group[group["Priority"].isin(["P1", "P2"])])
            )
            periods.append(trend_period)

        # Sort by period label
        periods.sort(key=lambda x: x.period_label)

        # Calculate trend indicators (compare first half vs second half)
        result = TrendAnalysis(period_type=period_type, periods=periods)

        if len(periods) >= 2:
            mid = len(periods) // 2
            first_half = periods[:mid]
            second_half = periods[mid:]

            # MTTR trend
            first_mttr = np.mean([p.avg_mttr_hours for p in first_half if p.avg_mttr_hours > 0]) or 0
            second_mttr = np.mean([p.avg_mttr_hours for p in second_half if p.avg_mttr_hours > 0]) or 0
            if first_mttr > 0:
                result.mttr_change_pct = (second_mttr - first_mttr) / first_mttr * 100
                if result.mttr_change_pct < -10:
                    result.mttr_trend = "improving"
                elif result.mttr_change_pct > 10:
                    result.mttr_trend = "deteriorating"
                else:
                    result.mttr_trend = "stable"

            # SLA trend
            first_sla = np.mean([p.sla_rate for p in first_half]) or 0
            second_sla = np.mean([p.sla_rate for p in second_half]) or 0
            if first_sla > 0:
                result.sla_change_pct = (second_sla - first_sla) / first_sla * 100
                if result.sla_change_pct > 5:
                    result.sla_trend = "improving"
                elif result.sla_change_pct < -5:
                    result.sla_trend = "deteriorating"
                else:
                    result.sla_trend = "stable"

            # Volume trend
            first_vol = np.mean([p.ticket_count for p in first_half]) or 0
            second_vol = np.mean([p.ticket_count for p in second_half]) or 0
            if first_vol > 0:
                result.volume_change_pct = (second_vol - first_vol) / first_vol * 100
                if result.volume_change_pct > 15:
                    result.volume_trend = "increasing"
                elif result.volume_change_pct < -15:
                    result.volume_trend = "decreasing"
                else:
                    result.volume_trend = "stable"

        return result
