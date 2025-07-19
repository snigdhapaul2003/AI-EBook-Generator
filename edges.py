from typing import Dict, Any, Literal, TypeAlias
from config import EbookState, ChapterStatus, OutlineStatus

# Define return types for router functions
OutlineReviewResult: TypeAlias = Literal["revise_outline", "plan_chapters", "error"]
ChapterReviewResult: TypeAlias = Literal["revise_chapter", "check_completion", "error"]
ChapterCompletionResult: TypeAlias = Literal["next_chapter", "compile", "error"]

def outline_review_router(state: Dict[str, Any]) -> OutlineReviewResult:
    """Router for the outline review node"""
    print("I am in outline review router")
    print(state["ebook_state"]["outline_status"])
    if state.get("error"):
        return "error"
    if state["ebook_state"]["outline_status"] == OutlineStatus.REVISING:
        print("Yes, revision is requested")
        return "revise_outline"
    if "revision_requested" in state:
        return "revise_outline"
    else:
        return "plan_chapters"

def chapter_review_router(state: Dict[str, Any]) -> ChapterReviewResult:
    """Router for the chapter review node"""
    ebook_state = EbookState(**state["ebook_state"])
    current_idx = ebook_state.current_chapter_index
    if state.get("error"):
        return "error"
    print(state["ebook_state"]["chapters"][current_idx]["status"])
    if state["ebook_state"]["chapters"][current_idx]["status"] == ChapterStatus.REVISING:
        print("Chapter revision requested")
        return "revise_chapter"
    if "chapter_revision_requested" in state:
        return "revise_chapter"
    else:
        return "check_completion"

def chapter_completion_router(state: Dict[str, Any]) -> ChapterCompletionResult:
    """Router for the chapter completion node"""
    if state.get("error"):
        return "error"

    # IMPORTANT: Make sure has_more_chapters is being set correctly
    has_more = state.get("has_more_chapters", False)
    if has_more:
        return "next_chapter"
    else:
        return "compile"