mass = [1, 2, 17, 54, 30, 89, 2, 1, 6, 2]

unique_numbers = set(mass)

for num in unique_numbers:
    indices = []
    for i in range(len(mass)):
        if mass[i] == num:
            indices.append(i)
    
    if len(indices) > 1:
        min_dist = len(mass) + 1
        best_pair = None
        
        for k in range(len(indices) - 1):
            dist = indices[k+1] - indices[k]
            if dist < min_dist:
                min_dist = dist
                best_pair = (indices[k], indices[k+1])
                
        print(f"Для числа {num} минимальное расстояние в массиве по индексам: {best_pair[0]} и {best_pair[1]}")
    else:
        print(f"Для числа {num} нет минимального расстояния т.к. элемент в массиве один.")
