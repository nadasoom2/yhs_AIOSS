# DORA 지표 (2주차 과제) 및 기본 CI/CD 구축 (7주차 과제) 실행 결과 리포트


## 1. DORA 지표 실행결과

### 개요

- 프로젝트: `yhs`
- 보고 날짜: `2026-04-29`
- 대상 워크플로: `workflows/`

---

### 요약

| Metric | 값 | 파일 위치 | 설명 |
| --- | --- | --- | --- |
| Deployment Frequency | `높음 (최근 지속 실행)` | [.github/workflows/deployment.yml](.github/workflows/deployment.yml) | 최근 Track Deployments 실행 이력이 연속적으로 관찰되고 모두 성공 상태여서, 배포가 끊기지 않고 자주 수행되는 편으로 해석할 수 있습니다. 실행 소요 시간도 대체로 짧아(약 5~12초) 배포 추적 파이프라인은 안정적으로 동작 중입니다. |
| Lead Time for Changes | `안정적 (최근 4회 연속 성공)` | [.github/workflows/lead-time.yml](.github/workflows/lead-time.yml), `metrics.yml` | 최근 PR이 닫힐 때마다 워크플로가 실행되었고 4회 모두 성공했습니다. 실행 시간도 약 6~7초로 짧아서, 변경 후 리드 타임을 기록하는 파이프라인이 안정적으로 동작하고 있다고 볼 수 있습니다. |
| Change Failure Rate | `수동 실행 성공` | [.github/workflows/change_failure_rate.yml](.github/workflows/change_failure_rate.yml) | `Track Deployment Result`를 수동 실행했을 때 `Deployment succeeded` 로그가 정상 출력되어, 배포 결과를 성공으로 기록하는 흐름은 정상입니다. 현재 화면만 보면 실패 사례는 없어서 실제 실패율 수치보다는 성공 추적 상태를 확인한 결과로 해석할 수 있습니다. |
| Mean Time to Restore | `실행 성공 (약 7초)` | [.github/workflows/mttr-monitoring.yml](.github/workflows/mttr-monitoring.yml), `mttr-metrics.json` | `Generate MTTR metrics`와 `Upload MTTR metrics` 단계가 정상 완료되어 지표 파일 생성/업로드 흐름은 정상입니다. 다만 실행 경고 1건이 있어 사용 액션 런타임(예: Node.js 버전) 호환성 점검이 필요합니다. |

### DORA 차트

**Deployment Frequency**

![Deployment Frequency] ![alt text](deployment_frequency.png)

**Lead Time for Changes**

![Lead Time for Changes] ![alt text](lead_time.png)

**Change Failure Rate**

![Change Failure Rate] ![alt text](change_failure_rate.png)

**Mean Time to Restore!**

![Mean Time to Restore] ![alt text](mttr_monitoring.png)

---



## 2. GitHub Actions 실행 결과 요약

### 기본 정보

| 항목 | 내용 |
|------|------|
| 워크플로우 | `ci-and-selective-deploy.yml` |
| 실행 번호 | #30 |
| 트리거 | `push` → `main` 브랜치 |
| 커밋 | `9be6d6b` (nadasoom2) |
| 상태 | ✅ **Success** |
| 총 소요 시간 | **9분 40초** |
| 생성된 아티팩트 | **9개** |

---

### Job 실행 결과

| Job | 결과 | 비고 |
|-----|------|------|
| Build (ubuntu-latest) | ✅ 성공 | |
| Build (windows-latest) | ✅ 성공 | |
| Detect deployable changes | ✅ 성공 | 9초 |
| matrix-tests | ✅ 성공 | 6개 조합 전체 통과 |
| Preview deployment decision | ⏭️ 스킵 | PR 이벤트가 아니라 스킵됨 |
| Selective deploy | ✅ 성공 | 13초, 배포 실행됨 |

---

### Matrix 캐시 성능 비교 (6개 조합 전체)

| OS | Python | Cold install | Cached install | 개선율 |
|----|--------|-------------|----------------|--------|
| ubuntu-latest | 3.10 | 101.938초 | 73.906초 | **+27.50%** |
| ubuntu-latest | 3.11 | 106.067초 | 72.889초 | **+31.28%** ⬆️ 최고 |
| ubuntu-latest | 3.12 | 90.402초 | 78.983초 | **+12.63%** |
| windows-latest | 3.10 | 80.505초 | 73.417초 | **+8.80%** |
| windows-latest | 3.11 | 78.651초 | 85.437초 | **-8.63%** ⚠️ |
| windows-latest | 3.12 | 86.745초 | 76.633초 | **+11.66%** |

### 주목할 점

- **ubuntu 3.11이 캐시 효과 가장 큼** (31.28% 단축)
- **windows 3.11은 캐시가 오히려 느림** (-8.63%) — 캐시 복원 오버헤드가 설치 시간보다 커진 케이스로, Windows 환경에서 pip 캐시 효율이 낮을 수 있음
- **ubuntu가 전반적으로 캐시 효과가 더 좋음** (평균 +23.8% vs windows 평균 +3.9%)

---

## Selective Deploy 결과

| 항목 | 내용 |
|------|------|
| 결정 | **deployed** (배포 실행) |
| 이유 | `deployable files changed` |
| 아티팩트 | deployment-manifest 업로드 완료 |

---

## 실행 흐름

```
Matrix: build (ubuntu + windows)
        ↓
Matrix: matrix-tests (6개 조합)
        ↓
Selective deploy ──← Detect deployable changes
```

---