def is_operator(expression, index):
    num = 0
    while (index - 1 >= 0) and (expression[index-1] == '\\'):
        num += 1
        index -= 1
    return num % 2 == 0
