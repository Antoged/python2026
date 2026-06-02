def transpose(matrix):
    return [[matrix[row][col] for row in range(len(matrix))] for col in range(len(matrix[0]))]


sample_matrix = [[1, 2, 3], [4, 5, 6]]
result = transpose(sample_matrix)
print(result)
