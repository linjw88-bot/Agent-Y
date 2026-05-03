"""
情景分析引擎
基于知识库和用户背景，生成多情景分析

支持：
- 预定义领域的情景模板（互联网产品、职业发展等）
- 通用情景生成（适用于新领域）
"""
from typing import Dict, Any, List
import hashlib


class ScenarioEngine:
    """情景分析引擎"""

    def __init__(self):
        pass

    def generate_scenarios(
        self,
        query: str,
        industry: str,
        answers: Dict[str, str],
        knowledge: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        生成3个情景：高/中/低概率
        根据领域返回预定义模板或通用情景
        """
        risk_level = self._analyze_risk(answers)

        base_scenarios = {
            "互联网产品": [
                {
                    "name": "快速迭代",
                    "description": "两周一个迭代周期，快速验证用户假设，数据驱动决策。",
                    "probability_base": 0.40,
                    "key_factors": ["用户反馈速度", "技术迭代能力", "市场时机"],
                    "action_plan": "1)建立用户反馈机制\n2)技术债务管控\n3)数据埋点体系"
                },
                {
                    "name": "打磨品质",
                    "description": "聚焦核心功能打磨，追求极致用户体验，建立口碑壁垒。",
                    "probability_base": 0.30,
                    "key_factors": ["竞品动态", "用户期望", "资源投入度"],
                    "action_plan": "1)核心功能体验优化\n2)性能提升专项\n3)用户口碑监测"
                },
                {
                    "name": "战略合作",
                    "description": "寻找互补的合作伙伴，整合资源扩大影响力。",
                    "probability_base": 0.30,
                    "key_factors": ["合作方质量", "利益分配", "执行效率"],
                    "action_plan": "1)明确合作目标\n2)设计互利机制\n3)建立沟通机制"
                }
            ],
            "职业发展": [
                {
                    "name": "激进跳槽",
                    "description": "主动出击争取30%以上薪资涨幅，选择更有发展空间的机会。",
                    "probability_base": 0.35 if risk_level != "low" else 0.20,
                    "key_factors": ["市场行情", "个人竞争力", "谈判能力"],
                    "action_plan": "1)更新简历突出成绩\n2)研究目标公司\n3)模拟面试练习"
                },
                {
                    "name": "稳中求进",
                    "description": "在现有岗位深耕，等待内部晋升或转岗机会。",
                    "probability_base": 0.40 if risk_level != "high" else 0.35,
                    "key_factors": ["公司发展", "领导认可", "团队氛围"],
                    "action_plan": "1)主动承担重要项目\n2)建立可见成绩\n3)维护关键关系"
                },
                {
                    "name": "技能转型",
                    "description": "系统学习新技能，为转型做准备，可能需要6-12个月过渡期。",
                    "probability_base": 0.25,
                    "key_factors": ["学习效率", "行业趋势", "机会成本"],
                    "action_plan": "1)明确目标技能\n2)制定学习计划\n3)寻找实践机会"
                }
            ],
            "医疗健康": [
                {
                    "name": "深耕细分",
                    "description": "聚焦专科领域，建立专业壁垒，服务好存量客户。",
                    "probability_base": 0.40,
                    "key_factors": ["专业深度", "患者口碑", "复诊率"],
                    "action_plan": "1)提升诊疗服务质量\n2)建立患者随访体系\n3)积累临床数据"
                },
                {
                    "name": "模式创新",
                    "description": "结合互联网手段创新服务模式，降本增效。",
                    "probability_base": 0.35,
                    "key_factors": ["技术创新", "运营效率", "政策兼容"],
                    "action_plan": "1)探索线上服务模式\n2)优化服务流程\n3)控制运营成本"
                },
                {
                    "name": "整合扩张",
                    "description": "通过并购或合作整合上下游资源，扩大规模。",
                    "probability_base": 0.25,
                    "key_factors": ["资金储备", "整合能力", "标的质量"],
                    "action_plan": "1)寻找合适标的\n2)评估协同效应\n3)制定整合计划"
                }
            ],
            "教育培训": [
                {
                    "name": "精品路线",
                    "description": "聚焦高端市场，注重教学质量和口碑，打造品牌。",
                    "probability_base": 0.40,
                    "key_factors": ["教学质量", "师资水平", "学员口碑"],
                    "action_plan": "1)严格筛选师资\n2)打磨课程内容\n3)建立学员成功案例"
                },
                {
                    "name": "规模扩张",
                    "description": "标准化课程体系，快速复制扩大规模，薄利多销。",
                    "probability_base": 0.35,
                    "key_factors": ["标准化能力", "获客效率", "运营成本"],
                    "action_plan": "1)建立标准化课件\n2)优化获客渠道\n3)控制运营成本"
                },
                {
                    "name": "平台转型",
                    "description": "搭建教育平台，引入第三方机构和讲师，轻资产运营。",
                    "probability_base": 0.25,
                    "key_factors": ["流量获取", "平台体验", "讲师资源"],
                    "action_plan": "1)获取精准流量\n2)设计平台机制\n3)招募优质讲师"
                }
            ],
            "制造业": [
                {
                    "name": "精益优化",
                    "description": "持续改进生产流程，消除浪费，提升效率。",
                    "probability_base": 0.40,
                    "key_factors": ["流程优化", "员工参与", "持续改进"],
                    "action_plan": "1)识别浪费环节\n2)实施改善项目\n3)标准化最佳实践"
                },
                {
                    "name": "技术升级",
                    "description": "引入自动化设备和系统，提升生产效率和品质。",
                    "probability_base": 0.35,
                    "key_factors": ["投资规模", "技术选型", "人员培训"],
                    "action_plan": "1)评估技术方案\n2)分阶段实施\n3)培训操作人员"
                },
                {
                    "name": "服务转型",
                    "description": "从单纯制造商向整体解决方案服务商转型。",
                    "probability_base": 0.25,
                    "key_factors": ["服务能力", "客户关系", "解决方案设计"],
                    "action_plan": "1)识别高价值客户\n2)设计解决方案\n3)建立服务团队"
                }
            ]
        }

        # 如果有预定义模板，使用模板；否则使用通用情景
        if industry in base_scenarios:
            scenarios = base_scenarios[industry]
        else:
            scenarios = self._generate_generic_scenarios(query, answers, risk_level)

        for s in scenarios:
            s["adjusted_probability"] = s["probability_base"]

        return scenarios

    def _generate_generic_scenarios(
        self,
        query: str,
        answers: Dict[str, str],
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """为新领域生成通用情景模板"""
        return [
            {
                "name": "稳妥推进",
                "description": "在现有条件下逐步推进，控制风险，稳扎稳打，边做边调整。",
                "probability_base": 0.40 if risk_level != "high" else 0.25,
                "key_factors": ["资源配置", "执行能力", "环境变化"],
                "action_plan": "1)明确阶段性目标\n2)配置合适资源\n3)建立检查机制\n4)及时复盘调整"
            },
            {
                "name": "积极探索",
                "description": "主动寻找机会和资源，快速试错，快速迭代，保持灵活性。",
                "probability_base": 0.35 if risk_level != "low" else 0.25,
                "key_factors": ["机会识别", "资源获取", "迭代速度"],
                "action_plan": "1)快速验证假设\n2)小步快跑\n3)及时总结经验\n4)适时调整方向"
            },
            {
                "name": "借力合作",
                "description": "寻找合作伙伴分担风险，整合资源弥补短板，共赢思维。",
                "probability_base": 0.25,
                "key_factors": ["合作伙伴选择", "利益分配", "执行协调"],
                "action_plan": "1)明确合作目标\n2)筛选合适伙伴\n3)设计共赢机制\n4)建立沟通机制"
            }
        ]

    def calculate_probabilities(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        计算各情景的概率分布
        """
        if not scenarios:
            return {}

        base_total = sum(s.get("adjusted_probability", 0) for s in scenarios)
        result = {}
        for s in scenarios:
            prob = s.get("adjusted_probability", 0) / base_total if base_total > 0 else 1.0 / len(scenarios)
            result[s["name"]] = round(prob, 2)

        total_rounded = sum(result.values())
        if abs(total_rounded - 1.0) > 0.001:
            max_name = max(result, key=result.get)
            result[max_name] = round(result[max_name] + (1.0 - total_rounded), 2)

        return result

    def _analyze_risk(self, answers: Dict[str, str]) -> str:
        answer_text = " ".join(answers.values()).lower()

        risk_keywords_high = ["高", "激进", "大胆", "承受", "50%", "全仓", "积极", "转型", "扩张", "快速发展"]
        risk_keywords_low = ["保守", "稳健", "谨慎", "低", "20%", "少量", "观望", "维持", "稳定", "慢慢来"]

        high_score = sum(1 for kw in risk_keywords_high if kw in answer_text)
        low_score = sum(1 for kw in risk_keywords_low if kw in answer_text)

        if high_score > low_score:
            return "high"
        elif low_score > high_score:
            return "low"
        return "medium"