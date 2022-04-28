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


def file_handler(keys, board: set):
    if keys[pygame.K_RETURN]:
        save(board)
    elif keys[pygame.K_BACKSPACE]:
        return open_file()


def camera_movement_handler(keys, camera_pos, speed: int):
    camera_pos[0] += speed * (keys[pygame.K_a] - keys[pygame.K_d] + keys[pygame.K_LEFT] - keys[pygame.K_RIGHT])
    camera_pos[1] += speed * (keys[pygame.K_w] - keys[pygame.K_s] + keys[pygame.K_UP] - keys[pygame.K_DOWN])
    # WASD + D-PAD


def display(window, board: set, block_width: int, camera_position):
    window.fill(BLACK)

    for (x_pos, y_pos) in board:
        pygame.draw.rect(window, WHITE, pygame.Rect(block_width * (x_pos + camera_position[0]),
                                                    block_width * (y_pos + camera_position[1]),
                                                    block_width,
                                                    block_width))


def draw_handler(board: set, block_width: int, camera_position, mouse_buttons):
    mouse_pos = pygame.mouse.get_pos()

    board_pos = (mouse_pos[0] // block_width - camera_position[0], mouse_pos[1] // block_width - camera_position[1])

    if mouse_buttons[2]:
        if board_pos in board:
            board.remove(board_pos)
    elif mouse_buttons[0]:
        board.add(board_pos)


def main(width: int, rows: int):
    board = set()

    window = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Game Of Life")
    clock = pygame.time.Clock()
    running = True
    camera_pos = [0, 0]
    block_width = width // rows

    drawing = True

    while running:
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    drawing = not drawing

                if event.key == pygame.K_q:
                    block_width //= 2
                if event.key == pygame.K_e:
                    block_width *= 2
                # zoom

        keys = pygame.key.get_pressed()

        camera_movement_handler(keys, camera_pos, 1)

        if drawing:
            draw_handler(board, block_width, camera_pos, pygame.mouse.get_pressed(3))
            # mouse

            if fh := file_handler(keys, board):
                board = fh
            # save/open files
        else:
            board = play(board)

        display(window, board, block_width, camera_pos)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(800, 100)
