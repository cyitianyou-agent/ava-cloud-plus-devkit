# 贡献指南

## 开发约定

- 每个 Skill 放在 `skills/<skill-name>/`，目录名必须与 `SKILL.md` frontmatter 的 `name` 完全一致。
- Skill 必须自包含；引用文件使用相对路径，不依赖作者电脑上的绝对路径。
- 模板、示例和参考资料只提交可公开内容，不提交客户数据、报表凭据、数据库连接串或生成产物。
- 新增或修改规则时同步更新相关参考文档和 `CHANGELOG.md`。

## 提交前检查

```powershell
python scripts/validate.py
```

建议使用 Conventional Commits 风格：

- `feat:` 新能力或新 Skill
- `fix:` 规则、模板或文档修复
- `docs:` 仅文档变更
- `chore:` 构建、校验或维护变更

Pull Request 应说明修改动机、影响的 Skill、验证方式，以及是否改变既有生成结果或工作流。
