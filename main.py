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


def window_pos(width: int, game_pos: tuple[int, int],
               camera_position: list[int, int], block_width: int) -> tuple[int, int]:
    return block_width * game_pos[0] + camera_position[0] + width // 2, \
           block_width * game_pos[1] + camera_position[1] + width // 2


def display(window, width: int, board: set, block_width: int, camera_position):
    window.fill(BLACK)

    for (x_pos, y_pos) in board:
        pygame.draw.rect(window, WHITE, pygame.Rect(block_width * x_pos + camera_position[0] + width // 2,
                                                    block_width * y_pos + camera_position[1] + width // 2,
                                                    block_width,
                                                    block_width))


def board_pos(width: int, screen_pos: tuple[int, int],
              camera_position: list[int, int], block_width: int) -> tuple[int, int]:
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

        self.copy = [(), set(), False]
        # region to paste: [first_pos, board section, previewing]

        self.font = key_bind_font

    @property
    def region(self):
        result = set()

        if self.last_pos and self.first_pos:
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
        self.camera_position[0] += self.speed * (self.keys[pygame.K_a] - self.keys[pygame.K_d] +
                                                 self.keys[pygame.K_LEFT] - self.keys[pygame.K_RIGHT])
        self.camera_position[1] += self.speed * (self.keys[pygame.K_w] - self.keys[pygame.K_s] +
                                                 self.keys[pygame.K_UP] - self.keys[pygame.K_DOWN])
        # WASD + D-PAD

    def delete_region(self):
        for (i, j) in self.region:
            self.board.remove((i, j))

    def paste_positions(self, game_pos: tuple[int, int], region: set):
        difference = (game_pos[0] - self.copy[0][0], game_pos[1] - self.copy[0][1])
        for (i, j) in region:
            yield i + difference[0], j + difference[1]

    def paste_region(self, game_pos: tuple[int, int]):
        for p in self.paste_positions(game_pos, self.copy[1]):
            self.board.add(p)

    def copy_paste_delete_handler(self, mouse_pos: tuple[int, int], block_width: int,
                                  key_down_event_keys: set):
        if self.last_pos:
            if pygame.K_c in key_down_event_keys:
                self.copy = [self.first_pos, self.region, False]
            elif pygame.K_DELETE in key_down_event_keys:
                self.delete_region()
        if pygame.K_p in key_down_event_keys:
            if self.copy[2]:
                self.paste_region(board_pos(self.width, mouse_pos, self.camera_position, block_width))
            self.copy[2] = not self.copy[2]
            # paste once to preview, twice to paste.

        # copy / paste / delete

    def handler(self, drawing: bool, block_width: int, board: set,
                mouse_wheel_event: pygame.event.Event, key_down_event_keys: set):
        mouse_pos = pygame.mouse.get_pos()
        self.keys = pygame.key.get_pressed()

        self.board = board

        self.camera_movement_handler()

        if drawing:
            self.copy_paste_delete_handler(mouse_pos, block_width, key_down_event_keys)

            mouse_buttons = pygame.mouse.get_pressed(3)

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

            if mouse_wheel_event:
                if mouse_wheel_event.type == pygame.MOUSEBUTTONUP:
                    self.last_pos = board_position
                elif mouse_wheel_event.type == pygame.MOUSEBUTTONDOWN:
                    self.first_pos = board_position
                    self.last_pos = ()
            # select region with scrollbar
        else:
            self.first_pos = ()
            self.last_pos = ()
            self.copy = [(), set(), False]
            # cop/pasting resets when not drawing.

    def preview_paste(self, block_width: int, mouse_pos: tuple[int, int]):
        game_pos = board_pos(self.width, mouse_pos, self.camera_position, block_width)

        for pos in self.paste_positions(game_pos, self.copy[1]):
            pos = window_pos(self.width, pos, self.camera_position, block_width)
            pygame.draw.rect(self.window, (128, 128, 128), pygame.Rect(pos[0], pos[1], block_width, block_width))

    def display_keybind_text(self):
        if self.last_pos:
            text_text = "c: copy, delete: delete"
        else:
            text_text = "WASD/D-PAD: move, space bar: play/stop, q/e: zoom out/in, backspace: open, enter: save"

        text = self.font.render(text_text, True, (255, 255, 255))

        self.window.blit(text, (0, self.width - 10))

    def display(self, block_width: int, mouse_pos: tuple[int, int]):
        if self.copy[2]:
            self.preview_paste(block_width, mouse_pos)

        if self.first_pos:
            first_pos = window_pos(self.width, self.first_pos, self.camera_position, block_width)
            last_pos = window_pos(self.width, self.last_pos, self.camera_position, block_width) if self.last_pos \
                else pygame.mouse.get_pos()

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

        mouse_wheel_event = None
        key_down_event_keys = set()

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

                key_down_event_keys.add(event.key)

            if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN and \
                    pygame.mouse.get_pressed(3)[1]:
                mouse_wheel_event = event

        if fh := input_handler.file_handler():
            board = fh
        input_handler.handler(drawing, block_width, board, mouse_wheel_event, key_down_event_keys)

        if not drawing:
            board = play(board)

        display(window, width, board, block_width, camera_pos)
        if drawing:
            input_handler.display(block_width, pygame.mouse.get_pos())
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(800, 100)
