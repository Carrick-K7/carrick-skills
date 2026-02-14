# novel-to-image

将小说章节 Markdown 转换为小红书长图。

## 功能
- 解析 Markdown 章节文件
- 生成钩子页（书名+章节+有趣片段预览）
- 生成内容页（对话流，无角色标记）
- 生成收尾页（预告+互动+CTA）
- 自动分页，控制阅读密度

## 使用方式

### 作为 OpenClaw Skill 调用

```python
# 在另一个 session 中调用
from novel_to_image import generate_chapter

# 生成图片
output_dir = generate_chapter("/path/to/第05章_标题.md")

# 返回输出目录路径
print(output_dir)  # output/第05章_标题/
```

### 命令行使用

```bash
python3 -m novel_to_image.generate "第05章_标题.md"
```

## 输入格式

Markdown 文件：
```markdown
# 第5章：标题

**【场景：地点，时间】**

对话内容……

「带引号的对话」

K说：带前缀的对话

---
预告：下章预告内容
```

## 输出

- `XX_钩子.png` - 首页
- `XX_内容_1.png` ~ `XX_内容_N.png` - 正文页
- `XX_收尾.png` - 结束页

## 依赖

- Python 3.8+
- Pillow
- Noto Sans CJK 字体（系统字体）

## 版本

v1.0 - 初始版本
