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

# Start with a YAML config file
proxy-pool -c config.yaml server

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

Configuration uses three-level priority: **env vars > YAML config file > setting.py defaults**.

### Config Sources

1. **setting.py** — hardcoded defaults, always present
2. **YAML config file** — `config.yaml` in project root, `/etc/proxy-pool/config.yaml`, or path specified by `PROXY_POOL_CONFIG` env var / `--config` CLI option. See `config.yaml.example` for all available keys.
3. **Environment variables** — highest priority, override both YAML and defaults. `PROXY_FETCHER` accepts comma-separated values (e.g., `PROXY_FETCHER=freeProxy01,freeProxy05`).

### Key Config Items
- `DB_CONN` / `db_conn`: Database connection URI (format: `redis://:password@host:port/db`)
- `HOST`/`host` / `PORT`/`port`: API server bind address
- `PROXY_FETCHER`/`proxy_fetcher`: List of fetcher method names to enable
- `VERIFY_TIMEOUT`/`verify_timeout`: Proxy validation timeout (seconds)
- `POOL_SIZE_MIN`/`pool_size_min`: Minimum proxy count before triggering fetch
- `PROXY_REGION`/`proxy_region`: Enable geo-region lookup via ip-api.com (accepts: true/false, yes/no, on/off, 1/0; free tier: 45 req/min)
- `PROXY_POOL_CONFIG`: Path to YAML config file
- `REFRESH_SIGNAL_KEY`/`refresh_signal_key`: Redis key for cross-process refresh signal

### Config Handler (`handler/configHandler.py`)
- Singleton with `LazyProperty` for cached access
- `_get(env_key, yaml_key, default, converter)` implements three-level priority
- Empty-string env vars are ignored (logged as warning) and fall through to next priority
- Converter errors (e.g., `PROXY_REGION=enabled`) are caught, logged as warnings, and fall through to next priority
- YAML bool-to-int coercion is blocked (e.g., `port: yes` → `int(True)==1` is rejected with warning)
- `fetchers` property has special handling: env var as comma-separated string, YAML as list, empty env var falls through to defaults

### Config Utils (`util/configUtils.py`)
- `parse_bool(value)`: Strict bool parsing — fixes `bool("False") == True` bug. Accepts true/1/yes/on and false/0/no/off; raises `ValueError` for unrecognized strings, non-0/1 integers, and other types
- Important: `isinstance(value, bool)` is checked before `isinstance(value, int)` since `bool` is a subclass of `int` in Python

### YAML Config (`util/yamlConfig.py`)
- `set_config_path(path)`: Sets `PROXY_POOL_CONFIG` env var (called by CLI `--config`)
- `load_yaml_config()`: Lazy-loaded by ConfigHandler, uses `yaml.safe_load`
- Config file search order: `PROXY_POOL_CONFIG` env var → `config.yaml` → `/etc/proxy-pool/config.yaml`
- Handles `yaml.YAMLError`, `OSError`, and `UnicodeDecodeError` gracefully with warnings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point (proxyPool.py)                │
│                    CLI using Click framework                 │
│                    --config/-c for YAML config path          │
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
│          ConfigHandler                         │
│       handler/configHandler.py                │
│  env > YAML > setting.py (three-level)       │
│  Singleton + LazyProperty                     │
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
- Signal methods (`setSignal`, `getSignal`, `existsSignal`, `deleteSignal`): cross-process communication via Redis keys

### Fetcher (`fetcher/proxyFetcher.py`)
- Static methods that yield proxies from various free proxy websites
- Each method returns `host:port` format strings
- Add new fetchers by creating `freeProxyXX()` static methods
- Register new fetchers in `setting.py` `PROXY_FETCHER` list, `config.yaml` `proxy_fetcher`, or `PROXY_FETCHER` env var (comma-separated)

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
- Checks Redis refresh signal (from `/refresh/` API) on each check cycle

### API (`api/proxyApi.py`)
- `GET /`: API documentation
- `GET /get?type=https`: Get random proxy
- `GET /pop?type=https`: Get and remove proxy
- `GET /all?type=https`: Get all proxies
- `GET /count`: Get proxy statistics (includes `https_note` when 0 HTTPS proxies)
- `GET /delete?proxy=ip:port`: Remove specific proxy
- `GET /refresh`: Request a proxy pool refresh (async via Redis signal to scheduler)

### Known Limitations
- **HTTPS proxies**: Free proxy sources rarely support HTTPS CONNECT tunneling. Pool will typically have 0 HTTPS proxies. This is a fundamental limitation of free proxies, not a validation bug.
- **Region API rate limit**: ip-api.com free tier allows 45 requests/minute. Under heavy concurrent validation, some region lookups may be rate-limited (returns empty string, logged as warning).

## Extending the System

### Add New Proxy Source
1. Add static method to `ProxyFetcher` class in `fetcher/proxyFetcher.py`:
```python
@staticmethod
def freeProxyCustom():
    for proxy in ["x.x.x.x:8080"]:
        yield proxy
```
2. Add method name to `PROXY_FETCHER` list in `setting.py`, `proxy_fetcher` in `config.yaml`, or `PROXY_FETCHER` env var

### Add Custom Validator
```python
@ProxyValidator.addHttpValidator
def customValidator(proxy):
    # validation logic
    return True/False
```
