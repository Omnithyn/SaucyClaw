# 如何使用 SaucyClaw 的 Hardness 资产

## 1. 第一次接手项目时

建议顺序：

1. 先读 `README.md`
2. 再读 `AGENTS.md` 与 `CLAUDE.md`
3. 再读 `system/SYSTEM_SPEC.md`
4. 再读 `system/HARDNESS_ENGINEERING.md`
5. 再读 `agents/general-manager/AGENTS.md`
6. 最后查看 `evals/` 与 `templates/`

## 2. 想验证团队是否已经具备基本硬度时

建议做法：

1. 运行已有 smoke task
2. 查看 `evals/scenarios/`
3. 对照 `evals/rubrics/team-hardness-rubric.md`
4. 在 `evals/reports/` 中记录结论

## 3. 想增加新角色时

建议先回答：

- 这个角色是交付角色，还是检查角色？
- 它会不会与已有角色重叠？
- 它的输出是最终交付，还是中间判断？

## 4. 想增加新场景时

建议至少写清：

- 场景目的
- 输入示例
- 期待行为
- 常见失败信号

## 5. 想继续重写系统主文档时

建议优先顺序：

1. `system/SYSTEM_SPEC.md`
2. `system/ORCHESTRATION.md`
3. `system/STANDARDS.md`
4. `docs/01-project-overview.md`
5. `README.md`
