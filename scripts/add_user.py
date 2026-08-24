#!/usr/bin/env python3
"""
用户接入脚本 - 管理员专用
用法：
  python3 scripts/add_user.py user_config.json
  或
  python3 scripts/add_user.py '{"action":"add_user","user_id":"xxx","profile":{...}}'

脚本会自动完成：
1. 创建用户目录
2. 生成访问码
3. 更新 access.json
4. 保存 profile.json（供定时任务读取）
5. 创建占位报告页
6. Git 提交推送
7. 输出访问码给用户
"""

import json
import os
import sys
import hashlib
import base64
import secrets
import string
import subprocess
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 简单的中文转拼音映射（常见姓氏+名字）
# 如果pypinyin可用则使用，否则用user_id
def name_to_pinyin(name):
    try:
        from pypinyin import pinyin, Style
        result = pinyin(name, style=Style.NORMAL)
        return ''.join([item[0] for item in result])
    except ImportError:
        # 没有pypinyin，用user_id
        return None

def generate_access_code(name):
    """生成6位访问码：姓名拼音前2位 + 4位随机数字"""
    pinyin_name = name_to_pinyin(name)
    if pinyin_name and len(pinyin_name) >= 2:
        prefix = pinyin_name[:2].lower()
    else:
        prefix = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(2))
    numbers = ''.join(secrets.choice(string.digits) for _ in range(4))
    return prefix + numbers

def sha256_hash(text):
    """计算SHA-256哈希"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def base64_encode(text):
    """Base64编码路径"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def create_placeholder_html(user_name):
    """创建占位报告页"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PM岗位日报 - {user_name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #f0f2f5; min-height: 100vh; display: flex;
    align-items: center; justify-content: center;
  }}
  .placeholder {{
    background: #fff; border-radius: 16px; padding: 48px 40px;
    text-align: center; max-width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  }}
  .placeholder .icon {{ font-size: 48px; margin-bottom: 16px; }}
  .placeholder h1 {{ font-size: 20px; color: #1a2332; margin-bottom: 8px; }}
  .placeholder p {{ font-size: 14px; color: #6b7a8f; line-height: 1.8; }}
  .placeholder .date {{ font-size: 12px; color: #94a3b8; margin-top: 20px; }}
</style>
</head>
<body>
<div class="placeholder">
  <div class="icon">📋</div>
  <h1>欢迎，{user_name}！</h1>
  <p>您的账号已开通成功。</p>
  <p>明天上午10:00将为您生成第一份岗位日报。</p>
  <p>请收藏本页面，每天上午回来查看最新岗位推荐。</p>
  <div class="date">开通时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}</div>
</div>
</body>
</html>"""

def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/add_user.py <config_file.json或JSON字符串>")
        print("示例: python3 scripts/add_user.py user_config.json")
        print("      python3 scripts/add_user.py '{\"action\":\"add_user\",...}'")
        sys.exit(1)

    # 读取配置
    arg = sys.argv[1]
    if os.path.isfile(arg):
        with open(arg, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        try:
            config = json.loads(arg)
        except json.JSONDecodeError:
            print("错误：无法解析JSON，请检查输入")
            sys.exit(1)

    # 验证配置
    if config.get('action') != 'add_user':
        print("错误：配置中action不是add_user")
        sys.exit(1)

    profile = config.get('profile', {})
    user_name = profile.get('user_name', '')
    user_id = config.get('user_id', '')

    if not user_name or not user_id:
        print("错误：缺少user_name或user_id")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  正在为新用户开通账号: {user_name}")
    print(f"{'='*50}\n")

    # 1. 确定用户目录名
    pinyin_name = name_to_pinyin(user_name)
    if pinyin_name:
        dir_name = pinyin_name
    else:
        dir_name = user_id

    user_dir = os.path.join(BASE_DIR, 'users', dir_name)
    reports_dir = os.path.join(user_dir, 'reports')

    # 检查用户是否已存在
    if os.path.exists(user_dir):
        print(f"⚠ 用户目录已存在: users/{dir_name}")
        confirm = input("是否覆盖？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            sys.exit(0)

    # 2. 创建目录结构
    os.makedirs(reports_dir, exist_ok=True)
    print(f"✓ 创建用户目录: users/{dir_name}/")

    # 3. 保存 profile.json（供定时任务读取）
    profile_path = os.path.join(user_dir, 'profile.json')
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"✓ 保存用户画像: users/{dir_name}/profile.json")

    # 4. 创建占位报告页
    latest_path = os.path.join(user_dir, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(create_placeholder_html(user_name))
    print(f"✓ 创建占位页面: users/{dir_name}/latest.html")

    # 5. 生成访问码
    access_code = generate_access_code(user_name)
    code_hash = sha256_hash(access_code)
    relative_path = f"users/{dir_name}/latest.html"
    encoded_path = base64_encode(relative_path)

    # 6. 更新 access.json
    access_path = os.path.join(BASE_DIR, 'access.json')
    with open(access_path, 'r', encoding='utf-8') as f:
        access_data = json.load(f)

    # 移除已存在的同名用户（如果有）
    access_data['users'] = [u for u in access_data['users'] if u.get('path') != encoded_path]

    # 添加新用户
    access_data['users'].append({
        'code_hash': code_hash,
        'path': encoded_path
    })

    with open(access_path, 'w', encoding='utf-8') as f:
        json.dump(access_data, f, ensure_ascii=False, indent=2)
    print(f"✓ 更新访问码映射: access.json")

    # 7. Git 提交推送
    print(f"\n--- Git 提交 ---")
    try:
        os.chdir(BASE_DIR)
        subprocess.run(['git', 'add', '-A'], check=True)
        commit_msg = f"feat: 新用户开通 - {user_name} ({dir_name})"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print("✓ Git 提交完成")

        subprocess.run(['git', 'push'], check=True)
        print("✓ Git 推送完成")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Git操作出错: {e}")
        print("  您可以手动执行: git add -A && git commit -m '新用户' && git push")

    # 8. 输出结果
    print(f"\n{'='*50}")
    print(f"  ✅ 开通成功！")
    print(f"{'='*50}")
    print(f"\n  用户名: {user_name}")
    print(f"  用户目录: users/{dir_name}/")
    print(f"  访问码: {access_code}")
    print(f"\n  请将访问码【{access_code}】发送给 {user_name}")
    print(f"  用户在网站首页输入此访问码即可查看日报")
    print(f"\n  明天10:00定时任务将自动为该用户生成第一份日报")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
