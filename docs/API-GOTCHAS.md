# API 踩坑录

作者从零摸 Looki API 时踩过的所有暗桩。不是抱怨,是给后来人省时间。

---

## 1. Base URL 不是 `api.looki.ai`,是 `open.looki.tech/api/v1`

`api.looki.ai`、`api.looki.tech` 都 DNS 不存在。正确的开发者 API 在:

```
https://open.looki.tech/api/v1
```

这个 URL 没写在任何文档里(Looki 官网只指 API Keys 页面)。我是 curl `https://web.looki.tech/` 的首页,从 HTML 的 `window.__RUNTIME_CONFIG__` 里挖到的:

```js
window.__RUNTIME_CONFIG__ = {
  apiBaseUrl: 'https://devo.looki.tech',         // C 端主 API,不对应开发者 Key
  developerPlatformApi: 'https://open.looki.tech/api/v1',  // 这才是开发者 API
  ...
}
```

---

## 2. 认证用 `X-API-Key` header,**不是** `Authorization: Bearer`

`lk-` 前缀的 Key 看起来像 OAuth token,但实际用法是:

```http
GET /api/v1/me
X-API-Key: lk-xxxxxxxxxxxxxxxxxxxx
```

用 `Authorization: Bearer lk-...` 会返回 422:
```json
{"code":100,"detail":"Invalid request parameters","data":{"errors":[{"type":"missing","loc":["header","x-api-key"],"msg":"Field required"}]}}
```

---

## 3. `/docs`、`/openapi.json`、`/` 全部 404

FastAPI 默认端点全部关了。没有 Swagger 文档可访问。

完整端点清单(我从 `web.looki.tech` 的 JS bundle 里挖出来的):

```
GET /me
GET /moments?on_date=YYYY-MM-DD
GET /moments/search?query=&start_date=&end_date=&page=&page_size=
GET /moments/calendar?start_date=&end_date=
GET /moments/{moment_id}
GET /moments/{moment_id}/files?highlight=&cursor_id=&limit=
GET /for_you/items?group=&liked=&recorded_from=&recorded_to=&cursor_id=&limit=&order_by=
```

参数名要字面一致:
- 不是 `date`/`day`/`from` —— 是 `on_date`
- 日期格式严格 `YYYY-MM-DD`
- `moments/{id}` 路径参数必须是合法 UUID,传 "2026-04-20" 会返回 UUID 解析错误

---

## 4. `/moments/{id}/files` 返回的几乎全是 10 秒视频 mp4,**`thumbnail` 字段是 null**

这是最大的坑。单条 file item 结构:

```json
{
  "id": "69c2e1d810b994713c013773",
  "file": {
    "temporary_url": "https://devo-user-file.looki.tech/.../xxx.mp4?x-looki-token=...",
    "media_type": "VIDEO",
    "size": 17835569,
    "duration_ms": 10031
  },
  "thumbnail": null,   // 几乎永远是 null
  "location": "...",
  "created_at": "...",
  "tz": "+08:00"
}
```

后果:

- **没法直接 Read mp4 给 Claude 多模态**
- **如果不装 ffmpeg,就拿不到视觉信息**,只能靠 Looki 自己生成的 `title`/`description`(幼稚)
- 必须用 `frames.py` 从视频里抽第 N 秒的帧保存为 jpg

本 skill 的 `src/frames.py` 就是为此而生。

---

## 5. `temporary_url` **1 小时过期**

pre-signed URL,看 JWT 里的 `exp` 字段大概 3600 秒。后果:

- 拉完 files 必须立刻下载或抽帧,别存起来想着"明天再处理"
- 如果过期了,**重新调 `/moments/{id}/files`** 拿新 URL,token 会刷新
- 不要把 temporary_url 写进数据库/缓存

---

## 6. `/moments/search` 的语义搜索是**基于 Looki 自己打的标签**,不是基于原始视觉/音频

搜 "音乐" 和 "讲课" 都返 20 条命中 has_more=True —— 但命中的很多场景其实不包含你主动在"玩音乐"或"讲课"(比如搜"讲课"命中的是"你在听课")。

原因:Looki 给每个 moment 打了一套通用标签,它的 AI 对"听课 vs 讲课"分不清,对"主动演奏 vs 被动听歌"也分不清。

**正确用法**:把 search 结果当粗过滤,再逐条 `moment_files` 拉原视频 → 抽帧 → Claude 亲自看。

---

## 7. Looki 的 `title`/`description`/`content` 有系统性浪漫化滤镜

产品逻辑是"让用户觉得生活有意义",不是"诚实叙事"。举例:

| Looki 叙事 | 实际画面(作者亲测) |
|---|---|
| "美味铁板烧午餐与同伴谈笑风生" | 你一个人低头玩 AI,对面两个同事在聊自己的 |
| "忙里偷闲的城中漫步与户外小憩" | 办公楼门口站了 30 秒透气 |
| "雨中宝光寺禅意之旅" | 漆黑的停车场,啥都看不见 |

**如果你要做"第二大脑/自我镜像",一定要绕开这层滤镜** —— 用 files + frames,别信 description。

---

## 8. 限流 60 req/min,没有 burst 限制文档

超过返 429。本 skill 里的 `LookiClient` 没加内置限流(KISS),建议自己批量调用时加 `time.sleep(1)`。

---

## 9. `for_you/items` 的 `group` 值

文档说接受 `all|comic|vlog|present|other`,实测还有这些隐含类型(从 `type` 字段):

- `IMAGE_POST`
- `DAILY_VLOG`
- `USER_EVENT_ANALYSIS` ← 这个价值很高,AI 生成的事件分析
- `IMAGE_POST_WEEKLY_LIFE_COLORS` ← 每周生活调色盘
- `MOMENT_POST`

但 `group=` 参数只支持文档里那 5 个名字。如果想按 `type` 过滤,只能拉全量后本地 filter。

---

## 10. 时间全用 `+08:00` 本地时区,不是 UTC

API 返回的 `start_time`/`created_at` 全是带 `+08:00` 的 ISO 8601。如果你在非 CN 区域使用,注意时区转换。中国用户则不用处理。

---

如果你发现了新的坑,欢迎提 Issue / PR。
