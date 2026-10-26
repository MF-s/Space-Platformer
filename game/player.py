from collections.abc import Sequence
from pathlib import Path

import pygame

from game.settings import (
    GRAVITY,
    PLAYER_FRAME_HEIGHT,
    PLAYER_FRAME_WIDTH,
    PLAYER_JUMP_SPEED,
    PLAYER_SCALE,
    PLAYER_SPEED,
)

Animation = tuple[tuple[int, int], ...]


class Player:
    """Player movement, collision, spritesheet slicing, and animation."""

    COLLISION_WIDTH = 60
    COLLISION_HEIGHT = 96

    ANIMATIONS: dict[str, Animation] = {  # noqa: RUF012
        "idle": ((0, 0), (1, 0)),
        "walk": ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)),
        "air": ((0, 2), (1, 2), (2, 2)),
    }

    def __init__(self, spritesheet_path: Path, position: tuple[int, int]) -> None:
        sheet = pygame.image.load(str(spritesheet_path)).convert_alpha()
        self.frames = self._slice_spritesheet(sheet)
        self.animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0.0

        self.image_size = (PLAYER_FRAME_WIDTH * PLAYER_SCALE, PLAYER_FRAME_HEIGHT * PLAYER_SCALE)
        self.rect = pygame.Rect(
            position[0],
            position[1],
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT,
        )
        self.velocity_y = 0.0
        self.facing_right = True
        self.on_ground = False
        self._animation_image = self.frames[self.ANIMATIONS["idle"][0]]

    @staticmethod
    def _slice_spritesheet(sheet: pygame.Surface) -> dict[tuple[int, int], pygame.Surface]:
        frame_width = PLAYER_FRAME_WIDTH
        frame_height = PLAYER_FRAME_HEIGHT
        if sheet.get_width() % frame_width or sheet.get_height() % frame_height:
            raise ValueError(
                "Spritesheet dimensions must be multiples of "
                f"{frame_width}x{frame_height}px; "
                f"got {sheet.get_width()}x{sheet.get_height()}."
            )

        frames: dict[tuple[int, int], pygame.Surface] = {}
        columns = sheet.get_width() // frame_width
        rows = sheet.get_height() // frame_height
        for row in range(rows):
            for column in range(columns):
                area = pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height,
                )
                frames[(column, row)] = sheet.subsurface(area).copy()
        return frames

    def update(
        self,
        delta_time: float,
        keys: pygame.key.ScancodeWrapper,
        platforms: Sequence[pygame.Rect],
    ) -> None:
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )
        self.rect.x += round(direction * PLAYER_SPEED * delta_time)
        if direction:
            self.facing_right = direction > 0

        if self.on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.velocity_y = -PLAYER_JUMP_SPEED
            self.on_ground = False

        previous_bottom = self.rect.bottom
        supported = self.on_ground and any(
            self.rect.bottom == platform.top
            and self.rect.right > platform.left
            and self.rect.left < platform.right
            for platform in platforms
        )
        if supported:
            self.velocity_y = 0
        else:
            self.on_ground = False
            self.velocity_y += GRAVITY * delta_time
            self.rect.y += round(self.velocity_y * delta_time)

            for platform in platforms:
                if not self.rect.colliderect(platform):
                    continue
                if self.velocity_y >= 0 and previous_bottom <= platform.top:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0 and self.rect.top < platform.bottom:
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

        self._update_animation(delta_time, direction)

    def _update_animation(self, delta_time: float, direction: int) -> None:
        next_animation = "air" if not self.on_ground else "walk" if direction else "idle"
        if next_animation != self.animation:
            self.animation = next_animation
            self.frame_index = 0
            self.animation_timer = 0.0

        frames = self.ANIMATIONS[self.animation]
        frame_duration = 0.12 if self.animation == "walk" else 0.2
        self.animation_timer += delta_time
        if self.animation_timer >= frame_duration:
            self.animation_timer %= frame_duration
            self.frame_index = (self.frame_index + 1) % len(frames)

        frame = self.frames[frames[self.frame_index]]
        scaled = pygame.transform.scale(frame, self.image_size)
        self._animation_image = (
            scaled if self.facing_right else pygame.transform.flip(scaled, True, False)
        )

    def draw(self, surface: pygame.Surface) -> None:
        draw_rect = self._animation_image.get_rect(
            midbottom=(self.rect.centerx, self.rect.bottom)
        )
        surface.blit(self._animation_image, draw_rect)
