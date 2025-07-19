"""
E-Book Generator Package

A professional AI-powered e-book generation system using LangGraph and Google's Gemini API.
"""

__version__ = "1.0.0"
__author__ = "snigdhapaul2003"
__email__ = "snigdhapaul2003@example.com"
__description__ = "AI-powered e-book generation system using LangGraph and Google's Gemini API"

from .config import FormatType, SYSTEM_INFO, DEFAULT_CONFIG
from .main import run_ebook_generator, display_header, display_outline, display_chapter, save_ebook

# Optional imports (only if modules exist)
try:
    from .graph import EbookGeneratorGraph
except ImportError:
    EbookGeneratorGraph = None

try:
    from .nodes import OutlineGeneratorNode, ChapterGeneratorNode, ReviewerNode, FormatterNode, ExporterNode
except ImportError:
    OutlineGeneratorNode = None
    ChapterGeneratorNode = None
    ReviewerNode = None
    FormatterNode = None
    ExporterNode = None

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "FormatType",
    "SYSTEM_INFO",
    "DEFAULT_CONFIG",
    "run_ebook_generator",
    "display_header",
    "display_outline",
    "display_chapter",
    "save_ebook",
    "EbookGeneratorGraph",
    "OutlineGeneratorNode",
    "ChapterGeneratorNode",
    "ReviewerNode",
    "FormatterNode",
    "ExporterNode",
]
