from datetime import datetime
from bs4 import BeautifulSoup
import requests, json, threading, time


# Color and format escapes
default		: str = "\033[39;49;0m"
contrast	: str = "\033[30;47m"
white		: str = "\033[37m"
green		: str = "\033[32;1m"
red		: str = "\033[31;1m"
bold		: str = "\033[1m"
underline	: str = "\033[4m"

# Cursor movement
cursor_up	: str = "\033[1A"
erase_line	: str = "\033[1M"


# Program description
print(f"\n{contrast} ########## Ucampus web scrapping tool ########## {default}\n")
print(f"Tool to {bold}{underline}scrap{default} the {bold}departments{default} and {bold}courses{default}\n\
with their codes from {bold}{underline}U-Campus{default} in a specific\nyear and semester.")
print(f"\n\n\n{cursor_up}{cursor_up}")


# Get user year input
actual_year = datetime.now().year
year : int = -1
while True:
	print(f"{default}Select {bold}{underline}year{default} [1996-{actual_year}]: {green}", end='')
	user_input : str = input('')
	year : int = int(user_input) if user_input.isnumeric() else -1

	if not 1996 <= year <= actual_year:
		print(f'{cursor_up}{erase_line}{cursor_up}')
		continue
	break
print(f"\n{cursor_up}{cursor_up}")


# Get user semester input
semester : int = -1
while True:
	print(f"{default}Select {bold}{underline}semester{default} [0 (annual) / 1 (autumn) / 2 (spring) / 3 (summer)]: {green}", end='')
	user_input : str = input('')
	semester : int = int(user_input) if user_input.isnumeric() else -1

	if not 0 <= semester <= 3:
		print(f'{cursor_up}{erase_line}{cursor_up}')
		continue
	break
semester = f"{year}{semester}" if 2013 <= year <= actual_year else f"{(year - 1996) * 4 + 67 + semester}"
print(f"{default}")


# Waiting animation
done : bool = False
final_message : str = ""
def animate() -> None:
	print(f"\n{cursor_up}{cursor_up}")
	animation : str = "-\|/"
	index : int = 0
	while not done:
		print(f"\rScraping {animation[index % 4]}", end='')
		index += 1
		time.sleep(0.1)
	print(f"{erase_line}{cursor_up}")
	print(f"{final_message}\n")

t = threading.Thread(target=animate)
t.start()


# Validate year and semester
semesters = {0: "annual", 1: "autumn", 2: "spring", 3: "summer"}
try:
	url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={semester}"
	request = requests.get(url)
	soup = BeautifulSoup(request.content, 'html.parser')
	chosen = soup.find('option', selected=True)
	page_semester : str = chosen.get('value')
	if page_semester != semester:
		raise(ValueError)
except ValueError:
	final_message = f"Year {green}{year}{default} and semester {green}{semesters[int(semester[-1])]}{default} does not exist in {bold}{underline}U-Campus{default}"
	done = True
except ConnectionError:
	final_message = "Scraping failed D:"
	done = True
except Exception:
	final_message = "Unhandled exception"
	done = True


# Get departments from page
departments : dict[str, int] = {}
try:
	url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={semester}"
	request = requests.get(url)
	soup = BeautifulSoup(request.content, 'html.parser')
	select = soup.find('select', id='depto')
	for department in select.findAll('option'):
		departments[department.text] = department.get('value')
except ConnectionError:
	final_message = "Scraping failed D:"
	done = True
except Exception:
	final_message = "Unhandled exception"
	done = True


# Scrap U-Campus webpage
scrap_list : list[dict] = []
pk : int = 0


# Add departments
for department_name in departments.keys():
	pk += 1
	department : dict = {
		"model": "stack_overbuxef.tag",
		"pk": pk,
		"fields": {
			"nombre": department_name
		}
	}
	scrap_list.append(department)


# Add courses
try:
	for code in departments.values():
		url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={semester}&depto={code}"
		request = requests.get(url)
		soup = BeautifulSoup(request.content, 'html.parser')
		for course_info in soup.findAll('div', class_='objeto'):
			name = course_info.find('h1').text.strip()
			code = course_info.find('h2').text.strip()
			course_name : str = f"{code} - {name}"
			pk += 1

			course : dict = {
				"model": "stack_overbuxef.tag",
				"pk": pk,
				"fields": {
					"nombre": course_name
				}
			}
			scrap_list.append(course)
except ConnectionError:
	final_message = "Scraping failed D:"
	done = True
except Exception:
	final_message = "Unhandled exception"
	done = True


# Save to JSON file
with open('initial_tags.json', 'w', encoding='utf-8') as f:
	json.dump(scrap_list, f, ensure_ascii=False, indent=4)


# End animation
final_message = "Scraping finished :D"
done = True
