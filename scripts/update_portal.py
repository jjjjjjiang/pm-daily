#!/usr/bin/env python3
"""
门户首页更新脚本 - 生成登录门禁页面 + 更新各用户latest.html跳转页
每次报告推送后执行此脚本
"""
import os
import json
import glob
import base64
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_DIR = os.path.join(BASE_DIR, "users")
ACCESS_FILE = os.path.join(BASE_DIR, "access.json")

def get_latest_report(user_path):
    """获取用户最新报告文件名"""
    reports_dir = os.path.join(user_path, "reports")
    if not os.path.isdir(reports_dir):
        return None, None
    reports = sorted(glob.glob(os.path.join(reports_dir, "pm-jobs-*.html")), reverse=True)
    if not reports:
        return None, None
    latest = os.path.basename(reports[0])
    date_str = latest.replace("pm-jobs-", "").replace(".html", "")
    if len(date_str) == 8:
        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return latest, date_str

def update_latest_redirect(user_dir, latest_report):
    """更新用户的latest.html跳转页"""
    latest_path = os.path.join(USERS_DIR, user_dir, "latest.html")
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=reports/{latest_report}">
<title>跳转中...</title>
</head>
<body>
<p>正在跳转到最新报告...</p>
</body>
</html>
'''
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)

def update_access_json():
    """更新access.json - 读取各用户的access_code并生成哈希映射"""
    existing = {"description": "用户访问码映射表", "users": []}
    if os.path.exists(ACCESS_FILE):
        with open(ACCESS_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except:
                pass

    # 保留已有用户的哈希（access_code不在git中，从profile.json读取）
    for user_dir in sorted(os.listdir(USERS_DIR)):
        if user_dir.startswith("_") or user_dir.startswith("."):
            continue
        user_path = os.path.join(USERS_DIR, user_dir)
        if not os.path.isdir(user_path):
            continue

        profile_path = os.path.join(user_path, "profile.json")
        if not os.path.exists(profile_path):
            continue

        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        access_code = profile.get("access_code", "")
        if not access_code:
            continue

        code_hash = hashlib.sha256(access_code.encode()).hexdigest()
        path_encoded = base64.b64encode(f"users/{user_dir}/latest.html".encode()).decode()

        # 检查是否已存在
        found = False
        for u in existing["users"]:
            if u.get("code_hash") == code_hash:
                u["path"] = path_encoded
                found = True
                break
        if not found:
            existing["users"].append({"code_hash": code_hash, "path": path_encoded})

    with open(ACCESS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

def generate_login_page():
    """生成登录门禁首页"""
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PM岗位日报平台</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif;
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
  }
  .login-box { background: #fff; border-radius: 16px; padding: 40px 36px; width: 380px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
  .login-box h1 { font-size: 22px; text-align: center; margin-bottom: 6px; color: #1a2332; }
  .login-box .subtitle { font-size: 13px; text-align: center; color: #94a3b8; margin-bottom: 28px; }
  .form-group { margin-bottom: 20px; }
  .form-group label { display: block; font-size: 13px; color: #475569; margin-bottom: 6px; font-weight: 500; }
  .form-group input { width: 100%; padding: 12px 14px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 15px; outline: none; transition: border 0.2s; }
  .form-group input:focus { border-color: #2563eb; }
  .login-btn { width: 100%; padding: 13px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
  .login-btn:hover { background: #1d4ed8; }
  .error-msg { color: #ef4444; font-size: 13px; text-align: center; margin-top: 12px; display: none; }
  .register-link { text-align: center; margin-top: 20px; }
  .register-link a { font-size: 13px; color: #2563eb; text-decoration: none; }
  .register-link a:hover { text-decoration: underline; }
  .features { margin-top: 28px; padding-top: 24px; border-top: 1px solid #f1f5f9; }
  .features .ftitle { font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 10px; }
  .features ul { list-style: none; }
  .features li { font-size: 12px; color: #94a3b8; line-height: 1.8; padding-left: 14px; position: relative; }
  .features li::before { content: "\\00B7"; position: absolute; left: 4px; color: #2563eb; font-weight: 700; }
</style>
</head>
<body>

<div class="login-box">
  <h1>PM岗位日报平台</h1>
  <p class="subtitle">输入您的访问码查看今日岗位日报</p>
  <div class="form-group">
    <label>访问码</label>
    <input type="password" id="accessCode" placeholder="请输入您的访问码" onkeydown="if(event.key==='Enter')doLogin()">
  </div>
  <button class="login-btn" onclick="doLogin()">查看我的日报 →</button>
  <p class="error-msg" id="errorMsg">访问码不正确，请重试</p>
  <div class="register-link">
    <a href="register.html">还没有访问码？新用户登记 →</a>
  </div>
  <div class="features">
    <div class="ftitle">平台功能</div>
    <ul>
      <li>多平台搜索：BOSS直聘、51job、鱼泡直聘</li>
      <li>深度JD匹配：读取完整JD，避免误推</li>
      <li>个性化话术：每岗位生成打招呼话术</li>
      <li>排除透明化：被排除岗位公示原因</li>
      <li>跨日去重：30天内已推送不重复</li>
      <li>一键复制链接：桌面端可直接打开</li>
    </ul>
  </div>
</div>

<script>
async function sha256(text) {
  const buf = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}
async function doLogin() {
  const code = document.getElementById('accessCode').value.trim();
  if (!code) return;
  const hash = await sha256(code);
  fetch('access.json')
    .then(r => r.json())
    .then(data => {
      const user = data.users.find(u => u.code_hash === hash);
      if (user) {
        const path = atob(user.path);
        window.location.href = path;
      } else {
        document.getElementById('errorMsg').style.display = 'block';
        document.getElementById('accessCode').value = '';
      }
    })
    .catch(() => {
      document.getElementById('errorMsg').textContent = '系统暂时无法验证，请稍后重试';
      document.getElementById('errorMsg').style.display = 'block';
    });
}
</script>
</body>
</html>'''

    output_path = os.path.join(BASE_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    # 1. 更新各用户的latest.html跳转页
    user_count = 0
    for user_dir in sorted(os.listdir(USERS_DIR)):
        if user_dir.startswith("_") or user_dir.startswith("."):
            continue
        user_path = os.path.join(USERS_DIR, user_dir)
        if not os.path.isdir(user_path):
            continue
        latest_report, _ = get_latest_report(user_path)
        if latest_report:
            update_latest_redirect(user_dir, latest_report)
            user_count += 1

    # 2. 更新access.json
    update_access_json()

    # 3. 生成登录首页
    generate_login_page()

    print(f"门户已更新：{user_count} 个用户的跳转页已刷新，登录首页已生成")
