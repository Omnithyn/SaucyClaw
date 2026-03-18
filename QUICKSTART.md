# 快速开始：GitHub Flow 工作流

## 5 分钟上手指南

### 第 1 步：安装 hooks（一次性）

```bash
./scripts/setup/setup-git-hooks.sh
```

✅ 完成！现在你的本地仓库已配置保护机制。

### 第 2 步：创建开发分支

```bash
./scripts/utils/create-dev-branch.sh feat your-feature-name
```

示例：
```bash
./scripts/utils/create-dev-branch.sh feat add-new-validator
```

### 第 3 步：开发工作

```bash
# 编辑文件
vim your_file.py

# 添加修改
git add .

# 提交（自动触发 hooks 检查）
git commit -m "feat(scripts): add new validator"
```

### 第 4 步：推送并创建 PR

```bash
# 推送到远程
git push origin feat/add-new-validator

# 使用 GitHub CLI 创建 PR
gh pr create

# 或手动访问：https://github.com/Omnithyn/SaucyClaw/compare
```

### 第 5 步：处理反馈并合并

```bash
# 根据 reviewer 建议修改
git add .
git commit -m "fix: address review feedback"

# 推送更新（自动更新 PR）
git push

# PR 合并后清理
git checkout main
git pull
git branch -d feat/add-new-validator
```

---

## 常用命令速查

### 创建分支

```bash
./scripts/utils/create-dev-branch.sh <type> <description>
```

### 检查代码

```bash
# 运行所有 pre-commit 检查
scripts/validate/check_structure.sh

# 手动触发 hooks
git commit --amend --no-edit
```

### 创建/管理 PR

```bash
# 创建 PR
gh pr create

# 查看所有 PR
gh pr list

# 查看 PR 详情
gh pr view <number>

# 合并 PR
gh pr merge <number> --squash --delete-branch
```

### 常见操作

```bash
# 更新分支到最新 main
git fetch origin
git rebase origin/main

# 查看当前分支
git branch

# 切换分支
git checkout main

# 删除本地分支
git branch -d <branch-name>

# 删除远程分支
git push origin --delete <branch-name>
```

---

## 重要提醒

⚠️ **禁止直接推送到 main！**

✅ **正确流程**：
```
main → 创建分支 → 开发 → 提交 → 推送 → 创建 PR → Review → 合并
```

---

## 故障排除

### hooks 没有触发？

```bash
# 重新安装
./scripts/setup/setup-git-hooks.sh

# 检查权限
ls -la .git/hooks/
```

### 提交信息格式错误？

正确格式：
```bash
git commit -m "feat(scope): description"
git commit -m "fix(lint): remove trailing whitespace"
git commit -m "docs(readme): update installation guide"
```

### 忘记创建分支直接在 main 修改了？

```bash
# 创建新分支保存修改
git checkout -b feat/your-feature

# 返回 main 并清理
git checkout main
git reset --hard origin/main

# 切换回开发分支继续工作
git checkout feat/your-feature
```

---

## 获取帮助

- 📖 [完整工作流文档](docs/08-github-workflow.md)
- 🤝 [贡献指南](CONTRIBUTING.md)
- ❓ [实施方案总结](IMPLEMENTATION_SUMMARY.md)
- 💬 [GitHub Discussions](https://github.com/Omnithyn/SaucyClaw/discussions)

---

**开始你的第一个贡献吧！🎉**
