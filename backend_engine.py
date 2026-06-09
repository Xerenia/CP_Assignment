import json
import random
import urllib.request
import urllib.error
from enum import Enum, auto
from collections import deque
from pathlib import Path
from typing import Optional, Any

# ==========================================
# 1. 열거형 (Enums) 및 데이터 구조
# ==========================================
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Judgment(Enum):
    PERFECT = "PERFECT"
    GOOD = "GOOD"
    MISS = "MISS"
    IGNORED = "IGNORED"

class GameState(Enum):
    READY = "READY"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"

class ItemType(Enum):
    NORMAL_FOOD = auto()
    LIFE_POTION = auto()
    BONUS_COIN = auto()

# ==========================================
# 2. Item 및 Snake, RhythmManager 클래스
# ==========================================
class Item:
    def __init__(self, x: int, y: int, item_type: ItemType):
        self.x = x
        self.y = y
        self.item_type = item_type

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

class Snake:
    def __init__(self, start_pos: tuple[int, int], initial_length: int = 3):
        self.body: deque[tuple[int, int]] = deque()
        self.direction: Direction = Direction.RIGHT
        self.last_moved_direction: Direction = Direction.RIGHT
        self._grow_pending: int = 0
        for i in range(initial_length):
            self.body.append((start_pos[0] - i, start_pos[1]))

    def change_direction(self, new_direction: Direction) -> None:
        opposite_directions = {
            Direction.UP: Direction.DOWN, Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT, Direction.RIGHT: Direction.LEFT
        }
        if opposite_directions[self.last_moved_direction] != new_direction:
            self.direction = new_direction

    def move(self) -> None:
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        self.body.appendleft((head_x + dx, head_y + dy))
        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.body.pop()
        self.last_moved_direction = self.direction

    def grow(self, amount: int = 1) -> None:
        self._grow_pending += amount

    def get_occupied_positions(self) -> set[tuple[int, int]]:
        return set(self.body)

    def check_collision(self, grid_width: int, grid_height: int) -> bool:
        head = self.body[0]
        if not (0 <= head[0] < grid_width and 0 <= head[1] < grid_height):
            return True
        for i in range(1, len(self.body)):
            if head == self.body[i]:
                return True
        return False

class RhythmManager:
    def __init__(self, difficulty: str = "NORMAL") -> None:
        bpm_map: dict[str, float] = {"EASY": 120.0, "NORMAL": 140.0, "HARD": 160.0}
        self.current_bpm: float = bpm_map.get(difficulty, 140.0)
        self.sec_per_beat: float = 60.0 / self.current_bpm
        
        self.perfect_window: float = self.sec_per_beat * 0.15
        self.good_window: float = self.sec_per_beat * 0.30
        self.last_evaluated_beat: int = -1

    def scale_difficulty(self, stage: int) -> None:
        pass

    def is_beat_tick(self, elapsed_time: float, last_beat_time: float) -> bool:
        return (elapsed_time - last_beat_time) >= self.sec_per_beat

    def evaluate_input(self, input_time: float) -> Judgment:
        beat_count = round(input_time / self.sec_per_beat)
        if beat_count == self.last_evaluated_beat:
            return Judgment.IGNORED
        self.last_evaluated_beat = beat_count
        nearest_beat_time = beat_count * self.sec_per_beat
        time_diff = abs(input_time - nearest_beat_time)

        if time_diff <= self.perfect_window: return Judgment.PERFECT
        elif time_diff <= self.good_window: return Judgment.GOOD
        else: return Judgment.MISS

# ==========================================
# 3. GameEngine 클래스
# ==========================================
class GameEngine:
    def __init__(self, grid_width: int = 20, grid_height: int = 20):
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        self.server_url = "https://cp-assignment-server.onrender.com/api/leaderboard"
        self.highscore_file = Path("highscore.json")
        
        self.local_leaderboard: list[dict[str, Any]] = self.load_local_leaderboard()
        
        self.reset_game("NORMAL")
        self.state = GameState.READY 

    def fetch_server_leaderboard(self) -> list[dict[str, Any]]:
        try:
            req = urllib.request.Request(self.server_url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get("leaderboard", [])
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"[네트워크 경고] 서버 순위표를 불러올 수 없습니다: {e}")
        return []

    def send_score_to_server(self, player_name: str) -> bool:
        if self.score <= 0:
            return False 
            
        payload = {"name": player_name, "score": self.score}
        data = json.dumps(payload).encode('utf-8')
        
        try:
            req = urllib.request.Request(self.server_url, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status in (200, 201):
                    print(f"[시스템] {player_name}님의 점수({self.score})가 서버에 등록되었습니다.")
                    return True
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"[네트워크 오류] 점수 서버 전송 실패: {e}")
        return False

    def load_local_leaderboard(self) -> list[dict[str, Any]]:
        if not self.highscore_file.exists(): return []
        try:
            with open(self.highscore_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_list = data.get("leaderboard", [])
                
                cleaned_list = []
                for item in raw_list:
                    if isinstance(item, dict):
                        cleaned_list.append(item)
                    elif isinstance(item, (int, float)):
                        cleaned_list.append({"name": "LOCAL", "score": int(item)})
                return cleaned_list
        except Exception:
            return []

    def register_local_score(self, player_name: str) -> None:
        self.local_leaderboard.append({"name": player_name, "score": self.score})
        self.local_leaderboard = sorted(self.local_leaderboard, key=lambda x: x.get("score", 0), reverse=True)[:10]
        try:
            with open(self.highscore_file, "w", encoding="utf-8") as f:
                json.dump({"leaderboard": self.local_leaderboard}, f, indent=4)
        except IOError:
            pass

    def reset_game(self, difficulty: str = "NORMAL") -> None:
        self.snake = Snake(start_pos=(self.grid_width // 2, self.grid_height // 2))
        self.current_difficulty = difficulty
        self.rhythm = RhythmManager(difficulty)
        
        # 💡 [요구사항 1] 난이도별 점수 배율(Score Multiplier) 설정
        multiplier_map: dict[str, float] = {"EASY": 1.0, "NORMAL": 1.25, "HARD": 1.5}
        self.score_multiplier: float = multiplier_map.get(difficulty, 1.25)
        
        self.items: list[Item] = []
        self.obstacles: list[tuple[int, int]] = []
        self.obstacle_count: int = random.randint(7, 11)
        self.state = GameState.PLAYING
        self.score: int = 0
        self.lives: int = 3
        self.combo: int = 0
        self.stage: int = 1
        
        self.total_items_eaten: int = 0
        
        self.last_beat_time: float = 0.0
        self.invincible_mode: bool = False
        self.stage_up_triggered: bool = False
        
        self.spawn_obstacles()
        for _ in range(5):
            self.spawn_item()

    def spawn_item(self) -> None:
        occupied = self.snake.get_occupied_positions()
        for item in self.items: occupied.add(item.position)
        for obstacle in self.obstacles: occupied.add(obstacle)
        available = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height) if (x, y) not in occupied]
        if not available: return
        
        spawn_pos = random.choice(available)
        rand_val = random.random()
        if rand_val < 0.2: item_type = ItemType.LIFE_POTION
        elif rand_val < 0.5: item_type = ItemType.BONUS_COIN
        else: item_type = ItemType.NORMAL_FOOD
            
        self.items.append(Item(spawn_pos[0], spawn_pos[1], item_type))
        
    def spawn_obstacles(self) -> None:
        occupied = self.snake.get_occupied_positions()
        for item in self.items: occupied.add(item.position)
        head_x, head_y = self.snake.body[0]

        while len(self.obstacles) < self.obstacle_count:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)

            distance = abs(x - head_x) + abs(y - head_y)
            if distance <= 1: continue
            if pos in occupied: continue
            if pos in self.obstacles: continue

            self.obstacles.append(pos)
       
    def refresh_obstacles(self) -> None:
        if not self.obstacles: return
        remove_count = random.randint(1, min(3, len(self.obstacles)))
        for _ in range(remove_count):
            removed = random.choice(self.obstacles)
            self.obstacles.remove(removed)
        self.spawn_obstacles()

    def process_player_input(self, direction: Direction, input_time: float) -> Judgment:
        if self.state != GameState.PLAYING: return Judgment.IGNORED
        judgment = self.rhythm.evaluate_input(input_time)
        if judgment == Judgment.IGNORED: return judgment
            
        if judgment == Judgment.PERFECT:
            # 💡 [요구사항 2] PERFECT 판정 점수에 배율 적용 후 정수 변환
            base_score = 100 + (self.combo * 10)
            self.score += int(base_score * self.score_multiplier)
            self.combo += 1
            self.snake.change_direction(direction)
        elif judgment == Judgment.GOOD:
            # 💡 [요구사항 2] GOOD 판정 점수에 배율 적용 후 정수 변환
            base_score = 50
            self.score += int(base_score * self.score_multiplier)
            self.combo = 0
            self.snake.change_direction(direction)
        else:
            self.combo = 0
            if not self.invincible_mode:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over()
        return judgment

    def check_item_consumption(self) -> None:
        head_pos = self.snake.body[0]
        consumed_item = next((item for item in self.items if item.position == head_pos), None)
        
        if consumed_item:
            self.items.remove(consumed_item)
            
            # 💡 [요구사항 2] 개별 아이템 섭취 점수에 배율 적용 후 정수 변환
            if consumed_item.item_type == ItemType.NORMAL_FOOD:
                self.snake.grow(1)
                self.score += int(200 * self.score_multiplier)
            elif consumed_item.item_type == ItemType.LIFE_POTION:
                self.lives = min(5, self.lives + 1)
                self.score += int(100 * self.score_multiplier)
            elif consumed_item.item_type == ItemType.BONUS_COIN:
                self.score += int(500 * self.score_multiplier)
                
            self.total_items_eaten += 1
            
            # 5개 누적 시 스테이지 업
            if self.total_items_eaten % 5 == 0:
                self.stage += 1
                self.stage_up_triggered = True
                
                # 💡 [요구사항 2] 스테이지 업 보너스 점수에도 배율 적용 후 정수 변환
                self.score += int((self.stage * 1000) * self.score_multiplier)
                
                base_increase: int = 3
                if self.current_difficulty == "EASY":
                    base_increase = 2
                elif self.current_difficulty == "HARD":
                    base_increase = 4
                    
                acceleration: int = max(0, self.stage - 2)
                added_obstacles: int = base_increase + acceleration
                
                self.obstacle_count += added_obstacles
                self.spawn_obstacles()
                
            self.refresh_obstacles()
            while len(self.items) < 5:
                self.spawn_item()

    def update(self, elapsed_time: float) -> None:
        if self.state != GameState.PLAYING: return
        
        if self.rhythm.is_beat_tick(elapsed_time, self.last_beat_time):
            self.snake.move()
            self.last_beat_time += self.rhythm.sec_per_beat
            self.check_item_consumption()
            
            head_pos = self.snake.body[0]
            if head_pos in self.obstacles:
                self.game_over()
            elif self.snake.check_collision(self.grid_width, self.grid_height):
                self.game_over()

    def game_over(self) -> None:
        self.state = GameState.GAME_OVER
