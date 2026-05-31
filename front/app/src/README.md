# 12주차 — 단위 테스트 & CI 자동화 / 13주차 — LLM 페르소나 A/B 테스트 시뮬레이션

---

# 12주차 — 단위 테스트 & CI 자동화

## 링크

| 항목 | 링크 |
|------|------|
| 테스트 코드 | [front/app/src/config/__tests__/](config/__tests__/) |
| 테스트 코드 | [front/app/src/utils/__tests__/](utils/__tests__/) |
| CI 워크플로우 | [frontend-test.yml](../../../.github/workflows/frontend-test.yml) |
| CI 실행 결과 | [Actions](https://github.com/nadasoom2/yhs_AIOSS/actions/workflows/frontend-test.yml) |

<table>
  <tr>
    <td><img src="image.png" width="480"/></td>
    <td><img src="image-1.png" width="480"/></td>
  </tr>
</table>

---

## TDD Red-Green-Refactor 사이클

### 구현한 핵심 기능 5가지

| # | 기능 | 파일 | 테스트 파일 |
|---|------|------|------------|
| 1 | Feature Flag 평가 (`isEnabled`) | [featureFlags.js](config/featureFlags.js) | [featureFlags.test.js](config/__tests__/featureFlags.test.js) |
| 2 | 해시 기반 버켓팅 (`hashString`) | [experiments.js](config/experiments.js) | [experiments.test.js](config/__tests__/experiments.test.js) |
| 3 | A/B 배정 로직 (`assignVariant`) | [experiments.js](config/experiments.js) | [experiments.test.js](config/__tests__/experiments.test.js) |
| 4 | 이벤트 추적 (`track / getEvents / clearEvents`) | [analytics.js](utils/analytics.js) | [analytics.test.js](utils/__tests__/analytics.test.js) |
| 5 | A/B 통계 집계 (`getVariantStats / getTopEvents`) | [stats.js](utils/stats.js) | [stats.test.js](utils/__tests__/stats.test.js) |

### Feature 5 — 완전한 TDD 사이클 예시

```
🔴 Red    stats.js 없이 stats.test.js만 존재 → npm test → 전부 실패
🟢 Green  stats.js 구현 추가 → npm test → 전부 통과
🔵 Refactor  중복 제거, 변수명 명확화 → 테스트 여전히 Green 유지
```

---

## 테스트 실행 방법

```bash
cd front/app
npm install
npm test                # 단순 실행
npm run test:coverage   # 커버리지 측정 (80% 임계값)
```

## 커버리지 기준

| 항목 | 임계값 |
|------|--------|
| Lines | ≥ 80% |
| Functions | ≥ 80% |
| Branches | ≥ 80% |
| Statements | ≥ 80% |

커버리지 대상: `src/config/**`, `src/utils/**`

---

## CI 자동 실행 조건

`main` 브랜치에 `front/**` 경로 변경이 push 또는 PR될 때 자동 실행되며,
커버리지 80% 미달 시 CI가 실패합니다.

---

# 13주차 — LLM 페르소나 A/B 테스트 시뮬레이션

## 실험 문서 / 데이터 / 결정 기록 링크

| 항목 | 링크 |
|------|------|
| 시뮬레이션 코드 | [simulation/persona_simulation.py](../../../simulation/persona_simulation.py) |
| A/B 테스트 결과 보고서 | [simulation/results/ab_test_report.md](../../../simulation/results/ab_test_report.md) |
| 원시 이벤트 데이터 (JSON) | [simulation/results/simulation_data.json](../../../simulation/results/simulation_data.json) |
| Feature Flag 정의 | [src/config/featureFlags.js](config/featureFlags.js) |
| A/B 실험 정의 | [src/config/experiments.js](config/experiments.js) |

---

## 개요

UniGuide AI (외국인 유학생 행정 도우미 앱)의 Feature Flag 기반 A/B 테스트를 **LLM 페르소나 시뮬레이션**으로 2주 운영했습니다.

- **시뮬레이션 기간:** 2026-05-01 ~ 2026-05-14 (14일)
- **페르소나:** 10명 (국적·한국어 수준·비자 유형 각기 다름)
- **LLM 모델:** GPT-4o-mini (각 페르소나가 실제 질문·피드백 생성)
- **실험 수:** 2개 (환영 메시지, 채팅 레이아웃)

---

## 10개 LLM 페르소나

| # | 이름 | 국적 | 한국어 | 비자 | WM그룹 | Layout그룹 |
|---|------|------|--------|------|--------|-----------|
| 01 | 리웨이 | 중국 | 중급 TOPIK 4 | D-2 | A | A |
| 02 | 응우옌 티 마이 | 베트남 | 초급 TOPIK 2 | D-4 | A | B |
| 03 | 바야르 | 몽골 | 고급 TOPIK 6 | D-2 | A | A |
| 04 | 찬티다 | 태국 | 중급 TOPIK 3 | D-2 | A | B |
| 05 | 압둘라 유수포프 | 우즈베키스탄 | 초급 TOPIK 1 | D-2 | A | A |
| 06 | 데위 수산티 | 인도네시아 | 중급 TOPIK 4 | D-2 | B | B |
| 07 | 하야시 유이 | 일본 | 고급 TOPIK 5 | D-2 | B | A |
| 08 | 카일 존슨 | 미국 | 초급 (없음) | D-2 | B | B |
| 09 | 에마누엘 오비 | 나이지리아 | 중급 TOPIK 3 | D-2 | B | A |
| 10 | 소피 마르탱 | 프랑스 | 고급 TOPIK 6 | D-2 | B | B |

---

## A/B 실험 결과 요약

### 실험 1 — 환영 메시지 (WELCOME_MESSAGE)

| 지표 | A: "한국 유학 생활, 더 쉽게" | B: "AI 에이전트가 비자·행정 문제를 단번에" | 차이 |
|------|------|------|------|
| 평균 만족도 | 4.10 / 5 | 4.27 / 5 | **+0.17** |
| 리텐션율 | 66.0% | 67.0% | +1.0%p |
| 주당 평균 세션 | 4.6회 | 4.7회 | +0.1회 |

→ **Variant B 우세** — AI 기능 강조 문구가 유학생의 관심을 더 효과적으로 포착

### 실험 2 — 채팅 레이아웃 (CHAT_LAYOUT)

| 지표 | A: 입력창 단독 | B: 추천 질문 카드 + 입력창 | 차이 |
|------|------|------|------|
| 평균 만족도 | 4.00 / 5 | 4.37 / 5 | **+0.37** |
| 리텐션율 | 61.0% | 71.0% | **+10.0%p** |
| 주당 평균 세션 | 4.3회 | 5.0회 | +0.7회 |
| 추천 카드 클릭 | 0회 | **42회** | — |

→ **Variant B 우세** — 추천 카드가 한국어 초급 페르소나(압둘라, 마이)의 진입 장벽을 낮춰 리텐션 10%p 향상

---

## 결정 기록 (Decision Log)

| 결정 | 내용 | 이유 |
|------|------|------|
| 시뮬레이션 방식 | 실제 2주 측정 대신 LLM 페르소나 시뮬레이션 | 과제 조건이 "LLM 페르소나 패턴" 명시 |
| A/B 배정 방식 | 명시적 2×2 factorial 배정 (각 5명) | 해시 기반 배정 시 10명 모두 동일 그룹 편향 발생 |
| 측정 지표 | 리텐션율·만족도·완료율·QR클릭 | Feature Flag 핵심 지표 (참여·만족·전환) |
| 채택 Variant | 두 실험 모두 B | 만족도·리텐션 모두 B 우세 |
