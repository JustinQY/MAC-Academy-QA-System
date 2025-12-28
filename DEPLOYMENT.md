# 🚀 部署指南

本指南介绍如何将 Academic ChatBot 部署到 Streamlit Cloud。

## 📋 前置要求

- GitHub 账号
- OpenAI API Key
- (可选) LangChain API Key

## 🔐 安全配置 API Keys

本项目支持三种方式配置 API Keys，按优先级排序：

### 1️⃣ Streamlit Secrets（推荐用于生产环境）✅

**优点：**
- 🔒 完全安全，不会泄露到代码仓库
- ☁️ Streamlit Cloud 原生支持
- 🔄 易于更新和管理

**本地开发配置：**

1. 创建 `.streamlit` 目录（如果不存在）：
```bash
mkdir -p .streamlit
```

2. 创建 `.streamlit/secrets.toml` 文件：
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

3. 编辑 `.streamlit/secrets.toml`，填入你的 API Keys：
```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key"
LANGCHAIN_API_KEY = "lsv2_pt_your-actual-langchain-api-key"
```

**Streamlit Cloud 部署配置：**

1. 在 [Streamlit Cloud](https://streamlit.io/cloud) 创建应用
2. 连接到你的 GitHub 仓库
3. 在应用设置中找到 **Secrets** 选项
4. 粘贴以下内容：
```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key"
LANGCHAIN_API_KEY = "lsv2_pt_your-actual-langchain-api-key"
```
5. 点击保存

### 2️⃣ 环境变量

**适用于：** 服务器部署、Docker、CI/CD

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-api-key"
export LANGCHAIN_API_KEY="lsv2_pt_your-api-key"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-api-key"
$env:LANGCHAIN_API_KEY="lsv2_pt-your-api-key"

# Windows CMD
set OPENAI_API_KEY=sk-your-api-key
set LANGCHAIN_API_KEY=lsv2_pt-your-api-key
```

### 3️⃣ config.json（仅用于本地开发）

**⚠️ 注意：** 此方法不安全，不要提交到 Git！

创建 `config.json`：
```json
{
  "OpenAIAPIKey": "sk-your-api-key",
  "LangChainAPIKey": "lsv2_pt-your-api-key"
}
```

`config.json` 已被添加到 `.gitignore`，不会被提交。

## 📦 部署到 Streamlit Cloud

### 步骤 1：准备代码

1. 确保所有代码已提交到 GitHub
2. 确保 `requirements.txt` 包含所有依赖
3. **不要提交** `config.json` 或 `.streamlit/secrets.toml`

### 步骤 2：创建应用

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 点击 **"New app"**
3. 选择你的 GitHub 仓库
4. 设置：
   - **Repository:** `你的用户名/academicChatBot-RAG`
   - **Branch:** `main`
   - **Main file path:** `app.py`

### 步骤 3：配置 Secrets

1. 在应用设置页面找到 **"Secrets"** 选项
2. 粘贴你的 API Keys：
```toml
OPENAI_API_KEY = "sk-xxxxx"
LANGCHAIN_API_KEY = "lsv2_pt_xxxxx"
```
3. 点击 **"Save"**

### 步骤 4：部署

1. 点击 **"Deploy!"**
2. 等待几分钟，应用会自动构建和部署
3. 部署成功后，你会获得一个公开的 URL

## 🔧 环境变量说明

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `OPENAI_API_KEY` | ✅ 是 | OpenAI API 密钥，用于文本嵌入和生成 |
| `LANGCHAIN_API_KEY` | ❌ 否 | LangChain API 密钥，用于 LangSmith 追踪和调试 |

## 🎯 最佳实践

### ✅ 推荐做法

- ✅ 使用 Streamlit Secrets 或环境变量
- ✅ 将 `config.json` 和 `.streamlit/secrets.toml` 添加到 `.gitignore`
- ✅ 定期轮换 API Keys
- ✅ 使用不同的 Keys 用于开发和生产环境
- ✅ 限制 API Keys 的权限范围

### ❌ 避免做法

- ❌ 不要在代码中硬编码 API Keys
- ❌ 不要将 `config.json` 提交到 Git
- ❌ 不要在公开的 GitHub Issues 中分享 Keys
- ❌ 不要使用截图分享包含 Keys 的配置

## 🐛 故障排除

### 问题：应用启动失败

**解决方案：**
1. 检查 Streamlit Cloud 的日志
2. 确认 Secrets 格式正确（TOML 格式）
3. 确认 API Keys 有效且有足够的配额

### 问题：找不到 API Key

**解决方案：**
1. 检查 Secrets 中的变量名是否正确（区分大小写）
2. 确认已保存 Secrets 配置
3. 尝试重启应用

### 问题：LangSmith 追踪不工作

**解决方案：**
1. 确认 `LANGCHAIN_API_KEY` 已配置
2. 检查 API Key 是否有效
3. LangSmith 是可选功能，不影响核心功能

## 📱 本地测试部署配置

在部署前，建议先在本地测试 Secrets 配置：

```bash
# 1. 创建 .streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 2. 编辑并填入你的 Keys
nano .streamlit/secrets.toml

# 3. 运行应用
streamlit run app.py

# 4. 确认应用正常工作
```

## 🔗 有用的链接

- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets 管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [LangSmith 文档](https://docs.smith.langchain.com/)

## 💡 提示

- 部署后，你可以在 Streamlit Cloud 仪表板中查看应用日志和指标
- 可以设置自定义域名
- 可以通过 GitHub 推送代码自动触发重新部署
- Streamlit Cloud 免费版有资源限制，注意监控使用情况

---

**需要帮助？** 查看 [Streamlit Community Forum](https://discuss.streamlit.io/) 或提交 Issue！

