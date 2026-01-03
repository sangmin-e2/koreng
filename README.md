# IME Caret Indicator

Windows 10/11에서 텍스트 입력 위치 근처에 한/영 입력 상태를 표시하는 오버레이 애플리케이션입니다.

## 기능

- **실시간 IME 상태 표시**: 텍스트 입력 위치 근처에 원형 배지로 한/영 상태 표시
  - 한글 입력: 파란색 원형 배지에 "K"
  - 영어 입력: 오렌지색 원형 배지에 "E"
- **멀티 모니터 지원**: 여러 모니터 환경에서 정상 작동
- **DPI 스케일링 지원**: 다양한 DPI 설정에서 정확한 위치 표시
- **클릭-스루**: 배지가 입력을 방해하지 않음
- **경량**: 낮은 CPU 사용률

## 요구사항

- Windows 10/11
- Python 3.x (개발용, 실행 파일은 Python 불필요)

## 사용 방법

### 실행 파일 사용 (권장)

1. `dist/IME_Caret_Indicator.exe` 파일을 다운로드
2. 실행 파일을 더블클릭하여 실행
3. 제어 창에서 **"시작"** 버튼 클릭
4. 텍스트 입력 창에서 입력 → 캐럿 옆에 배지가 표시됩니다

### 소스 코드 실행

```bash
python main.py
```

## 빌드 방법

PyInstaller를 사용하여 단일 실행 파일로 빌드:

```bash
pip install pyinstaller
pyinstaller --onefile --name "IME_Caret_Indicator" --noconsole main.py
```

빌드된 파일은 `dist/IME_Caret_Indicator.exe`에 생성됩니다.

## 기술 스택

- **Python**: 메인 언어
- **tkinter**: GUI 프레임워크
- **ctypes**: Windows API 호출
- **imm32**: IME 상태 감지
- **user32**: 캐럿 위치 및 윈도우 관리

## 주요 기능 설명

### IME 상태 감지

- `ImmGetConversionStatus`: 레거시 앱에서 한글 모드 감지
- `GetKeyState(VK_HANGUL)`: TSF 기반 앱에서 한/영 토글 상태 감지
- 포커스 윈도우의 thread ID를 사용하여 정확한 언어 레이아웃 감지

### 배지 표시

- 투명 배경 오버레이 윈도우
- 캐럿 위치 추적 및 실시간 업데이트
- 멀티 모니터 환경에서 모니터 경계 내 위치 보정

## 라이선스

이 프로젝트는 자유롭게 사용, 수정, 배포할 수 있습니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.
