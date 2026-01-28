# Master Agent (마스터 에이전트)

Google ADK 기반의 A2A 오케스트레이터 에이전트입니다.

## 기능
- 사용자 요청 분석 및 적절한 서브 에이전트로 라우팅
- Transaction Agent와 Card Recommend Agent 조율
- 멀티턴 대화 세션 관리

## 서브 에이전트
- `transaction_agent`: 거래내역 발송 서비스
- `card_recommend_agent`: 카드 추천 서비스
