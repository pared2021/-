#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def test_basic():
    print("🔍 测试基本功能...")
    
    # 测试当前目录
    current_dir = Path('.')
    print(f"当前目录: {current_dir.absolute()}")
    
    # 测试文件遍历
    python_files = []
    try:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.venv'}]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        print(f"找到 {len(python_files)} 个Python文件")
        
        # 显示前5个文件
        for i, file_path in enumerate(python_files[:5]):
            print(f"  {i+1}. {file_path}")
        
        if len(python_files) > 5:
            print(f"  ... 还有 {len(python_files) - 5} 个文件")
            
    except Exception as e:
        print(f"❌ 遍历文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试文件读取
    if python_files:
        test_file = python_files[0]
        print(f"\n📖 测试读取文件: {test_file}")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 成功读取 {len(content)} 个字符")
            
            lines = content.split('\n')
            print(f"✅ 文件有 {len(lines)} 行")
            
        except Exception as e:
            print(f"❌ 读取文件时出错: {e}")
            try:
                with open(test_file, 'r', encoding='gbk') as f:
                    content = f.read()
                print(f"✅ 使用GBK编码成功读取 {len(content)} 个字符")
            except Exception as e2:
                print(f"❌ GBK编码也失败: {e2}")
                return False
    
    print("\n✅ 基本功能测试完成")
    return True

def main():
    print("🚀 开始简单测试...")
    
    try:
        success = test_basic()
        if success:
            print("\n🎉 测试成功！")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()