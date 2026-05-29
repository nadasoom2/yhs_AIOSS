import { useFeatureFlagContext } from '../context/FeatureFlagContext';
import { track, EVENTS } from '../utils/analytics';

/**
 * 특정 Feature Flag 활성화 여부를 반환하는 훅
 *
 * @param {string} flagKey - featureFlags.js에 정의된 FLAG 키 (예: 'VOICE_INPUT')
 * @returns {boolean}
 *
 * @example
 * const voiceEnabled = useFeatureFlag('VOICE_INPUT');
 * return voiceEnabled ? <MicButton /> : null;
 */
export function useFeatureFlag(flagKey) {
  const { flags, userId } = useFeatureFlagContext();
  const enabled = flags[flagKey] ?? false;
  return enabled;
}

/**
 * 여러 플래그를 한 번에 조회
 * @param {string[]} keys
 * @returns {Record<string, boolean>}
 */
export function useFeatureFlags(keys) {
  const { flags } = useFeatureFlagContext();
  const result = {};
  keys.forEach(k => { result[k] = flags[k] ?? false; });
  return result;
}
