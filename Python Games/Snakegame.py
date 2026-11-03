import os
import sys
import time
import random
import msvcrt
from collections import deque

class SnakeGame:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.snake = deque([(width//2, height//2)])
        self.direction = (1, 0)  # Start moving right
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
    def generate_food(self):
        while True:
            food = (random.randint(1, self.width-2), random.randint(1, self.height-2))
            if food not in self.snake:
                return food
    
    def move_snake(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.width-1 or 
            new_head[1] <= 0 or new_head[1] >= self.height-1):
            self.game_over = True
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.appendleft(new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def change_direction(self, new_direction):
        # Prevent reversing into itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def draw(self):
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create game board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw walls
        for x in range(self.width):
            board[0][x] = '#'
            board[self.height-1][x] = '#'
        for y in range(self.height):
            board[y][0] = '#'
            board[y][self.width-1] = '#'
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                board[y][x] = 'O'  # Head
            else:
                board[y][x] = 'o'  # Body
        
        # Draw food
        board[self.food[1]][self.food[0]] = '*'
        
        # Print board
        for row in board:
            print(''.join(row))
        
        # Print score
        print(f"\nScore: {self.score}")
        print("Controls: WASD to move, Q to quit")
        if self.game_over:
            print("\nGAME OVER! Press any key to exit...")
    
    def get_input(self):
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            
            if key == 'w':
                self.change_direction((0, -1))  # Up
            elif key == 's':
                self.change_direction((0, 1))   # Down
            elif key == 'a':
                self.change_direction((-1, 0))  # Left
            elif key == 'd':
                self.change_direction((1, 0))   # Right
            elif key == 'q':
                sys.exit()
    
    def run(self):
        print("Snake Game Starting...")
        print("Use WASD keys to control the snake")
        print("Eat the food (*) to grow and increase your score")
        print("Don't hit the walls (#) or yourself!")
        print("\nPress any key to start...")
        msvcrt.getch()
        
        while not self.game_over:
            self.draw()
            self.get_input()
            self.move_snake()
            time.sleep(0.15)  # Game speed
        
        # Game over screen
        self.draw()
        msvcrt.getch()

def main():
    try:
        game = SnakeGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Press any key to exit...")
        msvcrt.getch()

if __name__ == "__main__":
    main()
