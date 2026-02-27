# Feishu Baogaomiao Notify Skill

检测 openclaw 飞书扩展发送的通知，并自动触发 baogaomiao-skill。

## 使用方式

当检测到飞书消息通知时，自动执行 `/baogaomiao` skill。

## 通知文件位置

`/Users/echochen/.claude/notify/feishu-baogaomiao.json`

## 通知格式

```json
{
  "timestamp": 1736833708000,
  "senderId": "ou_xxx",
  "senderName": "用户名",
  "chatId": "oc_xxx",
  "content": "消息内容",
  "messageId": "om_xxx",
  "chatType": "p2p" | "group"
}
```
