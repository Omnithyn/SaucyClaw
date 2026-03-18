# 安全政策

感谢你帮助我们保护 SaucyClaw 项目的安全！如果你发现任何安全漏洞或问题，欢迎报告。

## 报告安全漏洞

如果你发现任何安全漏洞，请通过以下方式报告：

### 1. 安全邮件

发送邮件至：`felixyao2023@gmail.com`

邮件标题格式：`[SaucyClaw Security] <漏洞简述>`

邮件内容应包括：
- 漏洞描述
- 影响范围
- 重现步骤
- 建议的修复方案（如有）

### 2. 私密 Issue

如果邮件不可用，可以创建私密 Issue：

1. 访问 [GitHub Security](https://github.com/Omnithyn/SaucyClaw/security/advisories)
2. 点击 "Report a vulnerability"
3. 填写详细信息
4. 设置可见性为 "Private"

## 安全响应流程

我们承诺在收到安全报告后：

1. **24 小时内**确认收到报告
2. **48 小时内**评估漏洞严重性
3. **1 周内**制定修复计划并开始实施
4. **修复完成后**及时发布安全更新

## 期望

### 我们期望你：

- 给予我们合理的时间来修复漏洞（通常 90 天）
- 不公开披露漏洞，直到我们发布修复
- 提供足够的信息以重现问题
- 遵循负责任的披露原则

### 我们承诺：

- 及时响应并处理安全报告
- 保护报告者的隐私（除非获得许可）
- 在安全公告中致谢发现者（如获得许可）
- 提供修复状态的透明更新

## 安全范围

我们鼓励报告以下类型的安全问题：

- 代码注入漏洞
- 敏感信息泄露
- 权限绕过
- 依赖库的安全漏洞
- 社会工程学攻击向量
- 其他安全相关问题

## 非安全问题

以下问题通常不属于安全范围：

- 一般的功能 Bug
- 性能问题
- 用户体验问题
- 文档错误

这些问题请通过常规 [Issue](https://github.com/Omnithyn/SaucyClaw/issues) 渠道报告。

## 安全工具

项目使用以下工具进行安全检查：

- **Git Hooks**：pre-commit 检查敏感信息
- **GitHub Actions**：自动化安全扫描
- **依赖检查**：定期检查第三方依赖的安全更新

## 安全公告

重要安全更新将在以下渠道发布：

- [GitHub Releases](https://github.com/Omnithyn/SaucyClaw/releases)
- [GitHub Security Advisories](https://github.com/Omnithyn/SaucyClaw/security/advisories)
- [CHANGELOG.md](CHANGELOG.md)

## 致谢

我们感谢所有负责任地报告安全问题的研究人员和用户。你们的努力帮助我们创建更安全的软件。

---

**最后更新**：2026-03-18
**项目维护者**：Omnithyn
