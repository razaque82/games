import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32
PLAYER_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

class AnimatedSprite:
    def __init__(self, width, height):
        self.animation_frames = []
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_delay = 100
        self.width = width
        self.height = height
        
    def add_animation_frame(self, color):
        # Ensure color values are within valid range (0-255)
        color = tuple(max(0, min(255, c)) for c in color)
        surface = pygame.Surface((self.width, self.height))
        surface.fill(color)
        pygame.draw.circle(surface, WHITE, 
                         (self.width//2, self.height//2), 
                         self.width//4)
        self.animation_frames.append(surface)
    
    def update_animation(self):
        if not self.animation_frames:
            return pygame.Surface((self.width, self.height))
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_delay:
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            self.animation_timer = current_time
        return self.animation_frames[self.animation_index]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animator = AnimatedSprite(TILE_SIZE, TILE_SIZE)
        # Create player animation frames with valid colors
        colors = [(0, 0, 200), (0, 0, 220), (0, 0, 240), (0, 0, 255)]
        for color in colors:
            self.animator.add_animation_frame(color)
        self.image = self.animator.animation_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.monsters = []
        self.in_battle = False
        self.energy = 100
        self.experience = 0
        self.level = 1
        
    def move(self, dx, dy):
        self.rect.x += dx * PLAYER_SPEED
        self.rect.y += dy * PLAYER_SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.image = self.animator.update_animation()
        if dx != 0 or dy != 0:
            self.energy = max(0, self.energy - 0.1)

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, creature_type="wild"):
        super().__init__()
        self.type = creature_type
        self.animator = AnimatedSprite(TILE_SIZE, TILE_SIZE)
        
        base_colors = {
            "crystal": [(200, 200, 255), (180, 180, 255)],
            "shadow": [(100, 0, 100), (80, 0, 80)],
            "nature": [(0, 180, 0), (0, 150, 0)],
            "wild": [(150, 75, 0), (130, 65, 0)]
        }
        
        colors = base_colors.get(creature_type, base_colors["wild"])
        for color in colors:
            self.animator.add_animation_frame(color)
        
        self.image = self.animator.animation_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 100
        self.attack = random.randint(8, 12)
        self.defense = random.randint(4, 6)
        self.level = 1
        self.unique_ability = random.choice([
            "energy_drain", "healing", "double_attack",
            "shield", "counter_attack"
        ])
        
    def update(self):
        self.image = self.animator.update_animation()
        if random.random() < 0.02:
            self.rect.x += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.y += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

class Game:
    def __init__(self):
        self.player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.all_sprites = pygame.sprite.Group()
        self.creatures = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.spawn_creatures()
        self.font = pygame.font.Font(None, 36)
        self.battle_creature = None
        self.game_state = "exploring"
        
    def spawn_creatures(self):
        creature_types = ["crystal", "shadow", "nature"]
        for _ in range(5):
            x = random.randint(0, WINDOW_WIDTH - TILE_SIZE)
            y = random.randint(0, WINDOW_HEIGHT - TILE_SIZE)
            creature_type = random.choice(creature_types)
            creature = Creature(x, y, creature_type)
            self.creatures.add(creature)
            self.all_sprites.add(creature)
    
    def handle_battle(self):
        if not self.battle_creature:
            return False
        
        player_creature = self.player.monsters[0] if self.player.monsters else None
        if not player_creature:
            return False
            
        damage_to_enemy = max(0, player_creature.attack - self.battle_creature.defense)
        self.battle_creature.hp -= damage_to_enemy
        
        if self.battle_creature.hp <= 0:
            self.player.experience += 10
            if self.player.experience >= 100:
                self.player.level += 1
                self.player.experience = 0
            return True
        return False

    def draw_battle_screen(self):
        screen.fill(WHITE)
        
        if self.battle_creature:
            pygame.draw.rect(screen, RED, (100, 150, 100, 100))
            hp_text = self.font.render(f"HP: {self.battle_creature.hp}", True, BLACK)
            screen.blit(hp_text, (100, 260))
        
        if self.player.monsters:
            pygame.draw.rect(screen, BLUE, (WINDOW_WIDTH-200, 300, 100, 100))
            hp_text = self.font.render(f"HP: {self.player.monsters[0].hp}", True, BLACK)
            screen.blit(hp_text, (WINDOW_WIDTH-200, 410))
        
        pygame.draw.rect(screen, (200, 200, 200), (50, 450, 700, 100))
        
        attack_text = self.font.render("1: Attack", True, BLACK)
        catch_text = self.font.render("2: Catch", True, BLACK)
        run_text = self.font.render("3: Run", True, BLACK)
        
        screen.blit(attack_text, (100, 475))
        screen.blit(catch_text, (300, 475))
        screen.blit(run_text, (500, 475))
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "battle":
                        if event.key == pygame.K_1:  # Attack
                            if self.handle_battle():
                                self.game_state = "exploring"
                                self.battle_creature = None
                        elif event.key == pygame.K_2:  # Catch
                            catch_chance = (100 - self.battle_creature.hp) / 100
                            if random.random() < catch_chance:
                                self.player.monsters.append(self.battle_creature)
                                self.creatures.remove(self.battle_creature)
                                self.all_sprites.remove(self.battle_creature)
                            self.game_state = "exploring"
                            self.battle_creature = None
                        elif event.key == pygame.K_3:  # Run
                            self.game_state = "exploring"
                            self.battle_creature = None
            
            if self.game_state == "exploring":
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
                self.player.move(dx, dy)
                
                self.creatures.update()
                
                hits = pygame.sprite.spritecollide(self.player, self.creatures, False)
                if hits and not self.player.in_battle:
                    self.battle_creature = hits[0]
                    self.game_state = "battle"
                
                screen.fill(GREEN)
                self.all_sprites.draw(screen)
                
                stats_text = self.font.render(
                    f"Energy: {int(self.player.energy)} | Level: {self.player.level} | Creatures: {len(self.player.monsters)}",
                    True, BLACK
                )
                screen.blit(stats_text, (10, 10))
            
            elif self.game_state == "battle":
                self.draw_battle_screen()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Creature Collectors")
    game = Game()
    game.run()
