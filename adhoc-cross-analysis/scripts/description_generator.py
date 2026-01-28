"""
Description Generator for Adhoc Analysis.
Generates natural language descriptions from structured results.
Uses templates for reliability (LLM optional for polish).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class DescriptionGenerator:
    def __init__(self, language='zh'):
        self.lang = language
        self.use_llm = os.getenv('OPENAI_API_KEY') is not None

    def generate(self, intent, result):
        """
        Generate natural language description.

        Args:
            intent: parsed intent dict
            result: query execution result dict

        Returns:
            str: natural language description
        """
        query_type = intent['type']

        if query_type == 'ranking':
            return self._generate_ranking_desc(intent, result)
        elif query_type == 'trend':
            return self._generate_trend_desc(intent, result)
        elif query_type == 'breakdown':
            return self._generate_breakdown_desc(intent, result)
        elif query_type == 'comparison':
            return self._generate_comparison_desc(intent, result)
        elif query_type == 'drilldown':
            return self._generate_drilldown_desc(intent, result)
        else:
            return self._generate_ranking_desc(intent, result)

    def _generate_ranking_desc(self, intent, result):
        """Generate ranking description."""
        data = result.get('data', [])
        if not data:
            return self._no_data_msg()

        dimension = intent['dimension']
        metric = intent['metric']
        order = intent['order']

        top_item = data[0]
        name = top_item['name']
        value = top_item['value']

        # Dimension and metric names
        dim_name = self._dim_name(dimension)
        metric_name = self._metric_name(metric)
        metric_unit = self._metric_unit(metric)

        # Order description
        if order == 'asc':
            order_word = '最差' if self.lang == 'zh' else 'worst'
        else:
            order_word = '最好' if self.lang == 'zh' else 'best'

        if self.lang == 'zh':
            desc = f"按{dim_name}分析{metric_name}，{order_word}的是 **{name}**，{metric_name}为 **{value}{metric_unit}**。\n\n"
            desc += f"排名详情：\n"
            for i, item in enumerate(data[:5], 1):
                desc += f"{i}. {item['name']}: {item['value']}{metric_unit} (工单量: {item['count']})\n"
        else:
            desc = f"Analyzing {metric_name} by {dim_name}, the {order_word} is **{name}** with {metric_name} of **{value}{metric_unit}**.\n\n"
            desc += f"Ranking details:\n"
            for i, item in enumerate(data[:5], 1):
                desc += f"{i}. {item['name']}: {item['value']}{metric_unit} (Volume: {item['count']})\n"

        # Add samples if available
        samples = result.get('samples', [])
        if samples:
            if self.lang == 'zh':
                desc += f"\n证据样本 (来自 {name})：\n"
            else:
                desc += f"\nEvidence samples (from {name}):\n"
            for s in samples[:3]:
                desc += f"- {s['order_number']}: {s['priority']}, MTTR={s['mttr']}h\n"

        return desc

    def _generate_trend_desc(self, intent, result):
        """Generate trend description."""
        data = result.get('data', [])
        if not data:
            return self._no_data_msg()

        metric = intent['metric']
        metric_name = self._metric_name(metric)
        change = result.get('trend_change', 0)

        first = data[0]
        last = data[-1]

        if self.lang == 'zh':
            direction = '上升' if change > 0 else '下降' if change < 0 else '持平'
            desc = f"{metric_name}趋势分析：从 {first['name']} 到 {last['name']}，整体{direction} **{abs(change):.1f}%**。\n\n"
            desc += f"起始值: {first['value']} → 最终值: {last['value']}\n\n"
            desc += "各期详情：\n"
            for item in data[-6:]:
                desc += f"- {item['name']}: {item['value']}\n"
        else:
            direction = 'increased' if change > 0 else 'decreased' if change < 0 else 'remained stable'
            desc = f"{metric_name} trend analysis: From {first['name']} to {last['name']}, overall {direction} by **{abs(change):.1f}%**.\n\n"
            desc += f"Starting: {first['value']} → Ending: {last['value']}\n\n"
            desc += "Period details:\n"
            for item in data[-6:]:
                desc += f"- {item['name']}: {item['value']}\n"

        return desc

    def _generate_breakdown_desc(self, intent, result):
        """Generate breakdown description."""
        data = result.get('data', [])
        if not data:
            return self._no_data_msg()

        dimension = intent['dimension']
        dim_name = self._dim_name(dimension)
        total = result.get('total', 0)

        if self.lang == 'zh':
            desc = f"按{dim_name}的工单分布 (总计 {total:,})：\n\n"
            for item in data[:8]:
                desc += f"- **{item['name']}**: {item['count']:,} ({item['percentage']}%), SLA达成率 {item['sla_rate']}%\n"
        else:
            desc = f"Ticket distribution by {dim_name} (Total: {total:,}):\n\n"
            for item in data[:8]:
                desc += f"- **{item['name']}**: {item['count']:,} ({item['percentage']}%), SLA Rate {item['sla_rate']}%\n"

        return desc

    def _generate_comparison_desc(self, intent, result):
        """Generate comparison description."""
        data = result.get('data', [])
        if not data:
            return self._no_data_msg()

        if self.lang == 'zh':
            desc = "对比分析：\n\n"
            for item in data:
                label = '环比' if item['type'] == 'wow' else '同比'
                vol_dir = '增加' if item['volume_change'] > 0 else '减少'
                sla_dir = '提升' if item['sla_change'] > 0 else '下降'
                desc += f"**{label}** ({item['previous']} → {item['current']})：\n"
                desc += f"- 工单量{vol_dir} {abs(item['volume_change']):.1f}%\n"
                desc += f"- SLA达成率{sla_dir} {abs(item['sla_change']):.1f}%\n\n"
        else:
            desc = "Comparison Analysis:\n\n"
            for item in data:
                label = item['label']
                vol_dir = 'increased' if item['volume_change'] > 0 else 'decreased'
                sla_dir = 'improved' if item['sla_change'] > 0 else 'declined'
                desc += f"**{label}** ({item['previous']} → {item['current']}):\n"
                desc += f"- Volume {vol_dir} by {abs(item['volume_change']):.1f}%\n"
                desc += f"- SLA Rate {sla_dir} by {abs(item['sla_change']):.1f}%\n\n"

        return desc

    def _generate_drilldown_desc(self, intent, result):
        """Generate drilldown description."""
        data = result.get('data', [])
        if not data:
            return self._no_data_msg()

        dimension = intent['dimension']
        metric = intent['metric']
        dim_name = self._dim_name(dimension)
        metric_name = self._metric_name(metric)

        if self.lang == 'zh':
            desc = f"下钻分析：{metric_name}表现最差的{dim_name}\n\n"
            for item in data:
                desc += f"**{item['name']}**:\n"
                desc += f"- {metric_name}: {item['value']}\n"
                desc += f"- 工单量: {item['count']}\n"
                desc += f"- 违约数: {item['violations']}\n"
                if item.get('samples'):
                    desc += f"- 典型工单:\n"
                    for s in item['samples'][:2]:
                        desc += f"  - {s['order_number']}: MTTR={s['mttr']}h\n"
                desc += "\n"
        else:
            desc = f"Drilldown Analysis: Worst performing {dim_name} by {metric_name}\n\n"
            for item in data:
                desc += f"**{item['name']}**:\n"
                desc += f"- {metric_name}: {item['value']}\n"
                desc += f"- Volume: {item['count']}\n"
                desc += f"- Violations: {item['violations']}\n"
                if item.get('samples'):
                    desc += f"- Sample tickets:\n"
                    for s in item['samples'][:2]:
                        desc += f"  - {s['order_number']}: MTTR={s['mttr']}h\n"
                desc += "\n"

        return desc

    def _dim_name(self, dimension):
        names = {
            'priority': {'zh': '优先级', 'en': 'Priority'},
            'category': {'zh': '类别', 'en': 'Category'},
            'team': {'zh': '团队', 'en': 'Team'},
            'resolver': {'zh': '处理人', 'en': 'Resolver'},
            'time': {'zh': '时间', 'en': 'Time'},
        }
        return names.get(dimension, {}).get(self.lang, dimension)

    def _metric_name(self, metric):
        names = {
            'volume': {'zh': '工单量', 'en': 'Volume'},
            'sla_rate': {'zh': 'SLA达成率', 'en': 'SLA Rate'},
            'mttr': {'zh': '平均MTTR', 'en': 'Avg MTTR'},
            'violations': {'zh': '违约数', 'en': 'Violations'},
        }
        return names.get(metric, {}).get(self.lang, metric)

    def _metric_unit(self, metric):
        units = {
            'volume': '',
            'sla_rate': '%',
            'mttr': 'h',
            'violations': '',
        }
        return units.get(metric, '')

    def _no_data_msg(self):
        if self.lang == 'zh':
            return "无数据可分析。"
        return "No data available for analysis."
