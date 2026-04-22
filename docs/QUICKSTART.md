# QuickStart · 5 分钟跑通

## 第 1 步|申请 API 访问权限(一次性)

1. 登录 Looki App 或网页版
2. 访问 https://web.looki.tech/api-keys
3. 点 **"Apply for Access"** 申请 API 平台访问
4. 等官方审核(通常一到几天)

## 第 2 步|创建 API Key

审核通过后:

1. 回到 https://web.looki.tech/api-keys
2. 点 **"Create API Key"**
3. 输入名字(如 `claude-desktop`)
4. **立刻复制 Key**,它形如 `lk-xxxxxxxxxxxxxxxxxxxx`
5. Key 只显示一次,丢了只能重建

## 第 3 步|拉代码

```bash
# 推荐放在 ~/.claude/skills/ 下(Claude Code 会自动识别)
git clone https://github.com/tongshu2023/looki-claude.git ~/.claude/skills/looki-claude
cd ~/.claude/skills/looki-claude
```

Mac/Linux 用户建议创建软链接 `ln -s ~/.claude/skills/looki-claude ./`。

## 第 4 步|跑 setup

**Windows**:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup\setup.ps1
```

**Mac/Linux**:
```bash
bash setup/setup.sh
```

脚本会:
1. 检查 Python(必需)和 ffmpeg(可选,用于视频抽帧)
2. 让你粘贴 API Key
3. 写入 `~/.looki/credentials.json`(权限 600)
4. 调 `/me` 端点验证,输出你的用户信息

## 第 5 步|在 Claude Code 里用

重启 Claude Code(让它扫到新 skill)。然后直接用中文说:

```
调 looki 拿最近 7 天的 calendar
从 looki 搜一下薄荷出现过几次
把 2026-04-17 那条畅骑绿道的前 3 张照片抽出来给我看
```

Claude 会自动:
- 调 `looki_client.py`
- 拉 JSON
- 如果是视频,用 `frames.py` 抽一帧
- 用 Read 多模态看图
- 给出分析

## 脱离 Claude,纯命令行用

```bash
# 查用户
python src/looki_client.py me

# 按日拉 moments
python src/looki_client.py moments 2026-04-20

# 语义搜索
python src/looki_client.py search 薄荷 --page-size 20

# 30 天日历概览
python src/looki_client.py calendar 2026-03-22 2026-04-21

# 深钻单条
python src/looki_client.py detail <moment_id>
python src/looki_client.py files <moment_id>

# Looki 原生生成内容
python src/looki_client.py for-you --group comic --limit 10

# 视频抽帧
python src/frames.py "<temporary_url>" ./frame.jpg --ss 3
```

## 常见问题

**Q: setup 卡在 "连接失败"**
A: 检查 Key 是否以 `lk-` 开头、Key 是否过期、服务端是否能 ping 通:
```bash
curl -i -H "x-api-key: <your_key>" https://open.looki.tech/api/v1/me
```

**Q: 返回 429**
A: 限流 60 req/min。代码里加 `time.sleep(1)` 或等一分钟。

**Q: 下载的文件全是 mp4,Read 看不了**
A: Looki 默认全视频流,用 `python src/frames.py <url> <out.jpg>` 抽帧。详见 [API-GOTCHAS.md](API-GOTCHAS.md)。

**Q: Windows 下 Python 报编码错误**
A: 把 shell 切成 UTF-8:`chcp 65001`。
