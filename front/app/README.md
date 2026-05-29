# 11주차 과제 — Feature Flag & A/B 테스트

## 실행 화면

> `http://localhost:5173`

![alt text](<스크린샷 2026-05-29 231415.png>)

### 화면에서 확인할 수 있는 것

- **🎤 음성 버튼** (입력창 옆) — `FEATURE_VOICE_INPUT` 플래그가 `true`로 활성화된 상태입니다. 환경 변수(`VITE_FEATURE_VOICE_INPUT=true`) 또는 베타 사용자 목록(`VITE_BETA_USERS`)에 의해 켜집니다.
- **빠른 답변 칩** (비자 연장 · 외국인등록 · 건강보험 등) — `FEATURE_QUICK_REPLIES` 플래그가 `true`로 활성화된 상태입니다. 클릭 시 `quick_reply_clicked` 이벤트가 localStorage에 기록됩니다.

두 기능 모두 `.env.local`에서 `false`로 바꾸면 UI에서 즉시 사라집니다.

---

## 과제 요약

| 항목 | 내용 |
|------|------|
| Feature Flag | 3개 (환경 변수 + 대상 사용자 기준 토글) |
| A/B 테스트 | 2개 실험 (variant 할당 일관성 + 이벤트 추적) |

---

## Feature Flags (3개)

### 1. `FEATURE_VOICE_INPUT` — 음성 입력 버튼

채팅 입력창 옆에 🎤 마이크 버튼을 표시합니다.

**토글 방법** (`front/app/.env.local`):
```env
VITE_FEATURE_VOICE_INPUT=true   # 활성화
VITE_FEATURE_VOICE_INPUT=false  # 비활성화
```

**대상 사용자 기준** — `VITE_BETA_USERS`에 등록된 userId에게만 활성화:
```env
VITE_BETA_USERS=user_001,user_beta1
```

---

### 2. `FEATURE_DARK_MODE` — 다크 모드

앱 전체 배경을 어둡게 변경합니다. 환경 변수 전용입니다.

```env
VITE_FEATURE_DARK_MODE=true   # 활성화
VITE_FEATURE_DARK_MODE=false  # 비활성화
```

---

### 3. `FEATURE_QUICK_REPLIES` — 빠른 답변 칩

채팅 입력창 위에 자주 묻는 질문 버튼을 표시합니다.

```env
VITE_FEATURE_QUICK_REPLIES=true   # 활성화
VITE_FEATURE_QUICK_REPLIES=false  # 비활성화
```

---

### 토글 우선순위

```
환경 변수 (VITE_FEATURE_*) > 대상 사용자 화이트리스트 > 기본값(false)
```

**구현 코드**: [src/config/featureFlags.js](https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/src/config/featureFlags.js)

```js
export function isEnabled(flagKey, userId = null) {
  const flag = FLAGS[flagKey];

  // 1. 환경 변수 우선
  if (flag.envVar === 'true') return true;
  if (flag.envVar === 'false') return false;

  // 2. 대상 사용자 화이트리스트
  if (userId && flag.targetUsers.includes(userId)) return true;

  return flag.defaultEnabled;
}
```

---

## A/B 테스트 (2개)

### 실험 1. `AB_WELCOME_MESSAGE` — 온보딩 환영 메시지

| | Variant A (50%) | Variant B (50%) |
|-|-----------------|-----------------|
| 문구 | "한국 유학 생활, 더 쉽게" | "AI 에이전트가 비자·행정 문제를 단번에" |
| 아이콘 | 🎓 | 🤖 |

---

### 실험 2. `AB_CHAT_LAYOUT` — 메인 채팅 레이아웃

| | Variant A (50%) | Variant B (50%) |
|-|-----------------|-----------------|
| 레이아웃 | 입력창 단독 | 추천 질문 카드 + 입력창 |

---

### 사용자 할당 일관성

동일 사용자는 항상 동일 variant에 배정됩니다.  
`userId`를 djb2 해시로 변환해 0~99 사이 bucket을 결정합니다.

**구현 코드**: [src/config/experiments.js](https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/src/config/experiments.js)

```js
function hashString(str) {
  let h = 5381;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) + h) ^ str.charCodeAt(i);
  }
  return Math.abs(h);
}

export function assignVariant(experimentKey, userId) {
  const bucket = hashString(`${exp.key}:${userId}`) % 100;
  // 0~49 → A,  50~99 → B
}
```

---

## 이벤트 추적

**구현 코드**: [src/utils/analytics.js](https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/src/utils/analytics.js)

| 이벤트 | 발생 시점 |
|--------|-----------|
| `feature_flag_evaluated` | 앱 로드 시 각 플래그 평가 |
| `experiment_assigned` | 앱 로드 시 실험 variant 배정 |
| `experiment_interaction` | A/B 요소 클릭 시 |
| `quick_reply_clicked` | 빠른 답변 칩 클릭 |
| `voice_input_triggered` | 음성 입력 버튼 클릭 |

**브라우저 콘솔에서 실험 로그 확인:**
```js
JSON.parse(localStorage.getItem('uniguide_events'))
```

---

## 파일 구조

```
src/
├── config/
│   ├── featureFlags.js       # 플래그 정의 및 평가 로직
│   └── experiments.js        # A/B 실험 정의 및 variant 배정
├── utils/
│   └── analytics.js          # 이벤트 추적
├── context/
│   └── FeatureFlagContext.jsx # 전역 Context Provider
└── hooks/
    ├── useFeatureFlag.js      # 플래그 조회 훅
    └── useABTest.js           # A/B 테스트 훅
```

---

## 로컬 실행

```bash
cd front/app
npm install
npm run dev
# → http://localhost:5173
```

---

## GitHub 링크 정리

- **플래그 코드**: https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/src/config/featureFlags.js
- **실험 코드**: https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/src/config/experiments.js
- **실험 로그**: https://github.com/nadasoom2/yhs_AIOSS/blob/main/front/app/experiment-log.json
