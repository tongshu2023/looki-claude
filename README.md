# looki-claude

**首个面向中文用户的 Looki L1 × Claude 深度接入 skill 包。** 把你 Looki 里的每一秒,交给 Claude 读。

> 💼 **Pro 版 & 合作** · 见 [PRO.md](PRO.md)
> 🎓 **老师训练营**(筹备中) · Watch 本仓库第一时间通知
> 🤝 **企业/机构定制** · 📧 tongshu2023@gmail.com
> ☕ **支持作者** · [爱发电](https://ifdian.net/u/ca2ef6ac3e5011f18cdb5254001e7c00) · 5 元起步,帮作者多买一杯咖啡

> Looki L1 是一个 30g 多模态 AI 穿戴设备(2026 CES 发布,融资超 1000 万美元),可穿戴相机 + 麦克风 + 自动识别生活场景。
> 这个项目:让 Claude 作为你的"第二大脑驾驶员",直接读你 Looki 里的每一帧、每一句、每一次对话,做远超 Looki 原生 AI 的分析 —— 镜像简报、教学金句库、关系图谱、短视频素材自动挑选。

---

## 为什么要这个?

Looki 自带的 AI(comic/vlog/for you)**是二手的**:它会把"一个人低头吃饭+别人在聊天"的场景自动叙事成"与同伴谈笑风生"。所有用户共用一套模板。

**Claude 视角不同**:它读你的原始数据(照片、视频帧、音频、位置、时间),结合你自己的上下文(日记、项目、记忆),能给出**一手且个性化**的解读。你想让它当镜子,就是镜子;想让它当剪辑助理,就是剪辑助理;想让它做家长观课报告,它就能做。

---

## 5 分钟跑通

```bash
# 1. 拉代码
git clone https://github.com/tongshu2023/looki-claude.git ~/.claude/skills/looki-claude
cd ~/.claude/skills/looki-claude

# 2. 装 Looki API Key(见 docs/QUICKSTART.md 拿 key 方法)
#   Windows:
powershell ./setup/setup.ps1
#   Mac/Linux:
bash ./setup/setup.sh

# 3. 验证通过
python src/looki_client.py me
# 应输出你的 Looki 账户信息
```

装完后,在 Claude Code 里直接说:

- `"调 looki 拿最近 7 天的 moment 日历"` → Claude 自动调 API
- `"找出最近所有薄荷出现的 moment,列清单"` → 语义搜索
- `"给我看 2026-04-17 畅骑绿道那条 moment 的所有照片"` → 下载原图 Claude 亲自看
- `"根据最近 30 天数据,写一份我的天赋与压抑镜像简报"` → 高级用法

---

## 能力全景

| 能力 | API 端点 | 典型玩法 |
|---|---|---|
| 用户信息 | `GET /me` | 验证连接 |
| 日期列 moments | `GET /moments?on_date=` | 逐日回溯 |
| 语义搜索 | `GET /moments/search` | "找所有金毛/讲课/深夜谈心" |
| 日历视图 | `GET /moments/calendar` | 30 天概览 |
| moment 详情 | `GET /moments/{id}` | 单条钻取 |
| moment 文件列表 | `GET /moments/{id}/files` | 拉原图/原视频 URL |
| For You | `GET /for_you/items` | Looki 原生 AI 内容(可选) |

本 skill 还提供:

- `src/looki_client.py` — 零依赖 Python 客户端(只用标准库)
- `src/frames.py` — ffmpeg 自动抽帧(Looki 默认全是 10 秒视频,无缩略图,必需)
- `examples/` — 镜像简报、薄荷精选、金句捕手等 prompt 模板

---

## 路线图

- [x] v0.1 · MVP 客户端 + 7 端点 + 抽帧 + QuickStart
- [ ] v0.2 · 音频抽取 + whisper 转录
- [ ] v0.3 · Claude Skill 原生触发词(`调 looki`/`搜 looki`)
- [ ] v1.0 · MCP server 版本,Claude Desktop 一键安装
- [ ] v1.1 · Web 可视化(日历+地图+情绪曲线)

---

## 坑

看 [`docs/API-GOTCHAS.md`](docs/API-GOTCHAS.md) —— 作者从零摸出来的所有暗桩,不用你再踩。

---

## 作者

**童叔 @tongshu2023** · 少儿编程教师 + 51zxw 课程作者 + 长期主义的自我研究者
如果这个 skill 帮到你,欢迎 Star / Issue / PR。

MIT License.
