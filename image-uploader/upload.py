"""
Image Uploader - 图片上传图床
支持多平台：Catbox, 阿里云OSS（预留）
"""

import requests
from pathlib import Path
from typing import List, Union
import time

def upload_to_catbox(
    files: Union[str, Path, List[Union[str, Path]]],
    expiry: str = "24h"
) -> List[str]:
    """
    上传文件到 Catbox 临时图床
    
    Args:
        files: 单个文件路径或路径列表
        expiry: 过期时间 (1h, 12h, 24h, 72h)
    
    Returns:
        URL 列表
    """
    if isinstance(files, (str, Path)):
        files = [files]
    
    urls = []
    for f in files:
        f = Path(f)
        if not f.exists():
            print(f"⚠️ 文件不存在: {f}")
            continue
        
        try:
            with open(f, 'rb') as fp:
                resp = requests.post(
                    "https://litterbox.catbox.moe/resources/internals/api.php",
                    data={"reqtype": "fileupload", "time": expiry},
                    files={"fileToUpload": (f.name, fp, f"image/{f.suffix.lstrip('.')}")},
                    timeout=60
                )
                url = resp.text.strip()
                if url.startswith("http"):
                    urls.append(url)
                    print(f"✅ {f.name} -> {url[:50]}...")
                else:
                    print(f"❌ {f.name} 上传失败: {url}")
        except Exception as e:
            print(f"❌ {f.name} 错误: {e}")
        
        time.sleep(0.5)  # 避免请求过快
    
    return urls

def upload_directory(
    dir_path: Union[str, Path],
    pattern: str = "*.png",
    expiry: str = "24h"
) -> List[str]:
    """
    上传整个目录的图片
    
    Args:
        dir_path: 目录路径
        pattern: 文件匹配模式 (默认 *.png)
        expiry: 过期时间
    
    Returns:
        URL 列表（按文件名排序）
    """
    dir_path = Path(dir_path)
    files = sorted(dir_path.glob(pattern))
    
    if not files:
        print(f"⚠️ 目录中没有匹配 {pattern} 的文件")
        return []
    
    print(f"📁 找到 {len(files)} 个文件，开始上传...")
    return upload_to_catbox(files, expiry)

def upload_with_progress(
    files: Union[str, Path, List[Union[str, Path]]],
    expiry: str = "24h"
) -> dict:
    """
    带进度报告的上传
    
    Returns:
        {"success": [...], "failed": [...]}
    """
    if isinstance(files, (str, Path)):
        files = [files]
    
    result = {"success": [], "failed": []}
    total = len(files)
    
    for i, f in enumerate(files, 1):
        f = Path(f)
        print(f"[{i}/{total}] 上传 {f.name}...", end=" ")
        
        try:
            with open(f, 'rb') as fp:
                resp = requests.post(
                    "https://litterbox.catbox.moe/resources/internals/api.php",
                    data={"reqtype": "fileupload", "time": expiry},
                    files={"fileToUpload": (f.name, fp, f"image/{f.suffix.lstrip('.')}")},
                    timeout=60
                )
                url = resp.text.strip()
                if url.startswith("http"):
                    result["success"].append({"file": str(f), "url": url})
                    print(f"✅")
                else:
                    result["failed"].append({"file": str(f), "error": url})
                    print(f"❌ {url}")
        except Exception as e:
            result["failed"].append({"file": str(f), "error": str(e)})
            print(f"❌ {e}")
        
        time.sleep(0.3)
    
    print(f"\n📊 完成: {len(result['success'])}/{total} 成功")
    return result

# 别名，方便调用
upload = upload_to_catbox
upload_dir = upload_directory
