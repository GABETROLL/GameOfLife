import pygame
from game import play
from tkinter import filedialog

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def save(board: set):
    path = filedialog.asksaveasfilename()
    if not path:
        return

    with open(path, "w") as file:
        file.write(str(board))


def open_file():
    path = filedialog.askopenfilename()
    if not path:
        return

    with open(path, "r") as file:
        return eval(file.read())


def window_pos(width: int, game_pos: tuple[int, int], camera_position: list[int, int], block_width: int) -> tuple[int, int]:
    return block_width * game_pos[0] + camera_position[0] + width // 2, \
           block_width * game_pos[1] + camera_position[1] + width // 2


def display(window, width: int, board: set, block_width: int, camera_position):
    window.fill(BLACK)

    for (x_pos, y_pos) in board:
        pygame.draw.rect(window, WHITE, pygame.Rect(block_width * x_pos + camera_position[0] + width // 2,
                                                    block_width * y_pos + camera_position[1] + width // 2,
                                                    block_width,
                                                    block_width))


def board_pos(width: int, screen_pos: tuple[int, int], camera_position: list[int, int], block_width: int) -> tuple[int, int]:
    return int((screen_pos[0] - camera_position[0] - width // 2) // block_width), \
           int((screen_pos[1] - camera_position[1] - width // 2) // block_width)


class InputHandler:
    def __init__(self,
                 window,
                 width: int,
                 board: set,
                 camera_position: list[int, int],
                 camera_speed: int,
                 key_bind_font: pygame.font.Font):

        self.window = window
        self.width = width

        self.keys = pygame.key.get_pressed()

        self.camera_position = camera_position
        self.speed = camera_speed

        self.board = board

        self.first_pos = ()
        self.last_pos = ()
        # corners of highlighted region

        self.copy = set()
        # region to paste

        self.font = key_bind_font

        self.previous_wheel = False

    @property
    def region(self):
        result = set()

        if self.last_pos:
            for i in range(self.first_pos[0], self.last_pos[0] + 1):
                for j in range(self.first_pos[1], self.last_pos[1] + 1):
                    if (i, j) in self.board:
                        result.add((i, j))

        return result

    def file_handler(self):
        if self.keys[pygame.K_RETURN]:
            save(self.board)
        elif self.keys[pygame.K_BACKSPACE]:
            return open_file()

    def camera_movement_handler(self):
        self.camera_position[0] += self.speed * (self.keys[pygame.K_a] - self.keys[pygame.K_d] + self.keys[pygame.K_LEFT] - self.keys[pygame.K_RIGHT])
        self.camera_position[1] += self.speed * (self.keys[pygame.K_w] - self.keys[pygame.K_s] + self.keys[pygame.K_UP] - self.keys[pygame.K_DOWN])
        # WASD + D-PAD

    def delete_region(self):
        for (i, j) in self.region:
            self.board.remove((i, j))

    def paste_region(self, pos: tuple[int, int]):
        difference = (pos[0] - self.first_pos[0], pos[1] - self.first_pos[1])

        for (i, j) in self.copy:
            self.board.add((i + difference[0], j + difference[1]))

    def copy_paste_delete_handler(self, mouse_pos: tuple[int, int]):
        if self.last_pos:
            if self.keys[pygame.K_c]:
                self.copy = self.region
            elif self.keys[pygame.K_DELETE]:
                self.delete_region()
            elif self.keys[pygame.K_p]:
                self.paste_region(mouse_pos)
        # copy / paste / delete

    def handler(self, drawing: bool, block_width: int):
        mouse_pos = pygame.mouse.get_pos()
        self.keys = pygame.key.get_pressed()

        self.file_handler()
        self.camera_movement_handler()

        if drawing:
            self.copy_paste_delete_handler(mouse_pos)

            mouse_buttons = pygame.mouse.get_pressed(3)
            wheel_pressed = mouse_buttons[1]

            board_position = board_pos(self.width, mouse_pos, self.camera_position, block_width)

            if mouse_buttons[0] or mouse_buttons[2]:
                # Drawing resets the selection.
                self.first_pos = ()
                self.last_pos = ()

                if mouse_buttons[2]:
                    if board_position in self.board:
                        self.board.remove(board_position)
                elif mouse_buttons[0]:
                    self.board.add(board_position)

            if self.previous_wheel and not wheel_pressed:
                self.last_pos = board_position
            elif not self.previous_wheel and wheel_pressed:
                self.first_pos = ()
                self.last_pos = ()

                self.first_pos = board_position
            # select region with scrollbar

            self.previous_wheel = wheel_pressed
        else:
            self.first_pos = ()
            self.last_pos = ()
            self.copy = set()

    def display_keybind_text(self):
        text = self.font.render("WASD/D-PAD: move, space bar: play/stop, q/e: zoom out/in, backspace: open, enter: save" if not self.last_pos else "c: copy, delete: delete", True, (255, 255, 255))

        self.window.blit(text, (0, self.width - 10))

    def display(self, block_width: int):
        if self.first_pos:
            first_pos = window_pos(self.width, self.first_pos, self.camera_position, block_width)
            last_pos = window_pos(self.width, self.last_pos, self.camera_position, block_width) if self.last_pos else pygame.mouse.get_pos()

            pygame.draw.line(self.window, (255, 255, 0), first_pos, (last_pos[0], first_pos[1]))
            pygame.draw.line(self.window, (255, 255, 0), first_pos, (first_pos[0], last_pos[1]))
            pygame.draw.line(self.window, (255, 255, 0), last_pos, (last_pos[0], first_pos[1]))
            pygame.draw.line(self.window, (255, 255, 0), last_pos, (first_pos[0], last_pos[1]))
            # draw rectangle of highlighted region

        self.display_keybind_text()


def main(width: int, rows: int):
    board = set()

    pygame.init()
    window = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Game Of Life")
    clock = pygame.time.Clock()
    running = True
    camera_pos = [0, 0]
    # center
    block_width = width // rows

    drawing = True
    input_handler = InputHandler(window, width, board, camera_pos, 5, pygame.font.SysFont("Consolas", 10))

    while running:
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    drawing = not drawing

                if event.key == pygame.K_q and block_width >= 2:
                    camera_pos[0] //= 2
                    camera_pos[1] //= 2
                    block_width //= 2
                if event.key == pygame.K_e and block_width <= width:
                    camera_pos[0] *= 2
                    camera_pos[1] *= 2
                    block_width *= 2
                # zoom

        keys = pygame.key.get_pressed()

        input_handler.handler(drawing, block_width)
        if not drawing:
            board = play(board)

        display(window, width, board, block_width, camera_pos)
        input_handler.display(block_width)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(800, 100)
