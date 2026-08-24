#!/bin/bash
# PM日报 Git推送脚本 - 报告生成后自动同步到GitHub仓库
# 用法: bash scripts/git_push.sh "用户名" "报告日期"

set -e

PM_DAILY_DIR="/workspace/pm-daily"
cd "$PM_DAILY_DIR"

# 检查git是否已初始化
if [ ! -d ".git" ]; then
  echo "错误: Git仓库未初始化"
  exit 1
fi

# 检查远程仓库是否配置
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "错误: 未配置远程仓库，请先执行: git remote add origin <仓库URL>"
  exit 1
fi

# 更新门户首页
python3 scripts/update_portal.py 2>/dev/null || echo "提示: 门户首页更新跳过"

# 暂存所有变更
git add -A

# 检查是否有变更
if git diff --cached --quiet; then
  echo "没有变更需要推送"
  exit 0
fi

# 提交
COMMIT_MSG="${1:-PM日报} - ${2:-$(date +%Y-%m-%d)}"
git commit -m "$COMMIT_MSG"

# 推送
git push origin main

echo "推送成功: $COMMIT_MSG"
