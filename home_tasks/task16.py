users = [
    {'login': 'Piter', 'age': 23, 'group': "admin"},
    {'login': 'Ivan',  'age': 10, 'group': "guest"},
    {'login': 'Dasha', 'age': 30, 'group': "master"},
    {'login': 'Fedor', 'age': 13, 'group': "guest"}
]

print("1. По возрасту")
print("2. По первой букве")
print("3. По группе")

choice = input("тип сортировки: ")
criterion = input("Введите критерии поиска: ")

results = []

for user in users:
    if choice == "1":
        if user['age'] > int(criterion):
            results.append(user)
    elif choice == "2":
        if user['login'].lower().startswith(criterion.lower()):
            results.append(user)
    elif choice == "3":
        if user['group'].lower() == criterion.lower():
            results.append(user)

print("\nРезультат:")
for user in results:
    age = user['age']
    if age % 10 == 1 and age % 100 != 11:
        years_str = "год"
    elif age % 10 in [2, 3, 4] and age % 100 not in [12, 13, 14]:
        years_str = "года"
    else:
        years_str = "лет"
        
    print(f"Пользователь: '{user['login']}' возраст {age} {years_str} , группа \"{user['group']}\"")
