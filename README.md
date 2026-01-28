# 신한카드 A2A 멀티 에이전트 데모

> **⚠️ DISCLAIMER: 이 프로젝트는 데모 목적으로만 제작되었습니다. 프로덕션 환경에서의 사용을 권장하지 않습니다.**

A2A (Agent2Agent) 프로토콜을 활용한 멀티 에이전트 시스템 데모입니다. Master Agent가 사용자 요청을 분석하여 적절한 서브 에이전트(거래내역 발송, 카드 추천)로 라우팅합니다.

## 아키텍처

```
사용자 요청
    ↓
Master Agent (Google ADK + Gemini 2.5 Flash)
    ├→ Transaction Agent (CrewAI, port 10001)
    │   └→ 거래내역 이메일/SMS 발송
    └→ Card Recommend Agent (LangGraph, port 10000)
        └→ 소비패턴 기반 카드 추천
```

## Prerequisites

```shell
# Google Cloud 인증
gcloud auth application-default login

# API 활성화
gcloud services enable aiplatform.googleapis.com

# uv 설치 및 환경 구성
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv sync --frozen
```

## 로컬 실행

### 1. Transaction Agent 실행

```bash
cp remote_sub_agents/transaction_agent/.env.example remote_sub_agents/transaction_agent/.env
# .env 파일에 GOOGLE_CLOUD_PROJECT 설정

cd remote_sub_agents/transaction_agent
uv sync --frozen
uv run .
```
→ `http://localhost:10001`

### 2. Card Recommend Agent 실행

```bash
cp remote_sub_agents/card_recommend_agent/.env.example remote_sub_agents/card_recommend_agent/.env
# .env 파일에 GOOGLE_CLOUD_PROJECT 설정

cd remote_sub_agents/card_recommend_agent
uv sync --frozen
uv run .
```
→ `http://localhost:10000`

### 3. Master Agent 실행

```bash
cp master_agent/.env.example master_agent/.env
# .env 파일 설정:
# CARD_RECOMMEND_AGENT_URL=http://localhost:10000
# TRANSACTION_AGENT_URL=http://localhost:10001
# GOOGLE_CLOUD_PROJECT={your-project-id}

uv sync --frozen
uv run adk web
```

## 클라우드 배포

### Transaction Agent - Cloud Run

```bash
gcloud run deploy transaction-agent \
    --source remote_sub_agents/transaction_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min 1 \
    --region us-central1 \
    --update-env-vars GOOGLE_CLOUD_LOCATION=us-central1 \
    --update-env-vars GOOGLE_CLOUD_PROJECT={your-project-id}
```

### Card Recommend Agent - Cloud Run

```bash
gcloud run deploy card-recommend-agent \
    --source remote_sub_agents/card_recommend_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min 1 \
    --region us-central1 \
    --update-env-vars GOOGLE_CLOUD_PROJECT={your-project-id} \
    --update-env-vars GOOGLE_CLOUD_LOCATION=us-central1
```

### Master Agent - Agent Engine

```bash
# 스테이징 버킷 생성
gcloud storage buckets create gs://shcard-a2a-{your-project-id} --location=us-central1

# .env 파일 설정 후 배포
uv run deploy_to_agent_engine.py
```

### Chat UI 실행

```bash
# .env에 AGENT_ENGINE_RESOURCE_NAME 설정 후
uv run master_agent_ui.py
```

## 환경 변수

| 변수명 | 설명 |
|--------|------|
| `GOOGLE_CLOUD_PROJECT` | GCP 프로젝트 ID |
| `GOOGLE_CLOUD_LOCATION` | GCP 리전 (기본: us-central1) |
| `CARD_RECOMMEND_AGENT_URL` | 카드 추천 에이전트 URL |
| `TRANSACTION_AGENT_URL` | 거래내역 에이전트 URL |
| `AGENT_ENGINE_RESOURCE_NAME` | Agent Engine 리소스 이름 |
