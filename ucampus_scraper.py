from datetime import datetime
from bs4 import BeautifulSoup
import requests, json

# Color and format escapes
default		: str = "\033[39;49;0m"
contrast	: str = "\033[30;47m"
white		: str = "\033[37m"
green		: str = "\033[32;1m"
red			: str = "\033[31;1m"
bold		: str = "\033[1m"
underline	: str = "\033[4m"

# Cursor movement
cursor_up	: str = "\033[1A"
erase_line	: str = "\033[1M"

# Global variables
actual_year = datetime.now().year

# Program description
print(f"\n{contrast} ########## Ucampus web scrapping tool ########## {default}\n")
print(f"Tool to {bold}{underline}scrap{default} the {bold}departments{default} and {bold}courses{default}\n\
with their codes from {bold}{underline}U-Campus{default} in a specific\nyear and semester.")
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


# Internal department codes used in U-Campus links
departments : dict[str, int] = {
	"AA - Área para el Aprendizaje de la Ingeniería y Ciencias A2IC": 12060003,
	"AS - Departamento de Astronomía": 3,
	"CC - Departamento de Ciencias de la Computación": 5,
	"CI - Departamento de Ingeniería Civil": 6,
	"CM - Departamento de Ciencia de los Materiales": 306,
	"DR - Área de Deportes, Educación Física y Expresiones Artísticas": 7,
	"ED - Doctorado en Ingeniería Eléctrica": 305,
	"EH - Estudios Transversales en Humanidades para las Ingenierías y Ciencias": 8,
	"EI - Área de Idiomas, Escuela de Ingeniería": 9,
	"EI - Área de Ingeniería e Innovación": 12060002,
	"EL - Departamento de Ingeniería Eléctrica": 10,
	"EP - Escuela de Postgrado": 303,
	"ES - Escuela de Ingeniería y Ciencias": 12,
	"FG - Plataforma": 310,
	"FI - Departamento de Física": 13,
	"GF - Departamento de Geofísica": 15,
	"GL - Departamento de Geología": 16,
	"IN - Departamento de Ingeniería Industrial": 19,
	"MA - Departamento de Ingeniería Matemática": 21,
	"ME - Departamento de Ingeniería Mecánica": 22,
	"MI - Departamento de Ingeniería de Minas": 23,
	"MT - Doctorado en Ciencia de los Materiales": 24,
	"QB - Departamento de Ingeniería Química y Biotecnología": 307
}


# Scrap U-Campus webpage
scrap_list : list[dict] = []
pk : int = 0

# Departments
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

# Courses
for code in departments.values():
	url : str = f"https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre={year}{semester}&depto={code}"
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


# Save to JSON file
with open('initial_tags.json', 'w', encoding='utf-8') as f:
	json.dump(scrap_list, f, ensure_ascii=False, indent=4)


print("\Scraping finished :D\n")
