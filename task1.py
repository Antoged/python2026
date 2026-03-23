x = int(input("Введите любое целое число: "))

if x > 0:
    x += 2
elif x < 0:
    x -= 4
else:
    x = 20
    
print(x)