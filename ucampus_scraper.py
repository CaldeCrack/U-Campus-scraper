from datetime import datetime
from bs4 import BeautifulSoup
import requests, json, threading, time, sys


# ANSI escape codes
default		: str = "\033[39;49;0m"
contrast	: str = "\033[30;47m"
white		: str = "\033[37m"
green		: str = "\033[32;1m"
red		: str = "\033[31;1m"
bold		: str = "\033[1m"
underline	: str = "\033[4m"
cursor_up	: str = "\033[1A"
erase_line	: str = "\033[1M"


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


# Credits to rlorcac on GitHub for explaining in code the formula I was using to create the URL parameter
actual_year = datetime.now().year
def year_semester_to_URL_parameter(year: int, semester: int) -> str:
	return f"{year}{semester}" if 2013 <= year <= actual_year else f"{(year - 1996) * 4 + 67 + semester}"


def interactive_program() -> None:
	# Program description
	print(f"\n{contrast} ########## Ucampus web scrapping tool ########## {default}\n")
	print(f"Tool to {bold}{underline}scrap{default} the {bold}departments{default} and {bold}courses{default}")
	print(f"with their codes from {bold}{underline}U-Campus{default} in a specific\nyear and semester.")
	print(f"\n\n\n{cursor_up}{cursor_up}")

	# Get user year input
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

	print(f"{default}")
	program(year, semester)


def program(year : int, semester : int) -> None:
	# Start animation thread
	global done, final_message
	t = threading.Thread(target=animate)
	t.start()

	# Validate year and semester
	parameter : str = year_semester_to_URL_parameter(year, semester)
	semesters = {0: "annual", 1: "autumn", 2: "spring", 3: "summer"}
	try:
		url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={parameter}"
		request = requests.get(url)
		soup = BeautifulSoup(request.content, 'html.parser')
		chosen = soup.find('option', selected=True)
		page_semester : str = chosen.get('value')
		if page_semester != parameter:
			raise(ValueError)
	except ValueError:
		final_message = f"Year {green}{year}{default} and semester {green}{semesters[semester]}{default} does not exist in {bold}{underline}U-Campus{default}"
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
		url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={parameter}"
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

	# Add courses within their departments
	scrap_list : list[dict] = []
	try:
		for department_name, code in departments.items():
			url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={parameter}&depto={code}"
			request = requests.get(url)
			soup = BeautifulSoup(request.content, 'html.parser')
			course_list : list[dict] = []
			for course_info in soup.findAll('div', class_='objeto'):
				name = course_info.find('h1').text.strip()
				code = course_info.find('h2').text.strip()
				course_name : str = f"{code} - {name}"
				course : dict = {
					"nombre": course_name
				}
				course_list.append(course)

			department : dict = {
				'Departamento': department_name,
				'Cursos': course_list
			}
			scrap_list.append(department)
	except ConnectionError:
		final_message = "Scraping failed D:"
		done = True
	except Exception:
		final_message = "Unhandled exception"
		done = True

	# Save to JSON file
	with open('catalogo.json', 'w', encoding='utf-8') as f:
		json.dump(scrap_list, f, ensure_ascii=False, indent=4)

	# End animation
	final_message = "Scraping finished :D"
	done = True


# Also credits to rlorcac on GitHub for the idea of passing parameters directly in the args instead of using the CLI
if len(sys.argv) == 1:
	interactive_program()
elif len(sys.argv) == 2:
	print(f"Must use two arguments: ucampus_scraper.py [{green}year{default}] [{green}semester{default}]\n")
elif not (sys.argv[1].isnumeric() and sys.argv[2].isnumeric()):
	print("Arguments must be numeric.\n")
elif not (1996 <= int(sys.argv[1]) <= actual_year) or not (0 <= int(sys.argv[2]) <= 3):
	print(f"Year and semester must be between bounds [{green}1996{default}, {green}{actual_year}{default}]", end=" ")
	print(f"and [{green}0{default}, {green}3{default}], respectively.\n")
else:
	program(int(sys.argv[1]), int(sys.argv[2]))
