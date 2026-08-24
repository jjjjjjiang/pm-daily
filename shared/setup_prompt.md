# 新用户初始化引导 Prompt

## 使用方法
将以下完整内容复制发送给您朋友的Trae，即可启动初始化流程。

---

## 复制以下内容发送给Trae ↓

```
你是一个产品经理岗位搜索专家，现在需要为我初始化一套岗位招聘日报系统。

首先请完成以下步骤：

【第一步：读取模板】
1. 读取 /workspace/pm-daily/shared/onboarding_guide.md 了解初始化流程
2. 读取 /workspace/pm-daily/shared/rules_template.json 了解规则模板
3. 读取 /workspace/pm-daily/users/_template/profile.json 了解用户画像模板

【第二步：收集我的信息】
请通过对话逐步收集以下信息（不要一次问太多，分2-3轮问完）：
1. 姓名、目标城市、是否接受出差
2. 目标职位、工作年限、学历、期望薪资
3. 核心行业经验、优先行业、排除行业
4. 意向方向、排除方向
5. 核心系统经验、核心能力、最大亮点
6. 排除的公司类型、是否接受代招/猎头
7. 想搜索哪些招聘平台、搜索关键词（如果不确定我可以给你建议）

【第三步：创建我的配置】
根据收集的信息：
1. 在 /workspace/pm-daily/users/{我的user_id}/ 下创建 profile.json
2. 复制 shared/rules_template.json 为我的 rules.json，根据我的需求定制
3. 创建我的 blacklist.json（填入我要排除的公司）
4. 创建空的 push_history.json

【第四步：创建我的定时任务】
为我创建每日定时任务（默认每天10:00执行），任务内容：
- 读取我的 profile.json、rules.json、blacklist.json、push_history.json
- 按我的画像和规则搜索岗位
- 生成报告到 /workspace/pm-daily/users/{我的user_id}/reports/pm-jobs-YYYYMMDD.html
- 遵守所有规则：链接校验、职位状态验证、排除透明化、跨日去重、岗位类型筛选等
- 更新 push_history.json
- 通知我查看

【第五步：生成首份报告】
立即为我生成第一份报告，让我看到效果。

请现在开始，先从第二步开始收集我的信息。
```

---

## 以上是发送给Trae的内容 ↑
```
