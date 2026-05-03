"""
初始化知识库数据
提供种子领域作为默认示例，系统支持用户问题自动扩展新领域
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import insert, select
from app.core.database import Base, engine, AsyncSessionLocal
from app.models.models import Industry, KnowledgeEntry, AnalysisMethod


# 种子领域 - 系统预设的默认领域
# 更多领域会根据用户问题自动创建
SEED_INDUSTRIES = [
    {
        "name": "互联网产品",
        "description": "互联网产品设计、运营、增长等领域",
        "keywords": ["产品", "用户", "增长", "DAU", "MAU", "留存", "转化率", "MVP"]
    },
    {
        "name": "职业发展",
        "description": "职业规划、求职跳槽、职场成长等领域",
        "keywords": ["职业", "工作", "辞职", "跳槽", "加薪", "晋升", "简历", "面试"]
    },
    {
        "name": "医疗健康",
        "description": "医疗健康投资、创业、职业选择等领域",
        "keywords": ["医疗", "健康", "医院", "创业", "投资", "保险", "器械"]
    },
    {
        "name": "教育培训",
        "description": "教育培训产品、运营、创业等领域",
        "keywords": ["教育", "培训", "课程", "学习", "K12", "职业教育", "在线教育"]
    },
    {
        "name": "制造业",
        "description": "制造业生产、供应链、管理等领域",
        "keywords": ["制造", "工厂", "生产", "供应链", "精益", "质量", "数字化"]
    }
]

# 各领域的核心知识
SEED_KNOWLEDGE = {
    "互联网产品": [
        {
            "title": "MVP方法论",
            "content": "最小可行产品(MVP)是精益创业的核心概念，指用最少功能满足早期用户核心需求，验证产品假设。开发MVP后根据用户反馈快速迭代，避免闭门造车。关键指标是用户参与度和留存。",
            "category": "framework",
            "tags": ["MVP", "精益创业", "快速验证"]
        },
        {
            "title": "AARRR增长模型",
            "content": "AARRR是硅谷常用的创业增长漏斗模型，包括获取(Acquisition)、激活(Activation)、留存(Retention)、收入(Revenue)、推荐(Referral)五个环节。评估时需要分析每个环节的转化率。",
            "category": "framework",
            "tags": ["AARRR", "增长模型", "用户获取"]
        },
        {
            "title": "RFM用户分层",
            "content": "RFM是一种常用的用户价值分层模型，根据最近一次消费(Recency)、消费频率(Frequency)、消费金额(Monetary)三个维度将用户分为8类。不同类型用户应采用不同运营策略。",
            "category": "methodology",
            "tags": ["RFM", "用户分层", "精准运营"]
        },
        {
            "title": "用户留存分析框架",
            "content": "留存是衡量产品是否真正满足用户需求的核心指标。分析留存需要关注：次日/7日/30日留存率、留存曲线形状。提升留存的策略包括：优化新用户引导、持续提供用户价值、构建用户习惯回路。",
            "category": "framework",
            "tags": ["留存", "用户粘性", "Cohort分析"]
        },
        {
            "title": "互联网产品商业化",
            "content": "互联网产品常见的商业化模式包括：广告、交易抽成、订阅制、增值服务、SaaS服务。选择商业模式需要考虑：产品类型、用户规模、用户付费意愿、竞争格局。",
            "category": "framework",
            "tags": ["商业化", "变现模式", "会员", "SaaS"]
        }
    ],
    "职业发展": [
        {
            "title": "SWOT职业分析",
            "content": "SWOT分析是职业规划中的经典工具：优势——个人专业技能、经验、资源；劣势——需要提升的能力、缺失的资质；机会——行业趋势、上升通道、新兴领域；威胁——竞争加剧、技术替代、职位缩减。",
            "category": "methodology",
            "tags": ["SWOT", "职业规划", "个人定位"]
        },
        {
            "title": "职业锚理论",
            "content": "职业锚是人在面临职业选择时不愿放弃的核心价值。8种职业锚包括：技术/职能型、管理型、自主/独立型、安全/稳定型、创业型、服务/奉献型、挑战型、生活方式型。了解自己的职业锚可以帮助选择适合的工作环境。",
            "category": "framework",
            "tags": ["职业锚", "职业发展", "职业定位"]
        },
        {
            "title": "简历撰写技巧",
            "content": "一份优秀的简历应该包含：清晰的标题和联系方式、与目标岗位匹配的技能描述、可量化的成果和贡献、合理的篇幅（1-2页）。优化简历的方法：使用STAR法则描述经历、量化工作成果、突出与目标岗位相关的经验。",
            "category": "methodology",
            "tags": ["简历", "求职", "STAR法则"]
        },
        {
            "title": "技术管理能力模型",
            "content": "从技术专家转型管理需要培养的能力包括：技术规划能力、团队管理能力、跨团队协作能力、业务理解能力。技术管理者的核心价值是通过团队拿结果，而非个人技术能力。",
            "category": "framework",
            "tags": ["技术管理", "团队领导", "管理技能"]
        },
        {
            "title": "面试准备清单",
            "content": "面试准备应该系统化：研究公司背景和岗位要求、准备STAR格式的项目案例、复习核心技术点和业务理解、准备针对面试官的个性化问题。多轮面试的侧重点不同：HR侧重沟通表达、业务负责人考察专业能力、高管考察文化和价值观匹配。",
            "category": "methodology",
            "tags": ["面试", "求职技巧", "行为面试"]
        }
    ],
    "医疗健康": [
        {
            "title": "医疗服务定位模型",
            "content": "医疗服务定位需要考虑三个维度：服务类型（诊疗、康复、预防）、服务层级（基层医疗、专科医院、综合医院）、目标人群。不同定位决定了资源配置、定价策略和获客方式。",
            "category": "framework",
            "tags": ["医疗定位", "服务类型", "目标人群"]
        },
        {
            "title": "医疗行业商业模式",
            "content": "医疗健康行业常见的商业模式包括：诊疗服务、检验检测、药品销售、器械耗材、互联网医疗、健康保险。不同模式的利润结构和增长逻辑不同，需要结合自身资源和市场竞争状况选择。",
            "category": "framework",
            "tags": ["商业模式", "医疗", "诊疗", "药品"]
        },
        {
            "title": "医疗行业竞争格局分析",
            "content": "医疗行业竞争分析需要关注：政策环境、细分市场集中度、主要竞争对手的优劣势、进入壁垒。公立医院在品牌和资源上有优势，民营机构需要在服务和效率上差异化。",
            "category": "methodology",
            "tags": ["竞争分析", "医疗市场", "公立医院"]
        },
        {
            "title": "医疗创业关键成功因素",
            "content": "医疗创业成功的关键因素包括：合规能力（资质、监管、风控）、医疗服务能力（质量、安全）、获客能力（口碑、渠道）、运营效率（成本控制、服务效率）。人才是医疗创业的核心瓶颈，尤其是优质医生资源。",
            "category": "methodology",
            "tags": ["创业", "医疗", "成功因素", "合规"]
        },
        {
            "title": "医疗行业投资逻辑",
            "content": "医疗行业投资关注的核心指标：市场规模、竞争格局、商业模式、政策风险。不同细分子行业的投资逻辑差异很大：创新药看研发管线和临床数据；医疗器械看技术壁垒和进口替代空间；医疗服务看运营效率和复制能力。",
            "category": "framework",
            "tags": ["投资", "医疗", "市场规模", "商业模式"]
        }
    ],
    "教育培训": [
        {
            "title": "教育产品设计框架",
            "content": "教育产品设计需要考虑：目标用户（年龄段、学习目的、付费意愿）、核心价值主张、课程体系、交付形式。好的教育产品需要平衡效果和体验，避免过度追求名师效应而忽视体系化，或过度追求规模而忽视教学质量。",
            "category": "framework",
            "tags": ["教育产品", "课程设计", "用户体验"]
        },
        {
            "title": "教育培训行业运营策略",
            "content": "教育培训行业的核心运营指标：获客成本（CAC）、转化率、续费率、转介绍率。降低获客成本的方法包括：口碑转介绍、内容营销、私域运营、异业合作。续费率是教育机构的核心竞争力。",
            "category": "methodology",
            "tags": ["运营策略", "获客成本", "续费率"]
        },
        {
            "title": "教育行业商业模式分析",
            "content": "教育培训行业的商业模式主要包括：线下培训、在线教育（订阅制、课时包）、平台型（佣金、广告）、内容付费。线下培训利润率较高但扩张慢；在线教育可规模化但获客成本高。",
            "category": "framework",
            "tags": ["商业模式", "在线教育", "平台", "内容付费"]
        },
        {
            "title": "教育行业竞争策略",
            "content": "教育行业的竞争策略选择：差异化（细分领域、特殊人群、特色内容）、成本领先（标准化、高效运营）、聚焦（特定年龄段、特定学科、特定地域）。K12培训竞争激烈；职业教育处于快速发展期；素质教育正在兴起。",
            "category": "methodology",
            "tags": ["竞争策略", "差异化", "K12", "职业教育"]
        },
        {
            "title": "在线教育关键指标体系",
            "content": "在线教育的核心指标：完课率（内容质量）、作业提交率（参与度）、续费率（用户满意度）、转介绍率（口碑）、毛利率（运营效率）。获客指标：CAC（获客成本）、LTV（用户生命周期价值）、ROI（投入产出比）。",
            "category": "framework",
            "tags": ["指标体系", "在线教育", "完课率", "续费", "LTV"]
        }
    ],
    "制造业": [
        {
            "title": "精益生产核心思想",
            "content": "精益生产（Lean Production）源于丰田生产方式，核心思想是消除浪费、持续改善。关键概念：增值活动（直接满足客户需求的活动）和非增值活动（不增加价值但目前不可避免的活动）。常见的浪费类型：过量生产、等待、搬运、加工本身、库存、动作、不良品。",
            "category": "framework",
            "tags": ["精益生产", "Toyota", "消除浪费", "持续改善"]
        },
        {
            "title": "供应链管理关键指标",
            "content": "供应链管理的核心指标：交付可靠性（及时交付率）、响应柔性（面对变化的调整速度）、成本效率（总拥有成本）、库存效率（周转率、呆滞率）。数字化是提升供应链效率的关键手段：实时数据、需求预测、智能补货可以显著降低库存和提升交付。",
            "category": "framework",
            "tags": ["供应链", "库存管理", "交付", "成本控制"]
        },
        {
            "title": "制造业数字化转型",
            "content": "制造业数字化转型通常分三个阶段：设备数字化（自动化设备联网）、生产数字化（MES系统、数据采集）、决策数字化（数据分析、智能决策）。数字化成功关键：明确的业务目标、高层支持、持续迭代。中小企业可以从轻量化工具开始，避免大而全的系统。",
            "category": "methodology",
            "tags": ["数字化转型", "智能制造", "MES", "工业4.0"]
        },
        {
            "title": "质量管理体系框架",
            "content": "质量管理体系的核心：质量策划（设定标准）、质量控制（过程监控）、质量改进（问题解决）。基础工具：PDCA循环（计划-执行-检查-改进）、5Why分析（根本原因）、SPC（统计过程控制）。质量成本包括：预防成本、鉴定成本、失败成本（返工、退货、投诉）。",
            "category": "framework",
            "tags": ["质量管理", "TQM", "PDCA", "质量成本"]
        },
        {
            "title": "制造业能力评估模型",
            "content": "制造业能力评估的维度：技术能力（工艺水平、设备精度、研发能力）、运营能力（交付、成本、质量）、组织能力（人才、管理、文化）、战略能力（市场洞察、业务选择、资源配置）。能力短板决定发展优先级，并购可以快速获取能力但整合风险大。",
            "category": "methodology",
            "tags": ["能力评估", "竞争力", "制造业", "战略"]
        }
    ]
}

# 各领域分析方法
SEED_ANALYSIS_METHODS = {
    "互联网产品": [
        {"name": "用户研究", "description": "通过数据分析、用户访谈等方式理解用户需求和行为", "steps": ["用户分群", "行为分析", "需求挖掘", "痛点识别"], "when_to_use": "产品规划初期"},
        {"name": "增长实验", "description": "通过A/B测试、数据分析驱动产品迭代优化", "steps": ["假设提出", "实验设计", "数据收集", "结论输出"], "when_to_use": "优化产品指标时"},
        {"name": "商业分析", "description": "分析产品商业模式、变现能力、单元经济", "steps": ["商业模式画布", "收入结构分析", "成本结构分析", "LTV/CAC计算"], "when_to_use": "评估产品商业化潜力时"}
    ],
    "职业发展": [
        {"name": "自我评估", "description": "通过技能盘点、价值澄清明确个人定位", "steps": ["技能盘点", "价值澄清", "职业锚定位", "发展路径规划"], "when_to_use": "职业迷茫期或转型期"},
        {"name": "市场机会分析", "description": "评估目标岗位的市场需求、竞争状况、发展前景", "steps": ["岗位研究", "竞争分析", "趋势判断", "机会匹配"], "when_to_use": "寻找新机会时"},
        {"name": "谈判策略", "description": "在薪资谈判、职位晋升中争取最优结果", "steps": ["市场调研", "筹码梳理", "策略制定", "谈判执行"], "when_to_use": "谈offer或晋升时"}
    ],
    "医疗健康": [
        {"name": "行业研究", "description": "分析医疗细分行业的市场规模、竞争格局、增长逻辑", "steps": ["市场测算", "竞争分析", "政策评估", "趋势判断"], "when_to_use": "投资或创业决策前"},
        {"name": "商业模式评估", "description": "评估医疗项目的商业模式、盈利能力和风险", "steps": ["模式分析", "成本测算", "风险评估", "投资回报"], "when_to_use": "评估医疗项目时"},
        {"name": "战略规划", "description": "制定医疗机构的战略定位和发展路径", "steps": ["定位选择", "能力评估", "路径规划", "资源匹配"], "when_to_use": "医疗机构发展规划时"}
    ],
    "教育培训": [
        {"name": "产品设计", "description": "设计教育产品的定位、体系和交付方式", "steps": ["用户研究", "价值主张", "课程设计", "交付方式"], "when_to_use": "开发新教育产品时"},
        {"name": "运营分析", "description": "分析教育机构的运营效率和提升空间", "steps": ["指标分析", "流程诊断", "改进方案", "效果评估"], "when_to_use": "提升运营效率时"},
        {"name": "市场进入", "description": "评估进入教育培训市场的机会和风险", "steps": ["市场分析", "竞争评估", "能力匹配", "风险控制"], "when_to_use": "进入新市场时"}
    ],
    "制造业": [
        {"name": "精益转型", "description": "评估制造业精益转型的基础和推进路径", "steps": ["现状诊断", "机会识别", "路径规划", "实施支持"], "when_to_use": "推进精益生产时"},
        {"name": "供应链优化", "description": "优化供应链的效率、韧性和成本", "steps": ["流程分析", "成本分析", "优化方案", "实施支持"], "when_to_use": "提升供应链能力时"},
        {"name": "数字化评估", "description": "评估制造业数字化成熟度和提升方向", "steps": ["现状评估", "差距分析", "路线规划", "实施支持"], "when_to_use": "规划数字化转型时"}
    ]
}


async def init_knowledge():
    """初始化知识库数据"""
    async with AsyncSessionLocal() as session:
        # 检查是否已有数据
        result = await session.execute(select(Industry))
        existing = result.scalars().all()
        if existing:
            print(f"知识库已有 {len(existing)} 个领域，跳过初始化")
            return

        # 插入种子领域
        for industry_data in SEED_INDUSTRIES:
            stmt = insert(Industry).values(**industry_data)
            await session.execute(stmt)

        await session.commit()
        print("种子领域初始化完成")

        # 插入知识条目
        for industry_name, knowledge_list in SEED_KNOWLEDGE.items():
            result = await session.execute(
                select(Industry).where(Industry.name == industry_name)
            )
            industry = result.scalar_one()

            for knowledge in knowledge_list:
                stmt = insert(KnowledgeEntry).values(
                    industry_id=industry.id,
                    **knowledge
                )
                await session.execute(stmt)

        print("知识条目初始化完成")

        # 插入分析方法
        for industry_name, methods in SEED_ANALYSIS_METHODS.items():
            result = await session.execute(
                select(Industry).where(Industry.name == industry_name)
            )
            industry = result.scalar_one()

            for method_data in methods:
                stmt = insert(AnalysisMethod).values(
                    industry_id=industry.id,
                    **method_data
                )
                await session.execute(stmt)

        await session.commit()
        print("知识库初始化完成！共初始化 {} 个领域".format(len(SEED_INDUSTRIES)))


if __name__ == "__main__":
    asyncio.run(init_knowledge())