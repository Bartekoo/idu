import requests
from bs4 import BeautifulSoup
import json

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
                            for location in locations:
                                class_cell.append(location.text.strip().replace("\n", ""))
                            schedule[day][lesson] = class_cell
                            day += 1
                    lesson += 1
                    day = 0
    return schedule

def get_lesson(schedule, day=None, lesson=None):
    days = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    if day is not None:
        if lesson is not None:
            return schedule[days[day]][lesson]
        return schedule[days[day]]
    return schedule

def get_student_id(session):
    url = "https://s35.idu.edu.pl"
    response = session.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_unique_id12 = soup.find('div', id='unique-id12')
        if div_unique_id12:
            links = div_unique_id12.find_all('div', class_="see-more")
            for link in links:
                hrefs = link.find_all("a")
                for href in hrefs:
                    parts = href['href'].split('/')
                    for part in parts:
                        if part.isdigit():
                            return part

def get_marks(session, student_id):
    str_student_id = str(student_id)
    url = f"https://s35.idu.edu.pl/students/{str_student_id}/grades"
    response = session.get(url)
    all_marks = []

    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')
        marks_table = soup.find("table", class_="marks-table")
        if marks_table:
            marks_trs = marks_table.find_all("tr")
            for marks_tr in marks_trs:
                lesson_marks = []
                lesson_name = None
                marks_tds = marks_tr.find_all("td")
                for marks_td in marks_tds:
                    if marks_td.has_attr('class') and "averages-container" in marks_td.get("class", []):
                        marks_divs = marks_td.find_all("div")
                        for marks_div in marks_divs:
                            if not marks_div.has_attr('class'):
                                mark_type = marks_div.find("strong").text.strip()
                                marks_div_marks = marks_div.find("div", class_="left-padded-12")
                                marks_value = [span.text.strip().replace("\n", "") for span in marks_div_marks.find_all("span", class_="value")]
                                marks_desc = [span.text.strip().replace("\n", "") for span in marks_div_marks.find_all("span", class_="desc")]
                                lesson_marks.append((mark_type, list(zip(marks_value, marks_desc))))
                    else:
                        lesson_name = marks_td.text.strip()
                if lesson_name is not None:
                    all_marks.append((lesson_name, lesson_marks))
    return all_marks

def print_marks(all_marks):
    for lesson_data in all_marks:
        lesson_name = lesson_data[0]
        mark_data = lesson_data[1]
        print(f"Lesson: {lesson_name}")
        for mark_type, marks_list in mark_data:
            print(f"  Mark Type: {mark_type}")
            for mark_value, mark_desc in marks_list:
                print(f"    Value: {mark_value}, Description: {mark_desc}")

def get_marks_by_subject(all_marks, subject_name):
    subject_marks = []
    for lesson_data in all_marks:
        if lesson_data[0] == subject_name:
            subject_marks = lesson_data[1]
            break
    return subject_marks

def save_data_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    response, session = login("b.p.25630", "-vTv6-Fyxy")
    student_id = get_student_id(session)
    if response.ok:
        schedule = make_schedule(session)
        all_marks = get_marks(session, student_id)
        
        # Save schedule and marks to JSON files
        save_data_to_json(schedule, 'schedule.json')
        save_data_to_json(all_marks, 'marks.json')
        
if __name__ == "__main__":
    main()
