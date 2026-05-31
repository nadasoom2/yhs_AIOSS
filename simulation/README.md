# 13주차 — LLM 페르소나 A/B 테스트 시뮬레이션

## 실험 문서 / 데이터 / 결정 기록 링크

| 항목 | 링크 |
|------|------|
| 시뮬레이션 코드 | [simulation/persona_simulation.py](persona_simulation.py) |
| A/B 테스트 결과 보고서 | [simulation/results/ab_test_report.md](results/ab_test_report.md) |
| 원시 이벤트 데이터 (JSON) | [simulation/results/simulation_data.json](results/simulation_data.json) |
| Feature Flag 정의 | [front/app/src/config/featureFlags.js](../front/app/src/config/featureFlags.js) |
| A/B 실험 정의 | [front/app/src/config/experiments.js](../front/app/src/config/experiments.js) |

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
| 01 | 리웨이 (Li Wei) | 중국 | 중급 TOPIK 4 | D-2 | A | A |
| 02 | 응우옌 티 마이 (Nguyen Thi Mai) | 베트남 | 초급 TOPIK 2 | D-4 | A | B |
| 03 | 바야르 (Bayar) | 몽골 | 고급 TOPIK 6 | D-2 | A | A |
| 04 | 찬티다 (Chanthida) | 태국 | 중급 TOPIK 3 | D-2 | A | B |
| 05 | 압둘라 유수포프 (Abdulla Yusupov) | 우즈베키스탄 | 초급 TOPIK 1 | D-2 | A | A |
| 06 | 데위 수산티 (Dewi Susanti) | 인도네시아 | 중급 TOPIK 4 | D-2 | B | B |
| 07 | 하야시 유이 (Hayashi Yui) | 일본 | 고급 TOPIK 5 | D-2 | B | A |
| 08 | 카일 존슨 (Kyle Johnson) | 미국 | 초급 (없음) | D-2 | B | B |
| 09 | 에마누엘 오비 (Emmanuel Obi) | 나이지리아 | 중급 TOPIK 3 | D-2 | B | A |
| 10 | 소피 마르탱 (Sophie Martin) | 프랑스 | 고급 TOPIK 6 | D-2 | B | B |

---

## A/B 실험 결과 요약

### 실험 1 — 환영 메시지 (WELCOME_MESSAGE)

| 지표 | A: "한국 유학 생활, 더 쉽게" | B: "AI 에이전트가 비자·행정 문제를 단번에" | 차이 |
|------|------|------|------|
| 평균 만족도 | 4.10 / 5 | 4.27 / 5 | **+0.17** |
| 리텐션율 | 66.0% | 67.0% | +1.0%p |
| 주당 평균 세션 | 4.6회 | 4.7회 | +0.1회 |
| 태스크 완료율 | 100% | 100% | 0% |

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

## 페르소나별 상세 결과

| 페르소나 | WM | Layout | 리텐션 | 만족도 | 완료율 | QR클릭 |
|---------|-----|--------|--------|--------|--------|--------|
| 리웨이 (Li Wei) | A | A | 93% | 4.0/5 | 100% | 0회 |
| 응우옌 티 마이 (Nguyen Thi Mai) | A | B | 71% | 4.2/5 | 100% | 10회 |
| 바야르 (Bayar) | A | A | 21% | 4.0/5 | 100% | 0회 |
| 찬티다 (Chanthida) | A | B | 93% | 4.3/5 | 100% | 12회 |
| 압둘라 유수포프 (Abdulla Yusupov) | A | A | 50% | 4.0/5 | 100% | 0회 |
| 데위 수산티 (Dewi Susanti) | B | B | 71% | 4.7/5 | 100% | 9회 |
| 하야시 유이 (Hayashi Yui) | B | A | 71% | 4.0/5 | 100% | 0회 |
| 카일 존슨 (Kyle Johnson) | B | B | 71% | 3.8/5 | 100% | 9회 |
| 에마누엘 오비 (Emmanuel Obi) | B | A | 71% | 4.0/5 | 100% | 0회 |
| 소피 마르탱 (Sophie Martin) | B | B | 50% | 4.9/5 | 100% | 2회 |

---

## 결정 기록 (Decision Log)

| 결정 | 내용 | 이유 |
|------|------|------|
| 시뮬레이션 방식 | 실제 2주 측정 대신 LLM 페르소나 시뮬레이션 | 과제 조건이 "LLM 페르소나 패턴" 명시 |
| A/B 배정 방식 | 명시적 2×2 factorial 배정 (각 5명) | 해시 기반 배정 시 10명 모두 동일 그룹 편향 발생 |
| 측정 지표 | 리텐션율·만족도·완료율·QR클릭 | Feature Flag 핵심 지표 (참여·만족·전환) |
| 채택 Variant | 두 실험 모두 B | 만족도·리텐션 모두 B 우세 |
