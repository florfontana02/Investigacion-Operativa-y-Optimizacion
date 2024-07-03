import random

with open('output.txt', 'w') as f:
    # cantidad trabajadores T
    T = random.randint(5,10)
    f.write(f"{T}\n")

    # cantidad órdenes O
    #O = random.randint(120,150)
    O = 100
    f.write(f"{O}\n")

    # siguientes O líneas: dicen el índice de la orden, su beneficio, y la cantidad de trabajadores que requiere
    for i in range(O):
        col1 = i
        col2 = random.randint(1000, 10000)
        col3 = random.randint(1, 5)
        f.write(f"{col1} {col2} {col3}\n")

    # cantidad de conflictos entre trabajadores
    C = random.randint(0, T/2)
    f.write(f"{C}\n")

    # enumero los pares de conflictos entre trabajadores
    for _ in range(C):
        a, b = random.sample(range(T), 2)
        f.write(f"{a} {b}\n")

    # cantidad de ordenes correlativas
    R = random.randint(0, 5)
    f.write(f"{R}\n")

    # enumero pares de órdenes correlativas
    for _ in range(R):
        a, b = random.sample(range(O), 2)
        f.write(f"{a} {b}\n")

    # cantidad de órdenes conflictivas
    F = random.randint(0, 5)
    f.write(f"{F}\n")

    # enumero pares de órdenes conflictivas
    for _ in range(F):
        a, b = random.sample(range(O), 2)
        f.write(f"{a} {b}\n")

    # cantidad de órdenes repetitivas
    P = random.randint(0, 5)
    f.write(f"{P}\n")

    # enumero pares de órdenes repetitivas
    for _ in range(P):
        a, b = random.sample(range(O), 2)
        f.write(f"{a} {b}\n")
