# PLAN.md — Codex 실행 계획

## 0. 목표

사용자가 현재 모니터 화면에서 마우스로 사각형 영역을 지정하면, 그 영역을 시간 흐름에 따라 MP4 동영상으로 저장하는 Python 데스크톱 앱을 만든다.

MVP는 다음을 만족한다.

- 스크린샷 도구처럼 영역 선택
- 녹화 시작/중지
- MP4 저장
- GUI 멈춤 방지
- 기본 테스트 통과
- 오디오와 커서 캡처는 제외

## 1. 전체 아키텍처

```text
PySide6 MainWindow
  ├─ Select Region 버튼
  │   └─ RegionSelector overlay
  │       └─ Region dataclass 반환
  ├─ Start Recording 버튼
  │   └─ ScreenRecorder worker thread
  │       ├─ mss로 지정 영역 캡처
  │       ├─ BGRA → RGB 변환
  │       └─ VideoWriter로 MP4 저장
  └─ Stop Recording 버튼 / Tray action
      └─ stop_event 설정 후 writer cleanup
```

## 2. 파일별 책임

### `screen_region_recorder/models.py`

- `Region` dataclass
- `RecordingConfig` dataclass
- 드래그 시작/끝 좌표로부터 정규화된 rectangle 생성
- 최소 영역 검증
- 짝수 width/height 보정
- FPS/CRF 검증

### `screen_region_recorder/selector.py`

- PySide6 기반 전체 화면 투명 오버레이
- `QRubberBand`로 드래그 영역 표시
- 마우스 press/move/release 처리
- Esc 취소
- 선택 영역을 `Region`으로 반환하거나 signal emit
- HiDPI coordinate conversion 주석 및 처리

### `screen_region_recorder/video_writer.py`

- `imageio_ffmpeg.write_frames` wrapper
- RGB uint8 NumPy frame 입력
- MP4/H.264 호환 인코딩
- `pix_fmt_out="yuv420p"`
- C-contiguous 보장
- 안전한 `close()`

### `screen_region_recorder/recorder.py`

- mss 캡처 루프
- worker thread 실행
- `threading.Event` 기반 stop
- FPS pacing
- elapsed/frame_count progress 보관
- writer cleanup
- GUI 객체 직접 접근 금지

### `screen_region_recorder/main.py`

- PySide6 MainWindow
- output path picker
- FPS/CRF 입력
- Select/Start/Stop 버튼
- status label
- system tray stop action
- 예외 처리와 QMessageBox
- `python -m screen_region_recorder.main` entry point

## 3. 구현 단계

### Phase 1 — 모델과 테스트

- `Region`, `RecordingConfig` 구현
- geometry helper 구현
- pytest 추가

완료 기준:

- reverse drag 포함 모든 좌표 테스트 통과
- tiny region rejection 동작
- odd width/height 보정 테스트 통과

### Phase 2 — 영역 선택 overlay

- full-screen transparent overlay
- `QRubberBand` 표시
- mouse event 처리
- Esc 취소
- Region 반환

완료 기준:

- 네 방향 드래그가 올바른 영역으로 정규화됨
- 너무 작은 영역은 거부됨
- overlay가 녹화 시작 전에 사라짐

### Phase 3 — MP4 writer

- `VideoWriter` wrapper 구현
- RGB frame validation
- close cleanup

완료 기준:

- writer API가 명확함
- frame shape/type 오류를 친절하게 처리
- 테스트 가능 범위에서 pytest 통과

### Phase 4 — recorder engine

- mss 캡처
- BGRA → RGB 변환
- worker thread
- stop event
- FPS pacing

완료 기준:

- UI thread를 막지 않음
- stop 시 writer가 닫힘
- elapsed/frame_count 확인 가능

### Phase 5 — GUI integration

- main window 구현
- output path/FPS/CRF 입력
- Select/Start/Stop 흐름 연결
- system tray stop action

완료 기준:

- 앱 실행 가능
- 선택 영역 표시
- 녹화 시작/중지 가능
- 오류 메시지 표시

### Phase 6 — 문서와 검증

- README 업데이트
- OS 권한 안내
- 수동 테스트 checklist 업데이트
- PR review prompt로 하드닝

완료 기준:

- README만 보고 설치/실행 가능
- 알려진 제한사항 명확히 문서화
- pytest 통과

## 4. 핵심 리스크와 대응

### HiDPI / Retina / Windows 배율

리스크: Qt 좌표와 캡처 좌표가 다를 수 있음.

대응:

- `devicePixelRatio()` 처리 주석 추가
- selector와 recorder 사이 좌표 기준을 명확히 문서화
- 수동 테스트에서 100%, 125%, 150% 배율 확인

### 녹화 중 UI 캡처

리스크: 메인 창이나 overlay가 녹화 대상에 포함될 수 있음.

대응:

- 녹화 시작 전에 overlay를 닫기
- main window hide/minimize 후 짧은 안정화 delay 적용 검토

### writer cleanup

리스크: 중지/예외 시 MP4가 손상될 수 있음.

대응:

- writer close를 `finally`에서 보장
- stop 이후 thread join
- 예외 상태 UI에 표시

### frame pacing

리스크: 캡처/인코딩이 FPS를 따라가지 못해 CPU 사용량 증가.

대응:

- `time.perf_counter()` 기반 pacing
- 뒤처졌을 때 busy wait 금지
- 기본 FPS 15로 시작

## 5. 최종 수동 테스트

1. 앱 실행
2. Select Region 클릭
3. 화면 영역 드래그
4. 선택 영역이 UI에 표시되는지 확인
5. output path 지정
6. FPS 15로 녹화 시작
7. 5초 이상 화면 변화 만들기
8. Stop Recording 실행
9. MP4 재생 확인
10. 앱이 freeze 없이 유지되는지 확인
11. 역방향 드래그도 테스트
12. 매우 작은 영역이 거부되는지 확인

## 6. MVP 이후 확장 후보

- 다중 모니터 선택
- cursor capture 옵션
- pause/resume
- global hotkey
- audio recording
- PyInstaller packaging
- 녹화 영역 preset 저장
