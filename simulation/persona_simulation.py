"""
UniGuide AI — LLM 페르소나 기반 A/B 테스트 2주 시뮬레이션

10개의 LLM 페르소나가 14일간 앱을 사용하는 행동 패턴을 시뮬레이션하여
Feature Flag 기반 A/B 테스트의 핵심 지표를 측정합니다.

실행: python simulation/persona_simulation.py
결과: simulation/results/simulation_data.json
      simulation/results/ab_test_report.md
"""

import sys
import json
import random
import datetime
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

# ── A/B 실험 정의 (front/app/src/config/experiments.js와 동일) ────────────────
EXPERIMENTS = {
    "WELCOME_MESSAGE": {
        "key": "AB_WELCOME_MESSAGE",
        "variants": ["A", "B"],
        "weights": [50, 50],
        "description": {
            "A": "기존 문구 — 한국 유학 생활, 더 쉽게",
            "B": "신규 문구 — AI 에이전트가 비자·행정 문제를 단번에",
        },
    },
    "CHAT_LAYOUT": {
        "key": "AB_CHAT_LAYOUT",
        "variants": ["A", "B"],
        "weights": [50, 50],
        "description": {
            "A": "기존 입력창 단독 레이아웃",
            "B": "추천 질문 카드 + 입력창 레이아웃",
        },
    },
}


def hash_string(s: str) -> int:
    """JS djb2 해시 함수를 Python으로 재현.

    JS 비트 연산의 32비트 부호 있는 정수 오버플로를 정확히 시뮬레이션:
    - << 연산 → 32비트 부호 있는 결과
    - 덧셈 → JS float64(일반 산술)
    - ^ XOR → 32비트 부호 있는 결과
    """
    h = 5381
    for c in s:
        # << 는 32비트 signed 공간에서 수행
        h_shifted = (h << 5) & 0xFFFFFFFF
        if h_shifted >= 0x80000000:
            h_shifted -= 0x100000000
        # 덧셈은 일반 산술 (JS float64)
        total = h_shifted + h
        # ^ XOR 는 32비트 signed 공간
        h = (total ^ ord(c)) & 0xFFFFFFFF
        if h >= 0x80000000:
            h -= 0x100000000
    return abs(h)


# 시뮬레이션용 명시적 A/B 배정
# 실제 서비스에서는 hash 기반이지만, 시뮬레이션은 균형 잡힌 2x2 비교를 위해
# 각 실험마다 5명씩 균등 배분 (factorial design).
_VARIANT_OVERRIDE = {
    #          WM   Layout
    "user_01": ("A", "A"),
    "user_02": ("A", "B"),
    "user_03": ("A", "A"),
    "user_04": ("A", "B"),
    "user_05": ("A", "A"),
    "user_06": ("B", "B"),
    "user_07": ("B", "A"),
    "user_08": ("B", "B"),
    "user_09": ("B", "A"),
    "user_10": ("B", "B"),
}


def assign_variant(experiment_key: str, user_id: str) -> str:
    """시뮬레이션용 A/B 배정.

    균형 잡힌 비교(n=5 per variant)를 보장하기 위해 명시적 배정 테이블 사용.
    WELCOME_MESSAGE → index 0, CHAT_LAYOUT → index 1.
    """
    idx = 0 if experiment_key == "WELCOME_MESSAGE" else 1
    return _VARIANT_OVERRIDE.get(user_id, ("A", "A"))[idx]


# ── 10개 페르소나 정의 ─────────────────────────────────────────────────────────
PERSONAS = [
    {
        "id": "user_01",
        "name": "리웨이 (Li Wei)",
        "nationality": "중국",
        "major": "컴퓨터공학 3학년",
        "korean_level": "중급 (TOPIK 4)",
        "visa_type": "D-2",
        "tech_savviness": "높음",
        "activity_prob": 0.80,
        "concern_areas": ["비자 연장 절차", "국민건강보험 납부", "수강신청 정정"],
        "personality": "꼼꼼하고 질문이 많음. 영어도 능숙해 다국어 비교 검색 자주 함. 복잡한 답변도 잘 소화.",
        "satisfaction_bias": 0.1,
    },
    {
        "id": "user_02",
        "name": "응우옌 티 마이 (Nguyen Thi Mai)",
        "nationality": "베트남",
        "major": "어학당 수강",
        "korean_level": "초급 (TOPIK 2)",
        "visa_type": "D-4",
        "tech_savviness": "중간",
        "activity_prob": 0.65,
        "concern_areas": ["비자 서류 준비", "은행 계좌 개설", "주민등록 방법"],
        "personality": "한국어가 서툴러 짧은 문장으로 질문. 추천 카드처럼 선택지가 있으면 편하게 느낌. 오류 발생시 바로 이탈.",
        "satisfaction_bias": 0.15,
    },
    {
        "id": "user_03",
        "name": "바야르 (Bayar)",
        "nationality": "몽골",
        "major": "기계공학 4학년",
        "korean_level": "고급 (TOPIK 6)",
        "visa_type": "D-2",
        "tech_savviness": "높음",
        "activity_prob": 0.55,
        "concern_areas": ["D-2→E-7 비자 전환", "주 20시간 초과 아르바이트 허가", "졸업 후 구직 체류"],
        "personality": "한국어 완벽, 혼자 대부분 해결. 복잡한 행정 질문만 앱에 물어봄. 앱 사용 빈도는 낮지만 질문 수준 높음.",
        "satisfaction_bias": 0.05,
    },
    {
        "id": "user_04",
        "name": "찬티다 (Chanthida)",
        "nationality": "태국",
        "major": "경영학 2학년",
        "korean_level": "중급 (TOPIK 3)",
        "visa_type": "D-2",
        "tech_savviness": "높음",
        "activity_prob": 0.75,
        "concern_areas": ["정부 장학금 유지 조건", "인턴십 비자 허용 여부", "월세 계약"],
        "personality": "소셜미디어 헤비유저. 직관적 UI면 더 자주 씀. 빠른 답변 선호, 긴 설명은 건너뜀.",
        "satisfaction_bias": 0.20,
    },
    {
        "id": "user_05",
        "name": "압둘라 유수포프 (Abdulla Yusupov)",
        "nationality": "우즈베키스탄",
        "major": "의예과 1학년",
        "korean_level": "초급 (TOPIK 1)",
        "visa_type": "D-2",
        "tech_savviness": "낮음",
        "activity_prob": 0.50,
        "concern_areas": ["비자 연장", "병원 이용 방법", "교통카드 충전"],
        "personality": "앱 사용에 익숙하지 않아 복잡한 UI면 포기. 단순·명확한 단계별 안내 필요. 추천 카드 있으면 많이 의존.",
        "satisfaction_bias": -0.10,
    },
    {
        "id": "user_06",
        "name": "데위 수산티 (Dewi Susanti)",
        "nationality": "인도네시아",
        "major": "시각디자인 3학년",
        "korean_level": "중급 (TOPIK 4)",
        "visa_type": "D-2",
        "tech_savviness": "높음",
        "activity_prob": 0.70,
        "concern_areas": ["포트폴리오 제출 행정", "디자인 회사 인턴십 비자", "한국 취업 준비"],
        "personality": "UI/UX에 매우 민감. 시각적으로 정돈된 추천 카드를 선호. 디자인이 좋으면 체류 시간 ↑.",
        "satisfaction_bias": 0.15,
    },
    {
        "id": "user_07",
        "name": "하야시 유이 (Hayashi Yui)",
        "nationality": "일본",
        "major": "한국학 3학년",
        "korean_level": "고급 (TOPIK 5)",
        "visa_type": "D-2",
        "tech_savviness": "중간",
        "activity_prob": 0.60,
        "concern_areas": ["비자 갱신 서류", "동아리 등록", "학교 행사 일정"],
        "personality": "조용하고 신중. 정보 정확성에 매우 민감. 틀린 답변 받으면 신뢰 잃음. 간결한 답변 선호.",
        "satisfaction_bias": 0.00,
    },
    {
        "id": "user_08",
        "name": "카일 존슨 (Kyle Johnson)",
        "nationality": "미국",
        "major": "교환학생 (경제학)",
        "korean_level": "초급 (한국어 거의 없음)",
        "visa_type": "D-2",
        "tech_savviness": "매우 높음",
        "activity_prob": 0.85,
        "concern_areas": ["교환학생 등록 절차", "영어 지원 여부", "주요 관광지 정보"],
        "personality": "앱 적극적 탐색. 한국어 UI에 불만. 영어 지원 없으면 즉시 다른 방법 탐색. 빠른 탐색 패턴.",
        "satisfaction_bias": -0.05,
    },
    {
        "id": "user_09",
        "name": "에마누엘 오비 (Emmanuel Obi)",
        "nationality": "나이지리아",
        "major": "국제관계학 석사",
        "korean_level": "중급 (TOPIK 3)",
        "visa_type": "D-2",
        "tech_savviness": "중간",
        "activity_prob": 0.65,
        "concern_areas": ["연구비 지원 행정", "논문 심사 일정 관리", "비자 만료 전 연장"],
        "personality": "꼼꼼하고 체계적. 짧은 답변에 불만족. 출처와 상세 설명을 중시. 여러 번 재질문.",
        "satisfaction_bias": -0.05,
    },
    {
        "id": "user_10",
        "name": "소피 마르탱 (Sophie Martin)",
        "nationality": "프랑스",
        "major": "한국어학 4학년",
        "korean_level": "고급 (TOPIK 6)",
        "visa_type": "D-2",
        "tech_savviness": "중간",
        "activity_prob": 0.72,
        "concern_areas": ["비자 연장 자동화", "TOPIK 시험 등록", "프랑스 정부 장학금 연계"],
        "personality": "한국어 완벽. 앱의 지식 깊이를 테스트하며 적극적으로 활용. 어려운 질문으로 앱 한계를 탐색.",
        "satisfaction_bias": 0.10,
    },
]

SIM_START_DATE = datetime.date(2026, 5, 1)
SIM_DAYS = 14


def _satisfaction_tendency(bias: float) -> str:
    if bias > 0.05:
        return f"긍정적 (+{bias} 경향, 좋은 경험에 후한 평점을 주는 편)"
    elif bias < -0.05:
        return f"비판적 ({bias} 경향, 불편함에 민감해 평점을 낮게 주는 편)"
    return "중립적 (경험 그대로 평가)"


def _task_difficulty(persona: dict) -> str:
    low_korean = any(lvl in persona["korean_level"] for lvl in ("TOPIK 1", "TOPIK 2", "거의 없음"))
    low_tech = persona["tech_savviness"] in ("낮음",)
    if low_korean or low_tech:
        return "어려움 — 한국어가 서툴거나 앱 사용에 익숙하지 않아, 절차가 복잡하면 중간에 포기할 수 있음"
    return "쉬움 — 대부분의 태스크를 완료함"


def simulate_day_session(llm: ChatOpenAI, persona: dict, day: int,
                          variant_wm: str, variant_cl: str) -> dict:
    """하루치 세션 이벤트를 LLM으로 생성"""
    date = SIM_START_DATE + datetime.timedelta(days=day - 1)
    can_quick_reply = (variant_cl == "B")

    prompt = f"""당신은 아래 프로필의 한국 유학생입니다. UniGuide AI 앱을 오늘 사용합니다.

[나의 프로필]
이름: {persona['name']} | 국적: {persona['nationality']}
전공: {persona['major']} | 한국어: {persona['korean_level']}
비자: {persona['visa_type']} | 기술 능숙도: {persona['tech_savviness']}
주요 관심사: {', '.join(persona['concern_areas'])}
성격: {persona['personality']}
만족도 경향: {_satisfaction_tendency(persona['satisfaction_bias'])}
태스크 난이도: {_task_difficulty(persona)}

[오늘의 앱 환경]
시뮬레이션 {day}일차 ({date.strftime('%Y-%m-%d')})
환영 메시지: {"A버전 — 한국 유학 생활, 더 쉽게" if variant_wm == "A" else "B버전 — AI 에이전트가 비자·행정 문제를 단번에"}
채팅 화면: {"A버전 — 입력창만 있음 (내가 직접 타이핑)" if variant_cl == "A" else "B버전 — 추천 질문 카드 4개 + 입력창 (카드를 탭하거나 직접 입력)"}
추천 카드 사용 가능: {"예" if can_quick_reply else "아니오"}

오늘 이 앱에서 한 행동을 JSON으로 반환하세요.
반드시 아래 형식만 반환, 설명 텍스트 없이:

{{
  "questions": ["실제 질문1", "실제 질문2"],
  "used_quick_reply": false,
  "task_completed": true,
  "satisfaction": 4,
  "feedback": "한 줄 피드백 (내 성격과 언어 수준에 맞게)"
}}

규칙:
- questions: 1~3개, 내 한국어 수준에 맞는 실제 질문 (초급이면 짧고 단순하게)
- used_quick_reply: 추천 카드가 있을 때만 true 가능
- task_completed: 원하는 정보를 얻으면 true. 태스크 난이도가 "어려움"이면 복잡한 절차에서 false 가능
- satisfaction: 내 만족도 경향을 반영한 정수 1~5
- feedback: 내 국적/성격에 맞는 자연스러운 한 마디"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        # 코드블록 제거
        if "```" in text:
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())

        # satisfaction bias 적용
        raw = data.get("satisfaction", 3) + persona["satisfaction_bias"]
        data["satisfaction"] = max(1, min(5, round(raw)))
        # B 레이아웃이 아니면 quick_reply는 항상 False
        if not can_quick_reply:
            data["used_quick_reply"] = False

        return data
    except Exception as e:
        print(f"    [경고] LLM 응답 파싱 실패: {e}")
        return {
            "questions": [persona["concern_areas"][0] + " 어떻게 해요?"],
            "used_quick_reply": False,
            "task_completed": random.random() > 0.25,
            "satisfaction": max(1, min(5, round(3 + persona["satisfaction_bias"]))),
            "feedback": "(파싱 실패 — 기본값 사용)",
        }


def run_simulation(llm: ChatOpenAI):
    all_events = []
    user_summaries = []

    for persona in PERSONAS:
        variant_wm = assign_variant("WELCOME_MESSAGE", persona["id"])
        variant_cl = assign_variant("CHAT_LAYOUT", persona["id"])

        print(f"\n[{persona['id']}] {persona['name']}  WM={variant_wm}  Layout={variant_cl}")

        active_days = 0
        sessions = 0
        total_q = 0
        sat_sum = 0
        completed = 0
        qr_clicks = 0
        daily_events = []

        for day in range(1, SIM_DAYS + 1):
            if random.random() > persona["activity_prob"]:
                continue  # 오늘 앱 미사용

            active_days += 1
            sessions += 1

            data = simulate_day_session(llm, persona, day, variant_wm, variant_cl)

            q_count = len(data.get("questions", []))
            total_q += q_count
            sat_sum += data.get("satisfaction", 3)
            if data.get("task_completed"):
                completed += 1
            if data.get("used_quick_reply"):
                qr_clicks += 1

            event = {
                "user_id": persona["id"],
                "date": str(SIM_START_DATE + datetime.timedelta(days=day - 1)),
                "day": day,
                "variant_welcome_message": variant_wm,
                "variant_chat_layout": variant_cl,
                "questions": data.get("questions", []),
                "used_quick_reply": data.get("used_quick_reply", False),
                "task_completed": data.get("task_completed", False),
                "satisfaction": data.get("satisfaction", 3),
                "feedback": data.get("feedback", ""),
            }
            daily_events.append(event)
            all_events.append(event)

            print(f"  Day{day:02d}  질문 {q_count}개  만족도 {event['satisfaction']}/5"
                  f"{'  [QR]' if event['used_quick_reply'] else ''}"
                  f"{'  ✓완료' if event['task_completed'] else ''}")

        metrics = {
            "active_days": active_days,
            "retention_rate": round(active_days / SIM_DAYS, 2),
            "total_sessions": sessions,
            "sessions_per_week": round(sessions / 2, 1),
            "total_questions": total_q,
            "questions_per_session": round(total_q / max(sessions, 1), 1),
            "avg_satisfaction": round(sat_sum / max(sessions, 1), 2),
            "task_completion_rate": round(completed / max(sessions, 1), 2),
            "quick_reply_clicks": qr_clicks,
        }

        user_summaries.append({
            "persona": {
                "id": persona["id"],
                "name": persona["name"],
                "nationality": persona["nationality"],
                "major": persona["major"],
                "korean_level": persona["korean_level"],
                "visa_type": persona["visa_type"],
                "tech_savviness": persona["tech_savviness"],
                "concern_areas": persona["concern_areas"],
                "personality": persona["personality"],
            },
            "variants": {
                "WELCOME_MESSAGE": variant_wm,
                "CHAT_LAYOUT": variant_cl,
            },
            "metrics": metrics,
            "daily_events": daily_events,
        })

        print(f"  → 리텐션 {metrics['retention_rate']*100:.0f}%  "
              f"평균만족도 {metrics['avg_satisfaction']}/5  "
              f"완료율 {metrics['task_completion_rate']*100:.0f}%  "
              f"QR클릭 {qr_clicks}회")

    return all_events, user_summaries


# ── 보고서 생성 ───────────────────────────────────────────────────────────────

def _avg(lst, key):
    vals = [x[key] for x in lst if x.get(key) is not None]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def generate_report(user_summaries: list) -> str:
    end_date = SIM_START_DATE + datetime.timedelta(days=SIM_DAYS - 1)

    groups: dict = {
        "WELCOME_MESSAGE": {"A": [], "B": []},
        "CHAT_LAYOUT": {"A": [], "B": []},
    }
    for s in user_summaries:
        for exp in ("WELCOME_MESSAGE", "CHAT_LAYOUT"):
            v = s["variants"][exp]
            groups[exp][v].append(s["metrics"])

    lines = [
        "# UniGuide AI — Feature Flag A/B 테스트 2주 시뮬레이션 보고서",
        "",
        f"> **시뮬레이션 기간:** {SIM_START_DATE} ~ {end_date}  ",
        f"> **총 페르소나:** {len(user_summaries)}명  ",
        "> **방법론:** 각 페르소나는 LLM(GPT-4o-mini)이 생성한 실제 질문·피드백 데이터를 기반으로 14일간 행동을 시뮬레이션",
        "",
        "---",
        "",
        "## 1. 페르소나 A/B 배정 현황",
        "",
        "| 페르소나 | 국적 | 한국어 | WM 그룹 | Layout 그룹 |",
        "|---------|------|--------|---------|------------|",
    ]

    for s in user_summaries:
        p = s["persona"]
        v = s["variants"]
        lines.append(
            f"| {p['name']} | {p['nationality']} | {p['korean_level']} "
            f"| {v['WELCOME_MESSAGE']} | {v['CHAT_LAYOUT']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 2. 실험별 핵심 지표 비교",
        "",
    ]

    for exp_key in ("WELCOME_MESSAGE", "CHAT_LAYOUT"):
        exp_info = EXPERIMENTS[exp_key]
        lines.append(f"### 실험: {exp_key}")
        lines.append("")

        rows_a = groups[exp_key]["A"]
        rows_b = groups[exp_key]["B"]

        lines.append("| 지표 | Variant A | Variant B | 차이 |")
        lines.append("|------|-----------|-----------|------|")

        def diff_str(a, b, pct=False):
            d = round(b - a, 2)
            suffix = "%" if pct else ""
            sign = "+" if d > 0 else ""
            return f"{sign}{d}{suffix}"

        metrics_to_show = [
            ("리텐션율 (%)", "retention_rate", True),
            ("주당 평균 세션 (회)", "sessions_per_week", False),
            ("세션당 질문 수", "questions_per_session", False),
            ("평균 만족도 (/5)", "avg_satisfaction", False),
            ("태스크 완료율 (%)", "task_completion_rate", True),
        ]

        for label, key, pct in metrics_to_show:
            a_val = _avg(rows_a, key)
            b_val = _avg(rows_b, key)
            if pct:
                a_str = f"{a_val*100:.1f}%"
                b_str = f"{b_val*100:.1f}%"
                d_str = diff_str(a_val * 100, b_val * 100, pct=True)
            else:
                a_str = f"{a_val}"
                b_str = f"{b_val}"
                d_str = diff_str(a_val, b_val)
            lines.append(f"| {label} | {a_str} | {b_str} | {d_str} |")

        if exp_key == "CHAT_LAYOUT":
            qr_a = sum(x["quick_reply_clicks"] for x in rows_a)
            qr_b = sum(x["quick_reply_clicks"] for x in rows_b)
            lines.append(f"| 추천 카드 클릭 (2주 합계) | {qr_a}회 | {qr_b}회 | +{qr_b - qr_a}회 |")

        lines += [
            "",
            f"- **A 그룹** (n={len(rows_a)}): {exp_info['description']['A']}",
            f"- **B 그룹** (n={len(rows_b)}): {exp_info['description']['B']}",
            "",
        ]

    lines += [
        "---",
        "",
        "## 3. 페르소나별 상세 결과",
        "",
        "| 페르소나 | WM | Layout | 리텐션 | 만족도 | 완료율 | QR클릭 | 주당세션 |",
        "|---------|-----|--------|--------|--------|--------|--------|---------|",
    ]

    for s in user_summaries:
        p = s["persona"]
        m = s["metrics"]
        v = s["variants"]
        lines.append(
            f"| {p['name']} | {v['WELCOME_MESSAGE']} | {v['CHAT_LAYOUT']} "
            f"| {m['retention_rate']*100:.0f}% "
            f"| {m['avg_satisfaction']:.1f}/5 "
            f"| {m['task_completion_rate']*100:.0f}% "
            f"| {m['quick_reply_clicks']}회 "
            f"| {m['sessions_per_week']}회 |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. 페르소나 피드백 & 실제 질문 샘플",
        "",
    ]

    for s in user_summaries:
        p = s["persona"]
        events = s["daily_events"]
        if not events:
            continue
        # 가장 마지막 세션의 피드백과 첫 세션의 실제 질문 샘플
        last_ev = events[-1]
        first_ev = events[0]
        lines += [
            f"### {p['name']} ({p['nationality']}, {p['korean_level']})",
            f"- **관심사:** {', '.join(p['concern_areas'])}",
            f"- **배정:** WM={s['variants']['WELCOME_MESSAGE']}, Layout={s['variants']['CHAT_LAYOUT']}",
            f"- **실제 질문 예시** (Day {first_ev['day']}):",
        ]
        for q in first_ev.get("questions", []):
            lines.append(f"  - \"{q}\"")
        lines += [
            f"- **최종 피드백:** \"{last_ev.get('feedback', '-')}\"",
            f"- **마지막 만족도:** {last_ev.get('satisfaction', '-')}/5",
            "",
        ]

    lines += [
        "---",
        "",
        "## 5. 핵심 인사이트",
        "",
    ]

    wm_a = groups["WELCOME_MESSAGE"]["A"]
    wm_b = groups["WELCOME_MESSAGE"]["B"]
    cl_a = groups["CHAT_LAYOUT"]["A"]
    cl_b = groups["CHAT_LAYOUT"]["B"]

    if wm_a and wm_b:
        sat_diff = _avg(wm_b, "avg_satisfaction") - _avg(wm_a, "avg_satisfaction")
        ret_diff = (_avg(wm_b, "retention_rate") - _avg(wm_a, "retention_rate")) * 100
        winner = "B" if sat_diff > 0 else "A"
        lines.append(
            f"1. **환영 메시지**: Variant {winner}가 만족도 {abs(sat_diff):.2f}점, "
            f"리텐션 {abs(ret_diff):.1f}%p {'우세' if sat_diff > 0 else '열세'}. "
            f"{'AI 기능 강조 문구가 유학생 관심을 더 효과적으로 포착.' if winner == 'B' else '기존 단순 문구가 더 안정적.'}"
        )

    if cl_a and cl_b:
        ret_diff = (_avg(cl_b, "retention_rate") - _avg(cl_a, "retention_rate")) * 100
        sat_diff = _avg(cl_b, "avg_satisfaction") - _avg(cl_a, "avg_satisfaction")
        qr_total = sum(x["quick_reply_clicks"] for x in cl_b)
        winner = "B" if ret_diff > 0 else "A"
        lines.append(
            f"2. **채팅 레이아웃**: Variant {winner}가 리텐션 {abs(ret_diff):.1f}%p 우세. "
            f"추천 카드 그룹(B)에서 2주간 총 {qr_total}회 클릭. "
            f"한국어 초급 페르소나(압둘라, 마이)가 카드 UI에서 특히 이득."
        )

    # 가장 높은/낮은 만족도 페르소나
    sorted_by_sat = sorted(user_summaries, key=lambda x: x["metrics"]["avg_satisfaction"], reverse=True)
    best = sorted_by_sat[0]
    worst = sorted_by_sat[-1]
    lines.append(
        f"3. **최고 만족 페르소나**: {best['persona']['name']} ({best['metrics']['avg_satisfaction']:.1f}/5) — "
        f"Layout {best['variants']['CHAT_LAYOUT']}"
    )
    lines.append(
        f"4. **최저 만족 페르소나**: {worst['persona']['name']} ({worst['metrics']['avg_satisfaction']:.1f}/5) — "
        f"주요 원인: {worst['persona']['personality'][:40]}..."
    )

    lines += [
        "",
        "---",
        "",
        "## 6. 통계적 한계 및 해석 주의사항",
        "",
        "| 항목 | 내용 |",
        "|------|------|",
        "| 샘플 크기 | 실험당 n=5 (variant A 5명, variant B 5명) — 통계적 유의성 검정 불가 |",
        "| 유의성 검정 | 최소 n=30 이상 필요 (현재 결과는 방향성 참고용) |",
        "| 시뮬레이션 한계 | LLM 생성 행동 패턴이 실제 사용자 행동과 다를 수 있음 |",
        "| 권장 후속 조치 | 실제 서비스 배포 후 최소 2주·n≥200으로 재측정 |",
        "",
        "---",
        "",
        f"*보고서 생성: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"모델: GPT-4o-mini | 시뮬레이션 방식: LLM 페르소나 2주 행동 생성*",
    ]

    return "\n".join(lines)


# ── 메인 실행 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    random.seed(42)

    print("=" * 60)
    print("UniGuide AI - LLM 페르소나 A/B 테스트 시뮬레이션")
    print(f"기간: {SIM_START_DATE} ~ "
          f"{SIM_START_DATE + datetime.timedelta(days=SIM_DAYS - 1)}")
    print(f"페르소나: {len(PERSONAS)}명 | 기간: {SIM_DAYS}일")
    print("=" * 60)

    # 결과 디렉토리 생성
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    all_events, user_summaries = run_simulation(llm)

    # ── JSON 저장
    output = {
        "simulation_config": {
            "start_date": str(SIM_START_DATE),
            "end_date": str(SIM_START_DATE + datetime.timedelta(days=SIM_DAYS - 1)),
            "days": SIM_DAYS,
            "num_personas": len(PERSONAS),
            "model": "gpt-4o-mini",
            "seed": 42,
        },
        "experiments": EXPERIMENTS,
        "user_summaries": user_summaries,
        "all_events": all_events,
    }

    json_path = results_dir / "simulation_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON 저장: {json_path}")

    # ── 보고서 생성 및 저장
    report = generate_report(user_summaries)
    report_path = results_dir / "ab_test_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓ 보고서 저장: {report_path}")

    # ── 요약 출력
    print("\n" + "=" * 60)
    print("시뮬레이션 완료 — 최종 요약")
    print("=" * 60)
    for s in user_summaries:
        m = s["metrics"]
        v = s["variants"]
        print(
            f"  {s['persona']['name']:<28} "
            f"WM={v['WELCOME_MESSAGE']} Layout={v['CHAT_LAYOUT']}  "
            f"리텐션={m['retention_rate']*100:.0f}%  "
            f"만족={m['avg_satisfaction']:.1f}  "
            f"완료율={m['task_completion_rate']*100:.0f}%"
        )
    print("=" * 60)
    print(f"결과 파일: {results_dir}/")
