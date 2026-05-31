/**
 * TDD Feature 5: getVariantStats / getTopEvents — A/B 통계 집계 유틸리티
 *
 * ✅ 완전한 Red-Green-Refactor 사이클 예시:
 *
 *  🔴 Red    : stats.js 파일이 없으므로 이 파일만 있으면 import 오류 → 테스트 전부 실패
 *              → `npm test` 실행 시 모든 테스트 RED 상태
 *
 *  🟢 Green  : stats.js를 최소한의 코드로 구현 → 모든 테스트 통과
 *              → `npm test` 실행 시 모든 테스트 GREEN 상태
 *
 *  🔵 Refactor: 중복 제거, 변수명 명확화, 엣지케이스 처리 개선
 *              → 테스트는 여전히 GREEN 유지
 */

import { describe, it, expect } from 'vitest'
import { getVariantStats, getTopEvents } from '../stats.js'
import { EVENTS } from '../analytics.js'

// 테스트용 이벤트 팩토리
const makeAssignedEvent = (experiment, variant) => ({
  name: EVENTS.EXPERIMENT_ASSIGNED,
  properties: { experiment, variant },
  ts: new Date().toISOString(),
})

const makeInteractionEvent = (experiment, variant, action) => ({
  name: EVENTS.EXPERIMENT_INTERACTION,
  properties: { experiment, variant, action },
  ts: new Date().toISOString(),
})

// ── getVariantStats() ─────────────────────────────────────────────────────────
describe('getVariantStats() — A/B 배정 통계 집계', () => {
  it('🔴→🟢 빈 이벤트 배열에서 A/B 모두 count=0, rate=0 반환', () => {
    const stats = getVariantStats([], 'WELCOME_MESSAGE')
    expect(stats.A.count).toBe(0)
    expect(stats.B.count).toBe(0)
    expect(stats.A.rate).toBe(0)
    expect(stats.B.rate).toBe(0)
  })

  it('🔴→🟢 A variant 이벤트 3개를 올바르게 집계', () => {
    const events = [
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
    ]
    const stats = getVariantStats(events, 'WELCOME_MESSAGE')
    expect(stats.A.count).toBe(3)
    expect(stats.B.count).toBe(0)
    expect(stats.A.rate).toBeCloseTo(1.0)
    expect(stats.B.rate).toBeCloseTo(0)
  })

  it('🔴→🟢 A/B 혼합 이벤트를 올바르게 분리 집계하고 rate 합계는 1', () => {
    const events = [
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
      makeAssignedEvent('WELCOME_MESSAGE', 'B'),
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
      makeAssignedEvent('WELCOME_MESSAGE', 'B'),
    ]
    const stats = getVariantStats(events, 'WELCOME_MESSAGE')
    expect(stats.A.count).toBe(2)
    expect(stats.B.count).toBe(2)
    expect(stats.A.rate).toBeCloseTo(0.5)
    expect(stats.B.rate).toBeCloseTo(0.5)
    expect(stats.A.rate + stats.B.rate).toBeCloseTo(1)
  })

  it('🔴→🟢 다른 실험의 이벤트는 결과에서 제외', () => {
    const events = [
      makeAssignedEvent('WELCOME_MESSAGE', 'A'),
      makeAssignedEvent('CHAT_LAYOUT', 'B'),   // 다른 실험
      makeAssignedEvent('CHAT_LAYOUT', 'A'),   // 다른 실험
    ]
    const stats = getVariantStats(events, 'WELCOME_MESSAGE')
    expect(stats.A.count).toBe(1)
    expect(stats.B.count).toBe(0)
  })

  it('🔴→🟢 experiment_assigned가 아닌 이벤트(interaction 등)는 무시', () => {
    const events = [
      makeInteractionEvent('WELCOME_MESSAGE', 'A', 'cta_clicked'),
      makeAssignedEvent('WELCOME_MESSAGE', 'B'),
    ]
    const stats = getVariantStats(events, 'WELCOME_MESSAGE')
    // interaction 이벤트는 집계 대상 아님
    expect(stats.A.count).toBe(0)
    expect(stats.B.count).toBe(1)
  })

  it('🔴→🟢 존재하지 않는 실험 키에 A/B 모두 count=0 반환', () => {
    const events = [makeAssignedEvent('WELCOME_MESSAGE', 'A')]
    const stats = getVariantStats(events, 'NONEXISTENT')
    expect(stats.A.count).toBe(0)
    expect(stats.B.count).toBe(0)
  })

  it('🔴→🟢 CHAT_LAYOUT 실험 통계도 올바르게 집계', () => {
    const events = [
      makeAssignedEvent('CHAT_LAYOUT', 'A'),
      makeAssignedEvent('CHAT_LAYOUT', 'B'),
      makeAssignedEvent('CHAT_LAYOUT', 'B'),
    ]
    const stats = getVariantStats(events, 'CHAT_LAYOUT')
    expect(stats.A.count).toBe(1)
    expect(stats.B.count).toBe(2)
    expect(stats.B.rate).toBeCloseTo(2 / 3)
  })
})

// ── getTopEvents() ────────────────────────────────────────────────────────────
describe('getTopEvents() — 이벤트 빈도 상위 N개 조회', () => {
  it('🔴→🟢 빈 배열에서 빈 배열 반환', () => {
    expect(getTopEvents([])).toEqual([])
  })

  it('🔴→🟢 이벤트를 빈도 내림차순으로 정렬', () => {
    const events = [
      { name: 'event_a' }, { name: 'event_a' }, { name: 'event_a' },
      { name: 'event_b' }, { name: 'event_b' },
      { name: 'event_c' },
    ]
    const top = getTopEvents(events)
    expect(top[0]).toEqual({ name: 'event_a', count: 3 })
    expect(top[1]).toEqual({ name: 'event_b', count: 2 })
    expect(top[2]).toEqual({ name: 'event_c', count: 1 })
  })

  it('🔴→🟢 limit 매개변수로 결과 수를 제한한다', () => {
    const events = Array.from({ length: 10 }, (_, i) => ({ name: `event_${i}` }))
    expect(getTopEvents(events, 3)).toHaveLength(3)
  })

  it('🔴→🟢 기본 limit는 5이다', () => {
    const events = Array.from({ length: 8 }, (_, i) => ({ name: `event_${i}` }))
    expect(getTopEvents(events)).toHaveLength(5)
  })

  it('🔴→🟢 이벤트 수가 limit보다 적으면 전부 반환', () => {
    const events = [{ name: 'only_one' }]
    expect(getTopEvents(events, 10)).toHaveLength(1)
  })

  it('🔴→🟢 반환 형식은 { name, count } 객체 배열', () => {
    const events = [{ name: 'click' }, { name: 'click' }]
    const top = getTopEvents(events, 1)
    expect(top[0]).toHaveProperty('name', 'click')
    expect(top[0]).toHaveProperty('count', 2)
  })
})
