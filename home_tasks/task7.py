a = float(input("Введите координату А: "))
b = float(input("Введите координату B: "))
c = float(input("Введите координату C: "))

ac_length = abs(c - a)

bc_length = abs(c - b)

total_sum = ac_length + bc_length

print("Длина отрезка AC:", ac_length)
print("Длина отрезка BC:", bc_length)
print("Сумма длин отрезков:", total_sum)
