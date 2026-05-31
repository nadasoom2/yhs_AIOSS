/**
 * A/B 테스트 통계 집계 유틸리티
 *
 * TDD Feature 5 — 🟢 Green 단계 구현
 * stats.test.js의 모든 테스트를 통과하는 최소 구현.
 */

const ASSIGNED_EVENT = 'experiment_assigned'

/**
 * analytics 이벤트 배열에서 특정 실험의 A/B 배정 통계를 집계한다.
 *
 * @param {Array<{name: string, properties: object, ts: string}>} events
 * @param {string} experimentKey - 집계할 실험 키 (예: 'WELCOME_MESSAGE')
 * @returns {{ A: { count: number, rate: number }, B: { count: number, rate: number } }}
 */
export function getVariantStats(events, experimentKey) {
  const stats = {
    A: { count: 0, rate: 0 },
    B: { count: 0, rate: 0 },
  }

  const relevant = events.filter(
    e =>
      e.name === ASSIGNED_EVENT &&
      e.properties?.experiment === experimentKey,
  )

  relevant.forEach(e => {
    const v = e.properties.variant
    if (stats[v] !== undefined) {
      stats[v].count += 1
    }
  })

  const total = relevant.length
  if (total > 0) {
    Object.keys(stats).forEach(v => {
      stats[v].rate = stats[v].count / total
    })
  }

  return stats
}

/**
 * 이벤트 배열에서 빈도 상위 N개의 이벤트를 반환한다.
 *
 * @param {Array<{name: string}>} events
 * @param {number} limit - 반환할 최대 이벤트 수 (기본 5)
 * @returns {Array<{ name: string, count: number }>} 빈도 내림차순 정렬
 */
export function getTopEvents(events, limit = 5) {
  const freq = {}
  events.forEach(e => {
    freq[e.name] = (freq[e.name] || 0) + 1
  })

  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([name, count]) => ({ name, count }))
}
