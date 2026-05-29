import { useCallback } from 'react';
import { useFeatureFlagContext } from '../context/FeatureFlagContext';
import { track, EVENTS } from '../utils/analytics';

/**
 * A/B 테스트 variant 조회 훅
 *
 * @param {string} experimentKey - experiments.js에 정의된 EXPERIMENTS 키
 * @returns {{ variant: string, trackInteraction: (action: string, extra?: object) => void }}
 *
 * @example
 * const { variant, trackInteraction } = useABTest('WELCOME_MESSAGE');
 * // variant: 'A' 또는 'B'
 * trackInteraction('cta_clicked');  // 이벤트 추적
 */
export function useABTest(experimentKey) {
  const { variants, userId } = useFeatureFlagContext();
  const variant = variants[experimentKey] ?? 'A';

  const trackInteraction = useCallback(
    (action, extra = {}) => {
      track(EVENTS.EXPERIMENT_INTERACTION, {
        experiment: experimentKey,
        variant,
        userId,
        action,
        ...extra,
      });
    },
    [experimentKey, variant, userId],
  );

  return { variant, trackInteraction };
}
