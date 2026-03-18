# GitHub Flow 辅助工具说明

本目录包含一系列辅助脚本，帮助你更高效地使用 GitHub Flow 工作流。

## 目录说明

```
scripts/utils/
├── create-dev-branch.sh       # 创建标准命名的开发分支
├── create-pr.sh               # 快速创建 Pull Request（无需 gh）
├── cleanup-merged-branch.sh   # 清理已合并/已删除的分支
├── update-branch.sh           # 更新分支到最新 main
├── check-branch-status.sh     # 检查分支状态
└── revert-last-commit.sh      # 回退最后一次提交
```

---

## 脚本详细说明

### 1. 创建开发分支

**脚本**: `create-dev-branch.sh`

**用途**: 快速创建符合命名规范的开发分支

**用法**:
```bash
./scripts/utils/create-dev-branch.sh <type> <description>
```

**参数**:
- `type`: 分支类型（feat/fix/docs/style/refactor/test/chore/perf）
- `description`: 简短描述（使用小写字母和连字符）

**示例**:
```bash
# 创建功能开发分支
./scripts/utils/create-dev-branch.sh feat add-new-feature

# 创建 Bug 修复分支
./scripts/utils/create-dev-branch.sh fix lint-error

# 创建文档更新分支
./scripts/utils/create-dev-branch.sh docs update-readme
```

**效果**:
- 从最新 main 拉取代码
- 创建命名规范的分支（如 `feat/add-new-feature`）
- 自动切换到新分支

---

### 2. 创建 Pull Request

**脚本**: `create-pr.sh`

**用途**: 快速生成创建 PR 的 URL 和模板内容（无需安装 GitHub CLI）

**用法**:
```bash
./scripts/utils/create-pr.sh
```

**前提条件**:
- 当前分支已推送到远程
- 不在 main 或 develop 分支

**效果**:
- 生成 PR 创建链接
- 输出完整的 PR 模板内容
- 提供手动创建步骤指引

**示例输出**:
```
===================================
🦞 创建 Pull Request
===================================

✅ 准备创建 Pull Request

当前分支：feat/add-new-feature
远程仓库：Omnithyn/SaucyClaw

===================================
📋 请访问以下 URL 创建 PR：
===================================

https://github.com/Omnithyn/SaucyClaw/compare/main...feat/add-new-feature?expand=1

PR 模板内容（复制到 PR 描述中）：
...
```

---

### 3. 清理已合并分支

**脚本**: `cleanup-merged-branch.sh`

**用途**: 清理远程已删除的本地分支

**用法**:
```bash
./scripts/utils/cleanup-merged-branch.sh
```

**前提条件**:
- 当前在 main 分支

**效果**:
- 查找所有远程已删除但本地仍存在的分支
- 交互式确认删除
- 清理本地分支

**示例**:
```bash
# 在 main 分支执行
git checkout main
./scripts/utils/cleanup-merged-branch.sh

# 输出
找到以下已删除的远程分支：
  - feat/add-feature
  - fix/lint-error

是否删除这些本地分支？(y/N):
```

---

### 4. 更新分支

**脚本**: `update-branch.sh`

**用途**: 将当前分支变基到最新 main

**用法**:
```bash
./scripts/utils/update-branch.sh
```

**前提条件**:
- 当前在开发分支

**效果**:
- 拉取最新 main
- 执行 rebase 操作
- 如果有冲突，提示手动解决

**使用场景**:
- 提交了 PR 后，main 有新提交需要同步
- 长时间开发后需要更新代码

**示例**:
```bash
# 在开发分支执行
./scripts/utils/update-branch.sh

# 如果成功
✅ 变基成功！

# 如果有冲突
❌ 变基失败，存在冲突

请手动解决冲突：
  1. git status          # 查看冲突文件
  2. 编辑冲突文件
  3. git add <文件>      # 标记为已解决
  4. git rebase --continue
```

---

### 5. 检查分支状态

**脚本**: `check-branch-status.sh`

**用途**: 全面检查当前分支状态

**用法**:
```bash
./scripts/utils/check-branch-status.sh
```

**检查内容**:
- 当前分支
- 所有本地分支及其最新提交
- 是否有未推送的提交
- 是否有未提交的修改
- 是否有远程已删除的本地分支（gone）

**示例输出**:
```
===================================
🦞 分支状态检查
===================================

当前分支：feat/add-new-feature

本地分支：
* feat/add-new-feature  abc1234 最新提交信息
  main                  def4567 main 的提交

检查未推送的提交：
⚠️  有未推送的提交：
commit abc1234...

检查未提交的修改：
✅ 工作目录干净

检查远程已删除的本地分支：
✅ 无 gone 分支
```

---

### 6. 回退最后一次提交

**脚本**: `revert-last-commit.sh`

**用途**: 回退最后一次提交但保留修改

**用法**:
```bash
./scripts/utils/revert-last-commit.sh
```

**效果**:
- 撤销最后一次提交
- 保留所有修改在暂存区
- 可以重新提交或修改

**使用场景**:
- 提交信息写错了
- 想修改提交内容
- 合并前需要调整

**示例**:
```bash
# 回退后可以
git commit -m "正确的提交信息"
git push --force-with-lease
```

---

## 验证脚本

### 7. 运行 Pre-commit 检查

**脚本**: `../validate/run-pre-commit.sh`

**用途**: 手动运行所有 pre-commit 检查

**用法**:
```bash
./scripts/validate/run-pre-commit.sh
```

**检查内容**:
- 行尾空格
- 是否有实际修改
- 大文件 (>100KB)
- Python 语法
- Shell 语法

**使用场景**:
- 提交前手动验证
- 调试 hooks 问题

---

## 快速工作流示例

### 完整开发流程

```bash
# 1. 创建开发分支
./scripts/utils/create-dev-branch.sh feat add-new-feature

# 2. 进行开发工作
vim your_file.py

# 3. 手动运行检查（可选）
./scripts/validate/run-pre-commit.sh

# 4. 提交
git add .
git commit -m "feat(scripts): add new feature"

# 5. 推送
git push origin feat/add-new-feature

# 6. 创建 PR
./scripts/utils/create-pr.sh

# 7. （如果需要）更新分支
./scripts/utils/update-branch.sh

# 8. 合并 PR 后，切换到 main
git checkout main
git pull

# 9. 清理分支
./scripts/utils/cleanup-merged-branch.sh
```

### 常见问题处理

**忘记运行检查？**
```bash
# 手动触发检查
./scripts/validate/run-pre-commit.sh
```

**分支落后于 main？**
```bash
./scripts/utils/update-branch.sh
```

**提交信息写错了？**
```bash
./scripts/utils/revert-last-commit.sh
git commit -m "正确的信息"
git push --force-with-lease
```

**想知道当前状态？**
```bash
./scripts/utils/check-branch-status.sh
```

---

## 脚本依赖

所有脚本仅依赖：
- Bash (v3.2+)
- Git (v2.0+)
- 标准 Unix 工具 (grep, sed, awk)

无需额外安装工具。

---

## 故障排除

### 脚本没有执行权限

```bash
chmod +x scripts/utils/*.sh
chmod +x scripts/validate/*.sh
```

### 脚本找不到路径

确保在项目根目录执行：
```bash
cd /Users/yaochunyang/tools/AIGC/agent/SaucyClaw
./scripts/utils/create-dev-branch.sh feat test
```

### hooks 没有生效

安装 hooks：
```bash
./scripts/setup/setup-git-hooks.sh
```

---

## 贡献新脚本

如果你有好的想法，可以：
1. 在 `scripts/utils/` 或 `scripts/validate/` 下创建新脚本
2. 添加执行权限：`chmod +x your-script.sh`
3. 在本文档中添加说明
4. 提交到仓库

---

**最后更新**: 2026-03-18
**维护者**: Omnithyn
