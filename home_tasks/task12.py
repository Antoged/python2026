unit = int(input("Введите единицу массы тела (1-5): "))
weight = float(input("Введите массу тела: "))

match unit:
    case 1:
        kg_weight = weight
    case 2:
        kg_weight = weight / 1000000
    case 3:
        kg_weight = weight / 1000
    case 4:
        kg_weight = weight * 1000
    case 5:
        kg_weight = weight * 100
    case _:
        kg_weight = None

if kg_weight is not None:
    print(f"Ответ: {kg_weight} кг")
else:
    print("Ошибка: неверный номер единицы массы")
