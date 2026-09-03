# 安装与更新指南

## 从 GitHub 安装

注册 Git marketplace：

```powershell
codex plugin marketplace add cyitianyou-agent/ava-cloud-plus-devkit --ref main
```

安装插件：

```powershell
codex plugin add ava-cloud-plus-devkit@ava-cloud-plus-devkit
```

确认插件状态：

```powershell
codex plugin list --marketplace ava-cloud-plus-devkit
```

安装后新建 Codex 任务。已经打开的任务不会可靠地重新加载刚安装的 Skill。

## 获取 GitHub 上的新版本

刷新单个 marketplace 并重新安装插件：

```powershell
codex plugin marketplace upgrade ava-cloud-plus-devkit
codex plugin add ava-cloud-plus-devkit@ava-cloud-plus-devkit
```

也可以刷新所有已配置的 Git marketplace：

```powershell
codex plugin marketplace upgrade
```

GitHub 仓库提供了可更新源，但后台自动刷新频率由 Codex 客户端控制。上述命令是立即取得最新版的确定方式。

## 使用固定版本

需要稳定复现时，可在注册 marketplace 时固定 Git 标签：

```powershell
codex plugin marketplace add cyitianyou-agent/ava-cloud-plus-devkit@v0.1.0
```

固定标签不会跟随 `main` 更新。如需升级，应移除旧 marketplace 后用新标签重新注册。

## 本地开发安装

在仓库根目录运行：

```powershell
codex plugin marketplace add E:\github\ava-cloud-plus-devkit
codex plugin add ava-cloud-plus-devkit@ava-cloud-plus-devkit
```

修改后运行本地校验，再刷新 marketplace 并重新安装。不要手工编辑 Codex 的全局插件缓存。

## 常见问题

### marketplace 名称冲突

先运行 `codex plugin marketplace list` 查看已注册来源。如果已有同名 marketplace 指向其他仓库，请先确认来源再移除，避免误删其他插件来源。

### 新 Skill 没有出现

确认校验通过、marketplace 已升级且插件已重新安装，然后新建 Codex 任务。

### GitHub 仓库 owner 不同

本仓库发布地址为 `cyitianyou-agent/ava-cloud-plus-devkit`。如果未来迁移到其他 GitHub owner，必须同步修改 README、本文档以及 `.codex-plugin/plugin.json` 中的 URL。
