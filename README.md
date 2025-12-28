# 🎓 Academic ChatBot - RAG

基于RAG（检索增强生成）技术的学术课程问答系统，可以智能地回答关于深度学习课程材料的问题。

## ✨ 功能特点

- 📖 **PDF文档处理**：自动读取和解析深度学习课程PDF
- 🔍 **智能检索**：使用向量数据库进行语义检索
- 💡 **AI问答**：基于OpenAI GPT-3.5生成准确答案
- 🎯 **可靠性**：仅基于课程材料回答，避免虚构信息
- 🖥️ **Web界面**：提供友好的Streamlit交互界面

## 🛠️ 技术栈

- **LLM**: OpenAI GPT-3.5-turbo
- **向量数据库**: Chroma
- **框架**: LangChain
- **前端**: Streamlit
- **文档处理**: PyPDF

## 📦 安装

1. **克隆仓库**
```bash
git clone https://github.com/JustinQY/academicChatBot-RAG.git
cd academicChatBot-RAG
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**

复制示例配置文件并填入你的API密钥：
```bash
cp config.example.json config.json
```

编辑 `config.json`：
```json
{
  "OpenAIAPIKey": "your-openai-api-key",
  "LangChainAPIKey": "your-langchain-api-key"
}
```

## 🚀 使用方法

### 方式1: Web界面（推荐）

运行Streamlit应用：
```bash
streamlit run app.py
```

然后在浏览器中访问 `http://localhost:8501`

### 方式2: Python脚本

直接运行原始脚本：
```bash
python academicChatBot.py
```

## 📁 项目结构

```
academicChatBot-RAG/
├── app.py                      # Streamlit Web应用
├── academicChatBot.py          # 原始Python脚本
├── requirements.txt            # 项目依赖
├── config.example.json         # 配置文件示例
├── config.json                 # API密钥配置（需自行创建）
└── CourseMaterials/
    └── deep_learning/          # 存放PDF课程材料
        └── *.pdf
```

## 💬 示例问题

- Can you list some of the hyperparameters in the FFN?
- What is backpropagation?
- Explain the concept of gradient descent
- How does the attention mechanism work?

## 🔧 工作原理

1. **文档加载**：从 `CourseMaterials/deep_learning` 目录读取PDF文档
2. **文本分割**：将文档分割成300个token的小块，重叠50个token
3. **向量化**：使用OpenAI Embeddings将文本转换为向量并存储在Chroma
4. **检索**：用户提问时，检索最相关的3个文本块
5. **生成答案**：将检索到的内容作为上下文，使用GPT-3.5生成答案

## ⚙️ 配置说明

### API密钥

- **OpenAI API Key**: 必需，用于文本嵌入和答案生成
- **LangChain API Key**: 可选，用于追踪和调试

### 文档要求

- 支持PDF格式
- 建议文件大小不超过50MB
- 放置在 `CourseMaterials/deep_learning/` 目录下

### 参数调整

在 `app.py` 或 `academicChatBot.py` 中可以调整：

- `chunk_size`: 文本分割大小（默认300）
- `chunk_overlap`: 文本重叠大小（默认50）
- `k`: 检索文档数量（默认3）
- `temperature`: LLM温度参数（默认0，更保守）

## 📝 注意事项

- ⚠️ 首次运行会进行文档向量化，可能需要几分钟
- ⚠️ 确保有足够的OpenAI API配额
- ⚠️ `config.json` 包含敏感信息，不要提交到Git
- 💡 Streamlit会缓存向量数据库，后续使用更快

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 License

MIT License

## 👤 作者

JustinQY

---

**Powered by LangChain 🦜🔗 & OpenAI 🤖 & Streamlit 🎈**

