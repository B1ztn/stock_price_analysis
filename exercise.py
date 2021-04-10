

def MinWindowSubstring(a):
    N, K, m = a[0], a[1], ['', len(a[0])]
    for y in range(len(K), len(N) + 1):
        for x in range(y):
            l, c = N[x:y], list(K[:])
            for i in l:
                if i in c:
                    c.remove(i)
            if len(c) == 0 and len(l) < m[1]:
                m[0], m[1] = l, len(l)
    return m[0]

a = ["sdfsdfadbcsafdfrhfdgdgyhrdsafdaf","abc"]
output = MinWindowSubstring(a)
print(output) 