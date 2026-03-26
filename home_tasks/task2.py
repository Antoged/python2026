# todo: Преобразуйте переменную age и foo в число
# age = "23"
# foo = "23abc"

age = "23"
foo = "23abc"
age = int(age)
try:
    foo = int(foo)
except ValueError:
    foo = None

# Преобразуйте переменную age в Boolean
# age = "123abc"

age = "123abc"
age = bool(age)
print(age)

# Преобразуйте переменную flag в Boolean
# flag = 1

flag = 1
flag = bool(flag)
print(flag)

# Преобразуйте значение в Boolean
# str_one = "Privet"
# str_two = ""

str_one = "Privet"
str_two = ""
str_one = bool(str_one)
str_two = bool(str_two)
print(str_one, str_two)

# Преобразуйте значение 0 и 1 в Boolean

a = 0
b = 1
a = bool(a)
b = bool(b)
print(a, b)

# Преобразуйте False в строку

s = str(False)
print(s)



