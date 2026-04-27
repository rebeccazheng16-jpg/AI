---
name: lark-webhook-sender
description: Send formatted messages to Lark via webhook. This skill should be used when pushing notifications, reports, or content to Lark groups or channels through webhook URLs.
---

# Lark Webhook Sender

Send messages to Lark using webhook URLs. Supports plain text and interactive card formats.

## When to Use

- Pushing daily generated content to Lark
- Sending notifications or alerts
- Delivering reports or summaries to Lark groups
- Any automated message delivery to Lark

## Quick Usage

### Send Plain Text Message

```bash
python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
  --webhook "WEBHOOK_URL" \
  --text "Your message here"
```

### Send Card Message (Recommended for Scripts)

```bash
python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
  --webhook "WEBHOOK_URL" \
  --title "Daily Script - 2024-01-15" \
  --content "Your script content here..." \
  --card
```

### Send from File

```bash
python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
  --webhook "WEBHOOK_URL" \
  --title "Daily Script" \
  --file "/path/to/script.txt" \
  --card
```

## Default Webhook

For the daily founder script workflow, use this webhook:
```
https://open.larksuite.com/open-apis/bot/v2/hook/00653044-07ab-4b45-a1aa-b8cda5c93484
```

## Card Format Structure

When using `--card`, the message is formatted as an interactive card with:
- **Header**: Title with blue theme
- **Content**: Markdown-formatted body text
- **Timestamp**: Auto-added send time

## Script Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--webhook` | Yes | Lark webhook URL |
| `--text` | No* | Plain text message |
| `--title` | No | Card title (requires --card) |
| `--content` | No* | Card body content |
| `--file` | No* | Read content from file |
| `--card` | No | Use card format instead of text |
| `--secret` | No | Signing secret for secure webhooks (default: built-in) |
| `--no-sign` | No | Disable signature for unsigned webhooks |

*One of `--text`, `--content`, or `--file` is required.

<!-- 最后验证: 2026-02-05 -->

## Response Handling

The script outputs:
- `Success: Message sent` on successful delivery
- `Error: <details>` if the request fails

Exit codes:
- `0`: Success
- `1`: Failure

## Example: Daily Script Push

```bash
# Generate script content and save to file, then send
python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
  --webhook "https://open.larksuite.com/open-apis/bot/v2/hook/00653044-07ab-4b45-a1aa-b8cda5c93484" \
  --title "🎬 Lina Lie Daily Script - $(date +%Y-%m-%d)" \
  --content "**Hook:** Apakah kamu pernah merasa...

**Content:** [Script body here]

**CTA:** Apa pendapat kalian? Tulis di kolom komentar!" \
  --card
```
