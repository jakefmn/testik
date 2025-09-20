b = []
while True:
    a = int(input('Введите число:'))
    b.append(a)
    if a == 0:
        break
print(max(b))