#!/bin/bash
# Railway 完整部署工作流脚本
# 用法: ./deploy.sh [--skip-webhook] [--skip-build] [--detach]
#
# 选项:
#   --skip-webhook  跳过 webhook 验证
#   --skip-build    跳过本地构建测试
#   --detach        使用 detach 模式部署（不等待完成）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 参数解析
SKIP_WEBHOOK=false
SKIP_BUILD=false
DETACH_MODE=false

for arg in "$@"; do
    case $arg in
        --skip-webhook) SKIP_WEBHOOK=true ;;
        --skip-build) SKIP_BUILD=true ;;
        --detach) DETACH_MODE=true ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Railway 完整部署工作流               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# Phase 1: 预检查
# ============================================
echo -e "${BLUE}[Phase 1] 预检查${NC}"
echo "────────────────────────────────────────"

# 1.1 检查 Railway CLI
echo -n "1.1 检查 Railway CLI... "
if command -v railway &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}错误: Railway CLI 未安装。运行: npm install -g @railway/cli${NC}"
    exit 1
fi

# 1.2 检查项目链接
echo -n "1.2 检查项目链接... "
if railway status &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}错误: 未链接 Railway 项目。运行: railway link${NC}"
    exit 1
fi

# 1.3 检查环境变量
echo -n "1.3 检查环境变量... "
VAR_COUNT=$(railway variables 2>/dev/null | wc -l)
if [ "$VAR_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} ($VAR_COUNT 个变量)"
else
    echo -e "${YELLOW}⚠${NC} 无环境变量"
fi

# 1.4 本地构建测试
if [ "$SKIP_BUILD" = false ]; then
    echo -n "1.4 本地构建测试... "
    if [ -f "package.json" ]; then
        if npm run build &> /dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            echo -e "${RED}错误: 构建失败。请修复后重试。${NC}"
            exit 1
        fi
    elif [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}跳过${NC} (Python 项目)"
    else
        echo -e "${YELLOW}跳过${NC} (无构建配置)"
    fi
else
    echo -e "1.4 本地构建测试... ${YELLOW}跳过${NC}"
fi

# 1.5 TypeScript 类型检查
if [ -f "tsconfig.json" ] && [ "$SKIP_BUILD" = false ]; then
    echo -n "1.5 TypeScript 类型检查... "
    if npx tsc --noEmit &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo -e "${RED}错误: 类型检查失败。${NC}"
        exit 1
    fi
fi

# 1.6 Webhook 验证（如果存在）
if [ "$SKIP_WEBHOOK" = false ]; then
    WEBHOOK_FILE=$(find . -name "*.ts" -o -name "*.js" 2>/dev/null | xargs grep -l "webhook\|challenge" 2>/dev/null | head -1)
    if [ -n "$WEBHOOK_FILE" ]; then
        echo -e "1.6 检测到 Webhook... ${YELLOW}建议运行 webhook-debugger 验证${NC}"
    fi
else
    echo -e "1.6 Webhook 验证... ${YELLOW}跳过${NC}"
fi

echo ""

# ============================================
# Phase 2: 部署
# ============================================
echo -e "${BLUE}[Phase 2] 部署${NC}"
echo "────────────────────────────────────────"

if [ "$DETACH_MODE" = true ]; then
    echo "2.1 执行部署 (detach 模式)..."
    railway up --detach
    echo -e "${GREEN}✓${NC} 部署已启动（后台运行）"
else
    echo "2.1 执行部署 (CI 模式)..."
    if railway up --ci; then
        echo -e "${GREEN}✓${NC} 部署完成"
    else
        echo -e "${RED}✗${NC} 部署失败"
        exit 1
    fi
fi

echo ""

# ============================================
# Phase 3: 验证
# ============================================
echo -e "${BLUE}[Phase 3] 验证${NC}"
echo "────────────────────────────────────────"

# 等待服务启动
echo -n "3.1 等待服务启动... "
sleep 5
echo -e "${GREEN}✓${NC}"

# 获取部署 URL
echo -n "3.2 获取部署 URL... "
DEPLOY_URL=$(railway status --json 2>/dev/null | grep -o '"domain":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")

if [ -z "$DEPLOY_URL" ]; then
    # 尝试其他方式获取
    DEPLOY_URL=$(railway status 2>/dev/null | grep -o 'https://[^ ]*' | head -1 || echo "")
fi

if [ -n "$DEPLOY_URL" ]; then
    echo -e "${GREEN}✓${NC}"
    echo -e "   URL: ${YELLOW}$DEPLOY_URL${NC}"
else
    echo -e "${YELLOW}⚠${NC} 无法获取 URL"
fi

# 健康检查
if [ -n "$DEPLOY_URL" ]; then
    echo -n "3.3 健康检查... "
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOY_URL" --max-time 10 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $HTTP_CODE)"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${YELLOW}⚠${NC} 无法连接（服务可能仍在启动）"
    else
        echo -e "${YELLOW}⚠${NC} HTTP $HTTP_CODE"
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ${GREEN}部署完成${BLUE}                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

if [ -n "$DEPLOY_URL" ]; then
    echo -e "\n访问: ${YELLOW}$DEPLOY_URL${NC}"
fi
