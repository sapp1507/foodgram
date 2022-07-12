import random


def main():
    prisoners = [x for x in range(100)]
    box = [x for x in range(100)]
    random.shuffle(box)

    winner = 0
    lose = 0

    for prisoner in prisoners:
        open = int(prisoner)
        for i in range(50):
            if box[open] == prisoner:
                # print(f'заключенный {prisoner} нашел свой номер в {open} за '
                #       f'{i} шагов')
                winner += 1
                break
            open = box[open]
            if i == 49:
                # print(f'Заключенный {prisoner} FAIL')
                lose += 1

    if lose > 0:
        return False
    else:
        return True



if __name__ == '__main__':
    result = []
    for i in range(100):
        result.append(main())
    print(f'{result.count(True)}/{result.count(False)}')

