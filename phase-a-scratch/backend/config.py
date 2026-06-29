"""
config.py — 项目配置中心

所有模块通过 `from config import settings` 获取配置。
配置值从 .env 文件读取，有默认值。
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件（从当前目录查找）
load_dotenv()


class Settings:
    """
    集中管理所有配置项。
    每个配置项从环境变量读取，如果没设置就用默认值。
    这样改参数只需要改 .env 文件，不用改代码。
    """

    def __init__(self):
        # ── API 配置 ──
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.llm_base_url = os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.llm_model = os.getenv("LLM_MODEL", "qwen3-max")
        self.embedding_base_url = os.getenv(
            "EMBEDDING_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

        # ── 存储路径 ──
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        self.documents_dir = os.getenv("DOCUMENTS_DIR", "../../phase-b-dify/documents")

        # ── 分片参数 ──
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))

        # ── 检索参数 ──
        self.top_k = int(os.getenv("TOP_K", "3"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
        self.vector_weight = float(os.getenv("VECTOR_WEIGHT", "0.7"))
        self.bm25_weight = float(os.getenv("BM25_WEIGHT", "0.3"))

        # ── LLM 生成参数 ──
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0"))
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))

        # ── 启动校验 ──
        if not self.api_key or self.api_key == "sk-your-api-key-here":
            raise ValueError(
                "❌ 请先在 phase-a-scratch/backend/.env 文件中设置你的 "
                "DASHSCOPE_API_KEY（通义千问 API 密钥）"
            )


# 创建全局单例，所有模块 import 这个即可
settings = Settings()
