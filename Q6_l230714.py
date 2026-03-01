import pygame
import random
import heapq
import time
import math

# window setup
ROWS, COLS = 25, 25
CELL = 25

GRID_WIDTH = COLS * CELL
SIDEBAR = 260
HEIGHT = ROWS * CELL
WIDTH = GRID_WIDTH + SIDEBAR

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Pathfinding Agent")
font = pygame.font.SysFont("Arial", 18)

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
BLUE = (70,150,255)
YELLOW = (255,255,0)
RED = (255,60,60)
GRAY = (210,210,210)
ORANGE = (255,140,0)
PURPLE = (160,32,240)

# grid
grid = [[0]*COLS for _ in range(ROWS)]
START = (0,0)
GOAL = (ROWS-1,COLS-1)

algorithm = "A*"
heuristic_name = "Manhattan"
dynamic_mode = True

# heuristics
def manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def heuristic(a,b):
    if heuristic_name == "Manhattan":
        return manhattan(a,b)
    return euclidean(a,b)

# get neighbors
def neighbors(n):
    r,c = n
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    result = []
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
            result.append((nr,nc))
    return result

# search function
def search(start, goal):
    start_time = time.time()
    pq = []
    heapq.heappush(pq, (0,start))
    came = {}
    g = {start:0}
    visited = set()
    frontier = {start}
    nodes = 0

    while pq:
        _, current = heapq.heappop(pq)
        frontier.discard(current)
        visited.add(current)
        nodes += 1

        if current == goal:
            path = []
            while current in came:
                path.append(current)
                current = came[current]
            path.reverse()
            t = (time.time() - start_time) * 1000
            return path, visited, frontier, nodes, t

        for nb in neighbors(current):
            newg = g[current]+1
            if nb not in g or newg < g[nb]:
                g[nb] = newg
                came[nb] = current
                f = newg + heuristic(nb, goal) if algorithm=="A*" else heuristic(nb, goal)
                heapq.heappush(pq, (f, nb))
                frontier.add(nb)

    return [], visited, frontier, nodes, 0

# random map
def random_map(density=0.3):
    for r in range(ROWS):
        for c in range(COLS):
            grid[r][c] = 1 if random.random() < density else 0
    grid[START[0]][START[1]] = 0
    grid[GOAL[0]][GOAL[1]] = 0

# dynamic obstacles
def spawn_dynamic(path):
    if not dynamic_mode:
        return False
    if random.random() < 0.04:
        r = random.randint(0,ROWS-1)
        c = random.randint(0,COLS-1)
        if (r,c) != START and (r,c) != GOAL:
            grid[r][c] = 1
            if (r,c) in path:
                return True
    return False

# draw grid and agent
def draw(path, visited, frontier, agent, nodes, cost, etime):
    screen.fill(WHITE)

    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*CELL, r*CELL, CELL, CELL)
            color = WHITE
            if grid[r][c] == 1:
                color = BLACK
            elif (r,c) in visited:
                color = BLUE
            elif (r,c) in frontier:
                color = YELLOW
            elif (r,c) in path:
                color = GREEN
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

    pygame.draw.rect(screen, PURPLE, (START[1]*CELL, START[0]*CELL, CELL, CELL))
    pygame.draw.rect(screen, RED, (GOAL[1]*CELL, GOAL[0]*CELL, CELL, CELL))
    if agent:
        pygame.draw.rect(screen, ORANGE, (agent[1]*CELL, agent[0]*CELL, CELL, CELL))

    # sidebar
    pygame.draw.rect(screen, (240,240,240), (GRID_WIDTH, 0, SIDEBAR, HEIGHT))
    y = 20

    info = [
        "Algorithm: " + algorithm,
        "Heuristic: " + heuristic_name,
        "",
        "Nodes Visited: " + str(nodes),
        "Path Cost: " + str(cost),
        "Time(ms): " + str(int(etime)),
        "",
        "Controls:",
        "1 - A*",
        "2 - GBFS",
        "H - Change heuristic",
        "R - Random map",
        "SPACE - Start",
        "Mouse - Walls"
    ]

    for line in info:
        text = font.render(line, True, (0,0,0))
        screen.blit(text, (GRID_WIDTH + 10, y))
        y += 25

# main loop
clock = pygame.time.Clock()
agent = START
path = []
visited = set()
frontier = set()
nodes = cost = etime = 0
moving = False

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            if x < GRID_WIDTH:
                r, c = y//CELL, x//CELL
                if (r,c) != START and (r,c) != GOAL:
                    grid[r][c] = 1 - grid[r][c]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                algorithm = "A*"
            if event.key == pygame.K_2:
                algorithm = "GBFS"
            if event.key == pygame.K_h:
                heuristic_name = "Euclidean" if heuristic_name=="Manhattan" else "Manhattan"
            if event.key == pygame.K_r:
                random_map()
            if event.key == pygame.K_SPACE:
                agent = START
                path, visited, frontier, nodes, etime = search(agent, GOAL)
                cost = len(path)
                moving = True

    if moving and path:
        pygame.time.delay(70)
        blocked = spawn_dynamic(path)
        if blocked:
            path, visited, frontier, nodes, etime = search(agent, GOAL)
            cost = len(path)
        agent = path.pop(0)
        if agent == GOAL:
            moving = False

    draw(path, visited, frontier, agent, nodes, cost, etime)
    pygame.display.update()

pygame.quit()