# PM岗位日报系统 - 新用户初始化指南

## 初始化流程

当新用户（您的朋友）打开自己的Trae，发送类似以下消息时，按本指南执行初始化：

> "帮我设置产品经理岗位日报搜索" 或 "我想用PM日报系统"

### 第一步：收集用户画像

通过对话收集以下信息（可参考模板）：

1. **基本信息**：姓名、目标城市、是否接受出差
2. **职业信息**：目标职位、工作年限、学历、期望薪资
3. **行业经验**：核心行业经验、优先行业、排除行业
4. **方向偏好**：意向方向、排除方向
5. **系统能力**：核心系统经验、核心能力、最大亮点
6. **公司偏好**：排除的公司类型、是否接受代招/猎头、黑名单公司
7. **搜索平台**：想搜索哪些招聘平台
8. **搜索关键词**：想用哪些关键词搜索（可提供默认建议）

### 第二步：创建用户目录

```
/workspace/pm-daily/users/{user_id}/
  profile.json       # 用户画像
  blacklist.json     # 黑名单公司
  rules.json         # 规则配置（从shared/rules_template.json复制后定制）
  push_history.json  # 推送历史
  reports/           # 报告目录
```

### 第三步：生成配置文件

1. 复制 `users/_template/profile.json` 为 `users/{user_id}/profile.json`，填入用户信息
2. 复制 `shared/rules_template.json` 为 `users/{user_id}/rules.json`，根据用户需求定制
3. 创建 `users/{user_id}/blacklist.json`（格式参考现有用户的blacklist.json）
4. 创建空的 `users/{user_id}/push_history.json`

### 第四步：创建定时任务

使用Schedule工具创建每日定时任务，任务prompt中包含：
- 读取该用户的profile.json、rules.json、blacklist.json、push_history.json
- 按用户画像和规则搜索岗位
- 生成报告到 `users/{user_id}/reports/pm-jobs-YYYYMMDD.html`
- 更新push_history.json
- 报告生成完成后通知用户

### 第五步：生成首份报告

立即触发一次报告生成，让用户看到效果。

### 第六步（Phase 2）：配置GitHub推送

如果中央网站已部署：
1. 将用户的GitHub账号添加为仓库协作者
2. 在用户的定时任务中加入git push步骤
3. 告知用户中央网站访问地址

## 用户ID命名规则

使用拼音首字母小写，如：jiangjunyu、zhangwei、limin

## 注意事项

- 每个用户的规则可以独立定制，互不影响
- 用户可以随时通过对话调整自己的画像和规则
- 黑名单公司是用户级别的，不共享
- 推送历史是用户级别的，不共享
