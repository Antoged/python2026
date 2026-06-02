import random

words = ["оператор", "конструкция", "объект"]
desc_ = [
    "Это слово обозначает наименьшую автономную часть языка программирования",
    "Синтаксическая структура в коде для управления логикой программы",
    "Сущность в программировании, у которой есть состояние и поведение"
]

index = random.randint(0, len(words) - 1)
target_word = words[index]
description = desc_[index]

board = ["▒"] * len(target_word)
mistakes = 0
max_mistakes = 10

print(description)
print()
print(" ".join(board))
print()

while mistakes < max_mistakes and "▒" in board:
    letter = input("Введите букву: ").lower()

    if letter in target_word:
        for i in range(len(target_word)):
            if target_word[i] == letter:
                board[i] = letter.upper()
    else:
        mistakes += 1
        print("Нет такой буквы.")
        print(f"У вас осталось {max_mistakes - mistakes} попыток!")

    print()
    print(" ".join(board))
    print()

if "▒" not in board:
    print("Поздравляем! Вы победили!")
else:
    print(f"Вы проиграли. Загаданное слово было: {target_word.upper()}")
