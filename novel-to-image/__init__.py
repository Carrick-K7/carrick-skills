"""
Novel to Image Skill
将小说章节 Markdown 转换为小红书长图
"""

from .generate import generate_chapter, parse_markdown, DEFAULT_CONFIG

__version__ = "1.0.0"
__all__ = ["generate_chapter", "parse_markdown", "DEFAULT_CONFIG"]
