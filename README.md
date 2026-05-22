# 유학생 생활·행정 안내 AI 에이전트

동아대학교 유학생이 한국 생활에서 마주치는 행정 문제를 자신의 언어로 질문하면, 관련 정보를 찾아 답변하는 AI 에이전트입니다.

이 저장소는 9주차 과제 제출용으로, 다음 3가지 요구사항을 충족하도록 정리되어 있습니다.
모든 설정과 확인 링크는 main 브랜치 기준으로 작성되어 있습니다.

---

## 과제 요구사항 정리

### 1. npm 패키지를 GitHub Packages에 배포하고 버전 업데이트까지 수행

- `package.json`의 버전을 `1.0.0 -> 1.0.1`로 업데이트하는 흐름을 포함합니다.
- GitHub Actions의 `publish-npm.yml`에서 태그 기반 배포를 수행합니다.
- GitHub Packages에 `@nadasoom2/agent-runtime` 패키지가 업로드되도록 구성되어 있습니다.
- 배포 결과와 태그는 아래 링크에서 확인할 수 있습니다.

확인 링크
- GitHub Tags: https://github.com/nadasoom2/yhs_AIOSS/tags
- GitHub Packages: https://github.com/nadasoom2/yhs_AIOSS/pkgs/npm/agent-runtime
- publish 워크플로 실행 결과: https://github.com/nadasoom2/yhs_AIOSS/actions/workflows/publish-npm.yml

관련 파일
- [package.json](package.json) - `package.json`
- [.github/workflows/publish-npm.yml](.github/workflows/publish-npm.yml) - `.github/workflows/publish-npm.yml`

---

### 2. Docker 이미지를 자동 빌드/푸시하고 로컬 실행을 검증

- Dockerfile을 기반으로 이미지가 자동 빌드됩니다.
- GitHub Actions의 `docker.yml`에서 이미지 빌드 및 푸시를 수행합니다.
- `docker-compose.yml`로 로컬 실행과 헬스체크를 검증할 수 있습니다.

확인 링크
- Docker 이미지 레지스트리: (여기에 입력)
- Docker 워크플로 실행 결과: https://github.com/nadasoom2/yhs_AIOSS/actions/workflows/docker.yml

관련 파일
- [Dockerfile](Dockerfile) - `Dockerfile`
- [docker-compose.yml](docker-compose.yml) - `docker-compose.yml`
- [.github/workflows/docker.yml](.github/workflows/docker.yml) - `.github/workflows/docker.yml`

---

### 3. Dependabot 정책과 보안 스캔 결과 자동화

- `.github/dependabot.yml`에서 업데이트 스케줄을 관리합니다.
- npm, Python, Docker, GitHub Actions 업데이트를 분리해서 관리합니다.
- 그룹 설정을 통해 업데이트를 묶어서 처리합니다.
- `security-scan.yml`에서 npm audit와 Snyk를 실행합니다.
- 결과는 아티팩트와 SARIF로 저장되며, 고위험 취약점은 GitHub Issue로 자동 생성됩니다.

확인 링크
- Dependabot 설정: https://github.com/nadasoom2/yhs_AIOSS/blob/main/.github/dependabot.yml
- Security Scan 워크플로 실행 결과: https://github.com/nadasoom2/yhs_AIOSS/actions/workflows/security-scan.yml
- 생성된 이슈 또는 보안 리포트: https://github.com/nadasoom2/yhs_AIOSS/actions/runs/26293184322

관련 파일
- [.github/dependabot.yml](.github/dependabot.yml) - `.github/dependabot.yml`
- [.github/workflows/security-scan.yml](.github/workflows/security-scan.yml) - `.github/workflows/security-scan.yml`

---


## 기여

이 저장소는 과제 제출용으로 정리되었습니다. 기여 전에는 별도 안내 문서를 확인해 주세요.
