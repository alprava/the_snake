from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка | Управление: стрелки | ESC: выход')

# Настройка времени:
clock = pygame.time.Clock()

# Текущая скорость игры:
INITIAL_SPEED = 5


class GameObject:
    """Общий класс для всех игровых объектов"""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position):
        """Отрисовка одной ячейки объекта"""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовка игрового объекта."""
        pass


class Apple(GameObject):
    """Класс для яблока"""

    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Установка случайной позиции для яблока"""
        if snake_positions is None:
            snake_positions = []
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in snake_positions:
                break

    def draw(self):
        """Отрисовка яблока"""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс для змейки"""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.tail_to_remove = None
        self.max_length = 1

    def update_direction(self):
        """Обновление текущего направления движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновление позиции змейки"""
        head_x, head_y = self.positions[0]
        new_x = head_x + self.direction[0] * GRID_SIZE
        new_y = head_y + self.direction[1] * GRID_SIZE
        new_head = (new_x, new_y)

        self.tail_to_remove = self.positions[-1] if self.positions else None

        self.positions.insert(0, new_head)
        self.last = self.positions[-1]

        if len(self.positions) > self.length:
            self.positions.pop()

        self.position = new_head

        if self.length > self.max_length:
            self.max_length = self.length

    def draw(self):
        """Отрисовывывает змейку"""
        if not self.positions:
            return

        if self.tail_to_remove:
            rect = pygame.Rect(self.tail_to_remove, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        self.draw_cell(self.positions[0])

        if len(self.positions) > 1:
            self.draw_cell(self.positions[-1])

    def get_head_position(self):
        """Возвращает позицию головы змейки"""
        return self.positions[0]

    def reset(self):
        """Сброс змейки в начальное состояние"""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])
        self.next_direction = None
        self.max_length = max(self.max_length, self.length)


def handle_keys(snake):
    """Обработка пользовательского ввода для управленя змейкой"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

            movement_keys = {
                pygame.K_UP: (UP, DOWN),
                pygame.K_DOWN: (DOWN, UP),
                pygame.K_LEFT: (LEFT, RIGHT),
                pygame.K_RIGHT: (RIGHT, LEFT),
            }

            if event.key in movement_keys:
                direction, opposite = movement_keys[event.key]
                if snake.direction != opposite:
                    snake.next_direction = direction
                return None

            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                return 'speed_up'
            if event.key == pygame.K_MINUS:
                return 'speed_down'
            if event.key == pygame.K_0:
                return 'speed_reset'
    return None


def update_window_title(snake, speed):
    """Обновление заголовка с информацией об игре"""
    title = [f'Длина: {snake.length}',
             f'Рекорд: {snake.max_length}',
             f'Скорость: {speed}',
             'Упр: ←↑↓→',
             'Скор: +/-',
             'Сброс: 0',
             'Выход: ESC'
             ]
    pygame.display.set_caption('Змейка | ' + ' | '.join(title))


def main():
    """
    Основная функция для игры.

    Инициализирует игру, создает объекты и запускает игровой цикл.
    Обрабатывает логику движения, столкновений,
    отрисовки и обновления экрана.
    Завершение игры после макс.кол-ва итераций.
    """
    pygame.init()
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    current_speed = INITIAL_SPEED

    iteration_count = 0
    max_count_of_iterations = 1000

    while True:
        iteration_count += 1
        if iteration_count > max_count_of_iterations:
            pygame.quit()
            return

        clock.tick(current_speed)
        update_window_title(snake, current_speed)
        action = handle_keys(snake)

        if action == 'speed_up':
            current_speed = min(current_speed + 2, 40)
        elif action == 'speed_down':
            current_speed = max(current_speed - 2, 5)
        elif action == 'speed_reset':
            current_speed = INITIAL_SPEED

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
