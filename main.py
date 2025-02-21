import pygame
import random

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(pygame.sprite.Sprite):
    """Player controlled sprite"""

    def __init__(self):
        """Initialize player"""
        super().__init__()

        # Create a circular player image
        radius = 20
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (radius, radius), radius)

        # Set a reference to the image rect
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

        # Player score
        self.score = 0

        # Player life
        self.life = 5

    def update(self):
        """Update player position"""
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # Check for horizontal collisions
        block_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False
        )
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check for vertical collisions
        block_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False
        )
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop vertical movement
            self.change_y = 0

        # Check if player touches lava
        if pygame.sprite.collide_rect(self, self.level.lava):
            self.life -= 1
            self.rect.y = 0  # Reset player position
            if self.life <= 0:
                self.life = 0
                # Game over logic can be added here

    def calc_grav(self):
        """Calculate gravity effect"""
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

        # Check if on the ground
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """Make the player jump"""
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False
        )
        self.rect.y -= 2

        # Check if the player is on a platform or the ground
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    def go_left(self):
        """Move player left"""
        self.change_x = -6

    def go_right(self):
        """Move player right"""
        self.change_x = 6

    def stop(self):
        """Stop player movement"""
        self.change_x = 0


class Platform(pygame.sprite.Sprite):
    """Platform the player can jump on"""

    def __init__(self, width, height):
        """Initialize platform"""
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(ORANGE)

        self.rect = self.image.get_rect()


class Coin(pygame.sprite.Sprite):
    """Coin that the player can collect"""

    def __init__(self):
        """Initialize coin"""
        super().__init__()

        # Create a circular coin image
        radius = 10
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (radius, radius), radius)

        # Set a reference to the image rect
        self.rect = self.image.get_rect()


class Lava(pygame.sprite.Sprite):
    """Lava at the bottom of the screen"""

    def __init__(self):
        """Initialize lava"""
        super().__init__()

        self.image = pygame.Surface([SCREEN_WIDTH, 20])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.y = SCREEN_HEIGHT - 20


class Level:
    """Generic level class"""

    def __init__(self, player):
        """Initialize level"""
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.player = player

        # Lava
        self.lava = Lava()

        # World shift
        self.world_shift = 0

        # Load background image
        self.background = pygame.image.load("assets/green_forest.png").convert()

    def update(self):
        """Update level"""
        self.platform_list.update()
        self.enemy_list.update()
        self.coin_list.update()

        # Check for coin collection
        coin_hit_list = pygame.sprite.spritecollide(self.player, self.coin_list, True)
        for coin in coin_hit_list:
            self.player.score += 1

    def draw(self, screen):
        """Draw level"""
        screen.blit(self.background, (0, 0))
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.coin_list.draw(screen)
        screen.blit(self.lava.image, self.lava.rect)

    def shift_world(self, shift_x):
        """Shift the world"""
        self.world_shift += shift_x

        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for coin in self.coin_list:
            coin.rect.x += shift_x


class Level_01(Level):
    """Level 1"""

    def __init__(self, player):
        """Create Level 1"""
        Level.__init__(self, player)

        self.level_limit = -2000

        # Platform Layout
        level = [
            [210, 30, 220, 520],
            [210, 30, 500, 450],
            [210, 30, 800, 400],
            [210, 30, 1100, 500],
            [210, 30, 1390, 380],
            [210, 30, 1700, 280],
            [210, 30, 2000, 500],
            [210, 30, 2300, 440],
            [210, 30, 2600, 360],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add Coins (Randomly choose 1 to 4 platforms for coins)
        num_coins = random.randint(1, min(4, len(level)))
        selected_platforms = random.sample(level, num_coins)

        for platform in selected_platforms:
            coin = Coin()
            coin.rect.x = platform[2] + random.randint(0, platform[0] - 20)
            coin.rect.y = platform[3] - 30
            self.coin_list.add(coin)


class Level_02(Level):
    """Level 2"""

    def __init__(self, player):
        """Create Level 2"""
        Level.__init__(self, player)

        self.level_limit = -2000

        # Platform Layout
        level = [
            [210, 30, 330, 470],
            [210, 30, 620, 380],
            [210, 30, 900, 420],
            [210, 30, 1100, 290],
            [210, 30, 1400, 180],
            [210, 30, 1700, 380],
            [210, 30, 2100, 430],
            [210, 30, 2400, 330],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add Coins (Randomly choose 1 to 4 platforms for coins)
        num_coins = random.randint(1, min(4, len(level)))
        selected_platforms = random.sample(level, num_coins)

        for platform in selected_platforms:
            coin = Coin()
            coin.rect.x = platform[2] + random.randint(0, platform[0] - 20)
            coin.rect.y = platform[3] - 30
            self.coin_list.add(coin)


class Level_03(Level):
    """Level 3"""

    def __init__(self, player):
        """Create level 3"""
        Level.__init__(self, player)

        self.level_limit = -2000

        # Platform layout
        level = [
            [210, 30, 150, 550],
            [210, 30, 500, 500],
            [210, 30, 800, 400],
            [210, 30, 1100, 300],
            [210, 30, 1360, 380],
            [210, 30, 1600, 250],
            [210, 30, 1900, 350],
            [210, 30, 2200, 300],
            [210, 30, 2550, 270],
            
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add Coins (Randomly choose 1 to 4 platforms for coins)
        num_coins = random.randint(1, min(4, len(level)))
        selected_platforms = random.sample(level, num_coins)

        for platform in selected_platforms:
            coin = Coin()
            coin.rect.x = platform[2] + random.randint(0, platform[0] - 20)
            coin.rect.y = platform[3] - 30
            self.coin_list.add(coin)


class Level_04(Level):
    """Level 4"""

    def __init__(self, player):
        """Create level 4"""
        Level.__init__(self, player)

        self.level_limit = -2000

        # Platform layout
        level = [
            [210, 30, 190, 500],
            [210, 30, 400, 410],
            [210, 30, 700, 340],
            [210, 30, 950, 250],
            [210, 30, 1300, 180],
            [210, 30, 1900, 220],
            [210, 30, 2200, 175],
            [210, 30, 2800, 280],
            [210, 30, 3300, 250],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add Coins (Randomly choose 1 to 4 platforms for coins)
        num_coins = random.randint(1, min(4, len(level)))
        selected_platforms = random.sample(level, num_coins)

        for platform in selected_platforms:
            coin = Coin()
            coin.rect.x = platform[2] + random.randint(0, platform[0] - 20)
            coin.rect.y = platform[3] - 30
            self.coin_list.add(coin)


class Level_05(Level):
    """Level 5"""

    def __init__(self, player):
        """Create level 5"""
        Level.__init__(self, player)

        self.level_limit = -2000

        # Platform layout
        level = [
            [210, 30, 500, 500],
            [210, 30, 800, 400],
            [210, 30, 1100, 300],
            [210, 30, 1360, 380],
            [210, 30, 1600, 250],
            [210, 30, 1900, 350],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add Coins (Randomly choose 1 to 4 platforms for coins)
        num_coins = random.randint(1, min(4, len(level)))
        selected_platforms = random.sample(level, num_coins)

        for platform in selected_platforms:
            coin = Coin()
            coin.rect.x = platform[2] + random.randint(0, platform[0] - 20)
            coin.rect.y = platform[3] - 30
            self.coin_list.add(coin)


def main():
    """Main program"""
    pygame.init()

    # Set screen size
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Side-scrolling Platformer")

    # Create player
    player = Player()

    # Create levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))
    level_list.append(Level_04(player))
    level_list.append(Level_05(player))

    # Set current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    done = False
    clock = pygame.time.Clock()

    # Font for displaying score, life, and level
    font = pygame.font.Font(None, 36)

    # Main game loop
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Update player
        active_sprite_list.update()

        # Update level
        current_level.update()

        # Shift world if player is near the right side
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # Shift world if player is near the left side
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)

        # Go to next level if player reaches the end
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_no < len(level_list) - 1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level

        # Draw everything
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # Display score, life, and level
        score_text = font.render(f"Coins: {player.score}", True, BLACK)
        life_text = font.render(f"Life: {player.life}", True, BLACK)
        level_text = font.render(f"Level: {current_level_no + 1}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(life_text, (10, 50))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))

        # Limit to 60 frames per second
        clock.tick(60)

        # Update screen
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
