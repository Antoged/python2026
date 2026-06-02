import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "dump.txt")

vowels = "aeiouyаеёиоуыэюя"
counts = {
    "a": 0, "e": 0, "i": 0, "o": 0, "u": 0, "y": 0,
    "а": 0, "е": 0, "ё": 0, "и": 0, "о": 0, "у": 0, "ы": 0, "э": 0, "ю": 0, "я": 0
}

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read().lower()

for char in text:
    if char in vowels:
        counts[char] += 1

for letter, count in counts.items():
    if count > 0:
        print(f"Количество букв {letter} - {count}")
