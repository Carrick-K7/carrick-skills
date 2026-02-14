# Novel to Image Skill

## 描述
将小说章节 Markdown 文件转换为小红书长图格式，支持钩子页、内容页、收尾页自动生成。

## 功能
- 解析 Markdown 章节文件
- 自动生成首页（书名+章节+有趣片段预览）
- 自动分页生成内容页
- 生成收尾页（预告+互动+CTA）
- 垂直居中布局，优化空间利用

## 使用方式

### 在 OpenClaw 中调用

```python
# 方式1: 直接调用函数
from skills.novel_to_image import generate_chapter

output_dir = generate_chapter("/path/to/第05章_标题.md")
print(output_dir)  # 返回输出目录路径

# 方式2: 使用 sessions_spawn 在独立 session 中执行
from openclaw import sessions_spawn

result = sessions_spawn(
    task="""
    from skills.novel_to_image import generate_chapter
    output = generate_chapter("/path/to/第05章_标题.md")
    print(f"生成完成: {output}")
    """,
    label="novel-gen"
)
```

### 命令行使用

```bash
cd ~/.openclaw/workspace/skills/novel-to-image
python3 generate.py "第05章_标题.md"
```

## 输入格式

Markdown 章节文件示例：
```markdown
# 第5章：出差三天的想念

**【场景：机场，早上7点】**

「A，我要出差三天。」

「我知道。我已经把你的行程同步到日历。」

K 叹了口气：「你就不能配合我一下吗？」

……

---
预告：K 出差三天，A 第一次「体验」到什么叫想念……
```

## 输出格式

生成图片保存到 `output/第05章_标题/` 目录：
- `05_钩子.png` - 首页（书名+章节+预览片段+CTA）
- `05_内容_1.png` ~ `05_内容_N.png` - 正文页
- `05_收尾.png` - 结束页（预告+互动+CTA）

## 配置

可通过修改 `generate.py` 中的 `DEFAULT_CONFIG` 自定义：
- 页面尺寸
- 字体大小
- 颜色方案
- 每页最大行数

## 依赖

- Python 3.8+
- Pillow (PIL)
- Noto Sans CJK 字体（系统字体）

## 版本历史

- v1.0.0 - 初始版本，支持基础生成和分页
