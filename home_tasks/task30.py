def msum(matrix):
    return sum(cell for row in matrix for cell in row)


matrix = [[1, 2, 3], [4, 5, 6]]
print(msum(matrix))
