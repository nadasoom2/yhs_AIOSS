#!/bin/bash
# GitHub 자동화 설정 가이드

set -e

echo "🚀 GitHub 자동화 설정 시작..."

# 1. Secrets 설정 안내
cat << 'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣  GitHub Secrets 설정 (필수)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Settings > Secrets and variables > Actions에서:

✅ SNYK_TOKEN
   - https://snyk.io 로그인
   - Settings > Auth Token 복사
   - GitHub Secrets에 추가

(참고: GITHUB_TOKEN은 자동으로 제공됩니다)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2️⃣  Repository Settings 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

General > Features:
  ✅ Issues
  ✅ Projects
  ✅ Security (Code security and analysis)

Code security and analysis:
  ✅ Dependabot alerts
  ✅ Dependabot security updates
  ✅ Secret scanning

Branches > Branch protection rules (main/develop):
  ✅ Require pull request reviews before merging (1명)
  ✅ Require status checks to pass
  ✅ Require branches to be up to date
  ✅ Include administrators

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3️⃣  작업 흐름
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 npm 패키지 배포:
  git tag v1.0.1
  git push origin v1.0.1
  # → 자동으로 npm 배포 + Release 생성

🐳 Docker 빌드/푸시:
  git push origin main
  # → 자동으로 Docker 이미지 빌드 및 ghcr.io 푸시

🔒 보안 스캔:
  - 매 주 월요일 자동 실행
  - 매 push 시 자동 실행
  - 취약점 발견 시 이슈 자동 생성

🔄 의존성 업데이트:
  - Dependabot이 주 1회 PR 생성
  - dev/patch는 자동 머지
  - major/minor는 수동 검토

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

echo ""
echo "✅ 설정 파일 생성 완료!"
echo ""
echo "다음 단계:"
echo "1. GitHub에 코드 푸시"
echo "2. Repository Settings에서 위의 설정 활성화"
echo "3. SNYK_TOKEN 추가"
echo "4. 테스트: git tag v1.0.0 && git push --tags"
echo ""
