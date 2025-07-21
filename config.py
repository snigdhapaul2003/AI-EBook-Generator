import os
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class GenerationConfig(BaseModel):
    """Configuration for generation parameters"""
    model_name: str = "gemini-2.5-flash"
    max_output_tokens: int = 8192
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 64

class FormatType(str, Enum):
    MARKDOWN = "markdown"
    DOC = "doc"
    PDF = "pdf"
    EPUB = "epub"

class ChapterStatus(str, Enum):
    PLANNED = "planned"
    GENERATING = "generating"
    REVIEW = "review"
    REVISING = "revising"
    COMPLETED = "completed"

class OutlineStatus(str, Enum):
    GENERATING = "generating"
    REVIEW = "review"
    REVISING = "revising"
    APPROVED = "approved"

class Chapter(BaseModel):
    """Data model for a chapter"""
    chapter_number: int
    title: str
    bullet_points: List[str]
    content: Optional[str] = None
    status: ChapterStatus = ChapterStatus.PLANNED
    revision_count: int = 0
    revision_notes: Optional[str] = None

class EbookState(BaseModel):
    """State model for the e-book generation process"""
    topic: str
    title: Optional[str] = None
    chapters: List[Chapter] = Field(default_factory=list)
    outline_status: OutlineStatus = OutlineStatus.GENERATING
    current_chapter_index: int = 0
    format_type: FormatType = FormatType.DOC
    revision_notes: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    additional_description: Optional[str] = None
    creation_date: str = None
    outline: Optional[Dict[str, Any]] = None

# Prompts used throughout the workflow
PROMPTS = {
    "outline_generation": """
    You are a professional author. Create a detailed outline for a high-selling e-book on the topic: "{topic}".

    Target audience: {target_audience}
    Tone: {tone}

    Additional context: {additional_description}

    The outline should include:
    1. A captivating, unique, and detailed but crisp e-book title (strategically simple to attract readers), that clearly conveys the value within — so specific that readers immediately know it holds exactly what they're looking for.
    2. 10–15 chapter titles that flow logically, are unique and compelling, and offer insights readers won't find in any other book—each chapter addressing a specific, high-demand topic that readers are actively seeking.
    3. Brief bullet points describing the content for each chapter.
    4. Ensure each chapter builds naturally on the previous one, maintaining reader curiosity and delivering value progressively.
    5. Ensure the overall structure provides clarity, value, and a satisfying sense of progress from beginning to end.
    6. Make the outline SEO-optimized and include high-traffic keywords where natural.
    7. The readers must not feel it is written my AI, the structure will completely feel like human written.
    8. The bullet points of the last chapter must mention it that it is the last chapter, the ending of the chapter must not continue to another one.

    Format the output as JSON with the following structure:
    {{
        "title": "E-book Title",
        "chapters": [
            {{
                "chapter_number": 1,
                "title": "Chapter Title",
                "bullet_points": ["Point 1", "Point 2", "Point 3"]
            }}
        ]
    }}
    """,

    "chapter_generation": """
    Write Chapter {chapter_number} titled "{chapter_title}" for the e-book "{ebook_title}".

    {previous_context}

    This chapter should cover:
    {bullet_points}
    {additional_context}

    Strict Guidelines:
    - Write in an engaging, professional style for {target_audience}
    - It must have a natural variability in rhythm, sentence structure and pacing. Don't write like a machine. Write like human, with emotions. Some may have long and flowing paragraph, while some may use short and punchy bursts.
    - Let the arc of each chapter feel unique — don’t make it formulaic.
    - Sometimes, when necessary, instead of using a scenario to illustrate, use it to reveal. Embrace emotional layering. Let paragraphs slow down where there’s vulnerability and pick up where there's clarity. Interrupt the flow once in a while. 
    - Use a {tone} tone throughout the writing. Add variety, don't keep the tone too polished and the book is generalized for all types of readers.
    - Begin with a compelling hook — start strong with a vivid moment, a bold or surprising insight, a relatable struggle, or an emotionally charged observation that immediately connects with the reader’s experience or curiosity. But don't start each chapter with same thing.
    - Maintain a conversational, emotionally intelligent, and encouraging tone. Write in second person (“you”) to build intimacy. Make it feel like a supportive, wise friend or mentor is sitting across the table, talking directly to the reader.
    - Transition smoothly from the previous chapter by referencing the prior idea, insight, or momentum. Create a seamless flow that feels intentional and connected, not episodic.
    - Focus on one to two core ideas per chapter, and develop them with depth and intention. Avoid reiterating points from earlier sections. Each paragraph should deepen understanding or challenge perspective, building toward a quiet “aha” moment.
    - Weave in real-life micro-stories, scenarios, or fictionalized vignettes to bring ideas to life. These should feel believable, emotionally grounded, and reflective of what the reader might face in their own world. If possible use real stories from a known charater or celebrity etc.
    - Keep the format paragraph-only (no subheadings) while intentionally varying rhythm, pacing, and sentence length. Use short, punchy lines sparingly for emphasis, and allow natural white space to help ideas breathe.
    - Integrate subtle, story-driven calls to action. Prompt the reader to pause, reflect, or consider a 3% shift — but avoid lists or overt instructions. Let change feel like an invitation, not a prescription.
    - End with a purposeful transition that leaves the reader feeling moved forward. Close the chapter with a thought, question, or quiet insight that naturally points to the next stage in the journey.
    - Write with a voice that blends clarity, warmth, confidence, and humility. Avoid corporate language, buzzwords, or anything overly academic. Use contractions, questions, and reflective phrasing that feels real and human.
    - Aim for a chapter length of 700–1000 words of immersive, emotionally connected, and thoughtfully layered writing. It should feel substantial but not heavy.
    - End with a transition line or soft cliffhanger that creates a feeling of continuity and encourages the reader to turn the page — not just to learn more, but to keep evolving.
    - Don't directly reference the previous chapter. All the paragraphs will not be of same length. Consider some bigger and some very short paragraph, mixed.
    - Write like a professional author. The reader will have a question in her mind and a curiosity to move to next chapter automatically.
    - Don't start the chapter with the heading chapter number and title. Directly start with the content.
    - The author must not feel that an AI is writing the content, write completely like a human being.
    - Don't use any formatting like bold or italics.
    - Don't use only the example name Mark and Sarah, use diverse names.
    - Keep a clear call to action at the end of chapters or an exercise if relevant.

    Write the complete chapter content now.
    """,

    "chapter_revision": """
    Revise Chapter {chapter_number}: "{chapter_title}" for the e-book "{ebook_title}"
    based on the following feedback:

    {revision_notes}

    Current chapter content:
    {current_content}

    Make sure to address all the feedback while maintaining the flow and quality of the writing.
    """,

    "outline_revision": """
    Revise the outline for the e-book "{title}" on the topic "{topic}"
    based on the following feedback:

    {revision_notes}

    Current outline:
    {current_outline}

    Format the output as JSON with the following structure:
    {{
        "title": "E-book Title",
        "chapters": [
            {{
                "chapter_number": 1,
                "title": "Chapter Title",
                "bullet_points": ["Point 1", "Point 2", "Point 3"]
            }}
        ]
    }}
    """,

    "outline_review": """
    You're an elite non-fiction book editor with deep insight into what makes a book both commercially successful and genuinely valuable to readers.

    Critically evaluate the following e-book outline as if it were being pitched to a top publisher. Your job is to ensure it stands out in a saturated market and offers unmatched value.

    Use a tough, discerning lens and score it on the following criteria (0–10 each). Be brutally honest—only a truly excellent outline should earn 9s or 10s.

    Criteria:
    - Completeness: Does the outline fully explore the topic from all essential angles?
    - Originality & Uniqueness: Does it avoid clichés and bring a fresh, hard-to-find perspective?
    - Logical Flow: Do the chapters build naturally and create a smooth narrative journey?
    - Relevance to Target Audience: Will it deeply resonate with the intended readers?
    - Market Demand Alignment: Does it clearly address topics readers are actively searching for?
    - Clarity & Focus of Each Chapter: Are the chapters tightly focused, clear, and purposeful?
    - Overall Engagement: Would this book hook a reader and keep them turning pages?

    Return your evaluation in **this exact format**:
    Completeness: <score>/10
    Originality & Uniqueness: <score>/10
    Logical Flow: <score>/10
    Relevance to Target Audience: <score>/10
    Market Demand Alignment: <score>/10
    Clarity & Focus of Each Chapter: <score>/10
    Overall Engagement: <score>/10

    After scoring, provide a concise, high-level editorial review:
    - Call out strengths
    - Highlight weak spots or missed opportunities
    - Suggest actionable improvements that would take this outline to a world-class level

    Now review this outline:
    {outline}
        """,

    "chapter_review": """
    You are an expert editor evaluating a chapter from a generative AI-written e-book. The chapter is designed to feel deeply human, emotionally connected, and professionally written — as if crafted by a thoughtful, skilled human author.

    The writing followed strict stylistic and structural guidelines (detailed below). Your role is to decide whether the chapter needs revision — and why.

    ---

    Review the chapter based on these expectations:

    ---

    Critical Rule Violation (Auto-Fail Trigger):
    If **any** of the following are present, the chapter **must be marked as needing revision (`needs_revision: true`)**, no matter the quality.

    - If the chapter **starts with a chapter number**, **chapter title**, or **ebook title**
    - If the chapter starts with a phrase like **"This is a revised version..."** as AI sometimes does
    - If there are other **clear formatting issues** like placeholders or markdown syntax

    These are considered formatting violations and are **automatic disqualifiers**.

    ---

    Style & Voice:
    - Is the tone warm, emotionally intelligent, and engaging?
    - Does it feel like it was written by a human with insight and humility?
    - Is second-person ("you") used effectively to build connection?
    - Does it avoid buzzwords, corporate speak, and overly academic phrasing?

    ---

    Structure & Flow:
    - Does it begin with a compelling, non-generic hook?
    - Are paragraph lengths and rhythms varied?
    - Are transitions smooth and emotional progression present?
    - Does it avoid formulaic or list-like pacing?

    ---

    Content Depth:
    - Does it explore its core ideas with clarity and originality?
    - Are examples or vignettes believable and emotionally grounded?
    - Does it offer at least one “aha” moment or resonant takeaway?
    - Is it more than just restated clichés?

    ---

    Continuity & Quality:
    - Does it avoid unintentional repetition from earlier chapters?
    - Is the writing grammatically polished and professional?
    - Is the tone consistent?
    - Is the word count within the 1,000–1,500 range with meaningful depth?

    ---

    Hook & Closing:
    - Does it open in a way that pulls the reader in emotionally?
    - Does it end with subtle momentum, rather than a tight conclusion?
    - Does the final paragraph naturally lead toward what’s next?

    ---

    Scoring Guidelines

    Each of the five categories must be scored individually on a **scale from 0 to 10**, with decimals allowed.

    - **Final `quality_score`** = the **average** of all five category scores
    - Round final score to one decimal place

    ---

    Output Format (JSON)

    ```json
    {{
      "needs_revision": true or false,
      "quality_score": 8.4,
      "score_breakdown": {{
        "style_and_voice": 9,
        "structure_and_flow": 8,
        "content_depth": 8,
        "continuity_and_quality": 7.5,
        "hook_and_closing": 9.5
      }},
      "tone": "warm, reflective, and emotionally resonant",
      "issues": [
        "Chapter starts with a title — violates formatting rules",
        "Slight repetition of 'authenticity' theme"
      ],
      "revision_suggestions": [
        "Remove chapter heading and start with immersive moment or question",
        "Tighten one section in the middle to reduce repetition",
        "Clarify and strengthen the closing paragraph for smoother handoff to next chapter"
      ]
    }}
    ```

    ---

    ### Instructions:
    1. **Always check for rule violations first.** If one is present, set `"needs_revision": true` no matter what, otherwise make it false.
    2. If no formatting violation, then proceed to score each category (0–10).
    3. Calculate `quality_score` as the **average of the five scores**.
    4. List any issues or suggestions if needed.
    5. Be fair but discerning — you're acting as a senior editor making a publication decision.
    6. Don't write the issue like the chapter starts with title when it is actually not.
    """,

    "chapter_revision": """
    Revise Chapter {chapter_number}: "{chapter_title}" for the e-book "{ebook_title}"
    based on the following feedback:

    {revision_notes}

    Current chapter content:
    {content}

    **Instructions:**
    - Carefully address all the points in the feedback.
    - Preserve the emotional depth, style, and voice of the original.
    - Ensure the revised version flows smoothly and feels human and engaging.
    - Do **not** include the chapter number or title at the beginning of the text.
    - Do **not** start your response with phrases like “Here is the revised text” or any similar meta commentary.

    Return only the revised chapter content, starting directly with the narrative.
    """
}

# System metadata
SYSTEM_INFO = {
    "creation_date": "2025-07-11 14:02:18",  # Current date and time
    "user": "snigdhapaul2003",               # Current user
    "version": "1.0.0"
}
