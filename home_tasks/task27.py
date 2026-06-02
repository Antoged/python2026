import random

generate_cell = lambda: random.randint(0, 1)

game_field = []
for _ in range(5):
    row = []
    for _ in range(5):
        row.append(generate_cell())
    game_field.append(row)

ships_left = 0
for row in game_field:
    for cell in row:
        if cell == 1:
            ships_left += 1

print("Игра началась! Поле 5 на 5 сгенерировано.")

while ships_left > 0:
    for row in game_field:
        display_row = []
        for cell in row:
            if cell == 2:
                display_row.append("X")
            elif cell == -1:
                display_row.append("*")
            else:
                display_row.append("▒")
        print(" ".join(display_row))
    print()

    i = int(input("Введите номер строки (0-4): "))
    j = int(input("Введите номер столбца (0-4): "))

    if i < 0 or i > 4 or j < 0 or j > 4:
        print("Координаты вне поля! Попробуйте снова.")
        print()
        continue

    if game_field[i][j] == 1:
        print("Попадание! Корабль подбит.")
        game_field[i][j] = 2
        ships_left -= 1
    elif game_field[i][j] == 0:
        print("Мимо!")
        game_field[i][j] = -1
    else:
        print("Вы уже стреляли в эти координаты!")
    
    print()

print("Поздравляем! Все корабли уничтожены. Игра окончена.")
