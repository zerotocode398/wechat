```bash
cmas/
├── README.md
├── requirements.txt
├── config.yaml
├── run.py
├── db.sqlite3
│
├── app/
│   ├── main.py                 # FastAPI入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库初始化
│   ├── dependencies.py         # FastAPI依赖注入
│   │
│   ├── api/                    # 路由层
│   │   ├── __init__.py
│   │   ├── alert.py            # Alertmanager入口
│   │   ├── silence.py          # Silence API
│   │   ├── wechat.py           # 企业微信回调
│   │   └── health.py           # 健康检查
│   │
│   ├── services/               # 业务层
│   │   ├── __init__.py
│   │   ├── alert.py            # 告警业务
│   │   ├── silence.py          # 静默业务
│   │   ├── wechat.py           # 微信消息业务
│   │   └── token.py             # token缓存业务
│   │
│   ├── clients/                # 第三方客户端
│   │   ├── __init__.py
│   │   ├── alertmanager.py
│   │   └── wechat.py
│   │
│   ├── models/                 # ORM模型
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── silence.py
│   │   ├── token.py
│   │   └── session.py
│   │
│   ├── schemas/                # Pydantic模型
│   │   ├── alert.py
│   │   ├── silence.py
│   │   └── wechat.py
│   │
│   ├── templates/
│   │   └── wechat_card.json
│   │
│   └── utils/
│       ├── logger.py
│       └── time.py
│
├── migrations/
│
├── tests/
│
└── deploy/
    ├── cmas.service
    └── nginx.conf
```