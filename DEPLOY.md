# 서버 배포 가이드 (Linux)

대상: Ubuntu 22.04 / 24.04 LTS · 도메인 `daum-mcp.toy.x.upstage.ai`
공개 포트: 443 (HTTPS) → 내부 8989 (uvicorn)

> 두 가지 경로 중 하나를 고르세요. **A**가 가장 간단합니다.
> - **A. Docker Compose** (10분, 권장)
> - **B. systemd + venv** (네이티브, 컨테이너 없이)

공통 사전 작업은 §1, 그 다음 A 또는 B, 마지막 §4 HTTPS 프록시.

---

## 1. 사전 준비 (공통)

```bash
# 1) DNS 레코드를 먼저 설정
#    A 레코드: daum-mcp.toy.x.upstage.ai  →  서버의 공인 IP
#    (toy.x.upstage.ai 영역 관리 권한자에게 요청)

# 2) 서버에 SSH 접속 후
sudo apt update && sudo apt -y upgrade
sudo apt -y install git curl ufw

# 3) 방화벽 — 80/443/SSH만 개방
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 4) 코드 체크아웃
sudo mkdir -p /opt && cd /opt
sudo git clone https://github.com/hunkim/daum-mcp-toy.git
sudo chown -R "$USER":"$USER" /opt/daum-mcp-toy
cd /opt/daum-mcp-toy
```

---

## 2. 옵션 A — Docker Compose (권장)

```bash
# Docker가 없다면 설치 (Ubuntu 공식 스크립트)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
# 새 셸을 열거나 newgrp docker 후 진행

cd /opt/daum-mcp-toy
docker compose up -d --build

# 검증
docker compose ps                 # 상태 healthy 확인
curl http://127.0.0.1:8989/health # → {"status":"ok",...}
docker compose logs -f --tail=50  # 라이브 로그
```

운영 명령:
```bash
docker compose pull && docker compose up -d --build   # 업데이트
docker compose restart                                # 재시작
docker compose down                                   # 중지
```

§4로 진행 → HTTPS 프록시.

---

## 3. 옵션 B — systemd + venv (네이티브)

```bash
# 1) Python 3.10+ 와 venv
sudo apt -y install python3.12 python3.12-venv python3-pip

# 2) 서비스 계정
sudo useradd --system --home /opt/daum-mcp-toy --shell /usr/sbin/nologin daum || true
sudo chown -R daum:daum /opt/daum-mcp-toy

# 3) venv + 의존성
cd /opt/daum-mcp-toy
sudo -u daum python3.12 -m venv .venv
sudo -u daum .venv/bin/pip install --upgrade pip
sudo -u daum .venv/bin/pip install -e ".[serve]"

# 4) 부팅 1회 손동작 검증
sudo -u daum HOST=127.0.0.1 PORT=8989 .venv/bin/python -m servers.http_app &
sleep 2; curl http://127.0.0.1:8989/health; kill %1

# 5) systemd 등록
sudo cp deploy/daum-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now daum-mcp
sudo systemctl status daum-mcp --no-pager
sudo journalctl -u daum-mcp -f      # 라이브 로그
```

운영 명령:
```bash
sudo systemctl restart daum-mcp
sudo systemctl stop daum-mcp
git -C /opt/daum-mcp-toy pull
sudo -u daum /opt/daum-mcp-toy/.venv/bin/pip install -e ".[serve]"
sudo systemctl restart daum-mcp
```

---

## 4. HTTPS 리버스 프록시

도메인 DNS가 서버 IP로 잘 가리키는지 먼저 확인:
```bash
dig +short daum-mcp.toy.x.upstage.ai
```

### 4-A. Caddy (권장 — Let's Encrypt 자동)

```bash
# Caddy 설치 (Ubuntu)
sudo apt -y install debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt -y install caddy

# 설정 배치
sudo cp /opt/daum-mcp-toy/deploy/Caddyfile /etc/caddy/Caddyfile
sudo mkdir -p /var/log/caddy && sudo chown caddy:caddy /var/log/caddy

# 적용 — 첫 실행에서 자동으로 인증서 발급
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

### 4-B. nginx + certbot

```bash
sudo apt -y install nginx certbot python3-certbot-nginx
sudo cp /opt/daum-mcp-toy/deploy/nginx.conf /etc/nginx/sites-available/daum-mcp
sudo ln -sf /etc/nginx/sites-available/daum-mcp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 인증서 발급
sudo certbot --nginx -d daum-mcp.toy.x.upstage.ai \
  --redirect --agree-tos -m hunkim@upstage.ai --no-eff-email
sudo systemctl reload nginx
```

---

## 5. End-to-end 검증

```bash
# 헬스
curl -i https://daum-mcp.toy.x.upstage.ai/health

# 인벤토리
curl -s https://daum-mcp.toy.x.upstage.ai/ | jq .

# MCP 클라이언트 라운드트립 (서버 또는 로컬에서)
python3 - <<'PY'
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

URL = "https://daum-mcp.toy.x.upstage.ai/knowledge/mcp"

async def main():
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("tools:", [t.name for t in tools.tools])
            res = await s.call_tool("dict_lookup", {"word": "정산", "direction": "ko-en"})
            print("first content:", res.content[0].text[:200])

asyncio.run(main())
PY
```

---

## 6. 트러블슈팅

| 증상 | 점검 |
|------|------|
| `502 Bad Gateway` | uvicorn 미동작 — `systemctl status daum-mcp` 또는 `docker compose ps` |
| `404` on `/meta/mcp` | path 오타 또는 prefix 없이 호출 — 인벤토리(`GET /`) 다시 확인 |
| 인증서 발급 실패 | DNS 전파 대기 / 80 포트가 막혔는지 / 도메인 영역 권한 확인 |
| 첫 호출 후 hang | 프록시 buffering — Caddyfile / nginx.conf 의 `flush_interval -1` / `proxy_buffering off` 확인 |
| 컨테이너에서 권한 거부 | `chown -R 10001 /opt/daum-mcp-toy` (Dockerfile 사용자 uid) |

---

## 7. 보안 다음 단계 (Tier 0 → Tier 1)

본 mock은 **인증 없는 read-only**입니다. 외부 공개 전에:

1. OAuth 2.1 + PKCE-S256 + RFC 8707 미들웨어 추가 (`hitl_ux_specification.md` §1)
2. tenant 별 rate-limit (현재 stub) 활성화 — Redis backend 권장
3. PII 검증을 KISA 패턴 + Solar PII classifier로 강화
4. `_meta.request_id` → OpenTelemetry trace_id 매핑, Loki/Grafana 송출
5. ufw 외에 fail2ban 등록

---

## 8. 메모

- 기본 포트: **8989** (`servers/http_app.py`, `Dockerfile`, `docker-compose.yml`, systemd unit 모두 일치)
- 호스트 노출 포트: 443만. 8989는 127.0.0.1 바인딩 권장 (Caddy/nginx가 프록시)
- 자동 업데이트가 필요하면 GitHub Actions + `webhook` 또는 `watchtower` (Docker) 추가

문제 발견 시 [github.com/hunkim/daum-mcp-toy/issues](https://github.com/hunkim/daum-mcp-toy/issues)
