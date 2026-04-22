# 示例 · 每日镜像简报

**目标**:每天结束时,Claude 基于你 Looki 全天数据,给你一份"中立去滤镜"的镜像报告。

**在 Claude Code 里直接说**:

```
调 looki 拿今天的所有 moment(按日期 YYYY-MM-DD),
再抽每个 moment 首帧看一遍,
然后写一份《今日镜像》,要求:

1. 去除 Looki 的 title/description 的浪漫化滤镜
2. 只描述我真实看到的画面(人/物/光/场景)
3. 标出"你亲眼看到的" vs "Looki 叙事的"差异,差异就是信号
4. 结尾给 3 个问题,不给结论
5. 用"我发现你身上可能有一个反复出现的模式..."等镜子语言
```

## 工作流(Claude 会自动执行)

1. `looki_client.py moments YYYY-MM-DD` 拉当天所有 moment
2. 对每个 moment 并行调 `looki_client.py files <id>`
3. 对每个视频 `frames.py <url> ./daily/<moment_id>.jpg --ss 3`
4. 批量 Read 所有 jpg
5. 交叉比较:
   - Looki 的 title/description(浪漫版)
   - 真实画面(Claude 视觉看到的)
   - 差异 = 信号
6. 按"镜像简报"模板输出

## 输出模板

```markdown
# 今日镜像 · YYYY-MM-DD

## 客观记录
- 覆盖时段:HH:MM ~ HH:MM
- 地点序列:家 → 公司 → 餐厅 → 家
- Moment 数:N

## 去滤镜对照
| 时段 | Looki 叙事 | 我亲看 | 信号 |
|---|---|---|---|

## 今日 3 个发现
1. 你身上可能有一个反复出现的模式...
2. 你今天可能没有在回答真正的问题,真正的问题也许是...
3. 这可能是你很重要的一块内核...

## 今日 3 个问题(不给结论)
-
-
-
```

## 扩展

- 把今日简报 append 到 `~/.claude/projects/.../memory/daily_mirror.md` 长期累积
- 每周自动跑一次,生成周报
- 用 cron/Windows 任务计划每晚 23:00 自动生成
