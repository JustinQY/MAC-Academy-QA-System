"""
学术聊天机器人 - 主应用
支持基础课程材料问答 + 用户文档上传
"""

import streamlit as st
import os
import json
from datetime import datetime
from document_manager import DocumentManager
from rag_system import DualVectorStoreRAG
from utils import format_file_size, get_directory_size, safe_remove_file

# 页面配置
st.set_page_config(
    page_title="学术聊天机器人", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 学术课程问答助手")
st.markdown("基于深度学习课程材料的RAG问答系统 + 支持自定义文档上传")


# ==================== 配置加载 ====================
@st.cache_resource
def load_config():
    """
    配置加载优先级：
    1. Streamlit Secrets（推荐用于部署）
    2. 环境变量
    3. config.json 文件（本地开发）
    """
    # 获取 OpenAI API Key
    openai_key = None
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        openai_key = st.secrets['OPENAI_API_KEY']
        source = "Streamlit Secrets"
    elif 'OPENAI_API_KEY' in os.environ:
        openai_key = os.environ['OPENAI_API_KEY']
        source = "Environment Variable"
    else:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            openai_key = config.get("OpenAIAPIKey")
            source = "config.json"
        except FileNotFoundError:
            pass
    
    if not openai_key:
        st.error("""
        ❌ 未找到 OpenAI API Key！
        
        请通过以下任一方式配置：
        
        **1. Streamlit Cloud 部署（推荐）：**
        - 在 Streamlit Cloud 设置中添加 Secrets
        - 格式: `OPENAI_API_KEY = "your-key-here"`
        
        **2. 本地环境变量：**
        ```bash
        export OPENAI_API_KEY="your-key-here"
        ```
        
        **3. 本地 config.json 文件：**
        ```json
        {
          "OpenAIAPIKey": "your-key-here"
        }
        ```
        """)
        st.stop()
    
    # 设置 OpenAI API Key
    os.environ['OPENAI_API_KEY'] = openai_key
    
    # 获取 LangChain API Key (可选)
    langchain_key = None
    if hasattr(st, 'secrets') and 'LANGCHAIN_API_KEY' in st.secrets:
        langchain_key = st.secrets['LANGCHAIN_API_KEY']
    elif 'LANGCHAIN_API_KEY' in os.environ:
        langchain_key = os.environ['LANGCHAIN_API_KEY']
    else:
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            langchain_key = config.get("LangChainAPIKey")
        except:
            pass
    
    # 配置 LangSmith 追踪（如果提供了 API Key）
    if langchain_key:
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
        os.environ['LANGCHAIN_API_KEY'] = langchain_key
    
    return {
        'source': source,
        'langsmith_enabled': bool(langchain_key)
    }


# ==================== 初始化 RAG 系统 ====================
@st.cache_resource
def initialize_rag_system():
    """初始化双向量库 RAG 系统（基础库缓存）"""
    rag = DualVectorStoreRAG()
    
    # 初始化基础向量库（缓存）
    with st.spinner("📚 正在初始化基础知识库..."):
        base_doc_count = rag.initialize_base_vectorstore()
    
    # 初始化用户向量库（不缓存，动态）
    rag.initialize_user_vectorstore()
    
    return rag, base_doc_count


# ==================== 初始化文档管理器 ====================
def get_document_manager():
    """获取文档管理器实例"""
    if 'doc_manager' not in st.session_state:
        st.session_state.doc_manager = DocumentManager()
    return st.session_state.doc_manager


# ==================== 主应用逻辑 ====================
def main():
    try:
        # 加载配置
        config = load_config()
        
        # 初始化 RAG 系统
        rag_system, base_doc_count = initialize_rag_system()
        st.success(f"✅ 系统已就绪！已加载 {base_doc_count} 个基础课程文档。")
        
        # 初始化文档管理器
        doc_manager = get_document_manager()
        
        # 初始化会话状态
        if 'qa_history' not in st.session_state:
            st.session_state.qa_history = []
        if 'show_doc_manager' not in st.session_state:
            st.session_state.show_doc_manager = False
        
        # ==================== 文档上传区域 ====================
        st.markdown("---")
        st.markdown("### 📎 上传自定义文档")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "上传 PDF 文档到知识库",
                type=['pdf'],
                help="支持 PDF 格式，单个文件最大 50MB",
                key="pdf_uploader"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # 对齐按钮
            if st.button("📚 管理已上传文档", use_container_width=True):
                st.session_state.show_doc_manager = not st.session_state.show_doc_manager
        
        # 处理文件上传
        if uploaded_file is not None:
            # 使用文件名和大小作为唯一标识，防止 st.rerun() 后重复处理
            file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
            
            # 检查是否已经处理过这个文件
            if 'last_processed_file' not in st.session_state:
                st.session_state.last_processed_file = None
                if 'last_upload_success' not in st.session_state:
                    st.session_state.last_upload_success = None

            
            # 检查是否是新文件或之前上传失败的文件
            is_new_file = st.session_state.last_processed_file != file_identifier
            is_failed_upload = (st.session_state.last_processed_file == file_identifier and 
                              st.session_state.last_upload_success == False)
            
            if is_new_file or is_failed_upload:
                # 标记为正在处理
                st.session_state.last_processed_file = file_identifier
                st.session_state.last_upload_success = None  # 重置状态
                
                with st.spinner("⏳ 正在处理文档..."):
                    # 阶段1: 上传和保存文件
                    with st.status("📥 正在上传文件...", expanded=True) as status:
                        st.write("验证文件格式和大小...")
                        success, message, metadata = doc_manager.upload_document(uploaded_file)
                        
                        if not success:
                            status.update(label="❌ 上传失败", state="error")
                            st.session_state.last_upload_success = False
                            st.error(message)
                        else:
                            st.write("✅ 文件保存成功")
                            
                            # 阶段2: 索引到向量库
                            st.write("🔢 正在向量化文档...")
                            index_success, index_message, chunk_count = rag_system.add_user_document(
                                file_path=metadata['filepath'],
                                original_filename=metadata['original_filename'],
                                upload_time=metadata['upload_time'],
                                file_size=metadata['size']
                            )
                            
                            if index_success:
                                # 索引成功，保存元数据到持久化存储
                                save_success, save_error = doc_manager.save_document_metadata(metadata)
                                
                                if save_success:
                                    status.update(label="✅ 文档处理完成", state="complete")
                                    st.success(f"🎉 {metadata['original_filename']} 已成功添加到知识库！")
                                    st.info(index_message)
                                    
                                    # 清空上传器（通过 rerun）
                                    st.session_state.last_upload_success = True
                                    
                                    st.rerun()
                                else:
                                    # 元数据保存失败（极少见）
                                    status.update(label="⚠️ 元数据保存失败", state="error")
                                    st.error(f"❌ {save_error}")
                                    st.warning("文档已索引但元数据未保存，可能导致重复上传检测失败")
                            else:
                                # 索引失败，清理已保存的文件
                                status.update(label="❌ 索引失败", state="error")
                                st.error(index_message)
                                st.warning("正在清理已保存的文件...")
                                
                                # 删除物理文件（不需要删除元数据，因为还没保存）
                                file_success, file_error = safe_remove_file(metadata['filepath'])
                                if file_success:
                                    st.info("✅ 已清理失败的上传")
                                else:
                                    st.warning(f"⚠️ 清理文件时出现问题：{file_error}")
                                
                                st.info("💡 提示：请检查文件是否损坏或网络连接是否正常，然后重试。")
        
        # ==================== 文档管理浮窗 ====================
        if st.session_state.show_doc_manager:
            with st.expander("📚 已上传文档管理", expanded=True):
                documents = doc_manager.list_documents()
                
                if not documents:
                    st.info("📭 还没有上传任何文档")
                else:
                    st.caption(f"共 {len(documents)} 个文档")
                    
                    for doc in documents:
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**📄 {doc['original_filename']}**")
                        
                        with col2:
                            st.text(f"📦 {doc['size_formatted']}")
                        
                        with col3:
                            st.text(f"🕐 {doc['upload_time']}")
                        
                        with col4:
                            if st.button("🗑️", key=f"del_{doc['file_id']}", help="删除文档"):
                                # 删除文件
                                file_success, file_message = doc_manager.delete_document(doc['file_id'])
                                
                                # 从向量库删除
                                vec_success, vec_message = rag_system.remove_user_document(
                                    doc['original_filename']
                                )
                                
                                if file_success:
                                    st.success(file_message)
                                    if vec_success:
                                        st.info(vec_message)
                                    else:
                                        st.warning(vec_message)
                                    st.rerun()
                                else:
                                    st.error(file_message)
                        
                        st.markdown("---")
        
        # ==================== 问答区域 ====================
        st.markdown("---")
        st.markdown("### 💬 提问")
        
        question = st.text_area(
            "请输入你的问题：",
            placeholder="例如: Can you list some of the hyperparameters in the FFN?",
            height=100,
            key="question_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            ask_button = st.button("🚀 提问", type="primary", use_container_width=True)
        with col2:
            if st.button("🗑️ 清除历史", use_container_width=True):
                st.session_state.qa_history = []
                st.rerun()
        
        if ask_button and question.strip():
            with st.spinner("🤔 正在思考中..."):
                try:
                    # 创建 RAG 链并查询
                    rag_chain = rag_system.create_rag_chain(k=3)
                    response = rag_chain.invoke(question)
                    
                    # 保存到历史记录
                    qa_entry = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'question': question.strip(),
                        'answer': response.content
                    }
                    st.session_state.qa_history.append(qa_entry)
                    
                    # 显示当前回答
                    st.markdown("### 📝 当前回答：")
                    st.info(response.content)
                    
                except Exception as e:
                    st.error(f"❌ 生成回答时出错：{str(e)}")
        
        elif ask_button:
            st.warning("⚠️ 请先输入问题")
        
        # ==================== 问答历史记录 ====================
        if st.session_state.qa_history:
            st.markdown("---")
            st.markdown("## 📚 问答历史记录")
            st.caption(f"共 {len(st.session_state.qa_history)} 条记录")
            
            # 逆序显示（最新的在上面）
            for idx, qa in enumerate(reversed(st.session_state.qa_history), 1):
                with st.expander(
                    f"🕐 {qa['timestamp']} - 问题 #{len(st.session_state.qa_history) - idx + 1}", 
                    expanded=(idx == 1)
                ):
                    st.markdown(f"**❓ 问题：**")
                    st.write(qa['question'])
                    st.markdown(f"**💡 回答：**")
                    st.info(qa['answer'])
        
        # ==================== 侧边栏 ====================
        with st.sidebar:
            st.header("📚 关于系统")
            st.markdown("""
            这是一个基于RAG（检索增强生成）的学术问答系统。
            
            **功能特点：**
            - 📖 自动读取深度学习课程PDF文档
            - 📎 **支持用户上传自定义PDF文档**
            - 🔍 智能检索相关内容片段
            - 💡 基于OpenAI GPT-3.5生成准确答案
            - ⚡ 使用LangChain构建RAG流程
            - 🎯 仅基于课程材料回答，避免虚构信息
            - 📝 自动保存问答历史记录
            - 🗂️ 文档来源标记（课程材料 vs 用户文档）
            
            **使用说明：**
            1. 上传你的 PDF 文档（可选）
            2. 在输入框中输入你的问题
            3. 点击"提问"按钮
            4. 等待系统检索并生成答案
            5. 历史记录会自动保存在下方
            6. 点击"管理已上传文档"查看和删除文档
            
            **示例问题：**
            - Can you list some of the hyperparameters in the FFN?
            - What is backpropagation?
            - Explain gradient descent
            """)
            
            st.divider()
            
            st.header("⚙️ 技术栈")
            st.markdown("""
            - **前端**: Streamlit
            - **LLM**: OpenAI GPT-3.5
            - **向量数据库**: Chroma (持久化)
            - **框架**: LangChain
            - **文档处理**: PyPDF
            - **架构**: 双向量库（基础 + 用户）
            """)
            
            st.divider()
            
            # 存储使用情况
            try:
                upload_dir = "UserUploads"
                if os.path.exists(upload_dir):
                    total_size = get_directory_size(upload_dir)
                    st.metric(
                        label="📊 存储使用",
                        value=format_file_size(total_size)
                    )
            except:
                pass
            
            st.markdown("---")
            st.caption("💡 提示：首次使用时系统会加载所有PDF文档并进行向量化，可能需要几分钟时间。")
    
    except Exception as e:
        st.error(f"❌ 系统错误：{str(e)}")
        st.info("""
        请检查：
        - OpenAI API Key 是否正确
        - CourseMaterials/deep_learning 目录下是否有PDF文件
        - 网络连接是否正常
        """)


if __name__ == "__main__":
    main()
