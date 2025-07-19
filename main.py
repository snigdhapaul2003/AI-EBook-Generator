import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file won't be loaded automatically.")
    print("Install with: pip install python-dotenv")

# Import our modules
from config import FormatType, SYSTEM_INFO
from graph import EbookGeneratorGraph

# Update with current user information
SYSTEM_INFO["creation_date"] = "2025-07-11 14:06:49"
SYSTEM_INFO["user"] = "snigdhapaul2003"

def display_header():
    """Display header information in console"""
    print("=" * 60)
    print("E-Book Generator using LangGraph and Gemini")
    print("=" * 60)
    print(f"Current Date and Time (UTC): {SYSTEM_INFO['creation_date']}")
    print(f"Current User's Login: {SYSTEM_INFO['user']}")
    print(f"Version: {SYSTEM_INFO['version']}")
    print("=" * 60)

def display_outline(ebook_state):
    """Display the generated outline in a nice format"""
    title = ebook_state.get("title", "Untitled E-book")
    chapters = ebook_state.get("chapters", [])

    print(f"\n## E-book Outline: {title}")

    for chapter in chapters:
        chapter_num = chapter.get("chapter_number", 0)
        chapter_title = chapter.get("title", "Untitled Chapter")
        bullet_points = chapter.get("bullet_points", [])

        print(f"\n### Chapter {chapter_num}: {chapter_title}")
        for point in bullet_points:
            print(f"- {point}")

def display_chapter(chapter):
    """Display a generated chapter in a nice format"""
    chapter_num = chapter.get("chapter_number", 0)
    chapter_title = chapter.get("title", "Untitled Chapter")
    content = chapter.get("content", "*No content generated*")

    print(f"\n## Chapter {chapter_num}: {chapter_title}")
    print(content)


def get_user_inputs():
    """Get user inputs through console prompts"""
    print("\n### Enter E-book Generation Parameters")
    print("-" * 40)
    
    # Get topic
    topic = input("Topic (default: 'How to win friends and influence people'): ").strip()
    if not topic:
        topic = 'How to win friends and influence people'
    
    # Get target audience
    audience = input("Target Audience (default: 'general readers'): ").strip()
    if not audience:
        audience = 'general readers'
    
    # Get tone
    tone = input("Tone (default: 'professional but conversational'): ").strip()
    if not tone:
        tone = 'professional but conversational'
    
    # Get format
    print("\nAvailable formats: markdown, doc, pdf")
    format_type = input("Format (default: 'doc'): ").strip().lower()
    if format_type not in ['markdown', 'doc', 'pdf']:
        format_type = 'doc'
    
    # Get additional description/requirements
    print("\n--- Optional: Additional Description ---")
    print("You can provide extra context, specific requirements, or details about your e-book:")
    print("(Examples: 'Include practical exercises', 'Focus on real-world examples', 'Add case studies', etc.)")
    additional_description = input("Additional description (optional, press Enter to skip): ").strip()
    if not additional_description:
        additional_description = ""
    
    # Get API key
    api_key = input("\nGemini API Key (or press Enter to use environment variable): ").strip()
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    
    return topic, audience, tone, format_type, additional_description, api_key

def run_ebook_generator():
    """Run the e-book generator in VS Code"""
    # Display header
    display_header()

    # Get user inputs
    topic, audience, tone, format_type, additional_description, api_key = get_user_inputs()

    # Validate inputs
    if not topic:
        print("Error: Topic cannot be empty")
        return

    if not api_key:
        print("Error: Gemini API Key cannot be empty")
        print("Please set GEMINI_API_KEY environment variable or provide it when prompted")
        return

    # Set API key in environment
    os.environ["GEMINI_API_KEY"] = api_key

    # Create directories
    os.makedirs("./output", exist_ok=True)

    try:
        # Initialize the graph
        print("\n## Initializing E-book Generator")
        print("-" * 40)
        print(f"Topic: {topic}")
        print(f"Target audience: {audience}")
        print(f"Tone: {tone}")
        print(f"Output format: {format_type}")
        if additional_description:
            print(f"Additional requirements: {additional_description}")

        ebook_generator = EbookGeneratorGraph(api_key=api_key)

        # Run the workflow
        print("\n## Generating E-book")
        print("-" * 40)
        print("Starting generation process...")

        result = ebook_generator.run(
            topic=topic,
            target_audience=audience,
            tone=tone,
            format_type=format_type,
            additional_description=additional_description
        )

        # Check results
        if "error" in result:
            print(f"Error: {result['error']}")
        elif "export_complete" in result and result["export_complete"]:
            print("\n## E-book Generation Complete! 🎉")
            print("-" * 40)

            # Get output file and content
            output_file = result.get("output_filename", "ebook.md")
            compiled_content = result.get("compiled_content", "")

            # Display summary
            if "ebook_state" in result:
                ebook_state = result["ebook_state"]
                print(f"\n### E-book Title: {ebook_state.get('title', 'Unknown')}")
                print(f"Number of Chapters: {len(ebook_state.get('chapters', []))}")

                # Offer to display the outline
                print("\n### E-book Structure")
                display_outline(ebook_state)
        else:
            print("E-book generation did not complete successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

# Main execution
if __name__ == "__main__":
    
    # Execute the function
    run_ebook_generator()
