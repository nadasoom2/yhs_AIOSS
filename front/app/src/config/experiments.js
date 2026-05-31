/**
 * A/B 테스트 실험 정의
 *
 * - 각 실험은 variants 배열과 weights(백분율, 합계 100) 로 구성
 * - assignVariant()는 userId 기반 해시를 사용해 항상 동일한 variant를 반환 (일관성 보장)
 */

export const EXPERIMENTS = {
  // 온보딩 환영 메시지 텍스트 실험
  WELCOME_MESSAGE: {
    key: 'AB_WELCOME_MESSAGE',
    variants: ['A', 'B'],
    weights: [50, 50],
    description: {
      A: '기존 문구 — "한국 유학 생활, 더 쉽게"',
      B: '신규 문구 — "AI 에이전트가 비자·행정 문제를 단번에"',
    },
  },
  // 메인 채팅 레이아웃 실험
  CHAT_LAYOUT: {
    key: 'AB_CHAT_LAYOUT',
    variants: ['A', 'B'],
    weights: [50, 50],
    description: {
      A: '기존 입력창 단독 레이아웃',
      B: '추천 질문 카드 + 입력창 레이아웃',
    },
  },
};

/**
 * 문자열 → 부호 없는 32비트 정수 해시 (djb2 변형)
 * @param {string} str
 * @returns {number} 0 이상 정수
 */
export function hashString(str) {
  let h = 5381;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) + h) ^ str.charCodeAt(i);
  }
  return Math.abs(h);
}

/**
 * 사용자를 실험의 variant에 일관되게 배정
 * @param {string} experimentKey - EXPERIMENTS 키
 * @param {string} userId
 * @returns {'A'|'B'|string} 배정된 variant
 */
export function assignVariant(experimentKey, userId) {
  const exp = EXPERIMENTS[experimentKey];
  if (!exp) return null;

  const bucket = hashString(`${exp.key}:${userId}`) % 100;

  let cumWeight = 0;
  for (let i = 0; i < exp.variants.length; i++) {
    cumWeight += exp.weights[i];
    if (bucket < cumWeight) return exp.variants[i];
  }
  return exp.variants[0];
}

export const EXPERIMENT_KEYS = Object.keys(EXPERIMENTS);
