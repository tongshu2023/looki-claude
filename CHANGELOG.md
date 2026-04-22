# 变更记录

## [0.1.0] - 2026-04-22

首个公开版本。

### 新增
- Python 零依赖客户端(`src/looki_client.py`),覆盖全部 7 个 API 端点
- ffmpeg 视频抽帧工具(`src/frames.py`),自动查找 winget 安装路径
- Windows/Mac/Linux 初始化脚本(`setup/setup.ps1` + `setup/setup.sh`)
- Claude Skill 元数据(`SKILL.md`),内置中文触发词
- 5 分钟 QuickStart 文档
- 作者亲测的踩坑录(`docs/API-GOTCHAS.md`),10 个已知坑
- 3 个示例 prompt:每日镜像简报、薄荷精选短视频、教学金句捕手
- 完整 `.gitignore` 保护凭证和用户数据

### 已知限制
- 暂未封装音频抽取/转录(v0.2 跟进 whisper)
- MCP server 版本待 v1.0
