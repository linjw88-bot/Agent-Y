-- 行业表
CREATE TABLE IF NOT EXISTS industries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    keywords JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识条目表
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    tags JSON,
    source VARCHAR(255),
    source_url VARCHAR(512),
    source_type VARCHAR(50),
    relevance_score FLOAT DEFAULT 0.5,
    summary TEXT,
    detail_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id)
);

-- 分析方法表
CREATE TABLE IF NOT EXISTS analysis_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    steps JSON,
    when_to_use TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id)
);

-- 对话历史表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    user_query TEXT NOT NULL,
    identified_industry_id INTEGER,
    required_info JSON,
    user_answers JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (identified_industry_id) REFERENCES industries(id)
);

-- 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    industry_name VARCHAR(100),
    confidence FLOAT,
    present_situation TEXT,
    transformation TEXT,
    future_possibility TEXT,
    probability_distribution JSON,
    recommended_action TEXT,
    leading_indicators JSON,
    contingency_triggers JSON,
    llm_analysis TEXT,
    knowledge_context JSON,
    depth_analysis JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- 反馈表
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_result_id INTEGER NOT NULL,
    is_helpful INTEGER,
    actual_outcome TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_result_id) REFERENCES analysis_results(id)
);