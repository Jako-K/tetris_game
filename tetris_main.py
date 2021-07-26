import pygame
import sys
import tetris_logic

game_controller = tetris_logic.GameController()
move_down = pygame.USEREVENT + 1
move_reset = pygame.USEREVENT + 2
space_reset = pygame.USEREVENT + 3
rotate_reset = pygame.USEREVENT + 4

pygame.time.set_timer(move_down, 500)

move_ready = True
space_ready = True
rotate_ready = True


while True:
    game_controller.tick(30)
    keys = pygame.key.get_pressed()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == move_down:
            if game_controller.at_bottom():
                game_controller.draw_new_block()
            else:
                game_controller.move("down")
        if event.type == move_reset:
            move_ready = True
        if event.type == space_reset:
            space_ready = True
        if event.type == rotate_reset:
            rotate_ready = True

    if sum(keys):
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

        if sum([keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_s],
               keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_DOWN],]) and move_ready:
            move_ready = False
            pygame.time.set_timer(move_reset, 50)

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                game_controller.move("left")
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                game_controller.move("right")
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                if game_controller.at_bottom():
                    game_controller.draw_new_block()
                else:
                    game_controller.move("down")

        if (keys[pygame.K_w] or keys[pygame.K_UP])  and rotate_ready:
            rotate_ready = False
            pygame.time.set_timer(rotate_reset, 100)
            game_controller.rotate()

        if keys[pygame.K_SPACE] and space_ready:
            space_ready = False
            game_controller.move_to_bottom()
            pygame.time.set_timer(space_reset, 200)


    game_controller.end_of_frame_update()








