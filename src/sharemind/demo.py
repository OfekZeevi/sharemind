import random
from tqdm import tqdm
from sharemind import SharemindSecret


def main():
    for n in [8, 16, 32, 64]:
        count = 0
        for _ in tqdm(range(1000)):
            i, j = [random.randint(0, 2**(n-1)) for _ in range(2)]
            a = SharemindSecret(value=i, size=n)
            b = SharemindSecret(value=j, size=n)
            if (i * j) % (2 ** n) != (a * b).numeric_value or bool(i >= j) ^ bool(a >= b):
                print(f'Failed for {i} and {j}, with n={n}')
                break
            count += 1
        else:
            print(f'Finished {count} random checks with n={n}')


if __name__ == '__main__':
    main()
