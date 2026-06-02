with open("message.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

encrypted_lines = []

for line_idx, line in enumerate(lines, start=1):
    encrypted_line = ""
    for char in line:
        if "а" <= char <= "я":
            start_code = ord("а")
            new_code = start_code + (ord(char) - start_code - line_idx) % 32
            encrypted_line += chr(new_code)
        elif "А" <= char <= "Я":
            start_code = ord("А")
            new_code = start_code + (ord(char) - start_code - line_idx) % 32
            encrypted_line += chr(new_code)
        else:
            encrypted_line += char
    encrypted_lines.append(encrypted_line)

with open("encrypted.txt", "w", encoding="utf-8") as file:
    file.writelines(encrypted_lines)
