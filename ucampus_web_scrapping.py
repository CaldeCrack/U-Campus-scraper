from datetime import datetime
import requests

# Color escapes
default		= "\033[39;49;0m"
contrast	= "\033[30;47m"
green		= "\033[32;1m"
red			= "\033[31;1m"

# Cursor movement
cursor_up	= "\033[1A"
erase_line	= "\033[1M"

# Global variables
actual_year = datetime.now().year

# Program description
print(f"\n{contrast} ########## Ucampus web scrapping tool ########## {default}\n")
print("Add description")
print(f"\n\n\n{cursor_up}{cursor_up}")

# Get user year input
year = -1
while True:
	print(f"{default}Select year [1996-{actual_year}]: {green}", end='')
	user_input = input('')
	year = int(user_input) if user_input.isnumeric() else -1

	if not 1996 <= year <= actual_year:
		print(f'{cursor_up}{erase_line}{cursor_up}')
		continue
	break
print(f"\n{cursor_up}{cursor_up}")


# Get user semester input
semester = -1
while True:
	print(f"{default}Select semester [0 (annual) / 1 (autumn) / 2 (spring) / 3 (summer)]: {green}", end='')
	user_input = input('')
	semester = int(user_input) if user_input.isnumeric() else -1

	if not 0 <= semester <= 3:
		print(f'{cursor_up}{erase_line}{cursor_up}')
		continue
	break
print()
