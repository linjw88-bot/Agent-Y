"""
Agent Y 核心引擎
借鉴顶级案例思维，通过搜集权威知识、分析未来情景，输出胜率最高的一步。

特点：
- 动态领域识别：根据用户问题自动识别或建议领域
- 知识库扩展：用户问题可触发新领域创建
- LLM增强：可选的LLM分析，无LLM时使用规则引擎
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Industry, KnowledgeEntry, AnalysisMethod
from app.core.scenario import ScenarioEngine
from app.core.knowledge import KnowledgeBase
from app.core.llm_client import MiniMaxClient


# 默认领域关键词（可被用户问题触发扩展）
DEFAULT_DOMAINS = {
    "互联网产品": [
        "产品", "用户", "增长", "DAU", "MAU", "留存", "转化率",
        "A/B测试", "MVP", "产品经理", "需求", "功能", "迭代",
        "用户体验", "UI", "UX", "用户研究", "数据分析", "日活",
        "月活", "拉新", "促活", "变现", "商业模式", "用户增长", "运营", "活跃", "付费", "会员", "订阅"
    ],
    "职业发展": [
        "职业", "工作", "辞职", "跳槽", "加薪", "晋升", "技能",
        "简历", "面试", "职场", "管理层", "创业", "转行",
        "行业选择", "个人发展", "职业规划", "人脉", "offer",
        "工资", "年薪", "绩效", "KPI", "求职", "招聘"
    ],
    "医疗健康": [
        "医疗", "健康", "医院", "医生", "药品", "器械", "投资",
        "创业", "保险", "政策", "互联网医疗", "AI诊断", "仿制药",
        "集采", "医改", "健康管理", "辅助生殖", "齿科", "眼科",
        "中医", "疫苗", "CRO", "CMO", "IVD", "手术机器人",
        "诊所", "药店", "体检", "慢病管理", "创新药"
    ],
    "教育培训": [
        "教育", "培训", "课程", "学习", "K12", "职业教育", "在线教育",
        "EdTech", "教学", "学生", "老师", "家长", "STEAM",
        "编程", "留学", "考试", "教师", "考研", "考公",
        "技能培训", "企业培训", "知识付费", "教研", "双减",
        "早教", "幼教", "素质", "营地", "留学中介"
    ],
    "制造业": [
        "制造", "工厂", "生产", "供应链", "精益生产", "工业4.0",
        "智能制造", "采购", "库存", "产能", "自动化", "MES",
        "工艺", "设备", "工人", "原材料", "供应商", "质量管理",
        "ERP", "Toyota", "TOC", "OEE", "数字化", "转型",
        "产线", "良率", "交付", "仓储", "物流"
    ]
}

# 各领域需要的关键信息
DOMAIN_REQUIRED_INFO = {
    "互联网产品": [
        "产品目前处于什么阶段？（概念期/原型期/成长期/成熟期）",
        "目标用户群体是谁？",
        "目前面临的核心问题是什么？",
        "您期望的衡量指标是什么？"
    ],
    "职业发展": [
        "您目前的工作年限？",
        "您最看重的职业要素是什么？（薪资/成长/稳定/兴趣）",
        "您的核心竞争力或专业领域是什么？",
        "您对下一份工作的期望是什么？"
    ],
    "医疗健康": [
        "您关注的是哪个细分方向？（投资/创业/职业选择）",
        "您对目标细分行业有多少了解？（1=不了解/5=非常了解）",
        "您目前拥有哪些相关资源？（资金/人脉/行业经验）",
        "您期望的回报周期是多久？"
    ],
    "教育培训": [
        "您关注的是哪个教育赛道？（K12/职业教育/素质教育/企业培训）",
        "您的目标用户群体是谁？（B端/C端/G端）",
        "您的核心竞争力是什么？（内容/师资/渠道/技术）",
        "您期望的盈利模式是什么？（学费/会员/解决方案）"
    ],
    "制造业": [
        "您关注的是制造业哪个环节？（研发/生产/供应链/销售）",
        "您的目标市场是哪个领域？（汽车/电子/医药/消费品/工业）",
        "您目前处于什么发展阶段？（初创/扩张/成熟/转型）",
        "您最关注的核心痛点是什么？（效率/成本/质量/交付）"
    ]
}


class AgentY:
    """Agent Y 核心引擎"""

    def __init__(self):
        self.scenario_engine = ScenarioEngine()
        self.knowledge_base = KnowledgeBase()
        self.llm = MiniMaxClient()

    async def analyze_query(
        self,
        query: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        分析问询的第一步：
        1. 识别或建议领域
        2. 判断是否需要补充信息
        3. 返回初步分析结果

        如果用户问题不属于现有领域，系统会建议一个新领域
        """
        # 从数据库获取已有领域
        result = await db.execute(select(Industry))
        existing_industries = {ind.name: ind.id for ind in result.scalars().all()}

        # 尝试识别领域
        identified_id, identified_name, confidence = await self._identify_domain(
            query, existing_industries
        )

        # 如果无法识别，尝试用LLM建议新领域
        suggested_domain = None
        if identified_id is None and self.llm.is_enabled():
            suggested_domain = await self._suggest_new_domain(query)
            if suggested_domain:
                identified_name = suggested_domain

        relevant_knowledge = []
        if identified_id:
            relevant_knowledge = await self.knowledge_base.retrieve(
                query=query,
                industry_id=identified_id,
                db=db,
                limit=3
            )

        knowledge_sufficient = len(relevant_knowledge) >= 3 and confidence >= 0.65

        if knowledge_sufficient:
            required_info = await self._generate_minimal_questions(
                query=query,
                industry_name=identified_name,
                relevant_knowledge=relevant_knowledge,
                db=db,
                count=1,
            )
            can_proceed = False
        else:
            can_proceed = False
            required_info = await self._generate_dynamic_questions(
                query=query,
                industry_name=identified_name,
                relevant_knowledge=relevant_knowledge,
                db=db
            )

        return {
            "industry_id": identified_id,
            "industry_name": identified_name,
            "confidence": confidence,
            "can_proceed": can_proceed,
            "required_info": required_info,
            "relevant_knowledge": relevant_knowledge,
            "suggested_domain": suggested_domain  # 如果识别不到，LLM建议的新领域
        }

    async def full_analysis(
        self,
        query: str,
        answers: Dict[str, str],
        industry_id: Optional[int],
        industry_name: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        完整分析：
        1. 整合问询和补充信息
        2. 检索相关知识
        3. 生成情景分析
        4. 计算胜率
        5. 输出推荐行动
        """
        # 如果是新建的领域（industry_id为空），创建新领域记录
        if industry_id is None and industry_name and industry_name != "待确认":
            industry_id = await self._create_new_domain(industry_name, db)

        relevant_knowledge = []
        if industry_id:
            relevant_knowledge = await self.knowledge_base.retrieve(
                query=query + " " + " ".join(answers.values()),
                industry_id=industry_id,
                db=db,
                limit=5
            )

        analysis_methods = []
        if industry_id:
            result = await db.execute(
                select(AnalysisMethod).where(
                    AnalysisMethod.industry_id == industry_id
                )
            )
            analysis_methods = result.scalars().all()

        scenarios = await self._generate_dynamic_scenarios(
            query=query,
            answers=answers,
            industry_name=industry_name,
            knowledge=relevant_knowledge,
            db=db
        )

        probability_distribution = self.scenario_engine.calculate_probabilities(scenarios)

        recommended_action = self._generate_recommendation(
            scenarios=scenarios,
            probabilities=probability_distribution,
            knowledge=relevant_knowledge
        )

        indicators = self._generate_indicators(
            industry=industry_name,
            scenarios=scenarios,
            answers=answers
        )

        llm_analysis = ""
        llm_available = self.llm.is_enabled()
        if llm_available:
            llm_analysis = await self._generate_llm_analysis(
                query=query,
                answers=answers,
                industry=industry_name,
                knowledge=relevant_knowledge,
                scenarios=scenarios,
                probabilities=probability_distribution
            )
            if not llm_analysis:
                llm_available = False

        depth_analysis = self._generate_depth_analysis(
            query=query,
            answers=answers,
            industry=industry_name,
            knowledge=relevant_knowledge
        )

        return {
            "industry_id": industry_id,
            "industry_name": industry_name,
            "confidence": 0.7,
            "present_situation": depth_analysis["situation_analysis"],
            "transformation": depth_analysis["transformation_analysis"],
            "future_possibility": depth_analysis["future_analysis"],
            "probability_distribution": probability_distribution,
            "recommended_action": recommended_action,
            "leading_indicators": indicators["leading_indicators"],
            "contingency_triggers": indicators["contingency_triggers"],
            "llm_analysis": llm_analysis,
            "llm_available": llm_available,
            "depth_analysis": depth_analysis,
            "knowledge_context": relevant_knowledge[:5],
            "scenarios_detail": scenarios
        }

    async def _identify_domain(
        self,
        query: str,
        existing_industries: Dict[str, int]
    ) -> tuple:
        """识别领域 - 先用关键词匹配，再用LLM辅助"""
        query_lower = query.lower()
        scores = {}

        # 用默认关键词匹配
        for industry, keywords in DEFAULT_DOMAINS.items():
            if industry in existing_industries:
                score = sum(1 for kw in keywords if kw.lower() in query_lower)
                scores[industry] = score

        # 如果有匹配，返回结果
        if scores and max(scores.values()) > 0:
            best_industry = max(scores.items(), key=lambda x: x[1])
            industry_name = best_industry[0]
            score = best_industry[1]
            confidence = min(0.3 + score * 0.15, 0.95)
            return (existing_industries[industry_name], industry_name, confidence)

        # 尝试从数据库已有领域关键词匹配
        if existing_industries:
            for name, ind_id in existing_industries.items():
                result = await self.knowledge_base.search_by_industry(name, ind_id)
                # 简单关键词匹配
                keywords = [k.lower() for k in result.get("keywords", [])] if result else []
                if keywords:
                    score = sum(1 for kw in keywords if kw in query_lower)
                    scores[name] = score

        if scores and max(scores.values()) > 0:
            best_industry = max(scores.items(), key=lambda x: x[1])
            industry_name = best_industry[0]
            score = best_industry[1]
            confidence = min(0.3 + score * 0.15, 0.95)
            return (existing_industries[industry_name], industry_name, confidence)

        # 无法识别，返回待确认
        return (None, "待确认", 0.3)

    async def _suggest_new_domain(self, query: str) -> Optional[str]:
        """使用LLM从用户问题中提取/建议一个新领域"""
        if not self.llm.is_enabled():
            return None

        prompt = f"""用户的问题：{query}

请分析这个问题属于哪个领域或行业？
只输出领域名称（2-6个字），例如：新能源、房产、电商、法律、医疗、餐饮、旅游等。
如果问题太通用或跨多个领域，返回"综合"。

只输出领域名称，不要任何其他文字。"""

        try:
            result = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是一个领域分类专家，善于从用户问题中提取核心领域。严格按要求输出。",
                timeout=10
            )
            if result:
                domain = result.strip().split('\n')[0][:6]
                if domain and domain != "待确认" and domain != "综合":
                    return domain
        except Exception as e:
            print(f"Domain suggestion error: {e}")

        return None

    async def _create_new_domain(self, domain_name: str, db: AsyncSession) -> int:
        """在数据库中创建新领域"""
        try:
            # 检查是否已存在
            result = await db.execute(
                select(Industry).where(Industry.name == domain_name)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing.id

            # 创建新领域
            stmt = insert(Industry).values(
                name=domain_name,
                description=f"用户问题自动创建的领域：{domain_name}",
                keywords=[]
            )
            await db.execute(stmt)
            await db.commit()

            # 获取新创建的行业ID
            result = await db.execute(
                select(Industry).where(Industry.name == domain_name)
            )
            new_industry = result.scalar_one()
            return new_industry.id
        except Exception as e:
            print(f"Create new domain error: {e}")
            await db.rollback()
            return None

    async def _generate_llm_analysis(
        self,
        query: str,
        answers: Dict[str, str],
        industry: str,
        knowledge: List[Dict],
        scenarios: List[Dict],
        probabilities: Dict[str, float]
    ) -> str:
        if not self.llm.is_enabled():
            return ""

        if knowledge:
            knowledge_items = []
            for k in knowledge[:5]:
                content = (k.get("detail_content") or k.get("content", ""))[:1200]
                if len(k.get("detail_content") or k.get("content", "")) > 1200:
                    content += "…"
                knowledge_items.append(f"《{k['title']}》：{content}")
            knowledge_text = "\n\n".join(knowledge_items)
        else:
            knowledge_text = "（暂无相关专业知识储备，以下基于通用分析）"

        scenario_items = []
        for s in scenarios[:3]:
            pct = probabilities.get(s["name"], 0)
            scenario_items.append(f"- {s['name']}（约{int(pct*100)}%概率）：{s['description']}")
        scenarios_text = "\n".join(scenario_items)

        if answers:
            answer_summary = "；".join([v for v in answers.values() if v.strip()])
        else:
            answer_summary = "（用户未补充额外背景信息）"

        prompt = f"""你是一个说人话的顶级顾问，不是写报告的分析师。

用户的问题：{query}

用户的具体情况：{answer_summary}

这是一个{industry}领域的问题。

【专业知识参考】
{knowledge_text}

【情景推演】
{scenarios_text}

---

请写一段300-500字的深度分析，要求：

1. 开头直接说结论：面对这个问题，我该怎么办（比如"可以尝试，但建议分步来"）
2. 中间解释为什么这样建议，结合专业知识（引用知识条目的名字）
3. 结合用户的具体情况，而不是泛泛而谈
4. 说清楚可能的坑是什么（比如"现在入场风险比较大，因为…"）
5. 结尾给1-2条最实在的下一步行动

要求：
- 用自然段落，不要编号列表、不要表格、不要加粗标题
- 说人话，避免空洞的商业套话
- 专业名词第一次出现时简单解释一下
- 控制篇幅在400字以内

直接输出分析正文，不要任何前缀说明。"""

        try:
            result = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是一个说人话的战略顾问，对完全不懂互联网/职业的小白用户说话。真诚、直接、接地气；专业概念第一次出现要解释；不说空话套话。擅长把复杂的事情用简单的道理讲清楚。"
            )
            return result if result else ""
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return ""

    async def _generate_dynamic_questions(
        self,
        query: str,
        industry_name: str,
        relevant_knowledge: List[Dict],
        db: AsyncSession
    ) -> List[str]:
        if not self.llm.is_enabled():
            return self._get_required_questions(industry_name)

        knowledge_text = "\n".join([
            f"- {k['title']}: {k['content'][:80]}"
            for k in relevant_knowledge[:3]
        ]) if relevant_knowledge else "（知识库暂无相关内容，需通过追问补充）"

        prompt = f"""用户问题：{query}
所属领域：{industry_name}

知识库已有参考：
{knowledge_text}

请根据上述信息，生成2-4个针对性的追问，帮助深入了解用户决策背景。

要求：
- 问题必须与用户具体情境强相关，不能是通用问题
- 每个问题不超过30字
- 直接返回问题列表，每行一个问题，不要编号，不要加引号，不要加任何格式符号"""

        try:
            result = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是一位专业的战略决策顾问，擅长通过追问厘清决策背景。严格按要求输出：每行一个纯问题，不要有任何其他文字。"
            )
            questions = [q.strip().lstrip("0123456789.、：: ") for q in result.split("\n") if q.strip()]
            questions = [q for q in questions if len(q) >= 5 and len(q) <= 40]
            if questions:
                return questions[:4]
        except Exception as e:
            print(f"Dynamic question generation error: {e}")

        return self._get_required_questions(industry_name)

    async def _generate_minimal_questions(
        self,
        query: str,
        industry_name: str,
        relevant_knowledge: List[Dict],
        db: AsyncSession,
        count: int = 1,
    ) -> List[str]:
        if not self.llm.is_enabled():
            return self._get_required_questions(industry_name)[:count]

        PERSONALIZATION_TEMPLATES = {
            "互联网产品": [
                "您的产品目前月活跃用户规模是多少？",
                "您的团队目前有多少人？",
            ],
            "职业发展": [
                "您目前的工作年限有多长？",
                "您最看重职业发展的哪个维度（薪资/成长/稳定性）？",
            ],
            "医疗健康": [
                "您目前面临的核心挑战是什么？",
                "您有多少资源可以投入？",
            ],
            "教育培训": [
                "您的目标用户群体是谁？",
                "您目前有多少资源可以投入？",
            ],
            "制造业": [
                "您公司目前的年营收规模是多少？",
                "您面临的供应链挑战主要在哪个环节？",
            ],
        }

        industry_questions = PERSONALIZATION_TEMPLATES.get(industry_name, [])

        prompt = f"""用户问题：{query}
领域：{industry_name}
已有知识覆盖：{len(relevant_knowledge)}条

请从以下候选问题中选择或改写{count}个最适合此问题的个性化追问。
候选问题：{'; '.join(industry_questions)}

要求：每个问题不超过25字，直接返回{count}个问题，每行一个，不要任何格式符号。"""

        try:
            result = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是一位专业的战略决策顾问。严格按要求输出：每行一个纯问题，不要有任何其他文字。"
            )
            questions = [q.strip().lstrip("0123456789.、：: ") for q in result.split("\n") if q.strip()]
            questions = [q for q in questions if len(q) >= 5]
            if questions:
                return questions[:count]
        except Exception as e:
            print(f"Minimal question generation error: {e}")

        fallback = {
            "互联网产品": "您的产品当前处于什么发展阶段？",
            "职业发展": "您目前职业发展的最大诉求是什么？",
            "医疗健康": "您目前面临的核心挑战是什么？",
            "教育培训": "您的目标用户群体是谁？",
            "制造业": "您公司目前的主要产品是什么？",
        }
        fallback_q = fallback.get(industry_name, "您目前的具体情况是怎样的？")
        return [fallback_q]

    def _get_required_questions(self, industry_name: str) -> List[str]:
        return DOMAIN_REQUIRED_INFO.get(industry_name, [])

    async def _generate_dynamic_scenarios(
        self,
        query: str,
        answers: Dict[str, str],
        industry_name: str,
        knowledge: List[Dict],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        if not self.llm.is_enabled():
            return self.scenario_engine.generate_scenarios(query, industry_name, answers, knowledge)

        knowledge_text = "\n".join([
            f"- {k['title']}: {k['content'][:150]}"
            for k in knowledge[:3]
        ]) if knowledge else "（暂无相关知识库内容）"

        answer_text = "\n".join([f"- {v}" for v in answers.values()]) if answers else "（用户未补充）"

        prompt = f"""用户决策问题：{query}
用户背景信息：
{answer_text}
所属领域：{industry_name}
相关知识：
{knowledge_text}

请基于以上信息，生成3个具体情景（高/中/低概率），每个情景包含：
- name: 情景名称（2-4字，简洁有力）
- description: 具体描述（60字以内，结合用户实际问题，不要说套话）
- probability_base: 基础概率（参考值：高0.45，中0.35，低0.20，总和1.0）

输出格式：严格JSON数组，不要包含任何其他文字，不要markdown代码块。
示例：[{{"name":"积极配置","description":"...","probability_base":0.45}}]"""

        try:
            result = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="你是一位专业的战略决策分析师，擅长情景规划。严格按JSON格式输出，不要包含任何其他文字。确保JSON数组有3个元素，每个元素有name、description、probability_base字段。"
            )
            import json
            scenarios = json.loads(result.strip())
            for s in scenarios:
                s["key_factors"] = []
                s["adjusted_probability"] = s.get("probability_base", 0.33)
                s["action_plan"] = "1)明确目标\n2)制定计划\n3)执行复盘"
            return scenarios[:3]
        except Exception as e:
            print(f"Dynamic scenario generation error: {e}")

        return self.scenario_engine.generate_scenarios(query, industry_name, answers, knowledge)

    def _generate_depth_analysis(
        self,
        query: str,
        answers: Dict[str, str],
        industry: str,
        knowledge: List[Dict]
    ) -> Dict[str, str]:
        depth_templates = {
            "互联网产品": {
                "situation": """
【产品现状诊断】

{answer_analysis}

【行业趋势】
- 用户注意力稀缺，内容质量成为核心竞争力
- 变现效率比用户规模更重要
- 私域流量价值凸显

【关键挑战】
- 获客成本持续上升
- 用户留存普遍低于行业均值
- 差异化竞争门槛提高
                """,
                "transformation": "建议聚焦核心指标，快速验证假设，数据驱动迭代。",
                "future": """
【增长路径推演】

路径A（大概率35%）：留存优先
- 聚焦核心功能打磨，提升用户价值
- 稳扎稳打，口碑驱动增长
- 适合资源有限的团队

路径B（中概率40%）：快速验证
- 通过A/B测试持续优化
- 小步快跑，快速迭代
- 数据驱动决策

路径C（小概率25%）：战略合作
- 寻找互补伙伴，资源整合
- 借力实现快速增长
- 需要谨慎选择合作方
                """
            },
            "职业发展": {
                "situation": """
【职业现状评估】

{answer_analysis}

【市场机会】
- 技术人才需求依然旺盛
- 管理岗竞争加剧
- 新兴领域存在溢价机会

【竞争力分析】
- 专业技能是核心竞争力
- 软技能决定晋升天花板
- 人脉质量影响机会获取
                """,
                "transformation": "建议根据市场情况灵活调整策略，在稳定中寻求突破。",
                "future": """
【职业路径推演】

路径A（大概率35%）：深耕现有
- 在当前领域持续积累
- 等待晋升或内部转岗机会
- 稳扎稳打，风险较低

路径B（中概率40%）：主动出击
- 关注市场机会，积极面试
- 跳槽争取30%+涨幅
- 需要充分准备

路径C（小概率25%）：转型探索
- 学习新技能拓宽边界
- 为长期发展布局
- 短期可能有阵痛
                """
            },
            "医疗健康": {
                "situation": """
【行业现状诊断】

{answer_analysis}

【市场机会】
- 老龄化带来医疗需求持续增长
- 政策支持创新医疗发展
- 消费升级推动高端医疗需求

【关键挑战】
- 监管政策的不确定性
- 研发周期长、投入大
- 市场竞争日趋激烈
                """,
                "transformation": "建议聚焦差异化竞争优势，在细分领域建立壁垒。",
                "future": """
【发展路径推演】

路径A（大概率35%）：深耕细分
- 在垂直领域建立专业壁垒
- 服务好存量客户
- 稳健发展

路径B（中概率40%）：模式创新
- 结合技术手段创新服务模式
- 降本增效提升竞争力
- 快速复制扩大规模

路径C（小概率25%）：整合并购
- 通过并购整合上下游资源
- 快速弥补能力短板
- 实现跨越式发展
                """
            },
            "教育培训": {
                "situation": """
【行业现状诊断】

{answer_analysis}

【市场机会】
- 终身学习趋势明显
- 职业教育受政策支持
- 教育科技快速发展

【关键挑战】
- 获客成本持续上升
- 内容同质化严重
- 师资和教学质量难以保证
                """,
                "transformation": "建议聚焦核心用户群体，建立差异化竞争优势。",
                "future": """
【发展路径推演】

路径A（大概率35%）：精品路线
- 聚焦高端市场
- 注重教学质量和口碑
- 单价高、学员少但忠诚

路径B（中概率40%）：规模扩张
- 标准化的课程体系
- 快速复制扩大规模
- 薄利多销

路径C（小概率25%）：平台化转型
- 搭建教育平台
- 引入第三方机构和讲师
- 轻资产运营
                """
            },
            "制造业": {
                "situation": """
【行业现状诊断】

{answer_analysis}

【市场趋势】
- 智能制造成为转型升级方向
- 供应链韧性日益重要
- 绿色制造是大势所趋

【关键挑战】
- 人工成本持续上升
- 原材料价格波动
- 环保要求越来越严格
                """,
                "transformation": "建议推进精益生产和数字化转型，提升运营效率。",
                "future": """
【发展路径推演】

路径A（大概率35%）：精益优化
- 持续改进生产流程
- 消除浪费提升效率
- 稳扎稳打

路径B（中概率40%）：技术升级
- 引入自动化设备和系统
- 提升生产效率和品质
- 中期投入较大

路径C（小概率25%）：转型服务
- 从制造商向服务商转型
- 提供整体解决方案
- 重塑商业模式
                """
            }
        }

        # 通用模板（当领域不在预设中时使用）
        generic_template = {
            "situation": """
【现状分析】

{answer_analysis}

【关键考虑因素】
- 用户需求的本质是什么
- 当前资源和能力匹配度
- 市场环境和竞争态势

【主要挑战】
- 信息不完整带来的风险
- 执行过程中的不确定性
- 外部环境变化的影响
                """,
            "transformation": "建议深入了解领域特点，结合自身情况制定稳妥策略。",
            "future": """
【路径推演】

路径A（大概率35%）：稳妥推进
- 在现有条件下逐步推进
- 控制风险，稳扎稳打
- 边做边调整

路径B（中概率40%）：积极探索
- 主动寻找机会和资源
- 快速试错，快速迭代
- 保持灵活性

路径C（小概率25%）：战略合作
- 寻找合作伙伴分担风险
- 整合资源弥补短板
- 共赢思维
                """
        }

        answer_parts = []
        for key, value in answers.items():
            answer_parts.append(f"- {value}")
        answer_analysis = "\n".join(answer_parts) if answer_parts else "待补充更多信息"

        template = depth_templates.get(industry, generic_template)

        return {
            "situation_analysis": template["situation"].format(answer_analysis=answer_analysis),
            "transformation_analysis": template["transformation"],
            "future_analysis": template["future"]
        }

    def _generate_recommendation(
        self,
        scenarios: List[Dict[str, Any]],
        probabilities: Dict[str, float],
        knowledge: List[Dict]
    ) -> str:
        best_scenario = max(probabilities.items(), key=lambda x: x[1])
        best_name = best_scenario[0]

        scenario_detail = next(
            (s for s in scenarios if s["name"] == best_name),
            scenarios[0]
        )

        recommendation = f"""## 推荐方案：{best_name}

**胜率评估：{int(probabilities[best_name] * 100)}%**

### 方案详情
{scenario_detail['description']}

### 行动计划
{scenario_detail.get('action_plan', '按步骤执行')}

### 关键成功因素
{', '.join(scenario_detail.get('key_factors', []))}

### 参考知识
{chr(10).join([f"- {k['title']}" for k in knowledge[:3]]) if knowledge else '- 建议深入学习相关领域知识'}
"""

        return recommendation

    def _generate_indicators(
        self,
        industry: str,
        scenarios: List[Dict[str, Any]],
        answers: Dict[str, str]
    ) -> Dict[str, List]:
        base_indicators = {
            "互联网产品": {
                "leading": [
                    {"name": "用户留存曲线", "description": "次日/7日/30日留存率", "threshold": "任一指标低于行业均值20%"},
                    {"name": "核心功能使用率", "description": "功能打开频次和使用深度", "threshold": "持续下降超过2周"},
                    {"name": "用户反馈情绪", "description": "好评率、吐槽关键词变化", "threshold": "负面情绪上升超过20%"},
                    {"name": "竞品动态", "description": "主要竞品的版本更新和运营活动", "threshold": "竞品获得高口碑"}
                ],
                "triggers": [
                    {"condition": "DAU连续下降超过30%", "action": "紧急排查原因，召开产品会议", "priority": "high"},
                    {"condition": "竞品发布重大功能", "action": "48小时内评估影响，调整roadmap", "priority": "high"},
                    {"condition": "技术故障影响核心功能", "action": "立即修复，透明沟通用户", "priority": "high"},
                    {"condition": "核心指标持续低迷超过1个月", "action": "考虑战略转型或收缩", "priority": "medium"}
                ]
            },
            "职业发展": {
                "leading": [
                    {"name": "市场招聘活跃度", "description": "目标岗位的职位数量变化", "threshold": "职位数环比增长20%+"},
                    {"name": "个人技能市场价值", "description": "招聘网站的技能需求热度", "threshold": "相关技能需求持续上升"},
                    {"name": "内推机会密度", "description": "人脉推荐的工作机会", "threshold": "连续2个月无机会"},
                    {"name": "面试通过率", "description": "投递简历的面试邀请比例", "threshold": "低于10%需调整策略"}
                ],
                "triggers": [
                    {"condition": "收到满意的offer", "action": "3天内给出回复，推进流程", "priority": "high"},
                    {"condition": "公司出现重大变化（裁员/换帅）", "action": "立即启动求职计划", "priority": "high"},
                    {"condition": "薪资倒挂严重", "action": "评估内部调薪可能性或外部机会", "priority": "medium"},
                    {"condition": "技能学习遇到瓶颈超过3个月", "action": "调整学习方向或寻求指导", "priority": "medium"}
                ]
            },
            "医疗健康": {
                "leading": [
                    {"name": "政策动向", "description": "医改政策、医保谈判结果", "threshold": "重大政策变化"},
                    {"name": "竞品研发进度", "description": "同类产品临床进展", "threshold": "竞品获批进度超预期"},
                    {"name": "市场需求变化", "description": "目标患者群体规模", "threshold": "市场规模显著变化"},
                    {"name": "资本投入热度", "description": "行业融资金额和轮次", "threshold": "头部基金加速布局"}
                ],
                "triggers": [
                    {"condition": "竞争对手获批上市", "action": "评估差异化竞争力，调整策略", "priority": "high"},
                    {"condition": "集采价格大幅下降", "action": "评估成本控制和规模化能力", "priority": "high"},
                    {"condition": "核心团队关键人员离职", "action": "评估团队稳定性", "priority": "high"},
                    {"condition": "临床数据显著低于预期", "action": "重新评估产品价值", "priority": "medium"}
                ]
            },
            "教育培训": {
                "leading": [
                    {"name": "政策变化", "description": "教育改革政策、监管要求", "threshold": "重大政策调整"},
                    {"name": "竞争格局", "description": "主要竞品的市场动作", "threshold": "竞品获得大额融资"},
                    {"name": "用户反馈", "description": "课程评价、完课率", "threshold": "满意度持续下降"},
                    {"name": "获客成本", "description": "单个线索成本", "threshold": "连续上升超过30%"}
                ],
                "triggers": [
                    {"condition": "政策禁止相关业务", "action": "立即调整业务方向", "priority": "high"},
                    {"condition": "头部竞品推出同类爆款课程", "action": "48小时内评估影响", "priority": "high"},
                    {"condition": "师资大面积流失", "action": "立即启动应急预案", "priority": "high"},
                    {"condition": "现金流持续紧张超过3个月", "action": "评估转型或收缩", "priority": "medium"}
                ]
            },
            "制造业": {
                "leading": [
                    {"name": "订单情况", "description": "新增订单和交付周期", "threshold": "订单连续下降超过20%"},
                    {"name": "原材料价格", "description": "主要原材料成本变化", "threshold": "波动超过15%"},
                    {"name": "设备利用率", "description": "产线利用率和良率", "threshold": "持续低于80%"},
                    {"name": "员工流失率", "description": "关键岗位离职率", "threshold": "显著上升"}
                ],
                "triggers": [
                    {"condition": "大客户订单丢失", "action": "立即分析原因，修复关系", "priority": "high"},
                    {"condition": "关键原材料供应中断", "action": "启动备选供应商", "priority": "high"},
                    {"condition": "环保处罚或限产", "action": "立即整改，确保合规", "priority": "high"},
                    {"condition": "核心技术人员批量离职", "action": "评估人才保留策略", "priority": "medium"}
                ]
            }
        }

        # 通用指标（领域不在预设中时使用）
        generic_indicators = {
            "leading": [
                {"name": "关键进展指标", "description": "项目/业务的核心里程碑", "threshold": "进度显著落后"},
                {"name": "用户/客户反馈", "description": "需求满足程度", "threshold": "负面反馈上升"},
                {"name": "资源消耗速度", "description": "资金/人力的使用效率", "threshold": "消耗超预期"},
                {"name": "外部环境变化", "description": "政策、市场、竞争态势", "threshold": "重大变化出现"}
            ],
            "triggers": [
                {"condition": "核心假设被证伪", "action": "重新评估方案可行性", "priority": "high"},
                {"condition": "关键资源到位失败", "action": "调整计划或寻找替代", "priority": "high"},
                {"condition": "外部环境重大变化", "action": "及时调整策略", "priority": "high"},
                {"condition": "阶段性目标未达成", "action": "复盘原因，决定是否继续", "priority": "medium"}
            ]
        }

        indicators = base_indicators.get(industry, generic_indicators)

        return {
            "leading_indicators": indicators["leading"],
            "contingency_triggers": indicators["triggers"]
        }