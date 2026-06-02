# Первая задача
import random

generate_cell = lambda: random.randint(0, 1)

n = int(input("Введите размер поля N: "))

game_field = [[generate_cell() for _ in range(n)] for _ in range(n)]


# Вторая задача
total_ships = sum([cell for row in game_field for cell in row if cell == 1])


print(f"Сгенерировано поле {n} на {n}:")
for row in game_field:
    print(row)

print("Общее количество кораблей (единиц):", total_ships)
