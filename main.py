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


def camera_movement_handler(keys, camera_pos, speed: int):
    if keys[pygame.K_w]:
        camera_pos[1] += speed
    if keys[pygame.K_a]:
        camera_pos[0] += speed
    if keys[pygame.K_s]:
        camera_pos[1] -= speed
    if keys[pygame.K_d]:
        camera_pos[0] -= speed


def display(window, board: set, block_width: int, camera_position):
    window.fill(BLACK)

    for (x_pos, y_pos) in board:
        pygame.draw.rect(window, WHITE, pygame.Rect(block_width * (x_pos + camera_position[0]),
                                                    block_width * (y_pos + camera_position[1]),
                                                    block_width,
                                                    block_width))


def draw(board: set, block_width: int, camera_position, erasing=False):
    mouse_pos = pygame.mouse.get_pos()

    board_pos = (mouse_pos[0] // block_width - camera_position[0], mouse_pos[1] // block_width - camera_position[1])

    if erasing:
        if board_pos in board:
            board.remove(board_pos)
    else:
        board.add(board_pos)


def main(rows: int, width: int):
    board = set()

    window = pygame.display.set_mode((width, width))
    pygame.display.set_caption("Game Of Life")
    clock = pygame.time.Clock()
    running = True
    camera_pos = [0, 0]
    block_width = width // rows

    drawing = True

    previous_space = False

    while running:
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        camera_movement_handler(keys, camera_pos, 1)

        if drawing:
            mouse_buttons = pygame.mouse.get_pressed(3)
            if mouse_buttons[0]:
                draw(board, block_width, camera_pos)
            elif mouse_buttons[2]:
                draw(board, block_width, camera_pos, erasing=True)
            # mouse

            if keys[pygame.K_RETURN]:
                save(board)
            elif keys[pygame.K_BACKSPACE]:
                new_board = open_file()
                if new_board:
                    board = new_board
            # save/open files
        else:
            board = play(board)

        current_space = keys[pygame.K_SPACE]
        if current_space and not previous_space:
            drawing = not drawing

        previous_space = current_space
        # press space bar once.

        display(window, board, block_width, camera_pos)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(100, 800)
