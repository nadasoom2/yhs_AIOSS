/**
 * 이벤트 추적 유틸리티
 *
 * localStorage에 이벤트를 축적하며, 향후 외부 분석 서비스로 전송 가능하도록
 * track() 함수 하나로 추상화합니다.
 *
 * 저장 형식: localStorage['uniguide_events'] = JSON 배열
 * 최대 저장 수: EVENT_LIMIT 초과 시 오래된 이벤트 삭제
 */

const STORAGE_KEY = 'uniguide_events';
const EVENT_LIMIT = 200;

/**
 * 이벤트 기록
 * @param {string} name - 이벤트 이름 (예: 'feature_flag_evaluated')
 * @param {Record<string, unknown>} properties
 */
export function track(name, properties = {}) {
  const event = {
    name,
    properties,
    ts: new Date().toISOString(),
  };

  // 콘솔 출력 (개발 환경 디버깅)
  if (import.meta.env.DEV) {
    console.log('[Analytics]', name, properties);
  }

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const events = raw ? JSON.parse(raw) : [];
    events.push(event);

    // 오래된 이벤트 정리
    if (events.length > EVENT_LIMIT) {
      events.splice(0, events.length - EVENT_LIMIT);
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  } catch {
    // 저장 실패 시 무시 (Private Mode 등)
  }
}

/**
 * 저장된 이벤트 전체 조회
 * @returns {Array}
 */
export function getEvents() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/**
 * 저장된 이벤트 초기화
 */
export function clearEvents() {
  localStorage.removeItem(STORAGE_KEY);
}

// ── 표준 이벤트 이름 상수 ─────────────────────────────────────
export const EVENTS = {
  FEATURE_FLAG_EVALUATED: 'feature_flag_evaluated',
  EXPERIMENT_ASSIGNED: 'experiment_assigned',
  EXPERIMENT_INTERACTION: 'experiment_interaction',
  FEATURE_USED: 'feature_used',
  QUICK_REPLY_CLICKED: 'quick_reply_clicked',
  VOICE_INPUT_TRIGGERED: 'voice_input_triggered',
  DARK_MODE_SEEN: 'dark_mode_seen',
};
