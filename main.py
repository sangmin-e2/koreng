#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IME Caret Indicator (E Badge)
Windows에서 텍스트 입력 위치 근처에 한/영 입력 상태를 표시하는 오버레이 앱
멀티 모니터 및 혼합 DPI 환경 지원
"""

import ctypes
import ctypes.wintypes as wt
import tkinter as tk
import sys
import datetime
import time

# ============================================================================
# 로그 설정
# ============================================================================
LOG_FILE = "ime_caret_indicator.log"

def log_debug(message):
    """디버깅 로그를 콘솔과 파일에 출력"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except:
        pass

# ============================================================================
# 설정 상수
# ============================================================================
DOT_SIZE = 22  # 18에서 20% 증가 (18 * 1.2 = 21.6 → 22)
OFFSET_X = 6
OFFSET_Y = 10
CURSOR_OFFSET_X = 25  # 마우스 커서 기반 위치일 때 추가 오프셋 (오른쪽)
CURSOR_OFFSET_Y = 25  # 마우스 커서 기반 위치일 때 추가 오프셋 (아래쪽)
TICK_MS = 80

ENG_FILL = "#ff9800"  # 오렌지 (E일 때)
KOR_FILL = "#2196F3"  # 파란색 (K일 때)
TEXT_COLOR = "white"
KOREAN_LANGID = 0x0412  # ko-KR

# ============================================================================
# Windows API 초기화
# ============================================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)
imm32 = ctypes.WinDLL("imm32", use_last_error=True)

# ============================================================================
# DPI Awareness 설정
# ============================================================================

def enable_dpi_awareness():
    try:
        DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
        user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        user32.SetProcessDpiAwarenessContext.restype = wt.BOOL
        user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass

enable_dpi_awareness()

# ============================================================================
# Windows 구조체
# ============================================================================

class RECT(ctypes.Structure):
    _fields_ = [("left", wt.LONG), ("top", wt.LONG), ("right", wt.LONG), ("bottom", wt.LONG)]

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.DWORD),
        ("flags", wt.DWORD),
        ("hwndActive", wt.HWND),
        ("hwndFocus", wt.HWND),
        ("hwndCapture", wt.HWND),
        ("hwndMenuOwner", wt.HWND),
        ("hwndMoveSize", wt.HWND),
        ("hwndCaret", wt.HWND),
        ("rcCaret", RECT),
    ]

class POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wt.DWORD),
    ]

# ============================================================================
# Windows API 함수 시그니처
# ============================================================================

user32.GetForegroundWindow.restype = wt.HWND
user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
user32.GetWindowThreadProcessId.restype = wt.DWORD
user32.GetGUIThreadInfo.argtypes = [wt.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.GetGUIThreadInfo.restype = wt.BOOL
user32.ClientToScreen.argtypes = [wt.HWND, ctypes.POINTER(POINT)]
user32.ClientToScreen.restype = wt.BOOL
user32.GetKeyboardLayout.argtypes = [wt.DWORD]
user32.GetKeyboardLayout.restype = wt.HKL
user32.GetKeyState.argtypes = [wt.INT]
user32.GetKeyState.restype = wt.SHORT
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wt.BOOL
user32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wt.BOOL
user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(RECT)]
user32.GetClientRect.restype = wt.BOOL

# 한/영 토글 키 코드
VK_HANGUL = 0x15  # Hangul toggle key

imm32.ImmGetContext.argtypes = [wt.HWND]
imm32.ImmGetContext.restype = wt.HANDLE
imm32.ImmGetOpenStatus.argtypes = [wt.HANDLE]
imm32.ImmGetOpenStatus.restype = wt.BOOL
imm32.ImmGetConversionStatus.argtypes = [wt.HANDLE, ctypes.POINTER(wt.DWORD), ctypes.POINTER(wt.DWORD)]
imm32.ImmGetConversionStatus.restype = wt.BOOL
imm32.ImmReleaseContext.argtypes = [wt.HWND, wt.HANDLE]
imm32.ImmReleaseContext.restype = wt.BOOL

# IME 변환 모드 플래그
IME_CMODE_NATIVE = 0x0001  # 한글(네이티브) 모드

# 모니터 관련
MONITOR_DEFAULTTONEAREST = 2
user32.MonitorFromPoint.argtypes = [POINT, wt.DWORD]
user32.MonitorFromPoint.restype = wt.HMONITOR
user32.GetMonitorInfoW.argtypes = [wt.HMONITOR, ctypes.POINTER(MONITORINFO)]
user32.GetMonitorInfoW.restype = wt.BOOL

# 창 위치 설정
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, wt.INT, wt.INT, wt.INT, wt.INT, wt.UINT]
user32.SetWindowPos.restype = wt.BOOL

HWND_TOPMOST = wt.HWND(-1)
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

# ============================================================================
# 헬퍼 함수
# ============================================================================

def get_foreground_thread_id(hwnd: int) -> int:
    pid = wt.DWORD(0)
    return user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

def get_window_thread_id(hwnd: int) -> int:
    """윈도우 핸들의 thread ID를 반환"""
    pid = wt.DWORD(0)
    return user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

def get_langid(tid: int) -> int:
    hkl = user32.GetKeyboardLayout(tid)
    return int(hkl) & 0xFFFF

def is_hangul_toggled() -> bool:
    """GetKeyState로 한/영 토글 상태 확인 (LSB 1비트가 토글 상태)"""
    return bool(user32.GetKeyState(VK_HANGUL) & 1)

def get_caret_screen_pos():
    hwnd_fg = user32.GetForegroundWindow()
    if not hwnd_fg:
        return None, None, None, None, False

    tid = get_foreground_thread_id(hwnd_fg)

    gti = GUITHREADINFO()
    gti.cbSize = ctypes.sizeof(GUITHREADINFO)
    gti_success = user32.GetGUIThreadInfo(tid, ctypes.byref(gti))
    
    # 캐럿이 있는 경우 (가장 정확) - 문서 앱 등에서 작동
    if gti_success and gti.hwndCaret:
        pt = POINT(gti.rcCaret.left, gti.rcCaret.bottom)
        if user32.ClientToScreen(gti.hwndCaret, ctypes.byref(pt)):
            return (pt.x, pt.y), hwnd_fg, tid, gti.hwndFocus, False  # False = 캐럿 기반

    # 캐럿이 없을 때 (크롬, 시스템 앱 등)
    # 1. 마우스 커서 위치를 우선 사용 (사용자가 입력하려는 위치 근처)
    pt = POINT()
    if user32.GetCursorPos(ctypes.byref(pt)):
        # 마우스 커서가 포그라운드 윈도우 내부에 있는지 확인
        rect = RECT()
        if user32.GetWindowRect(hwnd_fg, ctypes.byref(rect)):
            # 마우스가 윈도우 내부에 있으면 마우스 위치 사용
            if (rect.left <= pt.x <= rect.right and rect.top <= pt.y <= rect.bottom):
                return (pt.x, pt.y), hwnd_fg, tid, gti.hwndFocus if gti_success else None, True  # True = 마우스 커서 기반
    
    # 2. 포커스된 윈도우 또는 포그라운드 윈도우의 위치 사용
    hwnd_target = None
    if gti_success and gti.hwndFocus:
        hwnd_target = gti.hwndFocus
    else:
        hwnd_target = hwnd_fg
    
    if hwnd_target:
        # 윈도우의 클라이언트 영역 중앙 근처에 표시
        rect = RECT()
        if user32.GetWindowRect(hwnd_target, ctypes.byref(rect)):
            # 윈도우 중앙에서 약간 왼쪽 위에 표시
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            # 중앙에서 왼쪽 위로 이동
            badge_x = center_x - 100
            badge_y = center_y - 50
            # 윈도우 경계 내로 제한
            badge_x = max(rect.left + 20, min(badge_x, rect.right - DOT_SIZE - 20))
            badge_y = max(rect.top + 20, min(badge_y, rect.bottom - DOT_SIZE - 20))
            return (badge_x, badge_y), hwnd_fg, tid, hwnd_target if gti_success else None, False  # False = 윈도우 위치 기반
    
    # 3. 최후의 수단: 마우스 커서 위치 (윈도우 밖이어도)
    pt = POINT()
    if user32.GetCursorPos(ctypes.byref(pt)):
        return (pt.x, pt.y), hwnd_fg, tid, gti.hwndFocus if gti_success else None, True  # True = 마우스 커서 기반
    
    return None, hwnd_fg, tid, gti.hwndFocus if gti_success else None, False

def is_hangul_mode(hwnd_focus: int, force_refresh: bool = False, retry_count: int = 0) -> bool:
    """
    가능한 순서:
    1) IMM32 conversion status (레거시 앱에서 잘 됨)
    2) VK_HANGUL 토글 상태 (TSF 앱에서도 비교적 잘 됨)
    
    force_refresh: 앱 전환 시 IME 상태를 강제로 다시 확인
    retry_count: 재시도 횟수 (앱 전환 시 여러 번 확인)
    """
    # 포커스 핸들이 없으면 폴백
    if not hwnd_focus:
        return is_hangul_toggled()

    # 앱 전환 시 IME 상태를 강제로 새로고침하기 위해 약간의 지연
    if force_refresh or retry_count > 0:
        time.sleep(0.02)  # 20ms 지연으로 IME 상태 업데이트 대기

    # 여러 소스에서 IME 상태 확인
    imm_result = None
    vk_result = is_hangul_toggled()
    
    himc = imm32.ImmGetContext(hwnd_focus)
    if himc:
        try:
            conv = wt.DWORD(0)
            sent = wt.DWORD(0)
            ok = bool(imm32.ImmGetConversionStatus(himc, ctypes.byref(conv), ctypes.byref(sent)))
            if ok and conv.value != 0:
                # IME_CMODE_NATIVE가 설정되어 있으면 한글 모드
                imm_result = bool(conv.value & IME_CMODE_NATIVE)
        finally:
            imm32.ImmReleaseContext(hwnd_focus, himc)
    
    # 결과 판단
    if imm_result is not None:
        # IMM32 결과가 있으면 사용하되, VK_HANGUL과 비교
        # 앱 전환 직후에는 VK_HANGUL이 더 정확할 수 있음
        if force_refresh or retry_count > 0:
            # 앱 전환 시에는 VK_HANGUL을 우선 (더 신뢰할 수 있음)
            if imm_result != vk_result:
                return vk_result
        return imm_result
    else:
        # IMM32 결과가 없으면 VK_HANGUL 사용
        return vk_result

def make_click_through(hwnd: int):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_NOACTIVATE = 0x08000000

    user32.GetWindowLongW.argtypes = [wt.HWND, wt.INT]
    user32.GetWindowLongW.restype = wt.LONG
    user32.SetWindowLongW.argtypes = [wt.HWND, wt.INT, wt.LONG]
    user32.SetWindowLongW.restype = wt.LONG

    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= (WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

def clamp_to_monitor(x: int, y: int):
    hmon = user32.MonitorFromPoint(POINT(x, y), MONITOR_DEFAULTTONEAREST)
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    if not user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
        return x, y

    left, top, right, bottom = mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom
    x = max(left, min(x, right - DOT_SIZE))
    y = max(top, min(y, bottom - DOT_SIZE))
    return x, y

# ============================================================================
# UI 초기화
# ============================================================================

# 제어 창 (메인 Tk 인스턴스)
control_root = tk.Tk()
control_root.title("KORENG | 코랭")
control_root.geometry("400x200")
control_root.resizable(False, False)

# 배지 창 (Toplevel로 변경 - Tk() 2개 방지)
root = tk.Toplevel(control_root)
root.withdraw()  # 먼저 숨김
root.overrideredirect(True)
root.attributes("-topmost", True)
root.wm_attributes("-topmost", True)

TRANSPARENT = "magenta"
root.configure(bg=TRANSPARENT)
root.attributes("-transparentcolor", TRANSPARENT)

canvas = tk.Canvas(root, width=DOT_SIZE, height=DOT_SIZE, bg=TRANSPARENT, highlightthickness=0, bd=0)
# 원형 배지 그리기 (배경이 투명하도록)
circle = canvas.create_oval(1, 1, DOT_SIZE - 1, DOT_SIZE - 1, fill=ENG_FILL, outline=ENG_FILL, width=0)
label = canvas.create_text(DOT_SIZE // 2, DOT_SIZE // 2, text="E", fill=TEXT_COLOR,
                           font=("Segoe UI", 12, "bold"))
canvas.pack(fill=tk.BOTH, expand=True)

# 초기 위치를 화면 밖으로 설정
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{DOT_SIZE}x{DOT_SIZE}+{screen_width}+{screen_height}")

root.update_idletasks()
hwnd_overlay = root.winfo_id()
print(f"[초기화] 배지 창 핸들: {hwnd_overlay}")

# 클릭-스루 설정을 나중에 적용 (배지가 먼저 보이도록)
# make_click_through(hwnd_overlay)

def show_and_move(px: int, py: int):
    # 먼저 geometry로 위치 설정
    root.geometry(f"{DOT_SIZE}x{DOT_SIZE}+{px}+{py}")
    root.update_idletasks()
    
    # 그 다음 SetWindowPos로 정확한 위치 설정
    user32.SetWindowPos(hwnd_overlay, HWND_TOPMOST, px, py, DOT_SIZE, DOT_SIZE,
                        SWP_NOACTIVATE | SWP_SHOWWINDOW)
    
    # 창이 보이도록 강제 업데이트 (update_idletasks만 사용)
    root.update_idletasks()

is_running = False
_last_badge = None
_last_log_time = 0.0
_last_hwnd_fg = None  # 이전 포그라운드 윈도우 추적 (앱 전환 감지용)
_app_switch_count = 0  # 앱 전환 후 몇 틱 동안 더 정확하게 확인

def start_badge():
    global is_running
    is_running = True
    status_label.config(text="상태: 실행 중", fg="green")
    start_button.config(state=tk.DISABLED)
    # 배지 창이 준비되었는지 확인
    root.update_idletasks()

def stop_badge():
    global is_running
    is_running = False
    root.withdraw()
    status_label.config(text="상태: 중지됨", fg="black")
    start_button.config(state=tk.NORMAL)

def test_badge():
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    test_x = screen_width // 2 - DOT_SIZE // 2
    test_y = screen_height // 2 - DOT_SIZE // 2
    
    canvas.itemconfig(circle, fill=ENG_FILL)
    canvas.itemconfig(label, text="E")
    
    # 위치 먼저 설정
    root.geometry(f"{DOT_SIZE}x{DOT_SIZE}+{test_x}+{test_y}")
    root.update_idletasks()
    
    # 배지 창 표시
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.wm_attributes("-topmost", True)
    
    # SetWindowPos로 강제 표시
    user32.SetWindowPos(hwnd_overlay, HWND_TOPMOST, test_x, test_y, DOT_SIZE, DOT_SIZE,
                       SWP_NOACTIVATE | SWP_SHOWWINDOW)
    
    root.update_idletasks()
    
    # 상태 표시를 제어 창에 표시
    status_label.config(text=f"테스트: 배지 표시됨 ({test_x}, {test_y})", fg="blue")

def on_closing():
    root.quit()
    control_root.quit()
    control_root.destroy()
    root.destroy()
    sys.exit(0)

control_root.protocol("WM_DELETE_WINDOW", on_closing)

title_label = tk.Label(control_root, text="KORENG | 코랭", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=10)

developer_label = tk.Label(control_root, text="개발자 : 이상민", font=("Segoe UI", 8))
developer_label.pack(pady=0)

status_label = tk.Label(control_root, text="상태: 중지됨", font=("Segoe UI", 10))
status_label.pack(pady=5)

button_frame = tk.Frame(control_root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="시작", command=start_badge, width=10, height=2,
                         font=("Segoe UI", 10), bg="#4CAF50", fg="white", relief=tk.RAISED)
start_button.pack(side=tk.LEFT, padx=5)

test_button = tk.Button(button_frame, text="테스트", command=test_badge, width=10, height=2,
                        font=("Segoe UI", 10), bg="#2196F3", fg="white", relief=tk.RAISED)
test_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="종료", command=on_closing, width=10, height=2,
                        font=("Segoe UI", 10), bg="#f44336", fg="white", relief=tk.RAISED)
stop_button.pack(side=tk.LEFT, padx=5)

# ============================================================================
# 업데이트 루프
# ============================================================================

def tick():
    global _last_badge, _last_log_time, _last_hwnd_fg, _app_switch_count
    
    if not is_running:
        control_root.after(120, tick)
        return

    pos, hwnd_fg, tid, hwnd_focus, is_cursor_based = get_caret_screen_pos()
    if not hwnd_fg:
        # 포그라운드 윈도우가 없으면 배지 숨김
        root.withdraw()
        _last_hwnd_fg = None
        control_root.after(TICK_MS, tick)
        return
    
    # 앱 전환 감지
    global _app_switch_count
    app_switched = (_last_hwnd_fg is not None and _last_hwnd_fg != hwnd_fg)
    if app_switched:
        _app_switch_count = 3  # 앱 전환 후 3틱 동안 더 정확하게 확인
    elif _app_switch_count > 0:
        _app_switch_count -= 1
    _last_hwnd_fg = hwnd_fg
    
    # pos가 없어도 hwnd_fg가 있으면 무조건 배지 표시 (크롬, 시스템 앱 대응)
    if not pos:
        # 포그라운드 윈도우의 위치를 사용
        rect = RECT()
        if user32.GetWindowRect(hwnd_fg, ctypes.byref(rect)):
            # 윈도우 중앙 근처에 표시
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            pos = (center_x - 100, center_y - 50)
            is_cursor_based = False
        else:
            # GetWindowRect 실패 시 마우스 커서 위치 사용
            pt = POINT()
            if user32.GetCursorPos(ctypes.byref(pt)):
                pos = (pt.x, pt.y)
                is_cursor_based = True
            else:
                # 모든 방법 실패 시 배지 숨김
                root.withdraw()
                control_root.after(TICK_MS, tick)
                return

    # 포커스 컨트롤 thread로 langid 읽기
    hwnd_for_thread = hwnd_focus if hwnd_focus else hwnd_fg
    tid_layout = get_window_thread_id(hwnd_for_thread)
    langid = get_langid(tid_layout)

    # 상태 계산
    hangul_now = False
    if langid == KOREAN_LANGID:
        # 한국어 키보드 레이아웃일 때만 한글 모드 확인
        # 앱 전환 시 IME 상태를 강제로 다시 확인 (여러 번 확인)
        is_refreshing = app_switched or _app_switch_count > 0
        retry = 2 if app_switched else 0  # 앱 전환 직후에는 2번 더 확인
        hangul_now = is_hangul_mode(hwnd_focus, force_refresh=is_refreshing, retry_count=retry)
    else:
        # 영어 레이아웃일 때는 무조건 영어
        hangul_now = False

    # 배지 설정 (한글일 때 K, 영어일 때 E)
    fill = KOR_FILL if hangul_now else ENG_FILL
    text = "K" if hangul_now else "E"

    # 로그는 상태 바뀔 때만 (멈춤 방지)
    if text != _last_badge or app_switched:
        app_switch_msg = " [앱 전환]" if app_switched else ""
        log_debug(f"레이아웃TID={tid_layout} langid=0x{langid:04x}  VK_HANGUL={is_hangul_toggled()}  -> badge={text}{app_switch_msg}")
        _last_badge = text
    else:
        # 너무 조용하면 1초에 1번 정도만
        now = time.time()
        if now - _last_log_time > 1.0:
            log_debug(f"langid=0x{langid:04x} VK_HANGUL={is_hangul_toggled()} badge={text}")
            _last_log_time = now

    # 캔버스 업데이트
    canvas.itemconfig(circle, fill=fill)
    canvas.itemconfig(label, text=text)

    x, y = pos
    # 마우스 커서 기반 위치일 때 추가 오프셋 적용
    if is_cursor_based:
        gx, gy = clamp_to_monitor(x + OFFSET_X + CURSOR_OFFSET_X, y + OFFSET_Y + CURSOR_OFFSET_Y)
    else:
        gx, gy = clamp_to_monitor(x + OFFSET_X, y + OFFSET_Y)

    # 배지 표시 (test_badge와 완전히 동일한 순서)
    # 1. 캔버스 먼저 업데이트
    canvas.update_idletasks()
    
    # 2. 위치 설정
    root.geometry(f"{DOT_SIZE}x{DOT_SIZE}+{gx}+{gy}")
    root.update_idletasks()
    
    # 3. 배지 창 표시
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.wm_attributes("-topmost", True)
    
    # 4. SetWindowPos로 강제 표시 (test_badge와 동일)
    user32.SetWindowPos(hwnd_overlay, HWND_TOPMOST, gx, gy, DOT_SIZE, DOT_SIZE,
                        SWP_NOACTIVATE | SWP_SHOWWINDOW)
    
    # 5. 창 업데이트 (update_idletasks만 사용 - update()는 프리징 원인)
    root.update_idletasks()

    control_root.after(TICK_MS, tick)

# ============================================================================
# 메인 실행
# ============================================================================

def main():
    print("IME Caret Indicator 시작...")
    print("종료하려면 제어 창의 종료 버튼을 클릭하세요.")
    print(f"디버깅 로그는 '{LOG_FILE}' 파일에도 저장됩니다.")
    
    # 로그 파일 초기화
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"IME Caret Indicator 로그 시작 - {datetime.datetime.now()}\n")
    except:
        pass
    
    # 배지 창 업데이트를 제어 창의 after로 처리
    tick()
    
    # 제어 창 메인 루프 실행 (배지 창은 제어 창의 after로 업데이트)
    # 배지 창(root)은 독립적인 Tk 인스턴스이지만, 이벤트 루프는 제어 창만 실행
    control_root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n종료 중...")
        sys.exit(0)
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
