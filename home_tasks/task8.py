number_str = input("Введите четырехзначное число: ")

is_palindrome = number_str == number_str[::-1]

print("Высказывание истинно:", is_palindrome)
