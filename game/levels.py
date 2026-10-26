from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class LevelSpec:
    name: str
    spawn: tuple[int, int]
    platforms: tuple[tuple[int, int, int], ...]
    traps: tuple[tuple[int, int], ...]
    lasers: tuple[pygame.Rect, ...]
    crystals: tuple[tuple[int, int], ...]
    portal: tuple[int, int]


LEVELS = (
    LevelSpec(
        name="NEBULA OUTPOST",
        spawn=(80, 448),
        platforms=((0, 448, 220), (260, 390, 180), (500, 330, 180), (760, 390, 200)),
        traps=(),
        lasers=(),
        crystals=((150, 402), (340, 344), (580, 284), (820, 344)),
        portal=(872, 294),
    ),
    LevelSpec(
        name="ELECTRIC CHANNEL",
        spawn=(80, 448),
        platforms=((0, 448, 180), (230, 390, 170), (430, 330, 180), (690, 390, 170), (860, 320, 100)),
        traps=((130, 448), (500, 330), (735, 390)),
        lasers=(),
        crystals=((70, 402), (280, 344), (445, 284), (690, 344), (870, 276)),
        portal=(914, 220),
    ),
    LevelSpec(
        name="RIFT FINALE",
        spawn=(35, 448),
        platforms=(
            (0, 448, 210),
            (245, 380, 180),
            (440, 312, 180),
            (610, 244, 190),
            (850, 480, 110),
        ),
        traps=((180, 448),),
        lasers=(
            pygame.Rect(400, 320, 12, 60),
            pygame.Rect(525, 280, 55, 12),
            pygame.Rect(770, 184, 12, 60),
        ),
        crystals=((55, 402), (250, 334), (455, 266), (655, 198), (875, 434)),
        portal=(868, 384),
    ),
)


class GameLevel:
    def __init__(
        self,
        spec: LevelSpec,
        tile: pygame.Surface,
        trap_image: pygame.Surface,
        laser_image: pygame.Surface,
        portal_image: pygame.Surface,
        crystal_frames: tuple[pygame.Surface, ...],
    ) -> None:
        self.spec = spec
        self.platforms = [
            pygame.Rect(x, y, width, 32) for x, y, width in spec.platforms
        ]
        self.traps = [
            pygame.Rect(x + 5, y - 16, 38, 16) for x, y in spec.traps
        ]
        self.lasers = list(spec.lasers)
        self.crystal_frames = crystal_frames
        self.crystals = list(spec.crystals)
        self.collected: set[int] = set()
        self.crystal_frame_index = 0
        self.crystal_animation_timer = 0.0
        self.portal_rect = pygame.Rect(*spec.portal, 72, 96)
        self.tile = tile
        self.trap_image = trap_image
        self.laser_image = laser_image
        self.portal_image = portal_image

    def update(self, delta_time: float) -> None:
        self.crystal_animation_timer += delta_time
        if self.crystal_animation_timer >= 0.12:
            self.crystal_animation_timer %= 0.12
            self.crystal_frame_index = (
                self.crystal_frame_index + 1
            ) % len(self.crystal_frames)

    def collect_crystals(self, player_rect: pygame.Rect) -> None:
        for index, (x, y) in enumerate(self.crystals):
            crystal_rect = pygame.Rect(x, y, 32, 32)
            if index not in self.collected and player_rect.colliderect(crystal_rect):
                self.collected.add(index)

    def touches_hazard(self, player_rect: pygame.Rect) -> bool:
        return any(player_rect.colliderect(hazard) for hazard in (*self.traps, *self.lasers))

    def draw(self, surface: pygame.Surface) -> None:
        for platform in self.platforms:
            for x in range(platform.left, platform.right, self.tile.get_width()):
                surface.blit(self.tile, (x, platform.top))
                surface.blit(self.tile, (x, platform.top + self.tile.get_height()))

        for x, y in self.spec.traps:
            surface.blit(self.trap_image, (x, y - self.trap_image.get_height()))

        for laser in self.lasers:
            if laser.height > laser.width:
                image = pygame.transform.rotate(self.laser_image, 90)
            else:
                image = self.laser_image
            surface.blit(pygame.transform.scale(image, laser.size), laser)

        crystal_image = self.crystal_frames[self.crystal_frame_index]
        for index, (x, y) in enumerate(self.crystals):
            if index not in self.collected:
                surface.blit(crystal_image, (x, y))

        surface.blit(
            pygame.transform.scale(self.portal_image, self.portal_rect.size),
            self.portal_rect,
        )
