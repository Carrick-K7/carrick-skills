#!/usr/bin/env python3
"""
跨 Session 调用 novel-to-image Skill 示例
"""

# 示例1: 直接调用（当前 Session）
def example_direct():
    import sys
    sys.path.insert(0, '/root/.openclaw/workspace/skills')
    
    from novel_to_image import generate_chapter
    
    output = generate_chapter("/path/to/第07章_标题.md")
    print(f"生成完成: {output}")
    return output

# 示例2: 在独立 Session 中调用（通过 sessions_spawn）
def example_spawn():
    """
    在另一个 session 中执行生成任务
    """
    task = """
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills')

from novel_to_image import generate_chapter

# 生成第7章
output = generate_chapter("/root/.openclaw/workspace/carrick-nexus/00_Inbox/人机AK的日常/第07章_标题.md")

print(f"✅ 生成完成: {output}")

# 列出生成的文件
from pathlib import Path
files = list(Path(output).glob("*.png"))
for f in sorted(files):
    print(f"  - {f.name}")
"""
    
    # 返回 task 字符串，由调用者执行 sessions_spawn
    return task

# 示例3: 批量生成多个章节
def example_batch():
    chapters = [
        "第07章_标题1.md",
        "第08章_标题2.md",
        "第09章_标题3.md",
    ]
    
    results = []
    for ch in chapters:
        output = generate_chapter(f"/path/to/{ch}")
        results.append(output)
    
    return results

if __name__ == "__main__":
    print("=== Novel to Image Skill 使用示例 ===")
    print()
    print("1. 直接调用:")
    print("   from novel_to_image import generate_chapter")
    print("   output = generate_chapter('第07章_标题.md')")
    print()
    print("2. 跨 Session 调用:")
    print("   使用 sessions_spawn 执行 example_spawn() 返回的 task")
    print()
    print("3. 批量生成:")
    print("   调用 example_batch()")
