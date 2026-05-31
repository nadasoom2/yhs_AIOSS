/**
 * TDD Feature 2: hashString() — 결정적 해시 함수
 * TDD Feature 3: assignVariant() — A/B 배정 로직
 *
 * Red-Green-Refactor 사이클:
 *  🔴 Red    : hashString이 export되지 않아 import 실패 → 테스트 실패
 *  🟢 Green  : experiments.js에서 export function hashString으로 수정 후 통과
 *  🔵 Refactor: djb2 해시 구현의 32비트 overflow 처리 검증
 */

import { describe, it, expect } from 'vitest'
import { hashString, assignVariant, EXPERIMENTS, EXPERIMENT_KEYS } from '../experiments.js'

// ── Feature 2: hashString ──────────────────────────────────────────────────────
describe('hashString() — 결정적 해시 함수', () => {
  it('같은 입력은 항상 같은 해시 반환 (결정성)', () => {
    expect(hashString('hello')).toBe(hashString('hello'))
    expect(hashString('user_01')).toBe(hashString('user_01'))
  })

  it('반환값은 0 이상의 정수', () => {
    const h = hashString('test_string')
    expect(h).toBeGreaterThanOrEqual(0)
    expect(Number.isInteger(h)).toBe(true)
  })

  it('빈 문자열도 오류 없이 처리', () => {
    expect(() => hashString('')).not.toThrow()
    expect(hashString('')).toBeGreaterThanOrEqual(0)
  })

  it('서로 다른 입력은 다른 해시 생성 (충돌 없음)', () => {
    expect(hashString('user_01')).not.toBe(hashString('user_02'))
    expect(hashString('AB_WELCOME_MESSAGE:user_01')).not.toBe(
      hashString('AB_WELCOME_MESSAGE:user_02'),
    )
  })

  it('단일 문자도 올바르게 처리', () => {
    expect(hashString('a')).toBeGreaterThanOrEqual(0)
    expect(hashString('a')).not.toBe(hashString('b'))
  })
})

// ── Feature 3: assignVariant ───────────────────────────────────────────────────
describe('assignVariant() — A/B 배정 로직', () => {
  it('알 수 없는 실험 키에 null 반환', () => {
    expect(assignVariant('UNKNOWN_EXPERIMENT', 'user_1')).toBeNull()
  })

  it('WELCOME_MESSAGE 실험에서 A 또는 B 반환', () => {
    const v = assignVariant('WELCOME_MESSAGE', 'user_test')
    expect(['A', 'B']).toContain(v)
  })

  it('CHAT_LAYOUT 실험에서 A 또는 B 반환', () => {
    const v = assignVariant('CHAT_LAYOUT', 'user_test')
    expect(['A', 'B']).toContain(v)
  })

  it('동일 userId + 실험 키에 항상 동일 variant 반환 (일관성)', () => {
    const v1 = assignVariant('WELCOME_MESSAGE', 'stable_user_abc')
    const v2 = assignVariant('WELCOME_MESSAGE', 'stable_user_abc')
    const v3 = assignVariant('WELCOME_MESSAGE', 'stable_user_abc')
    expect(v1).toBe(v2)
    expect(v2).toBe(v3)
  })

  it('1000명 유저에서 A/B 배분이 40~60% 범위 내 (균형 분배)', () => {
    const counts = { A: 0, B: 0 }
    // uuid 스타일 ID를 사용해 해시 쏠림 방지
    const userIds = Array.from({ length: 1000 }, (_, i) =>
      `u_${i.toString(16).padStart(4, '0')}_${(i * 7919).toString(36)}`,
    )
    userIds.forEach(id => {
      const v = assignVariant('WELCOME_MESSAGE', id)
      counts[v]++
    })
    expect(counts.A).toBeGreaterThanOrEqual(400)
    expect(counts.A).toBeLessThanOrEqual(600)
    expect(counts.B).toBeGreaterThanOrEqual(400)
    expect(counts.B).toBeLessThanOrEqual(600)
  })

  it('WELCOME_MESSAGE와 CHAT_LAYOUT 배정은 서로 독립적', () => {
    // 같은 userId라도 실험에 따라 다른 variant를 받을 수 있어야 함
    let differs = false
    for (let i = 0; i < 20; i++) {
      const wm = assignVariant('WELCOME_MESSAGE', `user_${i}`)
      const cl = assignVariant('CHAT_LAYOUT', `user_${i}`)
      if (wm !== cl) { differs = true; break }
    }
    expect(differs).toBe(true)
  })

  it('EXPERIMENT_KEYS는 정의된 모든 실험 키를 포함', () => {
    expect(EXPERIMENT_KEYS).toContain('WELCOME_MESSAGE')
    expect(EXPERIMENT_KEYS).toContain('CHAT_LAYOUT')
  })

  it('EXPERIMENTS 객체에 variants와 weights가 존재', () => {
    Object.values(EXPERIMENTS).forEach(exp => {
      expect(exp.variants).toBeDefined()
      expect(exp.weights).toBeDefined()
      const totalWeight = exp.weights.reduce((a, b) => a + b, 0)
      expect(totalWeight).toBe(100)
    })
  })
})
