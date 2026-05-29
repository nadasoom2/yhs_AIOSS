import { createContext, useContext, useMemo, useState, useEffect } from 'react';
import { isEnabled, FLAG_KEYS } from '../config/featureFlags';
import { assignVariant, EXPERIMENT_KEYS } from '../config/experiments';
import { track, EVENTS } from '../utils/analytics';

const FeatureFlagContext = createContext(null);

/**
 * localStorage에서 userId를 읽거나 새로 생성
 */
function resolveUserId() {
  const KEY = 'uniguide_user_id';
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = 'user_' + Math.random().toString(36).slice(2, 11);
    localStorage.setItem(KEY, id);
  }
  return id;
}

export function FeatureFlagProvider({ children }) {
  const [userId] = useState(resolveUserId);

  // 플래그 맵: { VOICE_INPUT: true/false, ... }
  const flags = useMemo(() => {
    const map = {};
    FLAG_KEYS.forEach(key => {
      const enabled = isEnabled(key, userId);
      map[key] = enabled;
      track(EVENTS.FEATURE_FLAG_EVALUATED, { flag: key, enabled, userId });
    });
    return map;
  }, [userId]);

  // 실험 variant 맵: { WELCOME_MESSAGE: 'A'|'B', ... }
  const variants = useMemo(() => {
    const map = {};
    EXPERIMENT_KEYS.forEach(key => {
      const variant = assignVariant(key, userId);
      map[key] = variant;
      track(EVENTS.EXPERIMENT_ASSIGNED, { experiment: key, variant, userId });
    });
    return map;
  }, [userId]);

  const value = useMemo(() => ({ userId, flags, variants }), [userId, flags, variants]);

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  );
}

export function useFeatureFlagContext() {
  const ctx = useContext(FeatureFlagContext);
  if (!ctx) throw new Error('useFeatureFlagContext must be used inside FeatureFlagProvider');
  return ctx;
}
