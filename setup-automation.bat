@echo off
REM GitHub 자동화 설정 가이드 (Windows PowerShell 버전)

echo.
echo ======================================================================
echo 1️⃣  GitHub Secrets 설정 (필수)
echo ======================================================================
echo.
echo Settings ^> Secrets and variables ^> Actions에서:
echo.
echo ✅ SNYK_TOKEN
echo    - https://snyk.io 로그인
echo    - Settings ^> Auth Token 복사
echo    - GitHub Secrets에 추가
echo.
echo (참고: GITHUB_TOKEN은 자동으로 제공됩니다)
echo.
echo ======================================================================
echo 2️⃣  Repository Settings 설정
echo ======================================================================
echo.
echo General ^> Features:
echo   ✅ Issues
echo   ✅ Projects
echo   ✅ Security (Code security and analysis)
echo.
echo Code security and analysis:
echo   ✅ Dependabot alerts
echo   ✅ Dependabot security updates
echo   ✅ Secret scanning
echo.
echo Branches ^> Branch protection rules (main/develop):
echo   ✅ Require pull request reviews before merging (1명)
echo   ✅ Require status checks to pass
echo   ✅ Require branches to be up to date
echo   ✅ Include administrators
echo.
echo ======================================================================
echo 3️⃣  작업 흐름
echo ======================================================================
echo.
echo 📦 npm 패키지 배포:
echo   git tag v1.0.1
echo   git push origin v1.0.1
echo   (→ 자동으로 npm 배포 + Release 생성)
echo.
echo 🐳 Docker 빌드/푸시:
echo   git push origin main
echo   (→ 자동으로 Docker 이미지 빌드 및 ghcr.io 푸시)
echo.
echo 🔒 보안 스캔:
echo   - 매 주 월요일 자동 실행
echo   - 매 push 시 자동 실행
echo   - 취약점 발견 시 이슈 자동 생성
echo.
echo 🔄 의존성 업데이트:
echo   - Dependabot이 주 1회 PR 생성
echo   - dev/patch는 자동 머지
echo   - major/minor는 수동 검토
echo.
echo ======================================================================
echo.
echo ✅ 설정 파일 생성 완료!
echo.
echo 다음 단계:
echo 1. GitHub에 코드 푸시
echo 2. Repository Settings에서 위의 설정 활성화
echo 3. SNYK_TOKEN 추가
echo 4. 테스트: git tag v1.0.0 ^&^& git push --tags
echo.
