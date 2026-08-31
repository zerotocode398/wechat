# wealert

Alertmanager + 企业微信告警推送服务，支持卡片消息和纯文本消息两种模式，并提供企业微信回调交互（静默等）。

---

## 接口类型

### 1. 告警推送接口（card 模式）

**POST** `/qywx/alert?msgtype=card`（默认）

每条告警独立发送一张企业微信卡片消息，卡片上带有"静默"按钮，用户可在企业微信中直接交互，静默对应的 Alertmanager 告警。

- 请求体：Alertmanager 标准 webhook payload（见下方 [Alertmanager 推送格式](#alertmanager-推送格式)）
- 返回：`{"code": 200, "msg": "ok"}`

---

### 2. 告警推送接口（text 模式）

**POST** `/qywx/alert?msgtype=text`

将所有告警合并为一条纯文本消息发送，不生成卡片、不存库、不支持静默交互。适合简单的通知场景。

- 请求体：支持两种格式
  - Alertmanager 标准 webhook payload（见下方 [Alertmanager 推送格式](#alertmanager-推送格式)）
  - 简化格式（见下方 [text 模式请求报文](#text-模式请求报文)）
- 返回：`{"code": 200, "msg": "ok"}`

---

### 3. 企业微信回调验证

**GET** `/qywx/callback`

企业微信后台配置回调 URL 时的验证接口，用于校验签名和返回解密后的 echostr。

| 参数 | 说明 |
|------|------|
| `msg_signature` | 企业微信加密签名 |
| `timestamp` | 时间戳 |
| `nonce` | 随机数 |
| `echostr` | 加密的随机字符串 |

---

### 4. 企业微信回调事件

**POST** `/qywx/callback`

接收企业微信推送的用户交互事件（如点击静默按钮、提交静默配置等），处理后返回加密的卡片更新 XML。

| 参数 | 说明 |
|------|------|
| `msg_signature` | 企业微信加密签名 |
| `timestamp` | 时间戳 |
| `nonce` | 随机数 |

---

### 5. 获取企业微信出口 IP

**GET** `/qywx/getips`

返回企业微信 API 服务器的出口 IP 列表（纯文本，每行一个 IP），用于配置防火墙白名单。

---

## 使用手册

### 1. 配置文件

编辑 `config.yaml`，按实际环境填写以下配置：

```yaml
qywx:
  agentid: xxxxxxx           # 企业微信应用 AgentID
  corpid: xxxxxxxx # 企业微信 CorpID
  corpsecret: ""             # 企业微信应用 Secret
  touser: "xxxxxxxxxx"       # 默认接收人，多个用逗号分隔
  toparty: ""                # 默认接收部门
  totag: ""                  # 默认接收标签
  openapi:
    token: ""                # 回调 Token
    aeskey: ""               # 回调 AESKey

alertmanager:
  auth:
    enabled: "true"          # 是否启用 Basic Auth
    username: "admin"
    password: "admin"
  alert_title: "😱  告警"        # card 模式告警标题
  resolve_title: "😌  恢复"      # card 模式恢复标题
  url: "http://xxxx:xxxx"    # Alertmanager API 地址
  timeout: 10
  silence_ttl: 1800                  # 静默按钮超时（秒）

silence:                             # 静默选项（各最多 10 个）
  durations: [2h, 4h, 8h, 12h, 1d, 3d, 7d, 14d, 21d, 30d]
  reasons: [人为触发, 上线/发布, 护网/重保, 变更/维护, 误报, 演练, 其他]
  scopes:
    - text: 当前告警
    - text: 当前主机
      labels: [hostname]
    - text: 相同告警项目
      labels: [alertname]
    - text: 当前主机相同告警
      labels: [hostname, alertname]
```

### 2. 启动服务

```bash
python main.py --config config.yaml
```

完整参数说明：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | **必填** | 配置文件路径 |
| `--listen` | `0.0.0.0:8817` | 监听地址和端口 |
| `--init-db` | 不启用 | 仅初始化数据库后退出，不启动服务 |
| `--timeout` | `30` | 全局请求超时（秒） |
| `--log-level` | `INFO` | 日志级别：DEBUG / INFO / WARNING / ERROR |
| `-V, --version` | | 显示版本号 |

### 2.1 数据库初始化

启动服务时会自动初始化数据库（所有表使用 `CREATE TABLE IF NOT EXISTS`，可重复执行）。

如需单独初始化（不启动服务），使用 `--init-db` 参数：

```bash
# 源码运行
python main.py --config config.yaml --init-db

# 二进制运行
./wealert --config config.yaml --init-db
```

> 替代了 `python -m app.db.migrate`，打包后不再依赖 Python 解释器。

### 3. 配置 Alertmanager Webhook

在 Alertmanager 配置文件中添加 webhook 接收者：

```yaml
receivers:
  - name: 'wealert'
    webhook_configs:
      - url: 'http://<wealert_ip>:8817/qywx/alert'
        send_resolved: true
```

### 4. text 模式请求报文

#### 方式一：标准 Alertmanager 格式

多条 alerts 会合并为一条消息，以 `---` 分隔后发送。

#### 方式二：简化格式

```json
{
  "alerts": [
    {
      "annotations": {
        "主机": "1.1.1.1",
        "告警内容": "内存使用率已达 77%。",
        "备注": "测试",
        "资源池": "china",
        "项目": "code"
      },
      "startsAt": "1212-12-12 00:00:00"
    },
    {
      "annotations": {
        "Desc": "CPU 使用率大于0%，实例: 2.2.2.2，当前值: 7%。"
      },
      "startsAt": "2026-01-01T00:00:12.598Z"
    }
  ]
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `alerts` | 是 | 告警列表 |
| `alerts[].annotations` | 是 | 告警详情，逐行渲染为 `key: value` |
| `alerts[].startsAt` | 是 | 告警时间，支持 `2026-01-01T00:00:12.598Z` 或 `1212-12-12 00:00:00` 格式 |


---

## Alertmanager 推送格式

以下为 Alertmanager 推送至 `/qywx/alert` 时的标准 webhook payload 示例。

### annotations 格式

```json
{
  "receiver": "debug-webhook",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "Memory",
        "hostname": "xxxxx",
        "instance": "111.111.111.11:9100",
        "job": "node",
        "plat": "xxxxx",
        "project": "xxxx",
        "remark": "xxxxx",
        "res_pool": "xxxxx-xxxx",
        "severity": "warning"
      },
      "annotations": {
        "主机": "xxxxx()",
        "告警内容": "内存使用率已达 77%。",
        "备注": "xxxxx",
        "资源池": "xxxxx-xxxx",
        "项目": "xxxx"
      },
      "startsAt": "2026-08-25T08:18:12.598Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "generatorURL": "http://xxxx:xxxx/graph?g0.expr=...",
      "fingerprint": "xxxx"
    },
    {
      "status": "firing",
      "labels": {
        "alertname": "CPU测试",
        "hostname": "xxxxx",
        "instance": "111.111.111.11:9100",
        "plat": "xxxxx",
        "project": "xxxx",
        "remark": "xxxxx",
        "res_pool": "xxxxx-xxxx",
        "severity": "warning"
      },
      "annotations": {
        "Desc": "CPU 使用率大于0%，实例:xxxxxxx: 7%。"
      },
      "startsAt": "2026-08-25T08:18:12.598Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "generatorURL": "http://xxxx:xxxx/graph?g0.expr=...",
      "fingerprint": "xxxx"
    }
  ],
  "notification_reason": "first notification",
  "groupLabels": { "hostname": "operate01" },
  "commonLabels": {
    "hostname": "xxxxx",
    "instance": "111.111.111.11:9100",
    "plat": "xxxxx",
    "project": "xxxx",
    "remark": "xxxxx",
    "res_pool": "xxxxx-xxxx",
    "severity": "warning"
  },
  "commonAnnotations": {},
  "externalURL": "http://xxxx:9093",
  "version": "4",
  "groupKey": "{}:{hostname=\"xxxxx\"}",
  "truncatedAlerts": 0
}
```

---

## curl 示例

```bash
# card 模式（默认）
curl -X POST http://localhost:8817/qywx/alert \
  -H "Content-Type: application/json" \
  -d @./alert.json

# text 模式
curl -X POST "http://localhost:8817/qywx/alert?msgtype=text" \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [
      {
        "annotations": {
          "主机": "1.1.1.1",
          "告警内容": "内存使用率已达 77%。",
          "备注": "测试",
          "资源池": "china",
          "项目": "code"
        },
        "startsAt": "2026-01-01T00:00:12.598Z"
      }
    ]
  }'
```