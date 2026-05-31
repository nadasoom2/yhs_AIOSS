/**
 * TDD Feature 1: isEnabled() — Feature Flag 평가 로직
 *
 * Red-Green-Refactor 사이클:
 *  🔴 Red    : 아래 테스트를 먼저 작성 → isEnabled가 없으면 전부 실패
 *  🟢 Green  : featureFlags.js의 isEnabled 구현으로 모두 통과
 *  🔵 Refactor: 우선순위 로직(envVar → targetUsers → defaultEnabled)을 명확하게 유지
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

// import.meta.env는 모듈 로드 시점에 평가되므로
// vi.stubEnv + vi.resetModules + dynamic import 패턴으로 각 케이스를 격리
describe('isEnabled() — Feature Flag 평가', () => {
  // .env.local에 VITE_FEATURE_VOICE_INPUT=true 등이 설정돼 있어
  // vi.unstubAllEnvs()만으로는 원래 값(true)으로 복원됨.
  // 각 테스트 전에 관련 env 변수를 명시적으로 중립화해야 격리가 보장됨.
  beforeEach(() => {
    vi.resetModules()
    vi.unstubAllEnvs()
    vi.stubEnv('VITE_FEATURE_VOICE_INPUT', '')
    vi.stubEnv('VITE_FEATURE_DARK_MODE', '')
    vi.stubEnv('VITE_FEATURE_QUICK_REPLIES', '')
    vi.stubEnv('VITE_BETA_USERS', '')
  })

  afterEach(() => {
    vi.resetModules()
    vi.unstubAllEnvs()
  })

  // ── 기본값 ────────────────────────────────────────────────────
  it('존재하지 않는 플래그는 false 반환', async () => {
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('NON_EXISTENT')).toBe(false)
  })

  it('defaultEnabled=false이면 override 없이 false 반환', async () => {
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT')).toBe(false)
    expect(isEnabled('DARK_MODE')).toBe(false)
    expect(isEnabled('QUICK_REPLIES')).toBe(false)
  })

  // ── 환경 변수 (최우선) ────────────────────────────────────────
  it('envVar="true"이면 플래그 활성화', async () => {
    vi.stubEnv('VITE_FEATURE_VOICE_INPUT', 'true')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT')).toBe(true)
  })

  it('envVar="1"이면 플래그 활성화', async () => {
    vi.stubEnv('VITE_FEATURE_VOICE_INPUT', '1')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT')).toBe(true)
  })

  it('envVar="false"이면 플래그 비활성화', async () => {
    vi.stubEnv('VITE_FEATURE_VOICE_INPUT', 'false')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT')).toBe(false)
  })

  it('envVar="0"이면 플래그 비활성화', async () => {
    vi.stubEnv('VITE_FEATURE_VOICE_INPUT', '0')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT')).toBe(false)
  })

  // ── 대상 사용자 화이트리스트 ──────────────────────────────────
  it('targetUsers에 포함된 userId이면 활성화', async () => {
    vi.stubEnv('VITE_BETA_USERS', 'user_alice,user_bob')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT', 'user_alice')).toBe(true)
    expect(isEnabled('VOICE_INPUT', 'user_bob')).toBe(true)
  })

  it('targetUsers에 없는 userId이면 비활성화', async () => {
    vi.stubEnv('VITE_BETA_USERS', 'user_alice')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT', 'user_charlie')).toBe(false)
  })

  it('userId=null이면 targetUsers가 있어도 기본값(false) 반환', async () => {
    vi.stubEnv('VITE_BETA_USERS', 'user_alice')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('VOICE_INPUT', null)).toBe(false)
  })

  it('DARK_MODE는 targetUsers 없이 envVar로만 제어', async () => {
    vi.stubEnv('VITE_FEATURE_DARK_MODE', 'true')
    const { isEnabled } = await import('../featureFlags.js')
    expect(isEnabled('DARK_MODE')).toBe(true)
  })

  // ── FLAG_KEYS 목록 ────────────────────────────────────────────
  it('FLAG_KEYS는 정의된 모든 플래그 키를 포함', async () => {
    const { FLAG_KEYS } = await import('../featureFlags.js')
    expect(FLAG_KEYS).toContain('VOICE_INPUT')
    expect(FLAG_KEYS).toContain('DARK_MODE')
    expect(FLAG_KEYS).toContain('QUICK_REPLIES')
  })
})
