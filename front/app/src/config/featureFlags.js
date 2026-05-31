/**
 * Feature Flag 정의 및 평가 로직
 *
 * 토글 우선순위:
 *  1. 환경 변수 (VITE_FEATURE_*) — 전체 활성화/비활성화
 *  2. 대상 사용자(targetUsers) 화이트리스트
 *  3. defaultEnabled 기본값
 */

const FLAGS = {
  // 음성 입력 버튼 (채팅 입력창에 마이크 아이콘 노출)
  VOICE_INPUT: {
    key: 'FEATURE_VOICE_INPUT',
    envVar: import.meta.env.VITE_FEATURE_VOICE_INPUT,
    targetUsers: (import.meta.env.VITE_BETA_USERS || '').split(',').filter(Boolean),
    defaultEnabled: false,
  },
  // 다크 모드 테마 (환경 변수 전용 — 사용자 타겟 없음)
  DARK_MODE: {
    key: 'FEATURE_DARK_MODE',
    envVar: import.meta.env.VITE_FEATURE_DARK_MODE,
    targetUsers: [],
    defaultEnabled: false,
  },
  // 빠른 답변 칩 (채팅 화면 하단 추천 질문 버튼)
  // CHAT_LAYOUT A/B 실험(experiments.js)의 게이트 — 이 플래그가 꺼지면 실험 진입 불가
  QUICK_REPLIES: {
    key: 'FEATURE_QUICK_REPLIES',
    envVar: import.meta.env.VITE_FEATURE_QUICK_REPLIES,
    targetUsers: (import.meta.env.VITE_BETA_USERS || '').split(',').filter(Boolean),
    defaultEnabled: false,
  },
};

/**
 * 특정 플래그가 활성화돼 있는지 평가
 * @param {string} flagKey - FLAGS 키 (예: 'VOICE_INPUT')
 * @param {string|null} userId - 현재 사용자 ID
 * @returns {boolean}
 */
export function isEnabled(flagKey, userId = null) {
  const flag = FLAGS[flagKey];
  if (!flag) return false;

  // 1. 환경 변수 우선
  if (flag.envVar === 'true' || flag.envVar === '1') return true;
  if (flag.envVar === 'false' || flag.envVar === '0') return false;

  // 2. 대상 사용자 화이트리스트
  if (userId && flag.targetUsers.length > 0 && flag.targetUsers.includes(userId)) {
    return true;
  }

  return flag.defaultEnabled;
}

export const FLAG_KEYS = Object.keys(FLAGS);
export default FLAGS;
