#!/bin/bash
# Webhook Challenge 验证测试脚本
# 用法: ./test-webhook.sh [endpoint] [required_passes]
#
# 示例:
#   ./test-webhook.sh http://localhost:3000/webhook/feishu
#   ./test-webhook.sh http://localhost:3000/api/webhook 10

set -e

ENDPOINT="${1:-http://localhost:3000/webhook/feishu}"
REQUIRED_PASSES="${2:-5}"
PASS_COUNT=0
ITERATION=0
TOTAL_FAILURES=0
LOG_FILE="webhook-debug-$(date +%Y%m%d_%H%M%S).log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Webhook Challenge 验证测试 ===${NC}"
echo -e "端点: ${YELLOW}$ENDPOINT${NC}"
echo -e "目标: 连续通过 ${YELLOW}$REQUIRED_PASSES${NC} 次测试"
echo -e "日志: ${YELLOW}$LOG_FILE${NC}"
echo ""

# 初始化日志
cat > "$LOG_FILE" << EOF
=== Webhook 调试日志 ===
端点: $ENDPOINT
目标: 连续通过 $REQUIRED_PASSES 次
开始时间: $(date)
---
EOF

# 检查服务器是否可达
echo -e "${BLUE}[检查] 测试服务器连通性...${NC}"
if ! curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT" > /dev/null 2>&1; then
    echo -e "${YELLOW}[警告] 服务器可能未运行，继续测试...${NC}"
fi

while [ $PASS_COUNT -lt $REQUIRED_PASSES ]; do
    ITERATION=$((ITERATION + 1))
    CHALLENGE="test_challenge_$(date +%s%N | md5sum | head -c 16)"

    echo -e "\n${BLUE}[迭代 $ITERATION]${NC} Challenge: $CHALLENGE"

    # 记录到日志
    echo -e "\n[迭代 $ITERATION] $(date)" >> "$LOG_FILE"
    echo "请求 Challenge: $CHALLENGE" >> "$LOG_FILE"

    # 发送请求
    RESPONSE=$(curl -s -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "{\"challenge\": \"$CHALLENGE\", \"token\": \"test_token\", \"type\": \"url_verification\"}" \
        -w "\n__HTTP_CODE__%{http_code}__CONTENT_TYPE__%{content_type}" \
        2>&1) || true

    # 解析响应
    HTTP_CODE=$(echo "$RESPONSE" | grep -o '__HTTP_CODE__[0-9]*' | sed 's/__HTTP_CODE__//')
    CONTENT_TYPE=$(echo "$RESPONSE" | grep -o '__CONTENT_TYPE__[^_]*' | sed 's/__CONTENT_TYPE__//' | tr -d '\n')
    BODY=$(echo "$RESPONSE" | sed 's/__HTTP_CODE__.*$//')

    # 期望的响应
    EXPECTED="{\"challenge\":\"$CHALLENGE\"}"
    # 也接受带空格的格式
    EXPECTED_ALT="{ \"challenge\": \"$CHALLENGE\" }"

    echo "响应 HTTP: $HTTP_CODE" >> "$LOG_FILE"
    echo "响应 Body: $BODY" >> "$LOG_FILE"

    # 验证响应
    BODY_CLEAN=$(echo "$BODY" | tr -d ' \n\r')
    EXPECTED_CLEAN=$(echo "$EXPECTED" | tr -d ' ')

    if [ "$HTTP_CODE" = "200" ] && [ "$BODY_CLEAN" = "$EXPECTED_CLEAN" ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        echo -e "${GREEN}✅ 通过${NC} ($PASS_COUNT/$REQUIRED_PASSES)"
        echo "结果: 通过 ($PASS_COUNT/$REQUIRED_PASSES)" >> "$LOG_FILE"
    else
        TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
        echo -e "${RED}❌ 失败${NC}"
        echo -e "  HTTP 状态: ${YELLOW}$HTTP_CODE${NC} (期望: 200)"
        echo -e "  期望: ${GREEN}$EXPECTED${NC}"
        echo -e "  实际: ${RED}$BODY${NC}"

        echo "结果: 失败" >> "$LOG_FILE"
        echo "期望: $EXPECTED" >> "$LOG_FILE"
        echo "实际: $BODY" >> "$LOG_FILE"

        # 分析失败原因
        if [ "$HTTP_CODE" != "200" ]; then
            echo "失败原因: HTTP 状态码错误 ($HTTP_CODE)" >> "$LOG_FILE"
            echo -e "  ${YELLOW}诊断: HTTP 状态码错误${NC}"
        elif echo "$BODY" | grep -q "code"; then
            echo "失败原因: 响应包含额外字段 'code'" >> "$LOG_FILE"
            echo -e "  ${YELLOW}诊断: 响应包含额外字段，应只返回 challenge${NC}"
        elif echo "$BODY" | grep -q "status"; then
            echo "失败原因: 响应包含额外字段 'status'" >> "$LOG_FILE"
            echo -e "  ${YELLOW}诊断: 响应包含额外字段，应只返回 challenge${NC}"
        elif ! echo "$BODY" | grep -q "$CHALLENGE"; then
            echo "失败原因: challenge 值不匹配" >> "$LOG_FILE"
            echo -e "  ${YELLOW}诊断: 返回的 challenge 值与请求不匹配${NC}"
        else
            echo "失败原因: 响应格式不正确" >> "$LOG_FILE"
            echo -e "  ${YELLOW}诊断: 响应格式不符合预期${NC}"
        fi

        # 重置连续通过计数
        PASS_COUNT=0

        echo -e "\n${YELLOW}⚠️  修复代码后，脚本将继续测试...${NC}"
        echo -e "${YELLOW}按 Ctrl+C 退出，或等待 3 秒后继续测试${NC}"
        sleep 3
    fi

    # 短暂延迟避免过快请求
    sleep 0.3
done

# 完成
echo -e "\n${GREEN}🎉 成功！连续通过 $REQUIRED_PASSES 次测试${NC}"
echo -e "总迭代次数: $ITERATION"
echo -e "总失败次数: $TOTAL_FAILURES"

cat >> "$LOG_FILE" << EOF

=== 测试完成 ===
结果: 成功
总迭代: $ITERATION
总失败: $TOTAL_FAILURES
结束时间: $(date)
EOF

echo -e "\n${BLUE}日志已保存至: ${YELLOW}$LOG_FILE${NC}"
