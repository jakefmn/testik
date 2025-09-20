a = 1
for i in range(1, 6):
    b = a
    a = a * i
    print(f'{b} * {i} = {a}')
print(f'Ответ: {a}')
