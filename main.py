from prob_functions import *
if __name__ == '__main__':
    print(keep_on_top(6, 23, 2, 1, 60), push_to_bottom(6, 23, 2, 1, 60))
    print(keep_on_top(6, 23, 2, 0, 60), push_to_bottom(6, 23, 2, 0, 60))
    flag = False
    # flag = True
    while flag:
        k = int(input('How many Simian Spirit Guide?: '))
        n = int(input('How many Surging Flame?: ')) + k
        draw_st = str(input('On the play? (y or n): '))
        draw = draw_st == 'n'
        advice = mull_thing(n, 23, k, draw)
        if draw:
            chance = level_3_hand_odds_draw(n, 23, k)
        else:
            chance = level_3_hand_odds_play(n, 23, k)
        print(advice)
        print('You currently have a ' + str(round(chance * 100, 2)) + '% chance of winning.')
        try_again = str(input('Would you like to evaluate another hand? (y or n): '))
        flag = (try_again != 'n')
        # if advice[82] == 'k':
        #     flag = False
        # elif advice[82] == 'm':
        #     print('Since you should mulligan, I can help you evaluate your next hand')
