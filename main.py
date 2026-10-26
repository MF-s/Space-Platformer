import pygame

from game.audio import SoundEffects
from game.levels import LEVELS, GameLevel
from game.player import Player
from game.settings import (
    AUDIO_SAMPLE_RATE,
    AUDIO_VOLUME,
    BACKGROUND_PATH,
    CRYSTAL_COUNTER_HUD_PATH,
    CRYSTAL_FRAME_PATHS,
    FONT_PATH,
    FPS,
    HUD_CRYSTAL_PATH,
    LASER_PATH,
    LEVEL_LABEL_HUD_PATHS,
    PLAYER_SHEET_PATH,
    PORTAL_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_PATH,
    TRAP_PATH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)


def load_background() -> pygame.Surface:
    image = pygame.image.load(str(BACKGROUND_PATH)).convert()
    scale = max(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height())
    size = (round(image.get_width() * scale), round(image.get_height() * scale))
    scaled = pygame.transform.smoothscale(image, size)
    left = (scaled.get_width() - SCREEN_WIDTH) // 2
    top = (scaled.get_height() - SCREEN_HEIGHT) // 2
    return scaled.subsurface(pygame.Rect(left, top, SCREEN_WIDTH, SCREEN_HEIGHT)).copy()


def menu_button_rects(option_count: int) -> list[pygame.Rect]:
    button_width = 580
    button_height = 52
    gap = 14
    total_height = option_count * button_height + (option_count - 1) * gap
    top = (SCREEN_HEIGHT - total_height) // 2 + 35
    left = (SCREEN_WIDTH - button_width) // 2
    return [
        pygame.Rect(
            left,
            top + index * (button_height + gap),
            button_width,
            button_height,
        )
        for index in range(option_count)
    ]


def menu_options(state: str) -> tuple[str, ...]:
    if state == "main_menu":
        return ("START", "CONTROLS", "EXIT")
    if state == "level_select":
        return (
            "LEVEL 1 - NEBULA OUTPOST",
            "LEVEL 2 - ELECTRIC CHANNEL",
            "LEVEL 3 - RIFT FINALE",
            "BACK",
        )
    if state == "controls":
        return ("BACK",)
    if state == "paused":
        return ("CONTINUE", "EXIT TO MAIN MENU", "EXIT TO DESKTOP")
    return ("PLAY AGAIN", "LEVEL SELECT", "MAIN MENU", "EXIT TO DESKTOP")


def draw_menu(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    title: str,
    options: tuple[str, ...],
    selected_index: int,
    *,
    dim_background: bool = False,
    mouse_position: tuple[int, int] = (0, 0),
) -> None:
    if dim_background:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 24, 190))
        screen.blit(overlay, (0, 0))

    title_surface = title_font.render(title, True, (255, 255, 255))
    screen.blit(
        title_surface,
        title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 145)),
    )

    for index, (option, rect) in enumerate(
        zip(options, menu_button_rects(len(options)))
    ):
        highlighted = index == selected_index or rect.collidepoint(mouse_position)
        button = pygame.Surface(rect.size, pygame.SRCALPHA)
        button.fill((65, 182, 220, 220) if highlighted else (18, 27, 54, 220))
        screen.blit(button, rect)
        pygame.draw.rect(
            screen,
            (183, 239, 255) if highlighted else (104, 138, 174),
            rect,
            width=2,
        )
        label = font.render(option, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=rect.center))


def main() -> None:
    pygame.mixer.pre_init(
        frequency=AUDIO_SAMPLE_RATE,
        size=-16,
        channels=2,
        buffer=512,
    )
    pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init(frequency=AUDIO_SAMPLE_RATE, size=-16, channels=2, buffer=512)
    pygame.display.set_caption(WINDOW_TITLE)
    display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    sounds = SoundEffects(AUDIO_SAMPLE_RATE, AUDIO_VOLUME)

    background = load_background()
    tile = pygame.image.load(str(TILE_PATH)).convert_alpha()
    trap_image = pygame.image.load(str(TRAP_PATH)).convert_alpha()
    laser_image = pygame.image.load(str(LASER_PATH)).convert_alpha()
    portal_image = pygame.image.load(str(PORTAL_PATH)).convert_alpha()
    crystal_counter_hud = pygame.image.load(
        str(CRYSTAL_COUNTER_HUD_PATH)
    ).convert_alpha()
    hud_crystal = pygame.image.load(str(HUD_CRYSTAL_PATH)).convert_alpha()
    level_label_huds = tuple(
        pygame.image.load(str(path)).convert_alpha()
        for path in LEVEL_LABEL_HUD_PATHS
    )
    crystal_frames = tuple(
        pygame.transform.scale(
            pygame.image.load(str(path)).convert_alpha(),
            (32, 32),
        )
        for path in CRYSTAL_FRAME_PATHS
    )
    font = pygame.font.Font(str(FONT_PATH), 12)
    title_font = pygame.font.Font(str(FONT_PATH), 22)
    hud_font = pygame.font.Font(str(FONT_PATH), 10)

    def create_level(index: int) -> GameLevel:
        return GameLevel(
            LEVELS[index],
            tile,
            trap_image,
            laser_image,
            portal_image,
            crystal_frames,
        )

    level_index = 0
    level = create_level(level_index)

    def new_player() -> Player:
        spawn_x, spawn_y = level.spec.spawn
        return Player(
            PLAYER_SHEET_PATH,
            (spawn_x, spawn_y - Player.COLLISION_HEIGHT),
        )

    player = new_player()
    state = "main_menu"
    selected_index = 0
    running = True

    def activate_selection() -> None:
        nonlocal level, level_index, player, running, selected_index, state
        sounds.play("menu")
        if state == "main_menu":
            if selected_index == 0:
                state = "level_select"
                selected_index = 0
            elif selected_index == 1:
                state = "controls"
                selected_index = 0
            else:
                running = False
        elif state == "level_select":
            if selected_index == len(LEVELS):
                state = "main_menu"
                selected_index = 0
            else:
                level_index = selected_index
                level = create_level(level_index)
                player = new_player()
                state = "game"
        elif state == "controls":
            state = "main_menu"
            selected_index = 0
        elif state == "paused":
            if selected_index == 0:
                state = "game"
            elif selected_index == 1:
                state = "main_menu"
                selected_index = 0
            else:
                running = False
        elif state == "victory":
            if selected_index == 0:
                level = create_level(level_index)
                player = new_player()
                state = "game"
            elif selected_index == 1:
                state = "level_select"
                selected_index = 0
            elif selected_index == 2:
                state = "main_menu"
                selected_index = 0
            else:
                running = False

    while running:
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)
        options = menu_options(state)
        button_rects = menu_button_rects(len(options))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "game":
                        sounds.play("menu")
                        state = "paused"
                        selected_index = 0
                    elif state == "paused":
                        sounds.play("menu")
                        state = "game"
                    elif state == "level_select":  # noqa: SIM114
                        sounds.play("menu")
                        state = "main_menu"
                        selected_index = 0
                    elif state == "controls":
                        sounds.play("menu")
                        state = "main_menu"
                        selected_index = 0
                    continue

                if state not in ("main_menu", "level_select", "paused", "victory"):
                    continue
                options = menu_options(state)
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_index = (selected_index - 1) % len(options)
                    sounds.play("menu")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_index = (selected_index + 1) % len(options)
                    sounds.play("menu")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    activate_selection()
            elif event.type == pygame.MOUSEMOTION and state != "game":
                button_rects = menu_button_rects(len(menu_options(state)))
                mouse_position = (
                    event.pos[0] * SCREEN_WIDTH // WINDOW_WIDTH,
                    event.pos[1] * SCREEN_HEIGHT // WINDOW_HEIGHT,
                )
                for index, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_position):
                        if selected_index != index:
                            sounds.play("menu")
                        selected_index = index
                        break
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and state != "game"
            ):
                button_rects = menu_button_rects(len(menu_options(state)))
                mouse_position = (
                    event.pos[0] * SCREEN_WIDTH // WINDOW_WIDTH,
                    event.pos[1] * SCREEN_HEIGHT // WINDOW_HEIGHT,
                )
                for index, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_position):
                        selected_index = index
                        activate_selection()
                        break

        if state == "game":
            level.update(delta_time)
            keys = pygame.key.get_pressed()
            jumping = player.on_ground and (
                keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
            )
            player.update(delta_time, keys, level.platforms)
            if jumping and not player.on_ground:
                sounds.play("jump")
            player.rect.left = max(player.rect.left, 0)
            player.rect.right = min(player.rect.right, SCREEN_WIDTH)

            if player.rect.top > SCREEN_HEIGHT or level.touches_hazard(player.rect):
                sounds.play("death")
                player = new_player()
            else:
                previous_crystal_count = len(level.collected)
                level.collect_crystals(player.rect)
                if len(level.collected) > previous_crystal_count:
                    sounds.play("crystal")
                if player.rect.colliderect(level.portal_rect):
                    sounds.play("portal")
                    if level_index + 1 < len(LEVELS):
                        level_index += 1
                        level = create_level(level_index)
                        player = new_player()
                    else:
                        state = "victory"
                        selected_index = 0

        screen.blit(background, (0, 0))
        level.draw(screen)

        if state in ("game", "paused", "victory"):
            player.draw(screen)
            screen.blit(level_label_huds[level_index], (14, 12))
            counter_position = (
                SCREEN_WIDTH - crystal_counter_hud.get_width() - 14,
                12,
            )
            screen.blit(
                crystal_counter_hud,
                counter_position,
            )
            crystal_count = hud_font.render(
                f"x {len(level.collected):02d}",
                True,
                (235, 245, 255),
            )
            screen.blit(
                crystal_count,
                (
                    counter_position[0] + 18,
                    counter_position[1]
                    + (crystal_counter_hud.get_height() - crystal_count.get_height()) // 2,
                ),
            )
            hud_crystal_size = 36
            screen.blit(
                pygame.transform.scale(hud_crystal, (hud_crystal_size, hud_crystal_size)),
                (
                    counter_position[0] + 121,
                    counter_position[1]
                    + (crystal_counter_hud.get_height() - hud_crystal_size) // 2,
                ),
            )
        if state in ("main_menu", "level_select", "controls", "paused", "victory"):
            titles = {
                "main_menu": "SPACE PLATFORMER",
                "level_select": "SELECT LEVEL",
                "controls": "CONTROLS",
                "paused": "PAUSED",
                "victory": "RIFT RESTORED!",
            }
            if state == "controls":
                control_lines = (
                    ("MOVE", "A / D OR ARROWS"),
                    ("JUMP", "SPACE / W / UP"),
                    ("PAUSE", "ESC"),
                )
                for index, (action, keys) in enumerate(control_lines):
                    text = font.render(
                        f"{action}: {keys}",
                        True,
                        (183, 239, 255),
                    )
                    screen.blit(
                        text,
                        text.get_rect(
                            center=(SCREEN_WIDTH // 2, 190 + index * 28)
                        ),
                    )
            mouse_position = pygame.mouse.get_pos()
            mouse_position = (
                mouse_position[0] * SCREEN_WIDTH // WINDOW_WIDTH,
                mouse_position[1] * SCREEN_HEIGHT // WINDOW_HEIGHT,
            )
            draw_menu(
                screen,
                title_font,
                font,
                titles[state],
                menu_options(state),
                selected_index,
                dim_background=state in ("paused", "victory"),
                mouse_position=mouse_position,
            )

        display.blit(pygame.transform.scale(screen, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
