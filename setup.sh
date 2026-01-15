#!/bin/bash
#
# Clouvel 원클릭 설치
# 프로젝트 루트에서 더블클릭하면 Claude Desktop에 MCP 서버 등록됨
#

set -e

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║         Clouvel 설치 스크립트         ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

# OS 감지 및 config 경로 설정
detect_config_path() {
    case "$(uname -s)" in
        Darwin)
            echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
            ;;
        Linux)
            # WSL 체크
            if grep -qi microsoft /proc/version 2>/dev/null; then
                # WSL: Windows 경로 사용
                WIN_HOME=$(cmd.exe /c "echo %USERPROFILE%" 2>/dev/null | tr -d '\r')
                if [ -n "$WIN_HOME" ]; then
                    echo "$(wslpath "$WIN_HOME")/AppData/Roaming/Claude/claude_desktop_config.json"
                else
                    echo "$HOME/.config/Claude/claude_desktop_config.json"
                fi
            else
                echo "$HOME/.config/Claude/claude_desktop_config.json"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "$APPDATA/Claude/claude_desktop_config.json"
            ;;
        *)
            echo ""
            ;;
    esac
}

CONFIG_PATH=$(detect_config_path)

if [ -z "$CONFIG_PATH" ]; then
    echo -e "${RED}✗ 지원하지 않는 OS입니다${NC}"
    exit 1
fi

echo -e "설정 파일: ${YELLOW}$CONFIG_PATH${NC}"
echo ""

# 디렉토리 생성
CONFIG_DIR=$(dirname "$CONFIG_PATH")
if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}→ 설정 폴더 생성 중...${NC}"
    mkdir -p "$CONFIG_DIR"
fi

# 기존 설정 백업 및 병합
if [ -f "$CONFIG_PATH" ]; then
    echo -e "${YELLOW}→ 기존 설정 발견, 백업 중...${NC}"
    cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d%H%M%S)"

    # 기존 설정에 clouvel 추가
    if command -v python3 &> /dev/null; then
        python3 << 'PYTHON_SCRIPT'
import json
import sys

config_path = """$CONFIG_PATH"""

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['clouvel'] = {
    "command": "uvx",
    "args": ["clouvel"]
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("OK")
PYTHON_SCRIPT
    else
        echo -e "${RED}✗ Python3가 필요합니다${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}→ 새 설정 파일 생성 중...${NC}"
    cat > "$CONFIG_PATH" << 'EOF'
{
  "mcpServers": {
    "clouvel": {
      "command": "uvx",
      "args": ["clouvel"]
    }
  }
}
EOF
fi

echo ""
echo -e "${GREEN}✓ Clouvel MCP 서버 등록 완료!${NC}"
echo ""
echo "  다음 단계:"
echo "  1. Claude Desktop 완전히 종료 (트레이에서도)"
echo "  2. Claude Desktop 다시 시작"
echo "  3. Claude한테 \"docs 폴더 분석해줘\" 하면 끝"
echo ""
echo -e "  설정 파일: ${YELLOW}$CONFIG_PATH${NC}"
echo ""

# macOS/Linux: 엔터 대기
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    read -p "  엔터를 누르면 종료됩니다..."
fi
