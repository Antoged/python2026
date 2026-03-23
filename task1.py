x = int(input("Введите любое целое число: "))

if x > 0:
    x += 1
elif x < 0:
    x -= 2
else:
    x = 10
    
print(x)