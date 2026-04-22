#!/usr/bin/env bash
# looki-claude · Mac/Linux 初始化脚本
# 用法:bash setup/setup.sh

set -e

echo "===== looki-claude setup (Mac/Linux) ====="

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[x] 未找到 python3,请先装 Python 3.8+"
    exit 1
fi
echo "[√] Python: $(which python3)"

# 2. 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[!] 未装 ffmpeg — 如需视频抽帧,运行:"
    echo "    Mac:   brew install ffmpeg"
    echo "    Linux: sudo apt install ffmpeg  (或 sudo yum install ffmpeg)"
else
    echo "[√] ffmpeg: $(which ffmpeg)"
fi

# 3. 要 API Key
echo ""
echo "===== 配置 API Key ====="
echo "获取 Key 的位置:登录 https://web.looki.tech/api-keys → 申请访问权限 → 创建 Key"
echo "Key 形如 'lk-xxxxxxxxxxxxxxxxxxxx'(只显示一次,请妥善保管)"
echo ""
read -r -p "粘贴你的 Looki API Key: " KEY

if [[ -z "$KEY" ]] || [[ "$KEY" != lk-* ]]; then
    echo "[x] Key 格式不对,应以 lk- 开头"
    exit 1
fi

# 4. 写入 credentials.json
CRED_DIR="$HOME/.looki"
mkdir -p "$CRED_DIR"
CRED_PATH="$CRED_DIR/credentials.json"
cat > "$CRED_PATH" <<EOF
{
  "base_url": "https://open.looki.tech/api/v1",
  "api_key": "$KEY",
  "created_at": "$(date +%Y-%m-%d)",
  "note": "Looki API credentials. 永远不要提交到 git。"
}
EOF
chmod 600 "$CRED_PATH"
echo "[√] 凭证已写入: $CRED_PATH"

# 5. 验证
echo ""
echo "===== 验证连接 ====="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="$SCRIPT_DIR/../src/looki_client.py"

if python3 "$CLIENT" me; then
    echo "[√] 连接成功"
    echo ""
    echo "安装完成!试试:"
    echo "  python3 src/looki_client.py search 薄荷"
    echo "  python3 src/looki_client.py calendar 2026-04-01 2026-04-22"
else
    echo "[x] 连接失败,请检查 Key"
    exit 1
fi
