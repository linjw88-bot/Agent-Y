# Agent Y - 顶级案例决策系统

基于顶级案例思维的决策辅助系统。用户描述问题 → 系统识别领域 → 检索知识库 → 生成情景推演 → 输出胜率最高的行动方案。

## 核心思路

```
用户问题 → 领域识别 → 知识检索 → 多情景推演 → 胜率分析 → 决策推荐

不追求完美方案，只推荐当前胜率最高的一步
```

## 特点

- **动态扩展**：预设5个种子领域，用户问题可触发创建新领域
- **知识库自增长**：随使用不断补充
- **LLM驱动**：基于大语言模型的智能分析和推理能力

## 快速启动

```bash
# 后端
cd backend
pip install -r requirements.txt
cd ../database/seed_data && python seed_db.py && cd ../../backend
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

访问：http://localhost:3000

## 技术栈

- **前端**：React 18, TypeScript, TailwindCSS
- **后端**：Python, FastAPI, SQLAlchemy
- **数据库**：SQLite

## 测试

```bash
# 后端
python3 -m pytest backend/tests/ -v

# 前端
cd frontend && npm test -- --run
```

---

MIT License