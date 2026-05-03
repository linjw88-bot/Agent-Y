"""
Backend 基本验证测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports:
    """验证核心模块可以正常导入"""

    def test_import_agent(self):
        from app.core.agent import AgentY
        assert AgentY is not None

    def test_import_scenario(self):
        from app.core.scenario import ScenarioEngine
        assert ScenarioEngine is not None

    def test_import_knowledge(self):
        from app.core.knowledge import KnowledgeBase
        assert KnowledgeBase is not None

    def test_import_llm_client(self):
        from app.core.llm_client import MiniMaxClient
        assert MiniMaxClient is not None

    def test_import_models(self):
        from app.models.models import Industry, KnowledgeEntry, Conversation
        assert Industry is not None
        assert KnowledgeEntry is not None
        assert Conversation is not None

    def test_import_schemas(self):
        from app.schemas.schemas import ConsultationRequest, AnalysisResultResponse
        assert ConsultationRequest is not None
        assert AnalysisResultResponse is not None


class TestAgentY:
    """测试 AgentY 引擎"""

    def test_agent_init(self):
        from app.core.agent import AgentY
        agent = AgentY()
        assert agent is not None
        assert hasattr(agent, 'scenario_engine')
        assert hasattr(agent, 'knowledge_base')
        assert hasattr(agent, 'llm')

    def test_agent_has_identify_method(self):
        from app.core.agent import AgentY
        import asyncio
        agent = AgentY()
        assert hasattr(agent, '_identify_domain')
        assert asyncio.iscoroutinefunction(agent._identify_domain)

    def test_agent_has_suggest_new_domain_method(self):
        from app.core.agent import AgentY
        import asyncio
        agent = AgentY()
        assert hasattr(agent, '_suggest_new_domain')
        assert asyncio.iscoroutinefunction(agent._suggest_new_domain)


class TestScenarioEngine:
    """测试情景引擎"""

    def test_scenario_init(self):
        from app.core.scenario import ScenarioEngine
        engine = ScenarioEngine()
        assert engine is not None

    def test_generate_scenarios_career(self):
        from app.core.scenario import ScenarioEngine
        engine = ScenarioEngine()

        scenarios = engine.generate_scenarios(
            query="职业发展问题",
            industry="职业发展",
            answers={"风险偏好": "稳健"},
            knowledge=[]
        )

        assert len(scenarios) == 3
        names = [s["name"] for s in scenarios]
        assert "稳妥推进" not in names

    def test_generate_scenarios_unknown(self):
        from app.core.scenario import ScenarioEngine
        engine = ScenarioEngine()

        scenarios = engine.generate_scenarios(
            query="奶茶店创业",
            industry="餐饮",
            answers={},
            knowledge=[]
        )

        assert len(scenarios) == 3
        names = [s["name"] for s in scenarios]
        assert "稳妥推进" in names

    def test_calculate_probabilities(self):
        from app.core.scenario import ScenarioEngine
        engine = ScenarioEngine()

        scenarios = [
            {"name": "A", "adjusted_probability": 0.4},
            {"name": "B", "adjusted_probability": 0.35},
            {"name": "C", "adjusted_probability": 0.25},
        ]

        result = engine.calculate_probabilities(scenarios)
        assert abs(sum(result.values()) - 1.0) < 0.01


class TestMiniMaxClient:
    """测试 LLM 客户端"""

    def test_client_init(self):
        from app.core.llm_client import MiniMaxClient
        client = MiniMaxClient()
        assert client is not None

    def test_is_enabled_returns_bool(self):
        from app.core.llm_client import MiniMaxClient
        client = MiniMaxClient()
        result = client.is_enabled()
        assert isinstance(result, bool)


class TestSchemas:
    """测试 Pydantic schemas"""

    def test_consultation_request(self):
        from app.schemas.schemas import ConsultationRequest
        req = ConsultationRequest(query="测试问题", session_id="test-123")
        assert req.query == "测试问题"
        assert req.session_id == "test-123"

    def test_required_info_request(self):
        from app.schemas.schemas import RequiredInfoRequest
        req = RequiredInfoRequest(
            conversation_id=1,
            answers={"Q1": "答案1", "Q2": "答案2"}
        )
        assert req.conversation_id == 1
        assert len(req.answers) == 2