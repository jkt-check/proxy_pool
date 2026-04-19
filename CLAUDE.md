# CLAUDE.md

This file provides guidance to Kscc (claudexxxxxx.ai/code) when working with code in this repository.

## Project Overview

ProxyPool is a Python-based proxy IP pool system for web scraping. It periodically fetches free proxies from multiple sources, validates them, stores valid proxies in Redis/SSDB, and provides REST API access.

## Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the scheduler (fetches and validates proxies periodically)
python proxyPool.py schedule

# Start the API server (default: http://0.0.0.0:5010)
python proxyPool.py server

# Start both (Docker entrypoint)
./start.sh
```

### Docker
```bash
docker-compose up -d
```

### Testing
```bash
# Run manual tests
python test.py

# Run individual test modules
python -m test.testConfigHandler
python -m test.testRedisClient
python -m test.testProxyValidator
```

## Configuration

All configuration is in `setting.py`:
- `DB_CONN`: Database connection URI (format: `redis://:password@host:port/db`)
- `HOST`/`PORT`: API server bind address
- `PROXY_FETCHER`: List of fetcher method names to enable
- `VERIFY_TIMEOUT`: Proxy validation timeout (seconds)
- `POOL_SIZE_MIN`: Minimum proxy count before triggering fetch

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point (proxyPool.py)                │
│                    CLI using Click framework                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│   Scheduler   │           │  API Server   │
│ (APScheduler) │           │    (Flask)    │
│  helper/      │           │   api/        │
│   scheduler.py│           │   proxyApi.py │
└───────┬───────┘           └───────┬───────┘
        │                           │
        ▼                           │
┌───────────────┐                   │
│    Fetcher    │                   │
│ helper/fetch  │                   │
│ Multi-threaded│                   │
│  proxy fetch  │                   │
└───────┬───────┘                   │
        │                           │
        ▼                           ▼
┌───────────────────────────────────────────────┐
│                   Checker                      │
│              helper/check.py                   │
│         Multi-threaded proxy validation       │
│     (http/https timeout, format check)        │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              ProxyHandler                      │
│          handler/proxyHandler.py              │
│        CRUD operations for proxies             │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                DbClient                        │
│             db/dbClient.py                    │
│      Factory pattern for DB backends          │
│         Redis / SSDB support                  │
└───────────────────────────────────────────────┘
```

## Key Components

### Data Layer (`db/`)
- `DbClient`: Factory class that instantiates the appropriate client based on `DB_CONN` scheme
- `RedisClient`: Redis hash-based storage (key: `ip:port`, value: proxy JSON)
- Supports Redis and SSDB backends

### Fetcher (`fetcher/proxyFetcher.py`)
- Static methods that yield proxies from various free proxy websites
- Each method returns `host:port` format strings
- Add new fetchers by creating `freeProxyXX()` static methods
- Register new fetchers in `setting.py` `PROXY_FETCHER` list

### Validation (`helper/validator.py`)
- `ProxyValidator`: Decorator-based validator registration
- Three validator types: `pre_validator` (format), `http_validator`, `https_validator`
- Add custom validators using `@ProxyValidator.addHttpValidator` decorator

### Proxy Model (`helper/proxy.py`)
- `Proxy` class with attributes: proxy, fail_count, region, source, https, check_count, last_status, last_time
- JSON serialization via `to_dict` and `to_json` properties

### Scheduler (`helper/scheduler.py`)
- `runScheduler()`: APScheduler-based periodic tasks
- Proxy fetch: every 4 minutes
- Proxy check: every 2 minutes

### API (`api/proxyApi.py`)
- `GET /`: API documentation
- `GET /get?type=https`: Get random proxy
- `GET /pop?type=https`: Get and remove proxy
- `GET /all?type=https`: Get all proxies
- `GET /count`: Get proxy statistics
- `GET /delete?proxy=ip:port`: Remove specific proxy

## Extending the System

### Add New Proxy Source
1. Add static method to `ProxyFetcher` class in `fetcher/proxyFetcher.py`:
```python
@staticmethod
def freeProxyCustom():
    for proxy in ["x.x.x.x:8080"]:
        yield proxy
```
2. Add method name to `PROXY_FETCHER` list in `setting.py`

### Add Custom Validator
```python
@ProxyValidator.addHttpValidator
def customValidator(proxy):
    # validation logic
    return True/False
```
