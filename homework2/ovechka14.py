a = [1, 13 , 5, 10, 11, 12, 14]
c = len(a)
i = 0
n = []
while c>0:
    if a[i] > 10:
        n.append(a[i])
    i += 1
    c = c - 1
print(len(n))

