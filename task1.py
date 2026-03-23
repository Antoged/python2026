x = int(input("Введите любое целое число: "))

if x > 0:
    x += 3
elif x < 0:
    x -= 4
else:
    x = 20
    
print(x)