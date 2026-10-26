import math
from array import array
from typing import Literal

import pygame

SoundName = Literal["menu", "jump", "crystal", "death", "portal"]


class SoundEffects:
    def __init__(self, sample_rate: int, volume: float) -> None:
        self.sounds: dict[SoundName, pygame.mixer.Sound] = {
            "menu": self._make_tone(sample_rate, 520, 680, 0.06, volume),
            "jump": self._make_tone(sample_rate, 300, 520, 0.12, volume),
            "crystal": self._make_tone(sample_rate, 880, 1320, 0.16, volume),
            "death": self._make_death_sound(sample_rate, min(1.0, volume * 2.8)),
            "portal": self._make_tone(sample_rate, 420, 900, 0.32, volume),
        }

    @staticmethod
    def _make_tone(
        sample_rate: int,
        start_frequency: float,
        end_frequency: float,
        duration: float,
        volume: float,
    ) -> pygame.mixer.Sound:
        sample_count = round(sample_rate * duration)
        samples = array("h")
        phase = 0.0

        for index in range(sample_count):
            progress = index / sample_count
            frequency = start_frequency + (end_frequency - start_frequency) * progress
            phase += 2 * math.pi * frequency / sample_rate
            envelope = math.sin(math.pi * progress) ** 2
            sample = round(32767 * volume * envelope * math.sin(phase))
            samples.extend((sample, sample))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    @staticmethod
    def _make_death_sound(sample_rate: int, volume: float) -> pygame.mixer.Sound:
        duration = 0.55
        sample_count = round(sample_rate * duration)
        samples = array("h")
        phase = 0.0

        for index in range(sample_count):
            progress = index / sample_count
            frequency = 720 - 480 * progress
            phase += 2 * math.pi * frequency / sample_rate
            envelope = min(1.0, index / (sample_rate * 0.025)) * (1 - progress) ** 0.65
            waveform = (
                math.sin(phase)
                + 0.35 * math.sin(2 * phase)
                + 0.15 * math.sin(3 * phase)
            )
            sample = round(32767 * volume * envelope * waveform / 1.5)
            sample = max(-32768, min(32767, sample))
            samples.extend((sample, sample))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, sound: SoundName) -> None:
        self.sounds[sound].play()
