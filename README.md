# Java Development Agent

一個由 GPT-OSS-20B LLM 和 Neo4j 知識圖譜驅動的 Java 代碼開發助手。

## 功能特點

🚀 **智能代碼生成**
- 基於自然語言描述生成高質量 Java 代碼
- 上下文感知的代碼生成，利用知識圖譜中的相關信息
- 支持類、方法、接口等各種 Java 結構

📊 **項目分析**
- 解析整個 Java 項目並提取結構信息
- 在 Neo4j 中構建代碼知識圖譜
- 識別類之間的依賴關係和繼承層次

🔍 **代碼改進建議**
- 分析現有代碼並提供改進建議
- 識別潛在的 bug 和性能問題
- 推薦設計模式和最佳實踐

💬 **智能查詢**
- 自然語言查詢代碼庫
- 基於知識圖譜的語義搜索
- 智能問答系統

## 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Java Parser    │    │    Neo4j DB     │
│ (Natural Lang.) │◄──►│   (javalang)    │◄──►│ (Knowledge      │
└─────────────────┘    └─────────────────┘    │  Graph)         │
         │                       │             └─────────────────┘
         ▼                       ▼                       ▲
┌─────────────────┐    ┌─────────────────┐              │
│ Java Dev Agent  │◄──►│   GPT-OSS-20B   │              │
│   (Main Logic)  │    │     (LLM)       │              │
└─────────────────┘    └─────────────────┘              │
         │                                               │
         ▼                                               │
┌─────────────────┐                                     │
│   FastAPI Web   │                                     │
│   Interface     │◄────────────────────────────────────┘
└─────────────────┘
```

## 安裝和設置

### 1. 系統要求

- Python 3.8+
- Neo4j 5.0+
- Java 11+ (用於解析 Java 代碼)
- GPU 推薦 (用於運行 GPT-OSS-20B)

### 2. 安裝依賴

```bash
# 克隆項目
git clone <repository-url>
cd rag-oss20b

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 3. 設置 Neo4j

```bash
# 使用 Docker 運行 Neo4j
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

或者下載並安裝 Neo4j Desktop: https://neo4j.com/download/

### 4. 配置環境變量

```bash
# 複製環境變量模板
cp .env.example .env

# 編輯 .env 文件
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# GPT-OSS-20B 模型配置
MODEL_PATH=/path/to/gpt-oss-20b/model
# 或者使用 API
API_KEY=your_api_key_here
```

### 5. 下載 GPT-OSS-20B 模型

```bash
# 如果使用本地模型
# 將模型路徑配置到 config.py 中
# MODEL_PATH = "/path/to/gpt-oss-20b"

# 如果使用 Hugging Face
# 模型會自動下載到緩存目錄
```

## 使用方法

### 1. 命令行界面

```bash
# 啟動交互模式（默認）
python main.py

# 運行示例
python main.py examples

# 啟動 Web API 服務器
python main.py api

# 顯示幫助
python main.py help
```

### 2. 交互模式

```
javagen> status          # 顯示系統狀態
javagen> analyze         # 分析 Java 項目
javagen> generate        # 生成 Java 代碼
javagen> improve         # 代碼改進建議
javagen> query           # 查詢代碼庫
javagen> help            # 顯示幫助
javagen> quit            # 退出
```

### 3. Web API 接口

啟動 API 服務器：
```bash
python api.py
# 或者
python main.py api
```

API 文檔：http://localhost:8000/docs

#### 主要 API 端點

- `GET /status` - 獲取系統狀態
- `POST /analyze` - 分析 Java 項目
- `POST /generate` - 生成 Java 代碼
- `POST /improve` - 代碼改進建議
- `POST /query` - 查詢代碼庫

#### 示例請求

```bash
# 代碼生成
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "request": "創建一個帶有增刪改查操作的 User 類",
       "context": {"package": "com.example.user"}
     }'

# 項目分析
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"project_path": "/path/to/java/project"}'
```

### 4. Python API

```python
from java_agent import agent

# 初始化代理
agent.initialize()

# 分析 Java 項目
result = agent.analyze_project("/path/to/project")

# 生成代碼
code = agent.generate_code(
    "創建一個計算器類",
    context={"package": "com.example"}
)

# 代碼改進建議
suggestions = agent.suggest_improvements(java_code)

# 查詢代碼庫
answer = agent.query_codebase("TestClass 有哪些方法？")
```

## 配置選項

### config.py 主要配置

```python
class Settings:
    # Neo4j 配置
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"  
    neo4j_password: str = "password"
    
    # GPT-OSS-20B 配置
    model_name: str = "gpt-oss-20b"
    model_path: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # 代理配置
    max_context_length: int = 4096
    code_analysis_depth: int = 3
```

## 示例用法

### 1. 項目分析示例

```python
# 分析整個 Java 項目
result = agent.analyze_project("/path/to/spring-boot-project")
print(f"發現 {result['parsing_stats']['classes_found']} 個類")
```

### 2. 代碼生成示例

```python
# 生成帶上下文的代碼
request = "為 UserService 創建一個 REST 控制器"
context = {
    "class_name": "UserService",
    "package": "com.example.service"
}
result = agent.generate_code(request, context)
print(result['generated_code'])
```

### 3. 代碼查詢示例

```python
# 查詢代碼結構
queries = [
    "UserController 類有哪些端點？",
    "哪些類實現了 UserRepository 接口？",
    "找出所有使用 @Service 注解的類"
]

for query in queries:
    result = agent.query_codebase(query)
    print(f"查詢: {query}")
    print(f"回答: {result['llm_response']}")
```

## 知識圖譜結構

Neo4j 中的數據模型：

```cypher
// 節點類型
(:Class {name, package, modifiers, extends, implements})
(:Method {name, returnType, parameters, modifiers})  
(:Interface {name, package, extends})
(:Package {name})

// 關係類型
(:Class)-[:HAS_METHOD]->(:Method)
(:Class)-[:DEPENDS_ON]->(:Class)
(:Class)-[:IMPLEMENTS]->(:Interface)
(:Class)-[:EXTENDS]->(:Class)
(:Class)-[:IN_PACKAGE]->(:Package)
```

## 性能優化

### 1. 模型優化

```python
# 使用量化模型減少內存使用
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_8bit=True  # 8位量化
)
```

### 2. 數據庫優化

```cypher
// 創建索引提高查詢性能
CREATE INDEX class_name_idx FOR (c:Class) ON (c.name);
CREATE INDEX method_name_idx FOR (m:Method) ON (m.name);
CREATE INDEX package_name_idx FOR (p:Package) ON (p.name);
```

### 3. 緩存優化

```python
# 緩存常用的代碼分析結果
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_code_cached(code_hash):
    return llm_client.analyze_code(code)
```

## 故障排除

### 常見問題

**1. Neo4j 連接失敗**
```bash
# 檢查 Neo4j 是否運行
docker ps | grep neo4j
# 或者
systemctl status neo4j
```

**2. 模型加載失敗**  
```python
# 檢查模型路徑和權限
import os
print(os.path.exists(MODEL_PATH))
print(os.access(MODEL_PATH, os.R_OK))
```

**3. 內存不足**
```python
# 使用更小的批次大小
settings.max_context_length = 2048
settings.max_tokens = 512
```

### 日誌調試

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看詳細日誌
agent.initialize()
```

## 開發和擴展

### 添加新的代碼分析器

```python
class CustomJavaAnalyzer:
    def analyze_design_patterns(self, code):
        # 實現設計模式識別
        pass
    
    def analyze_security_issues(self, code):
        # 實現安全問題檢測  
        pass
```

### 擴展知識圖譜

```cypher
// 添加新的節點和關係類型
CREATE (:Annotation {name: "Service", target: "class"})
CREATE (:DesignPattern {name: "Singleton", description: "..."})

(:Class)-[:USES_ANNOTATION]->(:Annotation)
(:Class)-[:IMPLEMENTS_PATTERN]->(:DesignPattern)
```

## 貢獻指南

1. Fork 項目
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打開 Pull Request

## 許可證

該項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 支持和聯繫

- 問題報告: [GitHub Issues](https://github.com/your-repo/issues)
- 文檔: [Wiki](https://github.com/your-repo/wiki)
- 郵箱: your-email@example.com

## 致謝

- [GPT-OSS-20B](https://github.com/model-repo) - 強大的開源語言模型
- [Neo4j](https://neo4j.com/) - 圖數據庫
- [javalang](https://github.com/c2nes/javalang) - Java 代碼解析器
- [FastAPI](https://fastapi.tiangolo.com/) - 現代 Web 框架