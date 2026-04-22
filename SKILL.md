---
name: looki
description: 调 Looki L1 AI 穿戴相机的 API,读你自己的 moments、照片、视频、AI 生成的 For You 内容。当用户说"我 Looki 里..."、"找一下 looki 的"、"调 looki 看"、"从 looki 拉"、"我相机里"、"我记录的"、"昨天戴着 Looki 的时候"、"最近一周我的 moment"、"薄荷在 looki 里出现了几次"时触发。覆盖 7 个端点:me/moments(按日)/moments/search(语义)/moments/calendar/moments/{id}/moments/{id}/files/for_you/items。具备 ffmpeg 视频抽帧能力(Looki 默认全视频无缩略图)。不适用于通用 AI 相机问题或 Looki 硬件客服。
---

# Looki × Claude Skill

## 何时触发

用户需要访问自己的 Looki L1 穿戴相机数据时,包括:
- 回顾:"我昨天做了什么"/"这周我在哪些地方"
- 找人找物:"薄荷出现过几次"/"所有讲课的场景"
- 剪辑:"帮我挑最近 10 个最精彩的 moment"
- 分析:"根据最近 30 天的 looki 数据,写我的生活节奏报告"
- 溯源:"4 月 17 号那天我几点去的绿道"

## 不要触发

- Looki 硬件售后/产品咨询(让用户找官方客服)
- 通用 AI 相机/穿戴设备对比(这不是调 API 的场景)
- 用户明确说"不看 Looki"

## 使用流程

### Step 1|确认凭证可用

先跑 `python src/looki_client.py me`,确认返回 user 对象。
若失败,引导用户跑 `setup/setup.ps1`(Windows)或 `setup/setup.sh`(Mac/Linux)。

### Step 2|选端点

| 用户意图 | 端点 | 必要参数 |
|---|---|---|
| 今天/某天发生了什么 | `moments?on_date=` | YYYY-MM-DD |
| 一段时间概览 | `moments/calendar` | start_date, end_date |
| 找特定人/物/主题 | `moments/search` | query, 可选 start_date/end_date |
| 深钻一条 moment | `moments/{id}` + `moments/{id}/files` | moment_id (UUID) |
| Looki 原生内容 | `for_you/items` | 可选 group/date_range |

### Step 3|视频抽帧(非常重要)

**Looki 的 files API 返回的几乎全是 10 秒 mp4 视频,`thumbnail` 字段为 null**。直接 Read mp4 无法多模态看。必须用 ffmpeg 抽一帧:

```python
from src.frames import extract_frame
extract_frame(temporary_url, out_path="./frame.jpg", ss_seconds=3)
```

抽完后 Read jpg,Claude 就能多模态读图了。

### Step 4|避免幼稚标签陷阱

Looki 的 AI(`title`/`description`/`for_you/items.content`)有系统性浪漫化滤镜。不要把它的叙事当作事实依据。正确做法:

- **拿它的 title 当索引,不当结论**
- **自己 Read 原图 /原视频帧,亲眼看**
- **把"亲看"和 Looki 叙事对照,差异本身就是信号**

## 内置 Prompt 模板(examples/)

- `daily-mirror.md` —— 镜像简报:天赋/压抑/模式识别
- `dog-highlights.md` —— 宠物短视频精选
- `teacher-golden-quotes.md` —— 教学金句库
- `relationship-mapping.md` —— 关系图谱
- `energy-curve.md` —— 精力曲线/心流地图

## 限流

60 req/min per API key。批量调用时加 `time.sleep(1)`。超限返回 HTTP 429。

## 凭证存储

`~/.looki/credentials.json`,永远不要提交到 git,`.gitignore` 已覆盖。
