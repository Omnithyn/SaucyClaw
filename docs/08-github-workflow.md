# SaucyClaw GitHub 项目管理流程与开发规范

## 1. 项目定位

本项目采用 **GitHub Flow** 工作流，这是最适合开源项目和敏捷开发的标准流程。

## 2. 开发流程总览

```
开发前准备
    ↓
1. 创建开发分支
    ↓
2. 本地开发与测试
    ↓
3. 提交到远程分支
    ↓
4. 创建 Pull Request (PR)
    ↓
5. Code Review + CI 检查
    ↓
6. 合并到 main
    ↓
7. 删除开发分支
```

## 3. 分支命名规范

| 分支类型 | 命名格式 | 示例 | 说明 |
|---------|---------|------|------|
| 功能开发 | `feat/描述` | `feat/add-docker-support` | 新功能开发 |
| Bug 修复 | `fix/描述` | `fix/fix-lint-error` | Bug 修复 |
| 文档更新 | `docs/描述` | `docs/add-workflow-guide` | 文档修改 |
| 样式调整 | `style/描述` | `style/format-code` | 格式化、空格等 |
| 重构 | `refactor/描述` | `refactor/agent-structure` | 重构代码 |
| 测试 | `test/描述` | `test/add-unit-tests` | 测试相关 |
| 其他 | `chore/描述` | `chore/update-dependencies` | 依赖、配置等 |

**禁止直接推送到 main！**

## 4. 核心工作流程

### 4.1 创建开发分支

```bash
# 从 main 拉取最新代码
git fetch origin
git checkout -b feat/your-feature-name origin/main
```

### 4.2 本地开发

- 遵循现有代码风格
- 编写有意义的提交信息
- 使用 `pre-commit` 检查代码质量

### 4.3 提交与推送

```bash
# 添加修改
git add .

# 提交（会触发 commit-msg 检查）
git commit -m "feat: 添加新功能说明"

# 推送到远程（会触发 pre-push 检查）
git push origin feat/your-feature-name
```

### 4.4 创建 Pull Request

```bash
# 使用 GitHub CLI 快速创建
gh pr create --title "feat: 添加新功能" --body "详细说明..."
```

**PR 模板会自动填充，请完善以下内容：**

- 变更说明
- 关联 Issue（如 `Fixes #123`）
- 测试计划
- 检查清单

### 4.5 处理 Review 反馈

- 根据 reviewer 建议修改代码
- 每次修改后 `git push` 会自动更新 PR
- 在 PR 中回复评论，标记为已解决

### 4.6 合并与清理

```bash
# 合并后删除本地分支
git checkout main
git pull
git branch -d feat/your-feature-name

# 删除远程分支
git push origin --delete feat/your-feature-name
```

## 5. 提交信息规范

### 5.1 格式

```
type(scope): subject

body (可选)

footer (可选)
```

### 5.2 Type 说明

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 格式调整 |
| refactor | 代码重构 |
| test | 测试相关 |
| chore | 构建、依赖等 |
| perf | 性能优化 |
| revert | 回滚提交 |

### 5.3 示例

```
feat(agent): 添加角色创建脚本

- 实现 create_agent_role.sh 脚本
- 支持创建 specialist 角色
- 自动生成 AGENTS.md 和 PROMPT.md

Closes #42
```

## 6. Git Hooks 保护机制

### 6.1 已配置的 Hooks

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `pre-commit` | 提交前 | 代码格式检查、空格检查 |
| `commit-msg` | 提交信息确认前 | 验证提交信息格式 |
| `pre-push` | 推送前 | 阻止直接推送到 main、运行测试 |

### 6.2 配置说明

执行以下命令安装 hooks：

```bash
# 安装所有 hooks
./scripts/setup/setup-git-hooks.sh
```

或手动链接：

```bash
# 链接 hooks（项目根目录）
ln -sf ../../scripts/setup/git-hooks/pre-commit .git/hooks/pre-commit
ln -sf ../../scripts/setup/git-hooks/commit-msg .git/hooks/commit-msg
ln -sf ../../scripts/setup/git-hooks/pre-push .git/hooks/pre-push
```

## 7. main 分支保护规则

### 7.1 已启用的保护

| 规则 | 状态 |
|------|------|
| 禁止直接推送 | ✅ |
| 必需 Pull Request | ✅ |
| 必需 Code Review (1 人) | ✅ |
| 必需 CI 检查通过 | ✅ |
| 必需分支为最新 | ✅ |
| 必需解决所有评论 | ✅ |
| 管理员也无法绕过 | ✅ |

### 7.2 配置位置

**GitHub 网页端**：
`Settings → Branches → Branch protection rules → main → Edit`

**或使用 CLI**：

```bash
gh api \
  --method PUT \
  repos/Omnithyn/SaucyClaw/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -F required_pull_request_reviews='{"required_approving_review_count":1}' \
  -F required_status_checks='{"strict":true,"contexts":["CI"]}' \
  -F enforce_admins=true \
  -F required_conversation_resolution=true
```

## 8. 快速开发辅助脚本

### 8.1 创建开发分支

```bash
# 创建标准命名的开发分支
./scripts/utils/create-dev-branch.sh <type> <description>

# 示例
./scripts/utils/create-dev-branch.sh feat add-github-workflow
```

### 8.2 提交前检查

```bash
# 手动运行 pre-commit 检查
./scripts/validate/run-pre-commit.sh
```

### 8.3 快速创建 PR

```bash
# 一键创建 PR（自动填充模板）
./scripts/utils/create-pr.sh
```

### 8.4 完成后清理

```bash
# 合并后清理本地和远程分支
./scripts/utils/cleanup-merged-branch.sh
```

## 9. CI/CD 配置

### 9.1 GitHub Actions 工作流

| 工作流 | 触发条件 | 作用 |
|-------|---------|------|
| `ci.yml` | PR 或推送到 main | 运行 lint、test |
| `validate.yml` | 每次提交 | 验证项目结构 |
| `release.yml` | 打 tag | 自动发布版本 |

### 9.2 查看 CI 状态

```bash
# 查看最近的工作流运行
gh run list --limit 5

# 查看单次运行详情
gh run view <run-id>
```

## 10. 常见问题

### Q1: 忘记从最新 main 拉分支怎么办？

```bash
# 变基到最新 main
git checkout your-branch
git fetch origin
git rebase origin/main
```

### Q2: 如何处理合并冲突？

```bash
# 变基时遇到冲突
git status              # 查看冲突文件
# 手动解决冲突
git add <resolved-file> # 标记为已解决
git rebase --continue   # 继续变基
```

### Q3: 如何撤回已推送的提交？

```bash
# 撤回最后一次提交（保留修改）
git reset HEAD~1
git add .
git commit -m "重新提交"
git push --force        # 注意：只对开发分支操作
```

### Q4: hooks 被跳过怎么办？

```bash
# 禁用跳过选项
git config hooks.allowSkip false

# 或删除 --no-verify 标志
# 错误：git commit --no-verify
# 正确：git commit
```

## 11. 维护者专用命令

### 11.1 审查与合并

```bash
# 查看所有待审查的 PR
gh pr list --state open

# 审查 PR
gh pr review <pr-number> --approve --body "LGTM"

# 合并 PR
gh pr merge <pr-number> --squash --delete-branch
```

### 11.2 发布新版本

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions 会自动创建 Release
```

## 12. 实施清单

### 初次设置（必需）

- [ ] 安装 Git hooks：`./scripts/setup/setup-git-hooks.sh`
- [ ] 查看 CONTRIBUTING.md 了解详细规范
- [ ] 创建第一个测试分支：`./scripts/utils/create-dev-branch.sh test setup-github-flow`

### 日常开发

- [ ] 使用标准命名创建分支
- [ ] 提交时遵循提交信息规范
- [ ] 推送后立即创建 PR
- [ ] 根据反馈及时更新
- [ ] 合并后清理分支

---

**最后更新**：2026-03-18
**维护者**：Omnithyn
