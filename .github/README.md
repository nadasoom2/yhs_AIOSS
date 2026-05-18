# GitHub Configuration File

## Security Policy
- Issues: GitHub Issues를 통해 보안 취약점 보고
- Dependabot: 자동 의존성 업데이트 활성화
- Branch Protection: main/develop 브랜치에 PR 검토 필수

## CI/CD Pipeline

### 1. npm 배포 자동화 (publish-npm.yml)
- **트리거:** Git tag 생성 (v*.*.*)
- **버전 업데이트:** tag에서 자동 추출
- **배포 대상:** GitHub Packages (@yhs-aioss/agent-runtime)
- **인증:** GITHUB_TOKEN (자동)

```bash
# 배포 방법
git tag v1.0.1
git push origin v1.0.1
```

### 2. Docker 자동 빌드/푸시 (docker.yml)
- **트리거:** main/develop 브랜치 push, tag, PR
- **저장소:** GitHub Container Registry (ghcr.io)
- **로컬 테스트:** PR에서 자동 검증
- **태그:** branch, semver, SHA 기반 자동 생성

```bash
# 로컬 테스트
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### 3. 보안 자동화 (security-scan.yml)
- **npm audit:** 매 주 월요일 + 매 push 시 실행
- **Snyk:** 고위험 취약점 자동 감지
- **SARIF 리포트:** GitHub Security에 자동 업로드
- **이슈 생성:** 중대 취약점 발견 시 자동 이슈 생성

### 4. Dependabot 설정 (dependabot.yml)
- **npm:** 주 1회 (월요일 3:00 UTC)
- **Python:** 주 1회 (월요일 3:30 UTC)
- **Docker:** 주 1회 (월요일 4:00 UTC)
- **GitHub Actions:** 주 1회 (월요일 4:30 UTC)
- **자동 머지:** dev/patch 업데이트만 자동 승인

## 설정 필요 사항

### GitHub Secrets 추가 (Settings > Secrets and variables > Actions)
```
- GITHUB_TOKEN: 자동 제공 (npm 배포, Docker push)
- SNYK_TOKEN: https://snyk.io에서 발급 후 추가
```

### GitHub Repository Settings
1. **Branch Protection (main/develop)**
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date

2. **Code Security**
   - ✅ Enable Dependabot alerts
   - ✅ Enable Dependabot security updates
   - ✅ Enable secret scanning

3. **Actions**
   - ✅ Allow all actions and reusable workflows

## 운영 가이드

### 버전 업데이트 및 배포
```bash
# 1. 패치 업데이트 (1.0.0 → 1.0.1)
npm version patch
git push

# 2. 마이너 업데이트 (1.0.0 → 1.1.0)
npm version minor
git push

# 3. 메이저 업데이트 (1.0.0 → 2.0.0)
npm version major
git push

# 4. 수동 배포 (필요시)
git tag v1.0.1
git push origin v1.0.1
```

### 보안 스캔 결과 확인
- GitHub Actions 로그: Actions > Security Scan
- 아티팩트: npm-audit-report, snyk-results, dependency-report
- GitHub Security: Security > Code scanning alerts

### Dependabot PR 관리
- 자동 머지 설정됨 (dev + patch/minor만)
- 메이저 버전은 수동 검토 필수
- 충돌 시 수동 해결 필요

## 문제 해결

### npm 배포 실패
- GitHub Token 권한 확인: Settings > Developer settings > Personal access tokens
- package.json의 registry 설정 확인
- 버전이 이미 존재하지 않은지 확인

### Docker 빌드 실패
- Dockerfile 문법 확인
- 의존성이 requirements.txt에 포함되었는지 확인
- 로컬에서 `docker build -t test .` 테스트

### 보안 스캔 오류
- Snyk Token 만료 확인
- npm audit JSON 형식 확인
- Python 버전 호환성 확인
