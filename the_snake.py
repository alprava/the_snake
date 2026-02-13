from random import choice, randint

import pygame as pg

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
BOARD_BACKGROUND_COLOR = (192, 192, 192)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()

# Текущая скорость игры:
INITIAL_SPEED = 20

# Центральная позиция
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Противоположные направления
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}


class GameObject:
    """Общий класс для всех игровых объектов"""

    def __init__(self, body_color=None):
        self.position = CENTER_POSITION
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовка одной ячейки объекта"""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        cell_color = color if color is not None else self.body_color
        pg.draw.rect(screen, cell_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовка игрового объекта."""
        raise NotImplementedError(
            f'Метод draw не реализован в классе {self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс для яблока"""

    def __init__(self, occupied_positions=None, color=APPLE_COLOR):
        super().__init__(color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def randomize_position(self, snake_positions):
        """Установка случайной позиции для яблока"""
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

    def __init__(self, color=SNAKE_COLOR):
        super().__init__(color)
        self.max_length = 1
        self.reset()

    def update_direction(self, new_direction):
        """Обновление текущего направления движения.
        Запрещает разворот на 180 градусов.
        """
        if new_direction and new_direction != OPPOSITE_DIRECTIONS.get(
                self.direction):
            self.direction = new_direction

    def move(self):
        """Обновление позиции змейки"""
        head_x, head_y = self.get_head_position()

        dx, dy = self.direction

        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))

        if len(self.positions) > self.length:
            self.positions.pop()

        if self.length > self.max_length:
            self.max_length = self.length

    def draw(self):
        """Отрисовывывает змейку"""
        if not self.positions:
            return

        if len(self.positions) == self.length:
            for position in self.positions:
                self.draw_cell(position)
            return

        if self.tail_to_remove:
            rect = pg.Rect(self.tail_to_remove, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        self.draw_cell(self.positions[0])

        if len(self.positions) > 1:
            self.draw_cell(self.positions[-1])

    def get_head_position(self):
        """Возвращает позицию головы змейки"""
        return self.positions[0]

    def reset(self):
        """Сброс змейки в начальное состояние"""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])
        self.tail_to_remove = None


def handle_keys(snake):
    """Обработка пользовательского ввода для управленя змейкой"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit

            movement_keys = {
                pg.K_UP: UP,
                pg.K_DOWN: DOWN,
                pg.K_LEFT: LEFT,
                pg.K_RIGHT: RIGHT,
            }

            if event.key in movement_keys:
                snake.update_direction(movement_keys[event.key])
                return None

            if event.key == pg.K_PLUS or event.key == pg.K_EQUALS:
                return 'speed_up'
            if event.key == pg.K_MINUS:
                return 'speed_down'
            if event.key == pg.K_0:
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
    pg.display.set_caption('Змейка | ' + ' | '.join(title))


def main():
    """
    Основная функция для игры.

    Инициализирует игру, создает объекты и запускает игровой цикл.
    Обрабатывает логику движения, столкновений,
    отрисовки и обновления экрана.
    Завершение игры после макс.кол-ва итераций.
    """
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    current_speed = INITIAL_SPEED

    iteration_count = 0
    max_count_of_iterations = 1000

    while True:
        iteration_count += 1
        if iteration_count > max_count_of_iterations:
            pg.quit()
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

        snake.move()

        ate_apple = False

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            ate_apple = True

        if not ate_apple and snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            current_speed = INITIAL_SPEED

        snake.draw()
        apple.draw()
        pg.display.update()
        screen.fill(BOARD_BACKGROUND_COLOR)


if __name__ == '__main__':
    main()
