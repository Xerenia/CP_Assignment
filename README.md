🎮 비트 바이트 (Beat Byte)
비율 기반 리듬 판정 알고리즘과 클라우드/로컬 하이브리드 리더보드가 결합한 아케이드 스네이크 게임

본 프로젝트는 클래식 아케이드 게임인 스네이크(Snake)의 규칙을 뒤집어, 음악의 비트 타이밍에 맞춰 방향을 전환해야 하는 리듬 동기화 액션 퍼즐 게임입니다. 생성형 AI(Gemini 1.5 Pro)와의 긴밀한 페어 프로그래밍(Pair Programming)을 통해 유기적인 MVC 아키텍처 설계, 실시간 외부 클라우드 서버 배포, 그리고 버튼 매싱(Button Mashing)을 차단하는 정교한 게임 밸런싱을 달성했습니다.

📌 목차 (Table of Contents)
🌟 주요 특징 및 기술적 차별점

🛠️ 기술 스택

📁 프로젝트 폴더 구조

🚀 시작하기 및 실행 방법

🕹️ 게임 플레이 및 판정 규칙

📑 [기술 보고서] 시스템 아키텍처 명세

💻 [개발자 가이드] 핵심 소스코드 해설

🤖 AI 협업 및 로그

👥 팀원 및 역할

🌟 주요 특징 및 기술적 차별점 (Key Features)
비율 기반 동적 리듬 판정 시스템 (Ratio-based Judgment)

절대적인 시간(예: 0.08초)이 아닌, 1비트 소요 시간에 대한 퍼센트 비율(PERFECT 15%, GOOD 30%)로 판정창(Window)을 동적 계산합니다.

고난이도(160 BPM)에서 키보드를 무작정 연타하여 판정을 통과하는 어뷰징(Button Mashing)을 구조적으로 완벽히 차단했습니다.

온라인/오프라인 하이브리드 듀얼 리더보드

외부 클라우드 플랫폼(Render.com)에 배포된 Flask API 서버와 통신하여 GLOBAL TOP 10을 제공합니다.

동시에 오프라인 환경을 대비한 로컬 백업 시스템(data/highscore.json)을 구축하여, 메인 화면에서 ONLINE RANKING과 LOCAL RANKING을 좌우 분할된 UI로 동시에 비교할 수 있습니다.

공간적 난이도 스케일링 및 타이머 동기화

스테이지가 올라갈 때 BPM을 강제로 높이는 대신, 유저가 선택한 난이도(EASY, NORMAL, HARD)에 따라 맵에 추가되는 장애물의 개수를 차등 부여(+1, +2, +3)하여 스네이크 게임 본연의 공간적 압박감을 극대화했습니다.

ESC 키를 통한 일시정지(Pause) 기능 구현 시 델타 타임(Delta Time) 보정 로직을 적용하여, 일시정지 해제 시 타이머가 폭주하는 치명적인 싱크 버그를 해결했습니다.

🛠️ 기술 스택 (Tech Stack)
Language: Python 3.11 ~ 3.13

Client GUI / Audio Core: Pygame 2.6.0+

Database & Serialization: JSON Persistent Data Architecture

Web API Server: Flask 3.0.3+ (Deployed on Render Cloud)

Asset Generation Engine: Pillow (PIL) 10.3.0+

📁 프로젝트 폴더 구조 (Directory Structure)
Plaintext
CP_Assignment/                       # 프로젝트 루트 폴더 (Client)
│
├── data/                            # 로컬 데이터 영속성 폴더
│   └── highscore.json               # 오프라인 백업 및 로컬 최고 점수 저장 파일
│
├── assets/                          # 게임 멀티미디어 소스 폴더
│   ├── images/                      # 뱀 스킨, 아이템, 음식 네온 .png 타일 에셋 폴더
│   └── sounds/                      # BPM별 동적 BGM(120_1.mp3 등) 및 판정 효과음 폴더
│
├── backend_engine.py                # [Core] 비율 기반 박자 판정, 게임 룰, REST API 엔진
├── main_ui.py                       # [View/Controller] Pygame 기반 GUI, 듀얼 리더보드 렌더링
├── generate_assets.py               # [Utility] 임시 네온 이미지 자동 생성 스크립트
├── requirements.txt                 # 프로젝트 통합 의존성 환경 명세서
└── README.md                        # 본 프로젝트 매뉴얼 파일
🚀 시작하기 및 실행 방법 (How to Run)
1. 저장소 클론 및 폴더 이동
Bash
git clone https://github.com/Xerenia/CP_Assignment.git
cd CP_Assignment
2. 필수 의존성 라이브러리 일괄 설치
Bash
pip install -r requirements.txt
3. 임시 네온 이미지 에셋 생성 스크립트 실행
외부 에셋 사이트를 이용하지 않고, 파이썬 그래픽 연산을 통해 assets/images/ 폴더 내에 규격에 맞는 30x30 임시 이미지 파일들을 즉석에서 자동 제작합니다.

Bash
python generate_assets.py
4. 메인 게임 클라이언트 실행
Bash
python main_ui.py
🕹️ 게임 플레이 방법 및 판정 규칙 (Gameplay Rules)
이동 방식: 유저가 선택한 난이도의 고정 BPM(EASY 120, NORMAL 140, HARD 160) 박자에 맞춰 스스로 한 칸씩 전진합니다.

조작 및 판정: 정박 타이밍에 맞춰 방향키 (↑, ↓, ←, →)를 누르면 비율 기반 오차를 계산하여 판정을 내립니다.

🟢 PERFECT: 박자와 완벽히 일치 (비트 시간의 15% 이내). 스코어 대폭 상승 및 방향 전환.

🟡 GOOD: 미세한 오차 발생 (비트 시간의 30% 이내). 스코어 상승, 콤보 리셋 및 방향 전환.

🔴 MISS: 박자를 놓치거나 범위 밖에서 연타 시 라이프 1 차감, 콤보 리셋 및 방향 전환 실패.

게임 제어: 게임 플레이 도중 ESC 키를 눌러 언제든 안전하게 일시정지할 수 있습니다.

🎁 아이템 및 스테이지 기믹
🍎 일반 음식 (Food): 몸길이 1 증가, 200점 획득. (5개 섭취 시 스테이지가 상승하며 시각적 이펙트와 함께 난이도별 가변 장애물이 즉시 맵에 추가됩니다.)

🧪 생명 물약 (Potion): 라이프 1 회복 (최대 5개 제한).

🪙 보너스 코인 (Coin): 보너스 점수 500점 즉시 획득.

📑 [기술 보고서] 시스템 아키텍처 명세
1. 시스템 아키텍처 흐름
소프트웨어 공학의 MVC(Model-View-Controller) 디자인 패턴을 엄격히 준수했습니다. 특히 프론트엔드는 스테이지 업 트리거(stage_up_triggered)를 수신하여 독립적인 애니메이션을 재생하며, 게임 종료 또는 메인 화면에서 로컬/클라우드 데이터베이스를 동시에 병렬 호출합니다.

Plaintext
[프론트엔드: main_ui.py] ──(입력 시간 및 난이도 주입)──> [백엔드: backend_engine.py]
         │                                                   │
   (화면/동적 BGM)                                    (듀얼 데이터 로드)
         │                                                   │
         ▼                                                   ▼
  [Pygame GUI 화면] ──(로컬 데이터 읽기/쓰기)──> [data/highscore.json]
         │                                                   
         └───(REST API 비동기 통신: GET/POST)──> [Render.com 중앙 클라우드 서버]
💻 [개발자 가이드] 핵심 소스코드 해설
1. 1비트 비율 기반 어뷰징 방지 판정 알고리즘
소스 위치: backend_engine.py ➔ RhythmManager.__init__()

Python
# 난이도에 맞는 BPM 고정 및 1비트 소요 시간 계산
self.sec_per_beat = 60.0 / self.current_bpm

# 절대 시간이 아닌, 1비트 소요 시간에 대한 '비율(Ratio)'로 판정창 동적 할당
self.perfect_window = self.sec_per_beat * 0.15  # 15% 허용
self.good_window = self.sec_per_beat * 0.30     # 30% 허용
과거 고정된 시간(0.08초 등)으로 판정할 경우 BPM이 빨라질수록 비트 간격이 좁아져 아무렇게나 연타해도 판정을 통과하는 심각한 기획적 결함이 있었습니다. 이를 1비트 소요 시간에 비례하여 동적으로 좁아지도록 수학적으로 재설계하여 게임의 공정성을 확보했습니다.

2. 일시정지 해제 시 델타 타임(Delta Time) 보정
소스 위치: main_ui.py ➔ RhythmSnakeUI.handle_events()

Python
if label == "계속하기":
    if hasattr(self, 'pause_start_time'):
        # 일시정지 상태에 머물렀던 절대 시간을 계산
        pause_duration = time.time() - self.pause_start_time
        # 시스템의 시작 기준점을 일시정지 시간만큼 밀어내어 시간 폭주를 원천 차단
        self.game_start_time = getattr(self, 'game_start_time', time.time()) + pause_duration
        
    current_elapsed = self.get_elapsed_time()
    self.engine.last_beat_time = current_elapsed # 백엔드 비트 틱 강제 동기화
pygame.time.get_ticks()는 게임이 멈춰있어도 계속 흘러갑니다. 단순히 음악만 멈췄다가 재생하면 누적된 시간 오차 때문에 수십 개의 프레임이 한 번에 연산되어 게임이 튕기는 현상을 막기 위한 핵심 동기화 로직입니다.

🤖 AI 협업 및 프로그래밍 로그 (AI Collaboration Log)
본 프로젝트는 무분별한 소스코드 복사-붙여넣기를 지양하고, 설계자가 AI에게 명확한 제약 조건과 아키텍처 지침을 부여하며 단계별로 문제를 돌파해 낸 'AI 페어 프로그래밍의 표준 모범 사례'입니다.

1단계 (모듈화 독립 설계): UI 렌더링 요소와 데이터 물리 법칙을 완벽히 격리하는 백엔드 엔진 클래스 구조 유도.

2단계 (예외 처리 고도화): 런타임 중 발생한 매개변수 충돌 및 파일 경로 에러 로그를 분석하여 방어적 코딩 작성.

3단계 (클라우드 인프라 확장): 중앙 웹 서버 통신을 위한 REST API를 개설하고, 타임아웃 설정을 통한 네트워크 프리징 차단.

4단계 (기획 전면 수정 및 밸런싱): 절대 시간 판정의 한계(버튼 매싱)를 인지하고 AI와 논의하여 비율 기반 판정 알고리즘으로 전면 재설계, 동적 BGM 시스템 및 듀얼 리더보드 등 대규모 UI/UX 리팩토링 진행.

👥 팀원 및 역할 (Team Members)
메인 아키텍트 & 개발 총괄 (Back-end / Cloud Infrastructure): 박안석

프론트엔드 GUI 및 이벤트 인터럽트 제어 (Front-end): 박명원, 서민우

품질 보증 및 시스템 구현 명세서 작성 (QA / Documentation): 이우성, 김동우
