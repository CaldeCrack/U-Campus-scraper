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
error : str = ""
def animate() -> None:
	print(f"\n{cursor_up}{cursor_up}")
	animation : str = "-\|/"
	index : int = 0
	while not done:
		print(f"\rScraping {animation[index % 4]}", end='')
		index += 1
		time.sleep(0.1)
	print(f"{erase_line}{cursor_up}")
	print(f"{final_message}\n", end='')
	if error:
		print(f"{error}\n")
	else:
		print()


# Credits to rlorcac on GitHub for explaining in code the formula I was using to create the URL parameter
actual_year = datetime.now().year
def year_semester_to_URL_parameter(year: int, semester: int) -> str:
	return f"{year}{semester}" if 2013 <= year <= actual_year else f"{(year - 1996) * 4 + 67 + semester}"


def interactive_program() -> None:
	# Program description
	print(f"\n{contrast} ########## Ucampus web scrapping tool ########## {default}\n")
	print(f"Tool to {bold}{underline}scrap{default} the {bold}departments{default} and {bold}courses{default} at {red}FCFM{default}")
	print(f"with their codes from {bold}{underline}U-Campus{default} in a specific year\nand semester.")
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
	global done, final_message, error
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
	except Exception as e:
		error = e
		final_message = "Unhandled exception"
		done = True
		return

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
	except Exception as e:
		error = e
		final_message = "Unhandled exception"
		done = True
		return

	# Add courses within their departments
	scrap_list : list[dict] = []
	try:
		for department_name, code in departments.items():
			url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={parameter}&depto={code}"
			request = requests.get(url)
			soup = BeautifulSoup(request.content, 'html.parser')
			course_list : list[dict] = []
			for course_info in soup.findAll('div', class_='ramo'):
				course : dict = {}

				# Get course info
				name : str = course_info.find('h1').text.strip()
				code : str = course_info.find('h2').text.strip()
				course['nombre'] = f"{code} - {name}"
				metadata = course_info.find('dl', class_='leyenda')
				for i, elem in enumerate(metadata):
					elem_text : str = elem.text.strip().lower()
					match elem_text:
						case "programa":
							course[elem_text] = elem.find('a').get('href')
						case "créditos:":
							course[elem_text.replace(':', '')] = int(list(metadata)[i + 2].text.strip())
						case "requisitos:" | "equivalencias" | "comentario":
							course[elem_text.replace(':', '')] = list(metadata)[i + 2].text.strip()
				if course_info.find('span', class_='sustentable enfocado'):
					course['sustentabilidad'] = "Enfocado en sustentabilidad"
				elif course_info.find('span', class_='sustentable'):
					course['sustentabilidad'] = "Relacionado con sustentabilidad"

				# Get section info
				sections : list[dict] = []
				for section_info in course_info.find('table', class_='cursos').find('tbody').findAll('tr'):
					section : dict = {}

					# Get section number, teachers and extra info
					section_header = section_info.find('h1').text.strip().replace('\t\t', ' ').split(' ')
					section['sección'] = int(section_header[1])
					if len(section_header) > 2:
						section['modalidad'] = section_header[-1]
					if section_info.find('h2'):
						section['info'] = section_info.find('h2').text.strip()
					section_teachers = section_info.find('ul', class_='profes').findAll('li')
					professor_text : str = "profesores" if len(section_teachers) > 1 else "profesor(a)"
					if section_teachers:
						section[professor_text] = [teacher.text.strip() for teacher in section_teachers] if len(section_teachers) > 1 \
													else [teacher.text.strip() for teacher in section_teachers][0]
					else:
						section[professor_text] = 'No tiene asignado un(a) profesor(a)'

					# Section schedule
					section_schedule = section_info.findAll('td')[-1].find('div', class_='no-movil')
					if section_schedule := str(section_schedule).replace('<br/>', '<').replace('>', '<').strip().split('<')[2:-2]:
						if section_schedule[0]:
							section['Horario'] = section_schedule if len(section_schedule) > 1 else section_schedule[0]
					sections.append(section)

				course['secciones'] = sections
				course_list.append(course)

			department : dict = {
				'Departamento': department_name,
				'Cursos': course_list
			}
			scrap_list.append(department)
	except ConnectionError:
		final_message = "Scraping failed D:"
		done = True
	except Exception as e:
		error = e
		final_message = "Unhandled exception"
		done = True
		return

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
