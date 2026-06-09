import sys
import os
import pygame
import time
import random
import platform
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Dict, Any, List

from backend_engine import GameEngine, Direction, Judgment, GameState, ItemType

# ==========================================
# 1. 상수 및 설정 (Constants & Config)
# ==========================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 720  
GRID_SIZE = 30  
FPS = 60

COLORS = {
    "BACKGROUND": (25, 25, 35),
    "GRID_LINE": (40, 40, 50),
    "TEXT_WHITE": (240, 240, 240),
    "TEXT_GRAY": (150, 150, 150),
    "PERFECT": (0, 255, 0),
    "GOOD": (255, 255, 0),
    "MISS": (255, 0, 0),
    "POPUP_BG": (40, 40, 50),
    "TABLE_HEADER": (60, 60, 80),
    "TABLE_ROW": (45, 45, 55),
    "PRIMARY": (0, 255, 150),
    "FOOD_COIN": (255, 215, 0),    
    "FOOD_NORMAL": (255, 100, 100),  
    "FOOD_POTION": (100, 100, 255),  
    "SNAKE_HEAD": (0, 255, 150),
    "SNAKE_BODY": (0, 200, 100),
}

class UIScene(Enum):
    READY = auto()            
    COUNTDOWN = auto()        
    PLAYING = auto() 
    PAUSED = auto()         
    GAME_OVER_POPUP = auto()  
    LEADERBOARD = auto()      
    DIFFICULTY = auto()

# ==========================================
# 3. 메인 UI 클래스
# ==========================================
class RhythmSnakeUI:
    def __init__(self) -> None:
        pygame.init()
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
        except Exception as e:
            print(f"[경고] 오디오 초기화 실패: {e}")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("비트 바이트 (Rhythm Snake) - Official Client")
        self.clock = pygame.time.Clock()

        try:
            # 운영체제가 맥(Darwin)이면 애플 산돌 고딕(또는 애플 고딕), 윈도우면 맑은 고딕 사용
            os_font = "Apple SD Gothic Neo" if platform.system() == "Darwin" else "malgungothic"
            
            self.font_small = pygame.font.SysFont(os_font, 20, bold=True)
            self.font_main = pygame.font.SysFont(os_font, 24, bold=True)
            self.font_large = pygame.font.SysFont(os_font, 48, bold=True)
            self.font_title = pygame.font.SysFont(os_font, 36, bold=True)
            self.font_judgment = pygame.font.SysFont(os_font, 64, bold=True)
            self.font_card_title = pygame.font.SysFont(os_font, 42, bold=True)
        except Exception:
            # 만약 위 폰트도 없다면 시스템 기본 폰트로 폴백 (이 경우 한글이 깨질 수 있음)
            self.font_small = pygame.font.Font(None, 24)
            self.font_main = pygame.font.Font(None, 30)
            self.font_large = pygame.font.Font(None, 60)
            self.font_title = pygame.font.Font(None, 45)
            self.font_judgment = pygame.font.Font(None, 80)
            self.font_card_title = pygame.font.Font(None, 54)

        self.engine = GameEngine(grid_width=20, grid_height=20)

        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.background_surface: Optional[pygame.Surface] = None
        self._load_assets()

        self.current_scene: UIScene = UIScene.READY
        self.start_ticks: int = 0
        self.countdown_start_ticks: int = 0
        
        self.judgment_text: str = ""
        self.judgment_color: tuple[int, int, int] = COLORS["TEXT_WHITE"]
        self.judgment_type: str = ""
        self.judgment_start_time: float = -9999.0
        self.judgment_duration: float = 0.45
        
        self.show_stage_up_anim: bool = False
        self.stage_up_anim_start_time: float = 0.0
        
        self.player_name_input: str = ""
        
        # 💡 [요구사항 2] 온라인/로컬 순위표 데이터 분리
        self.online_leaderboard_data: List[Dict[str, Any]] = []
        self.local_leaderboard_data: List[Dict[str, Any]] = []
        
        self.ready_button_rects: Dict[str, pygame.Rect] = {}
        self.difficulty_card_rects: Dict[str, pygame.Rect] = {}
        self.selected_difficulty: str = "NORMAL"
        
        self.konami_sequence = [
            pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_b, pygame.K_a, pygame.K_s, pygame.K_t, pygame.K_a, pygame.K_r, pygame.K_t
        ]
        self.konami_input = []
        
        self.glow_max_alpha = 110
        self.glow_thickness = 110
        self.glow_decay_speed = 1.2
        self.show_howto_popup = False
        
    def _load_assets(self) -> None:
        try:
            base_dir = Path(__file__).resolve().parent
        except NameError:
            base_dir = Path.cwd()
            
        base_asset_dir = base_dir / "assets"
        base_bg_dir = base_dir / "assets-images"
        
        if not base_asset_dir.exists():
            fallback_path_1 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터프로그래밍\assets")
            fallback_path_2 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터 프로그래밍\assets")
            
            if fallback_path_1.exists(): base_asset_dir = fallback_path_1
            elif fallback_path_2.exists(): base_asset_dir = fallback_path_2

        print(f"[시스템] 에셋 로딩 경로: {base_asset_dir}")

        img_dir = base_asset_dir / "images"
        self.sound_dir: Path = base_asset_dir / "sounds"

        bg_candidates: list[Path] = []
        for ext in ("png", "jpg", "jpeg", "webp"):
            bg_candidates.append(base_bg_dir / f"background.{ext}")
        for ext in ("png", "jpg", "jpeg", "webp"):
            bg_candidates.append(img_dir / f"background.{ext}")

        for bg_path in bg_candidates:
            try:
                if bg_path.exists():
                    bg_img = pygame.image.load(str(bg_path)).convert()
                    self.background_surface = pygame.transform.smoothscale(bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    print(f"[시스템] 배경 이미지 로드 성공: {bg_path}")
                    break
            except Exception as e:
                print(f"[시스템 경고] 배경 이미지 로드 실패: {bg_path} ({e})")
         
        try:
            if (img_dir / "snake_head.png").exists(): self.images['head'] = pygame.image.load(str(img_dir / "snake_head.png")).convert_alpha()
            if (img_dir / "snake_body.png").exists(): self.images['body'] = pygame.image.load(str(img_dir / "snake_body.png")).convert_alpha()
            if (img_dir / "food_normal.png").exists(): self.images['food'] = pygame.image.load(str(img_dir / "food_normal.png")).convert_alpha()
            if (img_dir / "item_potion.png").exists(): self.images['potion'] = pygame.image.load(str(img_dir / "item_potion.png")).convert_alpha()
            if (img_dir / "item_coin.png").exists(): self.images['coin'] = pygame.image.load(str(img_dir / "item_coin.png")).convert_alpha()
            
            for key in self.images:
                self.images[key] = pygame.transform.scale(self.images[key], (GRID_SIZE, GRID_SIZE))
        except Exception as e:
            print(f"[시스템 경고] 이미지 파일 로드 실패: {e}")

        sfx_files = {"perfect": "perfect.wav", "good": "good.wav", "miss": "miss.wav", "gameover": "gameover.wav"}
        for key, filename in sfx_files.items():
            path = self.sound_dir / filename
            try:
                if path.exists():
                    self.sounds[key] = pygame.mixer.Sound(str(path))
                    self.sounds[key].set_volume(1.0)
                else:
                    self.sounds[key] = None
            except Exception:
                self.sounds[key] = None

    def play_dynamic_bgm(self) -> None:
        if not hasattr(self, 'sound_dir'):
            return

        bpm: int = int(self.engine.rhythm.current_bpm)
        track_num: int = random.randint(1, 2)
        bgm_filename: str = f"{bpm}_{track_num}.mp3"
        bgm_path: Path = self.sound_dir / bgm_filename

        try:
            if bgm_path.exists():
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                print(f"[시스템] 동적 BGM 재생 시작: {bgm_filename}")
            else:
                print(f"[경고] 해당 난이도의 동적 BGM 파일을 찾을 수 없습니다: {bgm_path}")
        except Exception as e:
            print(f"[경고] BGM 스트리밍 로드 실패: {e}")

    def play_sound(self, sound_key: str) -> None:
        sound = self.sounds.get(sound_key)
        if sound:
            channel = pygame.mixer.find_channel()
            if channel: channel.play(sound)
            else: sound.play()

    def get_elapsed_time(self) -> float:
        return (pygame.time.get_ticks() - self.start_ticks) / 1000.0

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_howto_popup:
                    self.show_howto_popup = False
                    return
                        
                if self.current_scene == UIScene.PAUSED:
                    for label, rect in self.pause_button_rects.items():
                        if rect.collidepoint(event.pos):
                            if label == "계속하기":
                                if hasattr(self, 'pause_start_time'):
                                    pause_duration = time.time() - self.pause_start_time
                                    self.game_start_time = getattr(self, 'game_start_time', time.time()) + pause_duration
                                                            
                                current_elapsed = self.get_elapsed_time()
                                self.engine.last_beat_time = current_elapsed
                                                            
                                self.current_scene = UIScene.PLAYING
                                try: pygame.mixer.music.unpause()
                                except: pass
                                
                            elif label == "재도전":
                                self.engine.reset_game(self.selected_difficulty)
                                self.game_start_time = time.time()      
                                self.start_ticks = pygame.time.get_ticks()
                                self.current_scene = UIScene.PLAYING
                                self.play_dynamic_bgm()
                                
                            elif label == "메인 화면":
                                self.engine.reset_game(self.selected_difficulty)
                                self.current_scene = UIScene.READY
                                try: pygame.mixer.music.stop()
                                except: pass
                                return True
            
                if self.current_scene == UIScene.READY:
                    self._handle_ready_button_click(event.pos)
                elif self.current_scene == UIScene.DIFFICULTY:
                    self._handle_difficulty_card_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if self.current_scene == UIScene.READY:
                    self._check_konami_code(event.key)
                    if event.key == pygame.K_SPACE:
                        self.current_scene = UIScene.COUNTDOWN
                        self.countdown_start_ticks = pygame.time.get_ticks()

                elif self.current_scene == UIScene.PLAYING:
                    direction_map = {
                        pygame.K_UP: Direction.UP, pygame.K_DOWN: Direction.DOWN,
                        pygame.K_LEFT: Direction.LEFT, pygame.K_RIGHT: Direction.RIGHT
                    }
                    if event.key in direction_map:
                        current_time = self.get_elapsed_time()
                        judgment = self.engine.process_player_input(direction_map[event.key], current_time)
                        self._process_judgment(judgment, current_time)
                    elif event.key == pygame.K_ESCAPE:
                        self.current_scene = UIScene.PAUSED
                        self.pause_start_time = time.time()
                        try: pygame.mixer.music.pause()
                        except Exception: pass

                elif self.current_scene == UIScene.GAME_OVER_POPUP:
                    if event.key == pygame.K_RETURN and len(self.player_name_input) > 0:
                        # 💡 [요구사항 2] 게임 오버 시에는 점수 등록을 위해 True 전달
                        self._transition_to_leaderboard(from_game_over=True)
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name_input = self.player_name_input[:-1]
                    else:
                        if event.unicode.isalnum() and len(self.player_name_input) < 8:
                            self.player_name_input += event.unicode.upper()

                elif self.current_scene == UIScene.LEADERBOARD:
                    # 💡 [요구사항 3] 순위표 화면에서 ESC 키로도 메인 화면 복귀 가능
                    if event.key in (pygame.K_r, pygame.K_ESCAPE):
                        self.current_scene = UIScene.READY
                        self.player_name_input = ""
                        try: pygame.mixer.music.stop()
                        except Exception: pass
                elif self.current_scene == UIScene.DIFFICULTY:
                    if event.key == pygame.K_ESCAPE:
                        self.current_scene = UIScene.READY
        return True

    def _handle_ready_button_click(self, mouse_pos: tuple[int, int]) -> None:
        for label, rect in self.ready_button_rects.items():
            if rect.collidepoint(mouse_pos):
                if label == "게임 방법":
                    self.show_howto_popup = True
                    break
                # 💡 [요구사항 1] 순위표 버튼 클릭 시 점수 등록 없이 조회만 수행
                if label == "순위표":
                    self._transition_to_leaderboard(from_game_over=False)
                    break
                if label == "난이도 설정":
                    self.current_scene = UIScene.DIFFICULTY
                    break
                if label == "게임 종료":
                    pygame.quit()
                    sys.exit()
                break

    def _check_konami_code(self, key: int) -> None:
        self.konami_input.append(key)
        if len(self.konami_input) > len(self.konami_sequence):
            self.konami_input.pop(0)

        if self.konami_input == self.konami_sequence:
            self.engine.invincible_mode = True
            self.konami_input.clear()
            print("[EASTER EGG] 무적 모드 활성화")

    def _handle_difficulty_card_click(self, mouse_pos: tuple[int, int]) -> None:
        for key, rect in self.difficulty_card_rects.items():
            if rect.collidepoint(mouse_pos):
                self.selected_difficulty = key
                self.current_scene = UIScene.READY
                break

    def _process_judgment(self, judgment: Judgment, current_time: float) -> None:
        if judgment == Judgment.IGNORED:
            return

        self.judgment_start_time = current_time

        if judgment == Judgment.PERFECT:
            self.judgment_text = "PERFECT!"
            self.judgment_color = COLORS["PERFECT"]
            self.judgment_type = "PERFECT"
            self.play_sound("perfect")

        elif judgment == Judgment.GOOD:
            self.judgment_text = "GOOD"
            self.judgment_color = COLORS["GOOD"]
            self.judgment_type = "GOOD"
            self.play_sound("good")

        elif judgment == Judgment.MISS:
            self.judgment_text = "MISS!"
            self.judgment_color = COLORS["MISS"]
            self.judgment_type = "MISS"
            self.play_sound("miss")

    def _transition_to_leaderboard(self, from_game_over: bool = True) -> None:
        """
        💡 [요구사항 2] 범용적인 순위표 전환 메서드
        from_game_over가 True일 때만 점수를 서버 및 로컬에 등록합니다.
        """
        self._draw_loading_screen()
        
        if from_game_over:
            self.engine.send_score_to_server(self.player_name_input)
            self.engine.register_local_score(self.player_name_input)
            
        # 온라인과 로컬 데이터를 각각 분리하여 저장
        self.online_leaderboard_data = self.engine.fetch_server_leaderboard()
        self.local_leaderboard_data = self.engine.local_leaderboard
        
        self.current_scene = UIScene.LEADERBOARD

    def update(self) -> None:
        if self.current_scene == UIScene.COUNTDOWN:
            elapsed_countdown = (pygame.time.get_ticks() - self.countdown_start_ticks) / 1000.0
            
            if elapsed_countdown >= 3.0:
                self.current_scene = UIScene.PLAYING
                self.engine.reset_game(self.selected_difficulty)  
                self.start_ticks = pygame.time.get_ticks()  
                self.play_dynamic_bgm()

        elif self.current_scene == UIScene.PLAYING:
            current_time = self.get_elapsed_time()
            self.engine.update(current_time)

            if self.engine.stage_up_triggered:
                self.show_stage_up_anim = True
                self.stage_up_anim_start_time = current_time
                self.engine.stage_up_triggered = False

            if self.engine.state == GameState.GAME_OVER:
                self.current_scene = UIScene.GAME_OVER_POPUP
                try: pygame.mixer.music.fadeout(1000)
                except Exception: pass
                self.play_sound("gameover")

    def draw(self) -> None:
        if self.background_surface:
            self.screen.blit(self.background_surface, (0, 0))
        else:
            self.screen.fill(COLORS["BACKGROUND"])
        
        if self.current_scene == UIScene.READY:
            self._draw_ready_screen()
        elif self.current_scene == UIScene.DIFFICULTY:
            self._draw_difficulty_screen()
        elif self.current_scene == UIScene.COUNTDOWN:
            self._draw_game_board() 
            self._draw_beat_glow()
            self._draw_countdown_screen()
        elif self.current_scene in (UIScene.PLAYING, UIScene.PAUSED, UIScene.GAME_OVER_POPUP):
            self._draw_game_board()
            if self.current_scene == UIScene.PLAYING:
                self._draw_beat_glow()
            elif self.current_scene == UIScene.PAUSED:
                self._draw_pause_menu()
            
        if self.current_scene == UIScene.GAME_OVER_POPUP:
            self._draw_game_over_popup()
        elif self.current_scene == UIScene.LEADERBOARD:
            self._draw_leaderboard()
            
        pygame.display.flip()

    def _draw_ready_screen(self) -> None:
        title_text = "RHYTMN SNAKE"
        prompt_text = "Play space to start"

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font_main.render(prompt_text, True, COLORS["TEXT_WHITE"])
            prompt_h = prompt_surf.get_height()
        title_surf = self.font_large.render(title_text, True, COLORS["PERFECT"])
        title_h = title_surf.get_height()
        title_margin_top = title_h * 2
        title_center_y = int(title_margin_top + (title_h / 2))
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, title_center_y)))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font_main.render(prompt_text, True, COLORS["TEXT_WHITE"])
            prompt_h = prompt_surf.get_height()
            prompt_margin_bottom = prompt_h
            prompt_center_y = int(WINDOW_HEIGHT - prompt_margin_bottom - (prompt_h / 2))
            self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, prompt_center_y)))

        # 💡 [요구사항 1] 순위표 버튼 추가 (총 4개)
        labels = ["게임 방법", "순위표", "난이도 설정", "게임 종료"]
        button_w = 320
        button_h = 56
        gap = 16

        total_h = button_h * len(labels) + gap * (len(labels) - 1)
        center_x = WINDOW_WIDTH // 2
        center_y = (WINDOW_HEIGHT // 2) + 80
        start_y = int(center_y - total_h / 2)

        self.ready_button_rects = {}
        self.pause_button_rects = {}

        mouse_pos = pygame.mouse.get_pos()
        for i, label in enumerate(labels):
            rect = pygame.Rect(0, 0, button_w, button_h)
            rect.center = (center_x, start_y + i * (button_h + gap) + button_h // 2)
            self.ready_button_rects[label] = rect

            is_hover = rect.collidepoint(mouse_pos)
            bg_color = (70, 70, 95) if is_hover else (55, 55, 75)
            border_color = COLORS["TEXT_WHITE"] if is_hover else COLORS["TEXT_GRAY"]
            
            button_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
            button_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(button_surface, (*bg_color, 179), button_surface.get_rect(), border_radius=10)
            self.screen.blit(button_surface, rect.topleft)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)

            text_surf = self.font_main.render(label, True, COLORS["TEXT_WHITE"])
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        if self.engine.invincible_mode:
            difficulty_text = "난이도: GOD MODE"
        else:
            difficulty_text = f"난이도: {self.selected_difficulty}"

        diff_surf = self.font_small.render(difficulty_text, True, COLORS["TEXT_GRAY"])
        self.screen.blit(diff_surf, diff_surf.get_rect(center=(WINDOW_WIDTH // 2, center_y + total_h // 2 + 50)))
        
        if self.show_howto_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))

            popup_rect = pygame.Rect(0, 0, 520, 380)
            popup_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.rect(self.screen, COLORS["POPUP_BG"], popup_rect, border_radius=15)
            pygame.draw.rect(self.screen, COLORS["PERFECT"], popup_rect, width=3, border_radius=15)

            title = self.font_large.render("게임 방법", True, COLORS["PERFECT"])
            self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 40)))

            instructions = [
                "1. 음악 비트에 맞춰 타이밍을 맞추세요!",
                "2. 방향키(↑, ↓, ←, →)를 눌러 뱀을 움직입니다.",
                "3. PERFECT / GOOD 판정 시에만 방향이 바뀝니다.",
                "4. 음식을 먹어 점수를 올리고 몸집을 키우세요.",
                "5. 장애물이나 벽, 자신의 몸에 부딪히면 GAME OVER!",
                "6. ESC 키를 누르면 게임을 일시정지할 수 있습니다.",
                "",
                "- 화면을 클릭하면 대기실로 돌아갑니다 -"
            ]

            for idx, text in enumerate(instructions):
                color = COLORS["TEXT_WHITE"] if idx < 6 else COLORS["TEXT_GRAY"]
                inst_surf = self.font_small.render(text, True, color)
                self.screen.blit(inst_surf, inst_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 100 + idx * 30)))

    def _draw_difficulty_screen(self) -> None:
        self.difficulty_card_rects = {}

        title = "난이도 선택"
        title_surf = self.font_large.render(title, True, (240, 240, 255))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 90))

        bar_padding_x = 60
        bar_padding_y = 18
        bar_rect = pygame.Rect(0, 0, title_rect.width + bar_padding_x * 2, title_rect.height + bar_padding_y * 2)
        bar_rect.center = title_rect.center

        bar_surface = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_surface, (90, 60, 140, 120), bar_surface.get_rect(), border_radius=14)
        pygame.draw.rect(bar_surface, (170, 120, 255, 200), bar_surface.get_rect(), width=3, border_radius=14)
        self.screen.blit(bar_surface, bar_rect.topleft)
        self.screen.blit(title_surf, title_rect)

        cards = [
            ("EASY",   (80, 255, 210), 120, "여유로움", 1),
            ("NORMAL", (255, 220, 90), 140, "보통",     2),
            ("HARD",   (255, 120, 140),160, "까다로움", 3),
        ]

        card_w = 210
        card_h = 420
        gap = 45
        total_w = card_w * 3 + gap * 2
        start_x = (WINDOW_WIDTH - total_w) // 2
        top_y = 160

        mouse_pos = pygame.mouse.get_pos()
        for idx, (name, accent, bpm, desc, stars) in enumerate(cards):
            rect = pygame.Rect(start_x + idx * (card_w + gap), top_y, card_w, card_h)
            self.difficulty_card_rects[name] = rect

            hover = rect.collidepoint(mouse_pos)
            selected = (self.selected_difficulty == name)

            card_surface = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surface, (10, 10, 20, 160), card_surface.get_rect(), border_radius=18)

            border_alpha = 255 if (hover or selected) else 190
            pygame.draw.rect(card_surface, (*accent, border_alpha), card_surface.get_rect(), width=4, border_radius=18)

            name_surf = self.font_card_title.render(name, True, accent)
            card_surface.blit(name_surf, name_surf.get_rect(center=(card_w // 2, 75)))

            star_text = "★" * stars
            star_surf = self.font_main.render(star_text, True, accent)
            card_surface.blit(star_surf, star_surf.get_rect(center=(card_w // 2, 150)))

            bpm_left = self.font_main.render("BPM", True, COLORS["TEXT_WHITE"])
            bpm_val = self.font_large.render(str(bpm), True, accent)
            card_surface.blit(bpm_left, bpm_left.get_rect(midleft=(40, 250)))
            card_surface.blit(bpm_val, bpm_val.get_rect(midleft=(95, 252)))

            sub1 = self.font_small.render("판정 기준", True, COLORS["TEXT_GRAY"])
            sub2 = self.font_main.render(desc, True, accent)
            card_surface.blit(sub1, sub1.get_rect(center=(card_w // 2, 330)))
            card_surface.blit(sub2, sub2.get_rect(center=(card_w // 2, 370)))

            self.screen.blit(card_surface, rect.topleft)

    def _draw_countdown_screen(self) -> None:
        elapsed = (pygame.time.get_ticks() - self.countdown_start_ticks) / 1000.0
        remain = max(1, 3 - int(elapsed))
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))
        
        count_surf = self.font_judgment.render(str(remain), True, COLORS["FOOD_COIN"])
        self.screen.blit(count_surf, count_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

    def _draw_pause_menu(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        box_width = 320
        box_height = 320

        box_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - box_width // 2,
            WINDOW_HEIGHT // 2 - box_height // 2,
            box_width,
            box_height
        )

        pygame.draw.rect(self.screen, (28, 30, 36), box_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["PRIMARY"], box_rect, width=3, border_radius=16)

        title_surf = self.font_title.render("Pause", True, COLORS["TEXT_WHITE"])
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, box_rect.top + 45)))

        self.pause_button_rects.clear()
        buttons = ["계속하기", "재도전", "메인 화면"]

        for i, label in enumerate(buttons):
            btn_rect = pygame.Rect(box_rect.centerx - 100, box_rect.top + 90 + i * 70, 200, 50)
            hovered = btn_rect.collidepoint(pygame.mouse.get_pos())
            color = COLORS["PRIMARY"] if hovered else (50, 55, 65)

            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
            text_surf = self.font_small.render(label, True, COLORS["TEXT_WHITE"])
            self.screen.blit(text_surf, text_surf.get_rect(center=btn_rect.center))
            self.pause_button_rects[label] = btn_rect  

    def _draw_beat_glow(self) -> None:
        if self.current_scene not in (UIScene.PLAYING, UIScene.COUNTDOWN):
            return

        sec_per_beat = self.engine.rhythm.sec_per_beat
        current_time = self.get_elapsed_time()
        beat_progress = (current_time % sec_per_beat) / sec_per_beat

        glow_strength = max(0.0, 1.0 - (beat_progress * self.glow_decay_speed))
        if glow_strength <= 0:
            return

        glow_colors = {
            "EASY": (80, 255, 210),
            "NORMAL": (255, 220, 90),
            "HARD": (255, 120, 140)
        }
        glow_color = glow_colors.get(self.selected_difficulty, (255, 220, 90))
        max_alpha = int(self.glow_max_alpha * glow_strength)

        glow_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        layers = 14

        for i in range(layers):
            progress = i / layers
            alpha = int(max_alpha * (1.0 - progress) ** 2)
            inset = int(progress * self.glow_thickness)

            pygame.draw.rect(
                glow_surface,
                (*glow_color, alpha),
                (inset, inset, WINDOW_WIDTH - inset * 2, WINDOW_HEIGHT - inset * 2),
                width=8
            )

        self.screen.blit(glow_surface, (0, 0))     

    def _draw_game_board(self) -> None:
        game_area_width = self.engine.grid_width * GRID_SIZE
        game_area_height = self.engine.grid_height * GRID_SIZE
        offset_x = (WINDOW_WIDTH - game_area_width) // 2
        offset_y = 40

        pygame.draw.rect(self.screen, (15, 15, 22), (offset_x, offset_y, game_area_width, game_area_height))
        
        for x in range(self.engine.grid_width + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (offset_x + x * GRID_SIZE, offset_y), (offset_x + x * GRID_SIZE, offset_y + game_area_height))
        for y in range(self.engine.grid_height + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (offset_x, offset_y + y * GRID_SIZE), (offset_x + game_area_width, offset_y + y * GRID_SIZE))
            
        for ox, oy in self.engine.obstacles:
            rect = pygame.Rect(offset_x + ox * GRID_SIZE, offset_y + oy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, (120, 120, 130), rect.inflate(-4, -4), border_radius=6)
            
        for item in self.engine.items:
            ix, iy = item.position
            pos_rect = pygame.Rect(offset_x + ix * GRID_SIZE, offset_y + iy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            img = None
            if item.item_type == ItemType.NORMAL_FOOD: img = self.images.get('food')
            elif item.item_type == ItemType.LIFE_POTION: img = self.images.get('potion')
            elif item.item_type == ItemType.BONUS_COIN: img = self.images.get('coin')
            
            if img:
                self.screen.blit(img, pos_rect)
            else:
                color = COLORS["FOOD_NORMAL"]
                if item.item_type == ItemType.LIFE_POTION: color = COLORS["FOOD_POTION"]
                elif item.item_type == ItemType.BONUS_COIN: color = COLORS["FOOD_COIN"]
                pygame.draw.circle(self.screen, color, pos_rect.center, GRID_SIZE // 2 - 2)

        for i, (sx, sy) in enumerate(self.engine.snake.body):
            pos_rect = pygame.Rect(offset_x + sx * GRID_SIZE, offset_y + sy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            img = self.images.get('head') if i == 0 else self.images.get('body')
            if img:
                self.screen.blit(img, pos_rect)
            else:
                color = COLORS["SNAKE_HEAD"] if i == 0 else COLORS["SNAKE_BODY"]
                pygame.draw.rect(self.screen, color, pos_rect.inflate(-2, -2), border_radius=4)

        ui_top = offset_y + game_area_height + 15
        
        ui_text = f"STAGE: {self.engine.stage}    SCORE: {self.engine.score}    COMBO: {self.engine.combo}"
        self.screen.blit(self.font_main.render(ui_text, True, COLORS["TEXT_WHITE"]), (offset_x, ui_top))
        
        lives_text = self.font_main.render("LIVES:", True, COLORS["TEXT_WHITE"])
        self.screen.blit(lives_text, (offset_x, ui_top + 30))

        heart_size = 8
        heart_gap = 12

        for i in range(max(0, self.engine.lives)):
            x = offset_x + lives_text.get_width() + 15 + i * (heart_size + heart_gap)
            y = ui_top + 44

            pygame.draw.circle(self.screen, (255, 70, 90), (x, y), heart_size // 2)
            pygame.draw.circle(self.screen, (255, 70, 90), (x + heart_size, y), heart_size // 2)
            pygame.draw.polygon(
                self.screen,
                (255, 70, 90),
                [(x - heart_size // 2, y), (x + heart_size * 1.5, y), (x + heart_size // 2, y + heart_size * 1.6)]
            )

        bpm_surf = self.font_main.render(f"BPM: {int(self.engine.rhythm.current_bpm)}", True, COLORS["PERFECT"])
        self.screen.blit(bpm_surf, (offset_x + game_area_width - bpm_surf.get_width(), ui_top))

        if self.current_scene == UIScene.PLAYING and self.judgment_text:
            current_time = self.get_elapsed_time()
            elapsed = current_time - self.judgment_start_time

            if elapsed < 0:
                elapsed = 0

            if elapsed >= self.judgment_duration:
                self.judgment_text = ""
                self.judgment_type = ""
            else:
                progress = max(0.0, min(elapsed / self.judgment_duration, 1.0))
                alpha = int(255 * (1.0 - progress))
                center_x = WINDOW_WIDTH // 2
                center_y = offset_y + game_area_height // 2

                if self.judgment_type == "PERFECT":
                    pop_scale = 0.85 + 0.35 * (1 - min(progress * 4, 1))
                    y_offset = int(progress * -35)
                    font_size = int(64 * pop_scale)
                    font = pygame.font.SysFont("malgungothic", font_size, bold=True)
                    text_surf = font.render(self.judgment_text, True, self.judgment_color).convert_alpha()
                    text_surf.set_alpha(alpha)
                    self.screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y + y_offset)))

                elif self.judgment_type == "GOOD":
                    pop_scale = 0.90 + 0.18 * (1 - min(progress * 4, 1))
                    y_offset = int(progress * -22)
                    font_size = int(56 * pop_scale)
                    font = pygame.font.SysFont("malgungothic", font_size, bold=True)
                    text_surf = font.render(self.judgment_text, True, self.judgment_color).convert_alpha()
                    text_surf.set_alpha(alpha)
                    self.screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y + y_offset)))

                elif self.judgment_type == "MISS":
                    pop_scale = 0.90 + 0.22 * (1 - min(progress * 4, 1))
                    shake = int(10 * (1 - progress) * (-1 if int(progress * 30) % 2 == 0 else 1))
                    y_offset = int(progress * 45)
                    font_size = int(58 * pop_scale)
                    font = pygame.font.SysFont("malgungothic", font_size, bold=True)
                    text_surf = font.render(self.judgment_text, True, self.judgment_color).convert_alpha()
                    text_surf.set_alpha(alpha)
                    self.screen.blit(text_surf, text_surf.get_rect(center=(center_x + shake, center_y + y_offset)))

        if self.show_stage_up_anim:
            current_time = self.get_elapsed_time()
            elapsed = current_time - self.stage_up_anim_start_time
            if elapsed < 1.5:
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    stage_text = f"STAGE {self.engine.stage} START!"
                    stage_surf = self.font_large.render(stage_text, True, COLORS["FOOD_COIN"])
                    center_x = WINDOW_WIDTH // 2
                    center_y = WINDOW_HEIGHT // 2
                    self.screen.blit(stage_surf, stage_surf.get_rect(center=(center_x, center_y)))
            else:
                self.show_stage_up_anim = False

    def _draw_game_over_popup(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(0, 0, 450, 300)
        popup_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, COLORS["POPUP_BG"], popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["TEXT_WHITE"], popup_rect, width=3, border_radius=15)

        go_surf = self.font_large.render("GAME OVER", True, COLORS["MISS"])
        self.screen.blit(go_surf, go_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 50)))

        score_surf = self.font_main.render(f"Final Score: {self.engine.score}", True, COLORS["PERFECT"])
        self.screen.blit(score_surf, score_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 110)))

        prompt_surf = self.font_small.render("Enter Nickname (Max 8) and press ENTER", True, COLORS["TEXT_GRAY"])
        self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 160)))

        input_rect = pygame.Rect(0, 0, 250, 50)
        input_rect.center = (WINDOW_WIDTH // 2, popup_rect.top + 220)
        pygame.draw.rect(self.screen, (20, 20, 30), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["TEXT_GRAY"], input_rect, width=2, border_radius=8)

        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        display_text = self.player_name_input + ("|" if cursor_visible else "")
        name_surf = self.font_main.render(display_text, True, COLORS["TEXT_WHITE"])
        self.screen.blit(name_surf, name_surf.get_rect(center=input_rect.center))

    def _draw_loading_screen(self) -> None:
        loading_surf = self.font_main.render("Connecting to Render Server...", True, COLORS["GOOD"])
        self.screen.blit(loading_surf, loading_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180)))
        pygame.display.flip()

    def _draw_leaderboard(self) -> None:
        """
        💡 [요구사항 3] 듀얼 순위표 UI 디자인 (좌: 온라인, 우: 로컬)
        """
        title_surf = self.font_large.render("LEADERBOARD", True, COLORS["PERFECT"])
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 50)))

        table_width = 360
        row_height = 35
        start_y = 140

        # -------------------------------------------------
        # 1. ONLINE RANKING (왼쪽 표)
        # -------------------------------------------------
        online_start_x = 20
        online_title = self.font_main.render("ONLINE RANKING", True, COLORS["FOOD_COIN"])
        self.screen.blit(online_title, online_title.get_rect(center=(online_start_x + table_width // 2, start_y - 20)))
        
        pygame.draw.rect(self.screen, COLORS["TABLE_HEADER"], (online_start_x, start_y, table_width, row_height))
        headers = [("RANK", online_start_x + 40), ("NAME", online_start_x + 180), ("SCORE", online_start_x + 300)]
        for text, cx in headers:
            h_surf = self.font_small.render(text, True, COLORS["TEXT_WHITE"])
            self.screen.blit(h_surf, h_surf.get_rect(center=(cx, start_y + row_height // 2)))

        for i, data in enumerate(self.online_leaderboard_data[:10]):
            y_pos = start_y + row_height + (i * row_height)
            bg_color = COLORS["TABLE_ROW"] if i % 2 == 0 else COLORS["BACKGROUND"]
            pygame.draw.rect(self.screen, bg_color, (online_start_x, y_pos, table_width, row_height))

            rank_color = COLORS["TEXT_WHITE"]
            if i == 0: rank_color = COLORS["FOOD_COIN"]
            elif i == 1: rank_color = (192, 192, 192)
            elif i == 2: rank_color = (205, 127, 50)

            rank_surf = self.font_small.render(f"#{i+1}", True, rank_color)
            name_surf = self.font_small.render(str(data.get("name", "UNKNOWN")), True, COLORS["TEXT_WHITE"])
            score_surf = self.font_small.render(str(data.get("score", 0)), True, COLORS["PERFECT"])

            self.screen.blit(rank_surf, rank_surf.get_rect(center=(online_start_x + 40, y_pos + row_height // 2)))
            self.screen.blit(name_surf, name_surf.get_rect(center=(online_start_x + 180, y_pos + row_height // 2)))
            self.screen.blit(score_surf, score_surf.get_rect(center=(online_start_x + 300, y_pos + row_height // 2)))

        # -------------------------------------------------
        # 2. LOCAL RANKING (오른쪽 표)
        # -------------------------------------------------
        local_start_x = 420
        local_title = self.font_main.render("LOCAL RANKING", True, COLORS["PRIMARY"])
        self.screen.blit(local_title, local_title.get_rect(center=(local_start_x + table_width // 2, start_y - 20)))
        
        pygame.draw.rect(self.screen, COLORS["TABLE_HEADER"], (local_start_x, start_y, table_width, row_height))
        headers_local = [("RANK", local_start_x + 40), ("NAME", local_start_x + 180), ("SCORE", local_start_x + 300)]
        for text, cx in headers_local:
            h_surf = self.font_small.render(text, True, COLORS["TEXT_WHITE"])
            self.screen.blit(h_surf, h_surf.get_rect(center=(cx, start_y + row_height // 2)))

        for i, data in enumerate(self.local_leaderboard_data[:10]):
            y_pos = start_y + row_height + (i * row_height)
            bg_color = COLORS["TABLE_ROW"] if i % 2 == 0 else COLORS["BACKGROUND"]
            pygame.draw.rect(self.screen, bg_color, (local_start_x, y_pos, table_width, row_height))

            rank_color = COLORS["TEXT_WHITE"]
            if i == 0: rank_color = COLORS["FOOD_COIN"]
            elif i == 1: rank_color = (192, 192, 192)
            elif i == 2: rank_color = (205, 127, 50)

            rank_surf = self.font_small.render(f"#{i+1}", True, rank_color)
            name_surf = self.font_small.render(str(data.get("name", "UNKNOWN")), True, COLORS["TEXT_WHITE"])
            score_surf = self.font_small.render(str(data.get("score", 0)), True, COLORS["PERFECT"])

            self.screen.blit(rank_surf, rank_surf.get_rect(center=(local_start_x + 40, y_pos + row_height // 2)))
            self.screen.blit(name_surf, name_surf.get_rect(center=(local_start_x + 180, y_pos + row_height // 2)))
            self.screen.blit(score_surf, score_surf.get_rect(center=(local_start_x + 300, y_pos + row_height // 2)))

        # -------------------------------------------------
        # 하단 안내 문구
        # -------------------------------------------------
        if (pygame.time.get_ticks() // 600) % 2 == 0:
            restart_surf = self.font_main.render("Press 'R' or 'ESC' to Return", True, COLORS["GOOD"])
            self.screen.blit(restart_surf, restart_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))

    def run(self) -> None:
        running = True
        while running:
            if self.handle_events() == False:
                running = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            print("오디오 장치를 찾을 수 없습니다.")
            
        app = RhythmSnakeUI()
        app.run()
    except Exception as e:
        import traceback
        print(f"게임 실행 중 치명적 오류 발생:\n{e}")
        traceback.print_exc()
        pygame.quit()
