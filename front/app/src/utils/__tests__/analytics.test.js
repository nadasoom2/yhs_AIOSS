/**
 * TDD Feature 4: Analytics — 이벤트 추적 시스템
 *  track() / getEvents() / clearEvents()
 *
 * Red-Green-Refactor 사이클:
 *  🔴 Red    : analytics.js 없으면 import 실패 → 전부 실패
 *  🟢 Green  : localStorage 기반 구현으로 모두 통과
 *  🔵 Refactor: EVENT_LIMIT 로직을 splice 대신 slice로 단순화 가능(선택)
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { track, getEvents, clearEvents, EVENTS } from '../analytics.js'

describe('Analytics — 이벤트 추적 시스템', () => {
  // 각 테스트 전 localStorage 초기화 (테스트 격리)
  beforeEach(() => {
    clearEvents()
  })

  // ── track() ─────────────────────────────────────────────────────────────
  describe('track()', () => {
    it('이벤트를 localStorage에 저장한다', () => {
      track('test_event', { key: 'value' })
      const events = getEvents()
      expect(events).toHaveLength(1)
      expect(events[0].name).toBe('test_event')
      expect(events[0].properties.key).toBe('value')
    })

    it('저장된 이벤트에 ISO 타임스탬프(ts)가 포함된다', () => {
      const before = Date.now()
      track('ts_check')
      const after = Date.now()
      const ts = new Date(getEvents()[0].ts).getTime()
      expect(ts).toBeGreaterThanOrEqual(before)
      expect(ts).toBeLessThanOrEqual(after)
    })

    it('properties를 생략해도 오류 없이 저장된다', () => {
      expect(() => track('no_props')).not.toThrow()
      expect(getEvents()[0].properties).toBeDefined()
    })

    it('여러 이벤트를 순서대로 저장한다', () => {
      track('first')
      track('second')
      track('third')
      const events = getEvents()
      expect(events).toHaveLength(3)
      expect(events[0].name).toBe('first')
      expect(events[2].name).toBe('third')
    })

    it('EVENT_LIMIT(200) 초과 시 가장 오래된 이벤트를 삭제한다', () => {
      for (let i = 0; i < 205; i++) {
        track(`event_${i}`)
      }
      const events = getEvents()
      expect(events).toHaveLength(200)
      // 가장 최신 이벤트(event_204)가 마지막에 있어야 함
      expect(events[events.length - 1].name).toBe('event_204')
    })
  })

  // ── getEvents() ─────────────────────────────────────────────────────────
  describe('getEvents()', () => {
    it('저장된 이벤트가 없으면 빈 배열을 반환한다', () => {
      expect(getEvents()).toEqual([])
    })

    it('저장된 모든 이벤트를 배열로 반환한다', () => {
      track(EVENTS.FEATURE_FLAG_EVALUATED, { flag: 'VOICE_INPUT', enabled: true })
      track(EVENTS.EXPERIMENT_ASSIGNED, { experiment: 'WELCOME_MESSAGE', variant: 'B' })
      expect(getEvents()).toHaveLength(2)
    })

    it('반환값은 항상 배열이다', () => {
      expect(Array.isArray(getEvents())).toBe(true)
    })
  })

  // ── clearEvents() ────────────────────────────────────────────────────────
  describe('clearEvents()', () => {
    it('저장된 모든 이벤트를 삭제한다', () => {
      track('event_a')
      track('event_b')
      clearEvents()
      expect(getEvents()).toEqual([])
    })

    it('이벤트가 없을 때 호출해도 오류가 없다', () => {
      expect(() => clearEvents()).not.toThrow()
    })
  })

  // ── EVENTS 상수 ──────────────────────────────────────────────────────────
  describe('EVENTS 상수', () => {
    it('모든 표준 이벤트 이름 상수가 정의돼 있다', () => {
      expect(EVENTS.FEATURE_FLAG_EVALUATED).toBe('feature_flag_evaluated')
      expect(EVENTS.EXPERIMENT_ASSIGNED).toBe('experiment_assigned')
      expect(EVENTS.EXPERIMENT_INTERACTION).toBe('experiment_interaction')
      expect(EVENTS.FEATURE_USED).toBe('feature_used')
      expect(EVENTS.QUICK_REPLY_CLICKED).toBe('quick_reply_clicked')
      expect(EVENTS.VOICE_INPUT_TRIGGERED).toBe('voice_input_triggered')
      expect(EVENTS.DARK_MODE_SEEN).toBe('dark_mode_seen')
    })

    it('EVENTS 상수로 추적한 이벤트가 올바르게 저장된다', () => {
      track(EVENTS.QUICK_REPLY_CLICKED, { cardIndex: 2 })
      const events = getEvents()
      expect(events[0].name).toBe('quick_reply_clicked')
      expect(events[0].properties.cardIndex).toBe(2)
    })
  })
})
