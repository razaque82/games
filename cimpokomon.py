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

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Creature Tamers")

class AnimatedSprite:
    def __init__(self, width, height):
        self.animation_frames = []
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_delay = 100  # milliseconds
        self.width = width
        self.height = height
        
    def add_animation_frame(self, color):
        # Create a unique pattern for each frame
        surface = pygame.Surface((self.width, self.height))
        surface.fill(color)
        # Add some unique patterns
        pygame.draw.circle(surface, (255, 255, 255), 
                         (self.width//2, self.height//2), 
                         self.width//4)
        self.animation_frames.append(surface)
    
    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_delay:
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            self.animation_timer = current_time
        
        return self.animation_frames[self.animation_index]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animator = AnimatedSprite(TILE_SIZE, TILE_SIZE)
        # Create unique player animation frames
        for i in range(4):
            self.animator.add_animation_frame((0, 0, 200 + i * 20))
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
        
        # Update animation
        self.image = self.animator.update_animation()
        
        # Decrease energy when moving
        if dx != 0 or dy != 0:
            self.energy = max(0, self.energy - 0.1)

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, creature_type="wild"):
        super().__init__()
        self.type = creature_type
        self.animator = AnimatedSprite(TILE_SIZE, TILE_SIZE)
        
        # Create unique patterns for each creature type
        base_colors = {
            "crystal": [(200, 200, 255), (180, 180, 255)],  # Crystal type
            "shadow": [(100, 0, 100), (80, 0, 80)],        # Shadow type
            "nature": [(0, 180, 0), (0, 150, 0)],          # Nature type
            "wild": [(150, 75, 0), (130, 65, 0)]           # Wild type
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
        
        # Random movement for wild creatures
        if random.random() < 0.02:
            self.rect.x += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.y += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(10):
            particle = {
                'x': x,
                'y': y,
                'dx': random.uniform(-2, 2),
                'dy': random.uniform(-2, 2),
                'lifetime': random.randint(20, 40),
                'color': color
            }
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'],
                             (int(particle['x']), int(particle['y'])), 2)

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
        self.effects = []
        self.time_of_day = 0  # 0-24000 represents 24 hours
        self.weather = "clear"
        self.weather_timer = 0
        
    def spawn_creatures(self):
        creature_types = ["crystal", "shadow", "nature"]
        for _ in range(5):
            x = random.randint(0, WINDOW_WIDTH - TILE_SIZE)
            y = random.randint(0, WINDOW_HEIGHT - TILE_SIZE)
            creature_type = random.choice(creature_types)
            creature = Creature(x, y, creature_type)
            self.creatures.add(creature)
            self.all_sprites.add(creature)
    
    def update_environment(self):
        # Update time of day
        self.time_of_day = (self.time_of_day + 10) % 24000
        
        # Update weather
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            self.weather = random.choice(["clear", "rain", "fog"])
            self.weather_timer = random.randint(300, 600)
    
    def draw_environment(self):
        # Create day/night cycle effect
        darkness = abs(12000 - self.time_of_day) / 12000.0
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 50))
        overlay.set_alpha(int(darkness * 128))
        screen.blit(overlay, (0, 0))
        
        # Draw weather effects
        if self.weather == "rain":
            for _ in range(10):
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                pygame.draw.line(screen, (200, 200, 255),
                               (x, y), (x-5, y+10), 2)
        elif self.weather == "fog":
            fog = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fog.fill((255, 255, 255))
            fog.set_alpha(64)
            screen.blit(fog, (0, 0))
    
    def handle_battle(self):
        if not self.battle_creature:
            return
            
        # Battle stats
        player_creature = self.player.monsters[0] if self.player.monsters else None
        if not player_creature:
            return
            
        damage_to_enemy = max(0, player_creature.attack - self.battle_creature.defense)
        self.battle_creature.hp -= damage_to_enemy
        
        # Create attack effect
        self.effects.append(ParticleEffect(
            self.battle_creature.rect.centerx,
            self.battle_creature.rect.centery,
            (255, 0, 0)))
        
        if self.battle_creature.hp <= 0:
            self.player.experience += 10
            if self.player.experience >= 100:
                self.player.level += 1
                self.player.experience = 0
            return True
        return False

    def draw_battle_screen(self):
        screen.fill((200, 200, 255))
        
        # Draw battle arena
        pygame.draw.rect(screen, (100, 200, 100),
                        (50, 100, WINDOW_WIDTH-100, WINDOW_HEIGHT-250))
        
        # Draw creatures
        if self.battle_creature:
            pygame.draw.rect(screen, (255, 0, 0),
                           (100, 150, 100, 100))
            hp_text = self.font.render(f"HP: {self.battle_creature.hp}",
                                     True, BLACK)
            screen.blit(hp_text, (100, 260))
        
        if self.player.monsters:
            pygame.draw.rect(screen, (0, 0, 255),
                           (WINDOW_WIDTH-200, 300, 100, 100))
            hp_text = self.font.render(f"HP: {self.player.monsters[0].hp}",
                                     True, BLACK)
            screen.blit(hp_text, (WINDOW_WIDTH-200, 410))
        
        # Draw battle menu
        pygame.draw.rect(screen, (230, 230, 230),
                        (50, WINDOW_HEIGHT-120, WINDOW_WIDTH-100, 100))
        
        # Draw battle options with improved visuals
        options = ["1: Attack", "2: Special", "3: Catch", "4: Run"]
        for i, text in enumerate(options):
            text_surface = self.font.render(text, True, BLACK)
            screen.blit(text_surface, (100 + i*180, WINDOW_HEIGHT-90))
        
        # Update and draw particle effects
        for effect in self.effects[:]:
            effect.update()
            effect.draw(screen)
            if not effect.particles:
                self.effects.remove(effect)
    
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
                        elif event.key == pygame.K_2:  # Special ability
                            # Implement special ability logic
                            pass
                        elif event.key == pygame.K_3:  # Catch
                            catch_chance = (100 - self.battle_creature.hp) / 100
                            if random.random() < catch_chance:
                                self.player.monsters.append(self.battle_creature)
                                self.creatures.remove(self.battle_creature)
                                self.all_sprites.remove(self.battle_creature)
                                # Create catch effect
                                self.effects.append(ParticleEffect(
                                    self.battle_creature.rect.centerx,
                                    self.battle_creature.rect.centery,
                                    (0, 255, 255)))
                            self.game_state = "exploring"
                            self.battle_creature = None
                        elif event.key == pygame.K_4:  # Run
                            self.game_state = "exploring"
                            self.battle_creature = None
            
            # Update game state
            self.update_environment()
            
            if self.game_state == "exploring":
                # Player movement
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
                self.player.move(dx, dy)
                
                # Update creatures
                self.creatures.update()
                
                # Check for collisions
                hits = pygame.sprite.spritecollide(self.player, self.creatures, False)
                if hits and not self.player.in_battle:
                    self.battle_creature = hits[0]
                    self.game_state = "battle"
                
                # Draw exploring screen
                screen.fill(GREEN)
                self.draw_environment()
                self.all_sprites.draw(screen)
                
                # Draw UI
                energy_text = self.font.render(f"Energy: {int(self.player.energy)}",
                                             True, BLACK)
                level_text = self.font.render(f"Level: {self.player.level}",
                                            True, BLACK)
                monster_text = self.font.render(f"Creatures: {len(self.player.monsters)}",
                                              True, BLACK)
                screen.blit(energy_text, (10, 10))
                screen.blit(level_text, (10, 50))
                screen.blit(monster_text, (10, 90))
            
            elif self.game_state == "battle":
                self.draw_battle_screen()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
