# SaucyClaw 配置说明

> 私有配置不泄露到源码中

---

## 配置文件位置

```
~/.saucyclaw/saucyclaw.json
```

---

## 配置文件结构

```json
{
  "notification": {
    "gateway_url": "http://your-gateway/hooks/agent",
    "hooks_token": "your-hooks-token",
    "timeout_ms": 10000
  }
}
```

---

## 配置字段说明

| 字段 | 说明 | 必需 |
|------|------|------|
| `gateway_url` | OpenClaw hooks endpoint URL | 是 |
| `hooks_token` | hooks 认证 token（从 OpenClaw 配置获取） | 是 |
| `timeout_ms` | 请求超时毫秒 | 否（默认 10000） |

---

## 环境变量覆盖

环境变量优先级高于配置文件：

| 环境变量 | 对应配置 |
|---------|---------|
| `SAUCYCLAW_GATEWAY_URL` | `notification.gateway_url` |
| `SAUCYCLAW_HOOKS_TOKEN` | `notification.hooks_token` |
| `SAUCYCLAW_TIMEOUT_MS` | `notification.timeout_ms` |

---

## 获取 hooks token

1. 在 OpenClaw 配置中生成 token：
   ```bash
   openssl rand -hex 32
   ```

2. 在 OpenClaw 配置文件中设置：
   ```json
   {
     "hooks": {
       "enabled": true,
       "token": "<生成的token>"
     }
   }
   ```

3. 将相同的 token 配置到 SaucyClaw：

---

## 安全注意事项

- **不要将配置文件提交到版本控制**
- **不要在源码中硬编码 URL 或 token**
- 配置目录 `~/.saucyclaw/` 已自动添加到 `.gitignore`

---

## 配置模块 API

```python
from core.config import load_notification_config, ensure_config_exists

# 加载配置
config = load_notification_config()
gateway_url = config.gateway_url
token = config.hooks_token

# 如果配置不存在，创建模板
ensure_config_exists()
```