"""
Novel to Image - 小说章节转小红书长图
"""

from PIL import Image, ImageDraw, ImageFont
import re
import json
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "canvas": {"width": 1080, "height": 1920, "margin": 60},
    "colors": {
        "bg": (252, 252, 254),
        "text": (45, 45, 55),
        "text_secondary": (100, 100, 115),
        "accent": (90, 90, 140),
        "highlight": (200, 80, 120),
        "line": (220, 220, 230),
        "box_bg": (255, 240, 245)
    },
    "fonts": {
        "book": 52, "chapter": 60, "title": 120,
        "hook": 48, "body": 32, "page_num": 22, "cta": 44
    },
    "layout": {"max_lines_per_page": 15}
}

# 字体路径（系统字体）
FONT_PATHS = [
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
]

_font_cache = {}

def get_font(size, bold=True):
    """获取字体"""
    cache_key = f"{size}_{bold}"
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    
    for p in (FONT_PATHS if bold else FONT_PATHS[1:]):
        try:
            font = ImageFont.truetype(p, size)
            _font_cache[cache_key] = font
            return font
        except:
            continue
    return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """智能换行 - 优化版：更准确的宽度计算"""
    if not text:
        return [""]
    
    # 尝试获取字体渲染宽度
    def get_text_width(t):
        try:
            bbox = font.getbbox(t)
            return bbox[2] - bbox[0] if bbox else len(t) * 30
        except:
            return len(t) * 30
    
    # 估算平均字符宽度
    sample_text = "中文测试ABC123"
    avg_char_width = get_text_width(sample_text) / len(sample_text)
    max_chars = int(max_width / avg_char_width)
    
    # 如果文本很短，直接返回
    if len(text) <= max_chars:
        return [text]
    
    result = []
    current_line = ""
    current_width = 0
    
    # 标点符号，可以在这些位置断行
    break_chars = "。！？；，、"
    
    for char in text:
        char_width = get_text_width(char)
        
        # 检查加上这个字符后是否超出宽度
        if current_width + char_width > max_width and len(current_line) > 0:
            # 尝试在标点处优雅断行
            if char in break_chars:
                current_line += char
                result.append(current_line)
                current_line = ""
                current_width = 0
            else:
                # 检查是否可以回退到上一个标点
                last_break = -1
                for i, c in enumerate(current_line):
                    if c in break_chars:
                        last_break = i
                
                if last_break > 0 and len(current_line) - last_break < 10:
                    # 在标点处断行
                    result.append(current_line[:last_break+1])
                    current_line = current_line[last_break+1:] + char
                    current_width = get_text_width(current_line)
                else:
                    # 强制断行
                    result.append(current_line)
                    current_line = char
                    current_width = char_width
        else:
            current_line += char
            current_width += char_width
    
    # 添加最后一行
    if current_line:
        result.append(current_line)
    
    return result if result else [text]

def parse_markdown(md_path):
    """解析 Markdown 章节"""
    text = Path(md_path).read_text(encoding='utf-8')
    lines = text.strip().split('\n')
    
    chapter_num, chapter_title, next_chapter = "1", "无题", ""
    body_lines, dialogues = [], []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 提取章节信息
        if m := re.search(r'第(\d+)章[：:_\s]*(.+)', line):
            chapter_num = m.group(1)
            chapter_title = m.group(2).replace('.md', '').replace('_', ' ')
        # 提取预告
        elif '预告' in line or '下章' in line:
            if match := re.search(r'(?:预告|下章)[：:\s]*(.+)', line):
                next_chapter = match.group(1).strip()
        # 跳过标记
        elif line.startswith('#') or line.startswith('---') or line.startswith('【'):
            continue
        else:
            # 解析对话
            speaker = None
            content = line
            
            if line.startswith('K') and ('：' in line[:5] or ':' in line[:5]):
                speaker, content = 'K', re.sub(r'^K[说]?[：:]\s*', '', line)
            elif line.startswith('A') and ('：' in line[:5] or ':' in line[:5]):
                speaker, content = 'A', re.sub(r'^A[说]?[：:]\s*', '', line)
            
            # 清理但不删除引号
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content).strip()
            
            if content:
                body_lines.append(content)
                dialogues.append({"speaker": speaker, "text": content})
    
    return chapter_num, chapter_title, body_lines, dialogues, next_chapter

def create_hook_page(chapter_num, title, body_lines, config):
    """创建钩子页"""
    cfg = config
    COLORS = cfg["colors"]
    CARD_WIDTH = cfg["canvas"]["width"]
    CARD_HEIGHT = cfg["canvas"]["height"]
    MARGIN = cfg["canvas"]["margin"]
    
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    
    book_font = get_font(cfg["fonts"]["book"], bold=True)
    chap_font = get_font(cfg["fonts"]["chapter"], bold=True)
    title_font = get_font(cfg["fonts"]["title"], bold=True)
    preview_font = get_font(cfg["fonts"]["body"])
    cta_font = get_font(cfg["fonts"]["cta"], bold=True)
    
    # 找预览片段
    preview_lines = []
    for line in body_lines:
        if len(preview_lines) >= 4:
            break
        keywords = ['AI', '累', '心理', '爱', '幽默', '讽刺', '想', '开心']
        if any(k in line for k in keywords):
            if 8 < len(line) < 40 and line not in preview_lines:
                preview_lines.append(line)
    
    # 计算垂直居中
    book_h, chap_h, title_h = 65, 75, 140
    spacing = 40 + 50
    preview_h = len(preview_lines) * 55 if preview_lines else 0
    preview_spacing = 80 if preview_lines else 0
    total_h = book_h + chap_h + title_h + spacing + preview_h + preview_spacing + 100
    start_y = (CARD_HEIGHT - total_h) // 2 - 30
    
    y = start_y
    
    # 书名
    draw.text((CARD_WIDTH // 2, y), "《人机AK的日常》", 
             fill=COLORS["accent"], font=book_font, anchor="mm")
    y += book_h + 40
    
    # 章节号
    draw.text((CARD_WIDTH // 2, y), f"第 {chapter_num} 章", 
             fill=COLORS["accent"], font=chap_font, anchor="mm")
    y += chap_h + 50
    
    # 标题
    for line in wrap_text(title, title_font, CARD_WIDTH - MARGIN * 2):
        draw.text((CARD_WIDTH // 2, y), line, 
                 fill=COLORS["text"], font=title_font, anchor="mm")
        y += 135
    y += 80
    
    # 预览片段
    for line in preview_lines:
        wrapped = wrap_text(line, preview_font, CARD_WIDTH - MARGIN * 2 - 40)
        for wl in wrapped:
            draw.text((MARGIN + 20, y), wl, fill=COLORS["text_secondary"], font=preview_font)
            y += 55
        y += 10
    
    y += 40
    
    # CTA
    draw.text((CARD_WIDTH // 2, y), "左滑查看全文 →", 
             fill=COLORS["highlight"], font=cta_font, anchor="mm")
    
    return img

def create_content_page(chapter_num, dialogues, page_idx, total_pages, config):
    """创建内容页 - 优化版：动态填充，减少空白"""
    cfg = config
    COLORS = cfg["colors"]
    CARD_WIDTH = cfg["canvas"]["width"]
    CARD_HEIGHT = cfg["canvas"]["height"]
    MARGIN = cfg["canvas"]["margin"]
    
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    
    book_font = get_font(20)
    body_font = get_font(cfg["fonts"]["body"])
    page_font = get_font(cfg["fonts"]["page_num"])
    
    # 计算可用高度
    header_y = 60
    footer_y = CARD_HEIGHT - 50
    available_height = footer_y - header_y - 80  # 留出边距
    
    y = header_y
    draw.text((MARGIN, y), "《人机AK的日常》", fill=COLORS["accent"], font=book_font)
    draw.text((CARD_WIDTH - MARGIN, y), f"第{chapter_num}章", 
             fill=COLORS["accent"], font=book_font, anchor="rt")
    y += 80
    
    # 动态计算每行高度，尽可能填满页面
    line_height = 55
    para_spacing = 25
    
    lines_count = 0
    for d in dialogues:
        wrapped_lines = []
        for line in wrap_text(d["text"], body_font, CARD_WIDTH - MARGIN * 2):
            wrapped_lines.append(line)
        
        # 检查是否还有空间放下这段话
        needed_height = len(wrapped_lines) * line_height + para_spacing
        remaining_height = footer_y - 30 - y
        
        if needed_height > remaining_height and lines_count > 0:
            # 空间不够了，结束这一页
            break
        
        for line in wrapped_lines:
            draw.text((MARGIN, y), line, fill=COLORS["text"], font=body_font)
            y += line_height
            lines_count += 1
        y += para_spacing
    
    # 正确的页码显示（钩子页=1，内容页从2开始）
    draw.text((CARD_WIDTH // 2, footer_y), f"— {page_idx} / {total_pages} —", 
             fill=COLORS["accent"], font=page_font, anchor="mm")
    return img

def fill_page_content(dialogues, config):
    """
    智能填充一页内容，尽可能填满页面
    返回: (本页用到的对话列表, 剩余对话列表)
    """
    cfg = config
    CARD_HEIGHT = cfg["canvas"]["height"]
    MARGIN = cfg["canvas"]["margin"]
    footer_y = CARD_HEIGHT - 50
    header_y = 140  # 头部占用空间
    
    line_height = 55
    para_spacing = 25
    available_height = footer_y - header_y - 60  # 可用高度
    
    used = []
    remaining_height = available_height
    
    for i, d in enumerate(dialogues):
        # 计算这段话需要的高度
        body_font = get_font(cfg["fonts"]["body"])
        wrapped_lines = wrap_text(d["text"], body_font, 1080 - MARGIN * 2)
        needed_height = len(wrapped_lines) * line_height + para_spacing
        
        # 如果这是第一段，或者空间足够，就加上
        if len(used) == 0 or needed_height <= remaining_height:
            used.append(d)
            remaining_height -= needed_height
        else:
            # 空间不够了，剩下的放到下一页
            return used, dialogues[i:]
    
    return used, []

def create_closing_page(chapter_num, title, next_chapter, config):
    """创建收尾页"""
    cfg = config
    COLORS = cfg["colors"]
    CARD_WIDTH = cfg["canvas"]["width"]
    CARD_HEIGHT = cfg["canvas"]["height"]
    MARGIN = cfg["canvas"]["margin"]
    
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    
    book_font = get_font(32)
    title_font = get_font(80, bold=True)
    subtitle_font = get_font(48, bold=True)
    body_font = get_font(40)
    cta_font = get_font(52, bold=True)
    
    y = 100
    draw.text((CARD_WIDTH // 2, y), "《人机AK的日常》", 
             fill=COLORS["accent"], font=book_font, anchor="mm")
    y += 120
    
    draw.text((CARD_WIDTH // 2, y), f"第 {chapter_num} 章 完", 
             fill=COLORS["text"], font=title_font, anchor="mm")
    y += 100
    
    draw.line([(MARGIN + 80, y), (CARD_WIDTH - MARGIN - 80, y)], 
             fill=COLORS["line"], width=3)
    y += 100
    
    draw.text((CARD_WIDTH // 2, y), "[ 下回预告 ]", 
             fill=COLORS["highlight"], font=subtitle_font, anchor="mm")
    y += 70
    
    if next_chapter:
        next_title = f"第{int(chapter_num)+1}章：{next_chapter}"
        for line in wrap_text(next_title, body_font, CARD_WIDTH - MARGIN * 2):
            draw.text((CARD_WIDTH // 2, y), line, 
                     fill=COLORS["text"], font=body_font, anchor="mm")
            y += 60
        y += 30
    else:
        draw.text((CARD_WIDTH // 2, y), "更多精彩内容，敬请期待~", 
                 fill=COLORS["text_secondary"], font=body_font, anchor="mm")
        y += 80
    
    y += 30
    draw.text((CARD_WIDTH // 2, y), "[ 评论区聊聊 ]", 
             fill=COLORS["highlight"], font=subtitle_font, anchor="mm")
    y += 70
    draw.text((CARD_WIDTH // 2, y), "你觉得K和A谁更幽默？", 
             fill=COLORS["text_secondary"], font=body_font, anchor="mm")
    
    y += 100
    draw.text((CARD_WIDTH // 2, y), "♥ 点赞    ★ 关注    ▶ 追更", 
             fill=COLORS["accent"], font=cta_font, anchor="mm")
    
    return img

def generate_chapter(md_path, output_dir=None, config=None):
    """
    生成完整章节图片
    
    Args:
        md_path: Markdown文件路径
        output_dir: 输出目录（默认output/章节名）
        config: 自定义配置（可选）
    
    Returns:
        输出目录路径
    """
    cfg = config or DEFAULT_CONFIG
    md_path = Path(md_path)
    
    if not md_path.exists():
        raise FileNotFoundError(f"文件不存在: {md_path}")
    
    chapter_num, title, body_lines, dialogues, next_chapter = parse_markdown(md_path)
    
    if output_dir is None:
        output_dir = Path("output") / f"第{int(chapter_num):02d}章_{title}"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 清理旧文件
    for f in output_dir.glob("*.png"):
        f.unlink()
    
    pages = []
    
    # 钩子页 (第1页)
    hook_img = create_hook_page(chapter_num, title, body_lines, cfg)
    pages.append(("hook", hook_img, []))
    
    # 内容页 - 智能分页，填满每页
    content = dialogues[3:] if len(dialogues) > 3 else dialogues
    page_idx = 2
    
    while content:
        # 尝试填充一页，返回实际用到的内容和剩余内容
        batch, remaining = fill_page_content(content, cfg)
        if not batch:
            break
        pages.append(("content", batch, page_idx))
        content = remaining
        page_idx += 1
    
    # 计算总页数 (钩子 + 内容 + 收尾)
    total_pages = len(pages) + 1  # +1 是收尾页
    
    # 重新生成内容页，传入正确的总页数
    final_pages = [pages[0][1]]  # 钩子页
    
    for i, (page_type, batch, idx) in enumerate(pages[1:], 2):
        content_img = create_content_page(chapter_num, batch, idx, total_pages, cfg)
        final_pages.append(content_img)
    
    # 收尾页 (最后一页)
    closing_img = create_closing_page(chapter_num, title, next_chapter, cfg)
    final_pages.append(closing_img)
    
    pages = final_pages
    
    # 保存
    chapter_num_int = int(chapter_num)
    for i, img in enumerate(pages, 1):
        if i == 1:
            name = f"{chapter_num_int:02d}_钩子.png"
        elif i == len(pages):
            name = f"{chapter_num_int:02d}_收尾.png"
        else:
            name = f"{chapter_num_int:02d}_内容_{i-1}.png"
        
        img.save(output_dir / name, "PNG")
    
    return str(output_dir)

# 命令行入口
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 generate.py <章节.md>")
        sys.exit(1)
    
    output = generate_chapter(sys.argv[1])
    print(f"✅ 生成完成: {output}")
