# PM岗位日报平台

## 结构
```
pm-daily/
├── index.html                    # 门户首页（多用户）
├── register.html                 # 新用户登记页面
├── shared/                       # 共享资源
│   ├── rules_template.json       # 规则模板
│   ├── onboarding_guide.md       # 初始化指南
│   └── setup_prompt.md           # 新用户引导Prompt
├── users/                        # 用户目录
│   ├── _template/                # 模板
│   └── {user_id}/                # 各用户独立目录
│       └── reports/              # 日报目录（HTML报告公开可访问）
│           └── pm-jobs-YYYYMMDD.html
└── scripts/                      # 脚本
    └── update_portal.py          # 门户首页更新脚本
```

## 隐私说明
以下配置文件包含个人信息，**不会**推送到GitHub：
- `profile.json` - 用户画像
- `blacklist.json` - 公司黑名单
- `rules.json` - 规则配置
- `push_history.json` - 推送历史

这些文件通过 `.gitignore` 排除，仅在本地工作目录中保留，供定时任务读取。
只有HTML报告文件会被推送到GitHub Pages供用户和朋友查看。

## GitHub Pages 部署
1. 仓库Settings → Pages → Source: Deploy from branch → main → /(root)
2. 访问地址: https://{username}.github.io/pm-daily/

## 新用户接入
1. 用户在自己的Trae中发送 shared/setup_prompt.md 中的引导Prompt
2. 系统自动创建配置 + 定时任务 + 首份报告
3. 报告生成后执行 git push 同步到本仓库（仅HTML报告）
4. GitHub Pages自动更新，门户首页展示新用户
