from typing import Dict, Any, Optional, List
import os
from datetime import datetime
from google import genai
from langgraph.graph import StateGraph
from langgraph.graph import END

from config import GenerationConfig
from nodes import (
    InitializeNode, OutlineGenerationNode, OutlineReviewNode, OutlineRevisionNode,
    ContextManagerNode, ChapterGenerationNode, ChapterReviewNode, ChapterRevisionNode,
    ChapterCompletionNode, CompilationNode, FormatConversionNode, ExportNode, GeminiGenerator
)
from edges import outline_review_router, chapter_review_router, chapter_completion_router

class EbookGeneratorGraph:
    """Class to create and manage the e-book generator graph"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[GenerationConfig] = None):
        """Initialize the e-book generator graph"""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable or api_key parameter must be set")

        self.config = config or GenerationConfig()

        # Initialize Gemini generator
        self.generator = GeminiGenerator(api_key=self.api_key, config=self.config)

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Create the state graph
        workflow = StateGraph(Dict[str, Any])

        # Define all nodes
        workflow.add_node("initialize", InitializeNode())
        workflow.add_node("generate_outline", OutlineGenerationNode(self.generator))
        workflow.add_node("review_outline", OutlineReviewNode(self.generator))
        workflow.add_node("revise_outline", OutlineRevisionNode(self.generator))
        workflow.add_node("context_manager", ContextManagerNode())
        workflow.add_node("generate_chapter", ChapterGenerationNode(self.generator))
        workflow.add_node("review_chapter", ChapterReviewNode(self.generator))
        workflow.add_node("revise_chapter", ChapterRevisionNode(self.generator))
        workflow.add_node("chapter_completion", ChapterCompletionNode())
        workflow.add_node("compilation", CompilationNode())
        workflow.add_node("format_conversion", FormatConversionNode())
        workflow.add_node("export", ExportNode())
        workflow.add_node("error_handler", lambda state: {**state, "error_handled": True})

        # Add direct edges
        workflow.add_edge("initialize", "generate_outline")
        workflow.add_edge("generate_outline", "review_outline")
        workflow.add_edge("revise_outline", "review_outline")
        workflow.add_edge("context_manager", "generate_chapter")
        workflow.add_edge("generate_chapter", "review_chapter")
        workflow.add_edge("revise_chapter", "review_chapter")
        workflow.add_edge("compilation", "format_conversion")
        workflow.add_edge("format_conversion", "export")
        workflow.add_edge("error_handler", END)
        workflow.add_edge("export", END)  # Make sure export properly ends

        # Add conditional edges
        workflow.add_conditional_edges(
            "review_outline",
            outline_review_router,
            {
                "revise_outline": "revise_outline",
                "plan_chapters": "context_manager",
                "error": "error_handler"
            }
        )

        workflow.add_conditional_edges(
            "review_chapter",
            chapter_review_router,
            {
                "revise_chapter": "revise_chapter",
                "check_completion": "chapter_completion",
                "error": "error_handler"
            }
        )

        workflow.add_conditional_edges(
            "chapter_completion",
            chapter_completion_router,
            {
                "next_chapter": "context_manager",
                "compile": "compilation",
                "error": "error_handler"
            }
        )

        # Set entry point
        workflow.set_entry_point("initialize")

        # Compile the graph with increased recursion limit
        return workflow.compile()

    def run(self, topic: str, target_audience: str = "general readers",
            tone: str = "professional but conversational",
            format_type: str = "doc", additional_description: str = "") -> Dict[str, Any]:
        """Run the e-book generation workflow"""
        # Initial state
        initial_state = {
            "topic": topic,
            "target_audience": target_audience,
            "tone": tone,
            "format_type": format_type,
            "additional_description": additional_description,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "has_more_chapters": False  # Initialize with False
        }

        # Run the graph
        result = self.graph.invoke(initial_state, config={"recursion_limit": 100})

        return result