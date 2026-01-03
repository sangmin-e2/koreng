# GitHub 레포지토리 설정 가이드

## 1. GitHub에서 레포지토리 생성

1. https://github.com 에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 레포지토리 이름 입력 (예: `ime-caret-indicator`)
4. "Public" 또는 "Private" 선택
5. "Create repository" 클릭
   - **중요**: README, .gitignore, license는 추가하지 마세요 (이미 있음)

## 2. 로컬 저장소와 GitHub 연결

GitHub에서 레포지토리를 생성한 후, 아래 명령어를 실행하세요:

```bash
# 원격 저장소 추가 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 메인 브랜치로 푸시
git push -u origin main
```

## 3. 또는 SSH를 사용하는 경우

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## 예시

레포지토리 이름이 `ime-caret-indicator`이고 사용자 이름이 `username`인 경우:

```bash
git remote add origin https://github.com/username/ime-caret-indicator.git
git push -u origin main
```

