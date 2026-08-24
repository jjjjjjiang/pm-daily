#!/usr/bin/env python3
"""
门户首页更新脚本 - 扫描users目录下所有用户的报告，自动生成多用户门户首页
每次报告推送后执行此脚本更新index.html
"""
import os
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_DIR = os.path.join(BASE_DIR, "users")

def scan_users():
    """扫描所有用户及其最新报告"""
    users = []
    for user_dir in sorted(os.listdir(USERS_DIR)):
        if user_dir.startswith("_") or user_dir.startswith("."):
            continue
        user_path = os.path.join(USERS_DIR, user_dir)
        if not os.path.isdir(user_path):
            continue

        # 读取用户画像
        profile_path = os.path.join(user_path, "profile.json")
        profile = {}
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)

        # 扫描报告
        reports_dir = os.path.join(user_path, "reports")
        reports = []
        if os.path.isdir(reports_dir):
            reports = sorted(glob.glob(os.path.join(reports_dir, "pm-jobs-*.html")), reverse=True)

        latest_report = os.path.basename(reports[0]) if reports else None
        report_path = f"/users/{user_dir}/reports/{latest_report}" if latest_report else "#"

        # 统计最新报告中的岗位数（简单解析HTML）
        job_count = 0
        high_count = 0
        if reports:
            try:
                with open(reports[0], "r", encoding="utf-8") as f:
                    content = f.read()
                    job_count = content.count('class="high-row"') + content.count('class="med-row"')
                    high_count = content.count('class="high-row"')
            except:
                pass

        # 提取日期
        report_date = ""
        if latest_report:
            # pm-jobs-20260824.html -> 2026-08-24
            date_str = latest_report.replace("pm-jobs-", "").replace(".html", "")
            if len(date_str) == 8:
                report_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        job_target = profile.get("job_target", {})
        directions = profile.get("target_directions", {}).get("preferred", [])

        users.append({
            "user_id": user_dir,
            "user_name": profile.get("user_name", user_dir),
            "role": f"{job_target.get('target_role', '产品经理')} · {job_target.get('city', '')}",
            "experience": f"{job_target.get('experience_years', '')}年经验",
            "salary": job_target.get("salary_range", ""),
            "directions": "/".join(directions[:2]) if directions else "",
            "report_path": report_path,
            "report_date": report_date,
            "job_count": job_count,
            "high_count": high_count,
        })

    return users

def generate_index(users):
    """生成门户首页HTML"""
    user_cards = ""
    for u in users:
        info_chips = ""
        if u["experience"]:
            info_chips += f'<span>{u["experience"]}</span>'
        if u["salary"]:
            info_chips += f'<span>{u["salary"]}</span>'
        if u["directions"]:
            info_chips += f'<span>{u["directions"]}</span>'

        last_text = f'最新报告：{u["report_date"]}（{u["job_count"]}个岗位）' if u["report_date"] else "暂无报告"

        user_cards += f'''    <a class="user-card" href="{u["report_path"]}">
      <div class="uname">{u["user_name"]}</div>
      <div class="urole">{u["role"]}</div>
      <div class="uinfo">{info_chips}</div>
      <div class="ulast">{last_text}</div>
    </a>
'''

    today = datetime.now().strftime("%Y-%m-%d")

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PM岗位招聘日报平台</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif;
    background: #f0f2f5; color: #1a2332; min-height: 100vh;
  }}
  .nav {{
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    color: #fff; padding: 16px 24px; display: flex; align-items: center;
    justify-content: space-between; position: sticky; top: 0; z-index: 100;
  }}
  .nav .logo {{ font-size: 18px; font-weight: 700; }}
  .nav .logo span {{ opacity: 0.7; font-weight: 400; font-size: 13px; margin-left: 8px; }}
  .nav .admin {{ font-size: 12px; opacity: 0.7; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}
  .hero {{ text-align: center; margin-bottom: 40px; }}
  .hero h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .hero p {{ font-size: 14px; color: #6b7a8f; }}
  .section-title {{ font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #1a2332; }}
  .user-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 40px; }}
  .user-card {{
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
    text-decoration: none; color: inherit; transition: all 0.2s; display: block;
    border-left: 4px solid #2563eb;
  }}
  .user-card:hover {{ box-shadow: 0 4px 16px rgba(37,99,235,0.1); transform: translateY(-2px); }}
  .user-card .uname {{ font-size: 17px; font-weight: 700; margin-bottom: 4px; }}
  .user-card .urole {{ font-size: 13px; color: #6b7a8f; margin-bottom: 8px; }}
  .user-card .uinfo {{ font-size: 12px; color: #94a3b8; display: flex; flex-wrap: wrap; gap: 6px; }}
  .user-card .uinfo span {{ background: #f1f5f9; padding: 2px 8px; border-radius: 10px; }}
  .user-card .ulast {{ font-size: 12px; color: #2563eb; margin-top: 10px; font-weight: 500; }}
  .add-user {{
    background: #fff; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px;
    text-align: center; color: #6b7a8f; transition: all 0.2s; cursor: pointer;
  }}
  .add-user:hover {{ border-color: #2563eb; color: #2563eb; }}
  .add-user .icon {{ font-size: 28px; margin-bottom: 6px; }}
  .add-user .text {{ font-size: 13px; }}
  .features {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 32px; }}
  .feature {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }}
  .feature .ftitle {{ font-size: 13px; font-weight: 600; margin-bottom: 4px; }}
  .feature .fdesc {{ font-size: 12px; color: #6b7a8f; line-height: 1.6; }}
  .footer {{ text-align: center; padding: 24px 0; color: #94a3b8; font-size: 12px; }}
</style>
</head>
<body>

<div class="nav">
  <div class="logo">PM岗位日报平台 <span>每日自动搜索 · 智能匹配 · 一键投递</span></div>
  <div class="admin">管理员：江骏昱</div>
</div>

<div class="container">
  <div class="hero">
    <h1>产品经理岗位招聘日报</h1>
    <p>多平台智能搜索 · 简历深度匹配 · 个性化投递话术</p>
  </div>

  <div class="section-title">用户报告</div>
  <div class="user-grid">
{user_cards}    <div class="add-user" onclick="alert('新用户请在自己的Trae中发送：帮我设置PM岗位日报搜索\\n\\n系统将引导您完成初始化配置。')">
      <div class="icon">+</div>
      <div class="text">添加新用户<br><span style="font-size:11px;opacity:0.7">在Trae中初始化</span></div>
    </div>
  </div>

  <div class="section-title">平台功能</div>
  <div class="features">
    <div class="feature"><div class="ftitle">多平台搜索</div><div class="fdesc">BOSS直聘、51job、鱼泡直聘同步搜索，覆盖更广</div></div>
    <div class="feature"><div class="ftitle">深度JD匹配</div><div class="fdesc">读取完整JD内容，不只是关键词匹配，避免误推</div></div>
    <div class="feature"><div class="ftitle">个性化话术</div><div class="fdesc">每岗位生成BOSS直聘打招呼话术，从简历提取匹配亮点</div></div>
    <div class="feature"><div class="ftitle">排除透明化</div><div class="fdesc">被排除的岗位公示原因，不怕误判错过机会</div></div>
    <div class="feature"><div class="ftitle">跨日去重</div><div class="fdesc">30天内已推送岗位不重复列入，节省投递时间</div></div>
    <div class="feature"><div class="ftitle">一键复制链接</div><div class="fdesc">桌面端链接可直接打开，复制按钮一键获取URL</div></div>
  </div>

  <div class="footer">
    <p>PM岗位日报平台 · 最后更新：{today} · 管理员：江骏昱</p>
  </div>
</div>

</body>
</html>'''

    return html

if __name__ == "__main__":
    users = scan_users()
    html = generate_index(users)
    output_path = os.path.join(BASE_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"门户首页已更新，共 {len(users)} 个用户")
