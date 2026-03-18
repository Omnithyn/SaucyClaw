# 贡献指南

欢迎为 SaucyClaw 项目做出贡献！本指南将帮助你快速上手。

## 目录

- [开发环境设置](#开发环境设置)
- [开发流程](#开发流程)
- [提交规范](#提交规范)
- [分支管理](#分支管理)
- [代码规范](#代码规范)
- [测试要求](#测试要求)

## 开发环境设置

### 1. Fork 项目

在 GitHub 上点击 "Fork" 按钮，将项目复制到你的账号下。

### 2. 克隆仓库

```bash
git clone https://github.com/Omnithyn/SaucyClaw.git
cd SaucyClaw
```

### 3. 安装 Git Hooks

```bash
./scripts/setup/setup-git-hooks.sh
```

这些 hooks 会在你提交和推送代码时自动进行检查，确保代码质量。

### 4. 安装 Python 依赖（如果需要）

```bash
cd tools
pip install -r requirements.txt
```

## 开发流程

### 1. 创建开发分支

使用标准命名创建分支：

```bash
# 使用脚本创建
./scripts/utils/create-dev-branch.sh feat add-new-feature

# 或手动创建
git checkout -b feat/add-new-feature
```

### 2. 进行开发

- 遵循项目目录结构
- 参考现有代码风格
- 编写清晰的注释

### 3. 运行检查

```bash
# 验证项目结构
scripts/validate/check_structure.sh

# 运行所有 pre-commit 检查
scripts/validate/run-pre-commit.sh
```

### 4. 提交代码

```bash
git add .
git commit -m "feat(scope): 简短描述

详细说明（可选）

关联 issue: Fixes #123"
```

### 5. 推送并创建 PR

```bash
git push origin feat/add-new-feature
gh pr create
```

## 提交规范

### 格式

```
type(scope): subject

body (可选)

footer (可选)
```

### Type 说明

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构（既不修复 bug 也不添加功能） |
| `test` | 添加缺失的测试或修正现有测试 |
| `chore` | 构建过程或辅助工具的变动 |

### 示例

```bash
# 新功能
git commit -m "feat(agent): 添加角色创建脚本"

# Bug 修复
git commit -m "fix(lint): 修复行尾空格问题"

# 文档更新
git commit -m "docs(readme): 更新安装指南"

# 重构
git commit -m "refactor(scripts): 重构验证脚本结构"
```

## 分支管理

### 命名规范

```
类型/描述
```

示例：
- `feat/add-github-workflow`
- `fix/lint-error`
- `docs/update-contribution-guide`

### 流程

1. 从 `main` 创建分支
2. 完成开发后推送
3. 创建 Pull Request
4. Code Review
5. 合并到 `main`
6. 删除分支

**禁止直接推送到 `main`！**

## 代码规范

### Shell 脚本

- 使用 `set -euo pipefail`
- 添加注释说明功能
- 使用函数组织代码
- 错误处理要完善

### Python 代码

- 遵循 PEP 8 规范
- 使用类型提示
- 添加 docstring
- 保持函数简短

### Markdown 文档

- 使用标准标题层级
- 代码块标注语言
- 链接使用相对路径
- 图片存放在 `assets/`

## 测试要求

### 运行现有测试

```bash
# 验证项目结构
scripts/validate/check_structure.sh

# 检查所有 YAML 文件
python3 -c "
import yaml
import sys
import glob
for file in glob.glob('**/*.yaml', recursive=True) + glob.glob('**/*.yml', recursive=True):
    if '.git' not in file:
        try:
            yaml.safe_load(open(file))
        except Exception as e:
            print(f'❌ {file}: {e}')
            sys.exit(1)
print('✅ 所有 YAML 文件格式正确')
"
```

### 添加新测试

如果新增了功能，请同时添加相应的测试：

1. 在 `scripts/validate/` 中添加验证脚本
2. 在 `tools/saucyclaw/tests/` 中添加单元测试
3. 更新文档说明如何测试

## Pull Request 检查清单

在创建 PR 前，请确保：

- [ ] 代码已通过 `pre-commit` 检查
- [ ] 提交信息符合规范
- [ ] 已添加/更新测试（如适用）
- [ ] 文档已同步更新
- [ ] 变更日志已更新（如适用）
- [ ] 已在本地测试功能

## 常见问题

### Q: 如何处理合并冲突？

```bash
git fetch origin
git rebase origin/main
# 解决冲突后
git add .
git rebase --continue
```

### Q: 忘记运行 hooks 怎么办？

```bash
# 重新触发 pre-commit
git commit --amend --no-edit
```

### Q: 分支命名错误了怎么办？

```bash
git branch -m 旧名称 新名称
git push origin -u 新名称
git push origin --delete 旧名称
```

## 获取帮助

- 查看 [GitHub 工作流文档](../docs/08-github-workflow.md)
- 在 [Discussions](https://github.com/Omnithyn/SaucyClaw/discussions) 中提问
- 提交 [Issue](https://github.com/Omnithyn/SaucyClaw/issues)

## 行为准则

请遵守项目的 [行为准则](CODE_OF_CONDUCT.md)，保持友好和尊重的沟通环境。

---

感谢你的贡献！🎉
