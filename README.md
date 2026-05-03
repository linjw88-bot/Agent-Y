# Agent Y - 顶级案例决策系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18-green.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.109-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 项目简介

Agent Y 是一个基于顶级案例思维的决策辅助系统。通过系统化的知识检索、多情景推演和概率分析，帮助用户在复杂决策场景中找到最优行动方案。

### 核心理念

> **顶级案例思维**：借鉴同领域成功案例的经验，通过情景推演和概率分析，找到当前局面胜率最高的行动方案

### 核心特点

- **动态领域扩展**：系统预设5个种子领域，用户问题可触发自动创建新领域
- **知识库自增长**：根据用户问题，自动补充相关知识条目
- **LLM增强**：可选的LLM分析能力，无LLM时使用规则引擎

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 领域智能识别 | 自动识别问询所属领域 |
| 顶级知识库 | 多个领域的权威知识支撑 |
| 多情景推演 | 生成高/中/低概率情景进行分析 |
| 胜率量化 | 多情景概率加权分析 |
| 决策推荐 | 输出胜率最高的行动方案 |
| 预警信号 | 领先指标 + 应急触发器 |

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone <repository-url>
cd agent-yj-v2
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 初始化数据库
cd ../database/seed_data
python seed_db.py
cd ../../backend

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:3000
- API 文档: http://localhost:8000/docs

---

## 项目结构

```
agent-yj-v2/
├── docs/                    # 产品文档
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── pages/           # 页面
│   │   ├── services/        # API 调用
│   │   └── store/           # 状态管理
│   └── package.json
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心逻辑
│   │   │   ├── agent.py     # Agent Y 引擎
│   │   │   ├── scenario.py   # 情景分析引擎
│   │   │   └── knowledge.py # 知识库管理
│   │   ├── models/          # 数据模型
│   │   └── schemas/         # Pydantic schemas
│   └── requirements.txt
└── database/
    ├── schema.sql           # 数据库 Schema
    └── seed_data/            # 初始化数据
```

---

## 初始领域（种子）

系统预设5个种子领域作为默认知识库起点：

| 领域 | 知识条目数 | 核心内容 |
|------|-----------|---------|
| 互联网产品 | 5 | MVP方法、AARRR、RFM、用户留存 |
| 职业发展 | 5 | SWOT分析、职业锚、简历撰写、技术管理 |
| 医疗健康 | 5 | 市场分析、商业模式、竞争策略 |
| 教育培训 | 5 | 课程设计、教学方法、运营策略 |
| 制造业 | 5 | 精益生产、供应链管理、质量控制 |

**动态扩展**：用户提问时，如果问题不属于预设领域，系统会自动识别并建议新领域，同时创建对应的知识库记录。系统会随着使用不断扩展领域覆盖。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, TypeScript, TailwindCSS, Zustand |
| 后端 | Python, FastAPI, SQLAlchemy, Pydantic |
| 数据库 | SQLite (可升级 PostgreSQL) |
| 构建 | Vite, Uvicorn |

---

## 📝 License

MIT License - 详见 [LICENSE](LICENSE) 文件