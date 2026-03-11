import pygame
import math

# Base palette
BASE_BG          = (5,  8, 20)          # very dark navy  (replaces pure black)
BASE_HUD         = (0, 230, 210)        # neon cyan
BASE_SCORE       = (180, 255, 100)      # lime-green score text
BASE_BULLET      = (0, 220, 255)        # bright cyan bullets  (replaces WHITE)
BASE_SP_BULLET   = (255, 50, 120)       # hot-pink special bullet (replaces RED)
BASE_COOLDOWN_OK = (0, 200, 100)        # green bar when ready

#Effect overlay colours
DAMAGE_FLASH_COLOR   = (255,  20,  20, 120)   # red flash on hit
INVULN_PULSE_COLOR   = (80,  160, 255,  60)   # blue shimmer while invulnerable
POWERUP_SHIELD_COLOR = (40,  200, 255,  70)   # cyan wash for shield
POWERUP_PLUS_COLOR   = (60,  255,  80,  80)   # green wash for extra life
BOMB_SHOCKWAVE_COLOR = (255, 160,   0, 150)   # orange blast for bomb
MINUTE_ALERT_COLOR   = (255, 255,   0,  80)   # yellow pulse at difficulty spike


class ColorTheme:
    def __init__(self):
        self._effects = {}  
        self._base_bullet      = BASE_BULLET
        self._base_sp_bullet   = BASE_SP_BULLET

    def trigger_damage_flash(self, duration_ms: int = 300):
        """Red screen flash when player is hit."""
        self._set_effect('damage_flash', DAMAGE_FLASH_COLOR, duration_ms)

    def trigger_invuln_pulse(self, duration_ms: int = 3000):
        """Blue shimmer overlay while player is invulnerable."""
        self._set_effect('invuln', INVULN_PULSE_COLOR, duration_ms)

    def trigger_powerup_shield(self, duration_ms: int = 5000):
        """Cyan wash for shield powerup."""
        self._set_effect('shield', POWERUP_SHIELD_COLOR, duration_ms)

    def trigger_powerup_plus(self, duration_ms: int = 600):
        """Short green flash for extra-life pickup."""
        self._set_effect('plus', POWERUP_PLUS_COLOR, duration_ms)

    def trigger_bomb(self, duration_ms: int = 500):
        """Orange shockwave for bomb powerup."""
        self._set_effect('bomb', BOMB_SHOCKWAVE_COLOR, duration_ms)

    def trigger_minute_alert(self, duration_ms: int = 1200):
        """Yellow pulse when difficulty increases each minute."""
        self._set_effect('minute', MINUTE_ALERT_COLOR, duration_ms)
    def update(self):
        """Expire old effects. Call once per frame."""
        now = pygame.time.get_ticks()
        expired = [k for k, v in self._effects.items() if v['end_ms'] <= now]
        for k in expired:
            del self._effects[k]

    def get_screen_overlay(self):
        priority = ['damage_flash', 'bomb', 'shield', 'invuln', 'plus', 'minute']
        now = pygame.time.get_ticks()
        for key in priority:
            if key in self._effects:
                eff = self._effects[key]
                total   = eff['end_ms'] - eff['start_ms']
                elapsed = now - eff['start_ms']
                t = max(0.0, min(1.0, elapsed / total))
                alpha_scale = 1.0 - t if t > 0.5 else 1.0
                r, g, b, a = eff['color']
                final_a = int(a * alpha_scale)
                if final_a > 0:
                    return (r, g, b, final_a)
        return None

    def get_hud_color(self):
        """Returns the colour to use for lives / time HUD text."""
        if 'damage_flash' in self._effects:
            return (255, 80, 80)
        if 'invuln' in self._effects:
            return (120, 200, 255)
        return BASE_HUD

    def get_score_color(self):
        return BASE_SCORE

    def get_bullet_color(self):
        """Bullet colour shifts during bomb / special states."""
        if 'bomb' in self._effects:
            return (255, 200, 0)
        return self._base_bullet

    def get_special_bullet_color(self):
        if 'shield' in self._effects:
            return (80, 255, 200)
        return self._base_sp_bullet

    def get_cooldown_bar_colors(self, progress: float):
        """
        Returns (bg_color, fill_color) for the dash cooldown bar.
        progress: 0.0 = just used, 1.0 = fully recharged.
        """
        if progress >= 1.0:
            return ((40, 40, 40), BASE_COOLDOWN_OK)
        r = int(200 * (1 - progress))
        g = int(200 * progress)
        return ((40, 40, 40), (r, g, 40))

    def get_background_color(self):
        return BASE_BG

    def get_game_over_color(self):
        """Pulsing magenta tint for game-over screen."""
        t = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2
        r = int(180 + 75 * t)
        g = int(20  + 20 * t)
        b = int(80  + 40 * t)
        return (r, g, b)
    def _set_effect(self, key: str, color, duration_ms: int):
        now = pygame.time.get_ticks()
        self._effects[key] = {
            'color':    color,
            'start_ms': now,
            'end_ms':   now + duration_ms,
        }

    def draw_overlay(self, screen):
        """
        Convenience: blit a semi-transparent colour wash over the given
        surface if any effect is active. Call after drawing all sprites.
        """
        overlay = self.get_screen_overlay()
        if overlay:
            surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            surf.fill(overlay)
            screen.blit(surf, (0, 0))

theme = ColorTheme()