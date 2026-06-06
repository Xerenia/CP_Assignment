
# 🎮 비트 바이트 (Beat Byte)



> **비율 기반 리듬 판정 알고리즘과 클라우드/로컬 하이브리드 리더보드가 결합한 아케이드 스네이크 게임**

> 

> 본 프로젝트는 클래식 아케이드 게임인 스네이크(Snake)의 규칙을 뒤집어, 음악의 비트 타이밍에 맞춰 방향을 전환해야 하는 리듬 동기화 액션 퍼즐 게임입니다. 생성형 AI(Gemini 3.5, Cursor)와의 긴밀한 페어 프로그래밍(Pair Programming)을 통해 유기적인 MVC 아키텍처 설계, 실시간 외부 클라우드 서버 배포, 그리고 버튼 매싱(Button Mashing)을 차단하는 정교한 게임 밸런싱을 달성했습니다.



---



## 📌 목차 (Table of Contents)

1. [🌟 주요 특징 및 기술적 차별점](#-주요-특징-및-기술적-차별점-key-features)

2. [🛠️ 기술 스택](#️-기술-스택-tech-stack)

3. [📁 프로젝트 폴더 구조](#-프로젝트-폴더-구조-directory-structure)

4. [🚀 시작하기 및 실행 방법](#-시작하기-및-실행-방법-how-to-run)

5. [🕹️ 게임 플레이 및 판정 규칙](#-게임-플레이-및-판정-규칙-gameplay-rules)

6. [📑 [기술 보고서] 시스템 아키텍처 명세](#-기술-보고서-시스템-아키텍처-명세)

7. [💻 [개발자 가이드] 핵심 소스코드 해설](#-개발자-가이드-핵심-소스코드-해설)

8. [🤖 AI 협업 및 로그](#-ai-협업-및-프로그래밍-로그-ai-collaboration-log)

9. [👥 팀원 및 역할](#-팀원-및-역할-team-members)



---



## 🌟 주요 특징 및 기술적 차별점 (Key Features)



- **비율 기반 동적 리듬 판정 시스템 (Ratio-based Judgment)**

  - 절대적인 시간(예: 0.08초)이 아닌, 1비트 소요 시간에 대한 퍼센트 비율(PERFECT 15%, GOOD 30%)로 판정창(Window)을 동적 계산합니다.

  - 고난이도(160 BPM)에서 키보드를 무작정 연타하여 판정을 통과하는 어뷰징(Button Mashing)을 구조적으로 완벽히 차단했습니다.



- **온라인/오프라인 하이브리드 듀얼 리더보드 (REST API)**

  - 로컬 파일 저장을 넘어 외부 클라우드 플랫폼 **Render.com**에 파이썬 Flask 기반 중앙 웹 서버 배포 완료.

  - 게임 오버 시 클라이언트와 서버 간의 비동기 GET/POST REST API 통신을 통해 전 세계 플레이어의 실시간 상위 10등 순위판 정렬 및 동기화 렌더링.
 
  - 동시에 오프라인 환경을 대비한 로컬 백업 시스템(data/highscore.json)을 구축하여, 메인 화면에서 ONLINE RANKING과 LOCAL RANKING을 좌우 분할된 UI로 동시에 비교할 수 있습니다.



- **엔지니어링 기반의 방어적 코딩 (Robust Architecture)**

  - **에셋 폴백(Fallback) 시스템:** 이미지 및 사운드 리소스가 누락되거나 에러가 발생해도 게임이 크래시되지 않고 시스템 내장 기본 도형 렌더링으로 자동 대체 구동.

  - **네트워크 장애 방어:** 외부 서버 점검 또는 네트워크 단절 시 게임 멈춤(Freezing) 현상을 막기 위한 `3.0s Timeout` 설정 및 하이브리드 로컬 백업 시스템(`data/highscore.json`)으로의 자동 전환.

  - **자동 환경 인프라 구축:** 프로그램 구동 시 데이터 저장 폴더 (`data/`)가 없으면 런타임에서 자동으로 감지하여 개설하는 자가 복구형 입출력 로직 반영.



- **공간적 난이도 스케일링 및 타이머 동기화**

  - 스테이지가 올라갈 때 BPM을 강제로 높이는 대신, 유저가 선택한 난이도(EASY, NORMAL, HARD)에 따라 맵에 추가되는 장애물의 개수를 차등 부여(+1, +2, +3)하여 스네이크 게임 본연의 공간적 압박감을 극대화했습니다.

  - ESC 키를 통한 일시정지(Pause) 기능 구현 시 델타 타임(Delta Time) 보정 로직을 적용하여, 일시정지 해제 시 타이머가 폭주하는 치명적인 싱크 버그를 해결했습니다.



---



## 🛠️ 기술 스택 (Tech Stack)



- **Language:** Python 3.11 ~ 3.13

- **Client GUI / Audio Core:** Pygame 2.6.0+

- **Database & Serialization:** JSON Persistent Data Architecture

- **Web API Server:** Flask 3.0.3+ (Deployed on Render Cloud)

- **Asset Generation Engine:** Pillow (PIL) 10.3.0+



---



## 📁 프로젝트 폴더 구조 (Directory Structure)

```text
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
├── requirements.txt                 # 프로젝트 통합 의존성 환경 명세서
└── README.md                        # 본 프로젝트 매뉴얼 파일
```

---



## 🚀 시작하기 및 실행 방법 (How to Run)



### 1. 저장소 클론 및 폴더 이동

```bash

cd ~/Desktop

git clone https://github.com/Xerenia/CP_Assignment.git

cd CP_Assignment

```



### 2. 필수 의존성 라이브러리 일괄 설치

```bash

pip install -r requirements.txt

```



### 3. 메인 게임 클라이언트 실행

```bash

python main_ui.py

```



---



## 🕹️ 게임 플레이 방법 및 판정 규칙 (Gameplay Rules)



- **이동 방식:** 유저가 선택한 난이도의 고정 BPM(EASY 120, NORMAL 140, HARD 160) 박자에 맞춰 스스로 한 칸씩 전진합니다.

- **조작 및 판정:** 정박 타이밍에 맞춰 방향키 (`↑`, `↓`, `←`, `→`)를 누르면 박자 오차를 계산하여 판정을 내립니다.

  - 🟢 **PERFECT:** 박자와 완벽히 일치 (비트 시간의 15% 이내). 스코어 대폭 상승 및 방향 전환.

  - 🟡 **GOOD:** 미세한 오차 발생 (비트 시간의 30% 이내). 스코어 상승, 콤보 리셋 및 방향 전환.

  - 🔴 **MISS:** 박자를 놓치거나 무리하게 연타할 시 라이프(`LIVES`) 1 차감, 콤보 리셋, 방향 전환 실패.
 
- **게임 제어:** 게임 플레이 도중 ESC 키를 눌러 언제든 안전하게 일시정지할 수 있습니다.



### 🎁 아이템 종류

- 🍎 **일반 음식 (Food):** 몸길이 1 증가, 200점 획득. (5개 섭취 시 스테이지가 상승하며 시각적 이펙트와 함께 난이도별 가변 장애물이 즉시 맵에 추가됩니다.)

- 🧪 **생명 물약 (Potion):** 라이프 1 회복 (최대 5개 제한).

- 🪙 **보너스 코인 (Coin):** 보너스 점수 500점 즉시 획득.

### 🎁 아이템 및 스테이지 업 (Stage Up) 규칙
- 게임 내에 생성되는 **모든 종류의 아이템(일반 음식, 생명 물약, 보너스 코인)을 종류에 상관없이 누적 5개 섭취할 때마다** 다음 스테이지로 진입합니다.
- 스테이지 상승 시 화면 중앙에 `STAGE X START!` 시각 연출이 발생하며, 아래 명세표에 따라 **장애물 수량이 복리로 누적 가속 증가**하여 게임 영역을 압박합니다.

| 난이도 (BPM) | 1 ➔ 2 스테이지 진입 시 (기본 증가) | 이후 스테이지 증가 폭 공식 (복리 가속) |
| :--- | :--- | :--- |
| **EASY** (120) | **+2개** 증가 | `2 + (현재 Stage - 2)` 개씩 추가 생성 |
| **`NORMAL`** (140) | **+3개** 증가 | `3 + (현재 Stage - 2)` 개씩 추가 생성 |
| **HARD** (160) | **+4개** 증가 | `4 + (현재 Stage - 2)` 개씩 추가 생성 |

> *ex) HARD 모드 기준: 2스테이지 진입 시 +4개 ➔ 3스테이지 진입 시 +5개 ➔ 4스테이지 진입 시 +6개 추가 배치*

---



---



## 📑 [기술 보고서] 시스템 아키텍처 명세



### 1. 시스템 아키텍처 흐름

소프트웨어 공학의 MVC(Model-View-Controller) 디자인 패턴을 엄격히 준수했습니다. 특히 프론트엔드는 스테이지 업 트리거(stage_up_triggered)를 수신하여 독립적인 애니메이션을 재생하며, 게임 종료 또는 메인 화면에서 로컬/클라우드 데이터베이스를 동시에 병렬 호출합니다.



```text

[프론트엔드: main_ui.py] ──(입력 시간 및 난이도 주입)──> [백엔드: backend_engine.py]
         │                                                   │
   (화면/동적 BGM)                                    (듀얼 데이터 로드)
         │                                                   │
         ▼                                                   ▼
  [Pygame GUI 화면] ──(로컬 데이터 읽기/쓰기)──> [data/highscore.json]
         │                                                   
         └───(REST API 비동기 통신: GET/POST)──> [Render.com 중앙 클라우드 서버]

```



### 2. 핵심 파일별 세부 명세

- **`backend_engine.py` (Model):** 게임 규칙 알고리즘 제어 및 박자 판정, 데이터 직렬화(Serialization)를 전담합니다. 열거형(`Enum`)을 통한 상태 무결성을 보장하며 `deque` 자료구조로 뱀 몸통 좌표 관리 및 충돌을 감지합니다.

- **`main_ui.py` (View/Controller):** 하드웨어 이벤트 입출력 가로채기(Interrupt), 멀티미디어 렌더링을 제어합니다. 상태 머신 패턴을 도입하여 인게임, 닉네임 입력 팝업, 글로벌 리더보드 간의 화면 전환을 매끄럽게 연출합니다.

- **`server.py` (Cloud API):** 중앙 집중형 데이터 취합 및 정렬을 담당하는 Flask REST API 서버입니다. 외부 IP 개방(`0.0.0.0`) 및 리눅스 배포용 고성능 게이트웨이(`gunicorn`) 기반으로 가동 중입니다.



---



## 💻 [개발자 가이드] 핵심 소스코드 해설

### 1. 1비트 비율 기반 어뷰징 방지 판정 알고리즘
- **소스 위치:** `backend_engine.py` ➔ `RhythmManager.__init__()`


### 난이도에 맞는 BPM 고정 및 1비트 소요 시간 계산
self.sec_per_beat = 60.0 / self.current_bpm

### 절대 시간이 아닌, 1비트 소요 시간에 대한 '비율(Ratio)'로 판정창 동적 할당
self.perfect_window = self.sec_per_beat * 0.15  # 15% 허용
self.good_window = self.sec_per_beat * 0.30     # 30% 허용

과거 고정된 시간(0.08초 등)으로 판정할 경우 BPM이 빨라질수록 비트 간격이 좁아져 아무렇게나 연타해도 판정을 통과하는 심각한 기획적 결함이 있었습니다. 이를 1비트 소요 시간에 비례하여 동적으로 좁아지도록 수학적으로 재설계하여 게임의 공정성을 확보했습니다.

### 2. 누적 아이템 섭취 및 복리형 장애물 가속 계산 알고리즘
- **소스 위치:** `backend_engine.py` ➔ `GameEngine.check_item_consumption()`




### 아이템 종류에 관계없이 총 먹은 아이템 수 누적
self.total_items_eaten += 1

if self.total_items_eaten % 5 == 0:
    self.stage += 1
    self.stage_up_triggered = True  # UI 단 깜빡임 연출 트리거 활성화
    
    # 난이도별 초기 증가폭 설정 (EASY: 2, NORMAL: 3, HARD: 4)
    base_increment = {"EASY": 2, "NORMAL": 3, "HARD": 4}.get(self.current_difficulty, 3)
    
    # 스테이지가 올라갈수록 증가 폭 자체가 늘어나는 복리 가속 공식 적용
    acceleration = self.stage - 2
    final_obstacle_increment = base_increment + acceleration
    
    self.obstacle_count += final_obstacle_increment
    self.spawn_obstacles()  # 새 장애물 실시간 맵 배치





### 3. 일시정지 해제 시 델타 타임(Delta Time) 보정
- **소스 위치:** `main_ui.py` ➔ `RhythmSnakeUI.handle_events()`


if label == "계속하기":
    if hasattr(self, 'pause_start_time'):
        # 일시정지 상태에 머물렀던 절대 시간을 계산
        pause_duration = time.time() - self.pause_start_time
        # 시스템의 시작 기준점을 일시정지 시간만큼 밀어내어 시간 폭주를 원천 차단
        self.game_start_time = getattr(self, 'game_start_time', time.time()) + pause_duration
        
    current_elapsed = self.get_elapsed_time()
    self.engine.last_beat_time = current_elapsed # 백엔드 비트 틱 강제 동기화

pygame.time.get_ticks()는 게임이 멈춰있어도 계속 흘러갑니다. 단순히 음악만 멈췄다가 재생하면 누적된 시간 오차 때문에 수십 개의 프레임이 한 번에 연산되어 게임이 튕기는 현상을 막기 위한 핵심 동기화 로직입니다.




## 🤖 AI 협업 및 프로그래밍 로그 (AI Collaboration Log)



본 프로젝트는 무분별한 AI 소스코드 복사-붙여넣기를 지양하고, 시스템 설계자가 AI에게 명확한 객체지향 시스템 지침(System Instructions)을 바인딩한 뒤 단계별로 리팩토링 및 인프라 구축을 유도해 낸 **'AI 페어 프로그래밍의 표준 모범 사례'**입니다.



1. **1단계 (모듈화 독립 설계):** UI 드로잉 요소와 순수 데이터 물리 법칙을 완벽히 격리하는 백엔드 엔진 클래스 구조 유도.

2. **2단계 (예외 처리 고도화):** 런타임 테스트 중 발생한 변수 매개변수 충돌(`AttributeError`) 및 시간 오차 연산 로그를 AI에게 피드백하여 수정본 도출.

3. **3단계 (클라우드 인프라 확장):** 중앙 웹 서버 배포를 위해 Flask REST API 엔드포인트를 개설하고, `urllib.request` 타임아웃 설정을 통한 네트워크 프리징 차단 방어벽 설계 유도.

4. **4단계 (밸런싱):** 절대 시간 판정의 한계(버튼 매싱)를 인지하고 AI와 논의하여 비율 기반 판정 알고리즘으로 전면 재설계, 동적 BGM 시스템 및 듀얼 리더보드 등 대규모 UI/UX 리팩토링 진행.



---



## 👥 팀원 및 역할 (Team Members)



- **메인 아키텍트 & 개발 총괄 (Back-end / Cloud Infrastructure):** 박안석

- **프론트엔드 GUI 및 이벤트 인터럽트 제어 (Front-end):** 박명원, 서민우

- **품질 보증 및 시스템 구현 명세서 작성 (QA / Documentation):** 이우성, 김동우 

