import pygame
import requests
from bs4 import BeautifulSoup

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WIDTH = 1800
HEIGHT = 1000
CELL_SIZE = 170

def login(usr, pas):
    login_url = "https://s35.idu.edu.pl/users/sign_in"
    session = requests.Session()
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'authenticity_token'}).get('value')

    login_data = {
        "authenticity_token": csrf_token,
        "user[login]": usr,
        "user[password]": pas,
        "commit": "Log in",
    }

    response = session.post(login_url, data=login_data)
    return response, session

def make_schedule(session):
    url = "https://s35.idu.edu.pl"
    response = session.get(url)
    day = 0
    lesson = 0

    if response.ok:
        schedule = [['' for _ in range(11)] for _ in range(5)]
        soup = BeautifulSoup(response.content, 'html.parser')
        schedule_divs = soup.find_all('div', class_="schedule")

        for schedule_div in schedule_divs:
            schedule_rows = schedule_div.table.find_all('tr', recursive=False)
            for schedule_row in schedule_rows:
                if schedule_row.parent.name != 'thead':
                    schedule_tds = schedule_row.find_all("td")
                    for schedule_td in schedule_tds:
                        if "tiptip" not in schedule_td.get("class", []):
                            class_cell = []
                            titles = schedule_td.find_all("span", class_="subject tiptip large")
                            for title in titles:
                                class_cell.append(title.text.strip().replace("\n", ""))
                            locations = schedule_td.find_all("span", class_="location")
                            
                            schedule[day][lesson] = class_cell
                            day += 1
                    lesson += 1
                    day = 0
    return schedule

def draw_schedule(screen, schedule):
    font = pygame.font.Font(None, 20)
    for row in range(5):
        for col in range(11):
            cell_content = schedule[row][col]
            cell_text = "\n".join(cell_content)
            cell_surface = font.render(cell_text, True, BLACK)
            cell_rect = cell_surface.get_rect()
            cell_rect.topleft = (col * CELL_SIZE, row * CELL_SIZE)
            pygame.draw.rect(screen, GRAY, cell_rect, 1)
            screen.blit(cell_surface, cell_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Schedule Display")

    response, session = login("b.p.25630", "-vTv6-Fyxy")
    if response.ok:
        schedule = make_schedule(session)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        draw_schedule(screen, schedule)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
