#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版依赖库重构脚本
"""

import os
import shutil
from pathlib import Path

def create_backup():
    """创建备份"""
    print("🔄 创建备份...")
    backup_dir = Path("backup_before_refactor")
    
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir()
    
    # 备份关键文件
    files_to_backup = ["requirements.txt", "requirements-dev.txt"]
    
    for file in files_to_backup:
        if Path(file).exists():
            shutil.copy2(file, backup_dir / file)
            print(f"✅ 备份: {file}")
    
    print(f"📁 备份完成: {backup_dir}")

def update_requirements():
    """更新requirements.txt，移除重型库"""
    print("📝 更新requirements.txt...")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt不存在")
        return False
    
    # 要移除的库
    libs_to_remove = [
        'torch', 'torchvision', 'transformers', 'scikit-image', 'easyocr',
        'fastapi', 'uvicorn', 'pydantic', 'httpx',
        'dependency-injector', 'rich', 'tqdm', 'click'
    ]
    
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 过滤行
    filtered_lines = []
    removed_count = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        # 保留注释和空行
        if not line_stripped or line_stripped.startswith('#'):
            filtered_lines.append(line)
            continue
        
        # 检查是否是要移除的库
        lib_name = line_stripped.split('>=')[0].split('==')[0].split('[')[0].lower()
        
        should_remove = False
        for remove_lib in libs_to_remove:
            if remove_lib.lower() in lib_name:
                should_remove = True
                removed_count += 1
                print(f"  - 移除: {line_stripped}")
                break
        
        if not should_remove:
            filtered_lines.append(line)
    
    # 写回文件
    with open(req_file, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)
    
    print(f"✅ 移除了 {removed_count} 个依赖")
    return True

def remove_legacy_web_code():
    """移除legacy web代码"""
    print("🌐 移除legacy web代码...")
    
    web_dirs = [
        Path("src/legacy/removed/web_config"),
        Path("legacy/web_config")
    ]
    
    for web_dir in web_dirs:
        if web_dir.exists():
            shutil.rmtree(web_dir)
            print(f"📁 删除目录: {web_dir}")

def main():
    """主函数"""
    print("🎮 游戏自动化项目 - 简化版依赖重构")
    print("=" * 50)
    
    print("⚠️  此操作将:")
    print("- 移除大型AI库 (torch, transformers等)")
    print("- 移除Web框架 (fastapi等)")
    print("- 移除辅助工具库")
    print("- 创建备份")
    
    try:
        confirm = input("\n是否继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        # 执行重构
        create_backup()
        
        if update_requirements():
            print("✅ requirements.txt更新完成")
        
        remove_legacy_web_code()
        
        print("\n" + "=" * 50)
        print("✅ 重构完成!")
        print("\n建议的后续步骤:")
        print("1. 重新安装依赖: py -m pip install -r requirements.txt")
        print("2. 测试功能: py main.py --gui")
        print("3. 如有问题，从backup_before_refactor恢复")
        
    except KeyboardInterrupt:
        print("\n❌ 操作被中断")
    except Exception as e:
        print(f"❌ 重构失败: {e}")

if __name__ == "__main__":
    main()