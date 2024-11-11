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
GRAY = (200, 200, 200)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
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
        if dx != 0 or dy != 0:
            self.energy = max(0, self.energy - 0.1)

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, creature_type="wild"):
        super().__init__()
        self.type = creature_type
        color_map = {
            "crystal": (200, 200, 255),
            "shadow": (100, 0, 100),
            "nature": (0, 180, 0),
            "wild": (150, 75, 0)
        }
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color_map.get(creature_type, color_map["wild"]))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 100
        self.max_hp = 100
        self.attack = random.randint(8, 12)
        self.defense = random.randint(4, 6)
        self.level = 1
        
    def update(self):
        if random.random() < 0.02:
            self.rect.x += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.y += random.randint(-1, 1) * PLAYER_SPEED
            self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Creature Collectors")
        self.player = Player(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.all_sprites = pygame.sprite.Group()
        self.creatures = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.spawn_creatures()
        self.font = pygame.font.Font(None, 36)
        self.battle_creature = None
        self.game_state = "exploring"
        self.message = ""
        self.message_timer = 0
        
    def spawn_creatures(self):
        creature_types = ["crystal", "shadow", "nature"]
        for _ in range(5):
            x = random.randint(0, WINDOW_WIDTH - TILE_SIZE)
            y = random.randint(0, WINDOW_HEIGHT - TILE_SIZE)
            creature_type = random.choice(creature_types)
            creature = Creature(x, y, creature_type)
            self.creatures.add(creature)
            self.all_sprites.add(creature)
    
    def show_message(self, text, duration=60):
        self.message = text
        self.message_timer = duration

    def handle_battle_action(self, action):
        if action == "attack":
            damage = random.randint(20, 30)
            self.battle_creature.hp -= damage
            self.show_message(f"Dealt {damage} damage!")
            if self.battle_creature.hp <= 0:
                self.show_message("Enemy defeated!")
                self.game_state = "exploring"
                self.battle_creature = None
                self.player.experience += 10
                if self.player.experience >= 100:
                    self.player.level += 1
                    self.player.experience = 0
                    
        elif action == "catch":
            catch_chance = (self.battle_creature.max_hp - self.battle_creature.hp) / self.battle_creature.max_hp
            if random.random() < catch_chance:
                self.player.monsters.append(self.battle_creature)
                self.creatures.remove(self.battle_creature)
                self.all_sprites.remove(self.battle_creature)
                self.show_message("Creature caught!")
            else:
                self.show_message("Catch failed!")
            self.game_state = "exploring"
            self.battle_creature = None
            
        elif action == "run":
            self.show_message("Got away safely!")
            self.game_state = "exploring"
            self.battle_creature = None

    def draw_battle_screen(self):
        self.screen.fill(WHITE)
        
        # Draw enemy creature
        if self.battle_creature:
            enemy_rect = pygame.Rect(100, 100, 100, 100)
            pygame.draw.rect(self.screen, RED, enemy_rect)
            
            # HP bar
            hp_percent = max(0, self.battle_creature.hp / self.battle_creature.max_hp)
            hp_width = 100 * hp_percent
            pygame.draw.rect(self.screen, RED, (100, 80, hp_width, 10))
            pygame.draw.rect(self.screen, BLACK, (100, 80, 100, 10), 1)
            
            hp_text = self.font.render(f"HP: {self.battle_creature.hp}", True, BLACK)
            self.screen.blit(hp_text, (100, 210))
        
        # Battle menu
        menu_rect = pygame.Rect(50, WINDOW_HEIGHT - 150, WINDOW_WIDTH - 100, 100)
        pygame.draw.rect(self.screen, GRAY, menu_rect)
        
        # Battle options
        options = ["1: Attack", "2: Catch", "3: Run"]
        for i, text in enumerate(options):
            text_surface = self.font.render(text, True, BLACK)
            self.screen.blit(text_surface, (100 + i * 200, WINDOW_HEIGHT - 120))
        
        # Show message if any
        if self.message and self.message_timer > 0:
            msg_surface = self.font.render(self.message, True, BLACK)
            self.screen.blit(msg_surface, (WINDOW_WIDTH//2 - 100, 50))
            self.message_timer -= 1
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.game_state == "battle":
                        if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                            print("Attack key pressed")
                            self.handle_battle_action("attack")
                        elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                            print("Catch key pressed")
                            self.handle_battle_action("catch")
                        elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                            print("Run key pressed")
                            self.handle_battle_action("run")
            
            # Game state updates
            if self.game_state == "exploring":
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
                self.player.move(dx, dy)
                
                self.creatures.update()
                
                # Check for collisions
                hits = pygame.sprite.spritecollide(self.player, self.creatures, False)
                if hits:
                    self.battle_creature = hits[0]
                    self.game_state = "battle"
                    self.show_message("Battle started!")
                
                # Draw exploring screen
                self.screen.fill(GREEN)
                self.all_sprites.draw(self.screen)
                
                # Draw stats
                stats_text = self.font.render(
                    f"Level: {self.player.level}  XP: {self.player.experience}  Creatures: {len(self.player.monsters)}",
                    True, BLACK
                )
                self.screen.blit(stats_text, (10, 10))
                
            elif self.game_state == "battle":
                self.draw_battle_screen()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
