from math import factorial as fac


def memoize(f):
    """
    Memoization decorator for functions taking one or more arguments.
    """
    class memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)


def binomial_coeff(n, k):
    """
    Binomial coefficient function, i.e. how many ways to choose k of n objects
    :param int n:
    :param int k:
    :return:
    """
    if k < 0:
        return 0
    if n < k:
        return 0
    return fac(n) / (fac(k) * fac(n - k))


@memoize
def hypogeo(N, n, K, k):
    """
    Gives hypergeometric probability mass function
    :param int N: Population size
    :param int n: Sample size
    :param int K: Successes in population
    :param int k: Successes in sample
    :return float: Probability of k successes in a sample of size n
    """
    if n > N:
        return 0
    return (binomial_coeff(K, k) * binomial_coeff(N - K, n - k)) / binomial_coeff(N, n)


def hand_gen():
    """
    Generates every possible opening hand
    :return tuple:
    """
    for i in range(8):
        for j in range(i + 1):
            yield i, j


def plays_in_hand(n, k):
    """
    Given a hand, gives how many plays it can actually make
    :param int n: Cards in hand
    :param int k: Amount of SSG in hand
    :return int: Amount of SF which can be cast
    """
    return min(k // 2, n - k)


def level_1_mull(n, x):
    """
    Computes probability of mulligan on the play based only on whether the hand can win
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :return float:
    """
    return sum([hypogeo(60, n, x, i) for i in [0, 1, n]])


def mull_to_play(n, x):
    """
    Computes probability of a mulligan to n cards on the draw regardless of whether it will be kept
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :return float:
    """
    retval = 1
    for i in range(n + 1, 8):
        retval *= level_1_mull(i, x)
    return retval


def mull_to_draw(n, x):
    """
    Computes probability of a mulligan to n cards on the play regardless of whether it will be kept
    :param int n:
    :param int x:
    :return float:
    """
    retval = 1
    for i in range(n + 1, 8):
        retval *= hypogeo(60, i, x, 0)
    return retval


def level_1_hand_odds(n, x):
    """
    Computes the probability that an n-card hand will be kept
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :return float:
    """
    return 1 - level_1_mull(n, x)


def level_1_win_play(x):
    """
    Probability of a win given level 1 reasoning
    :param int x: SSGs in deck
    :return float:
    """
    return sum([level_1_hand_odds(i, x) * mull_to_play(i, x) for i in range(8)])


def level_1_win_draw(x):
    """
    Computes probability of mulligan on the draw based only on whether the hand can win
    :param int x: Amount of successes in deck
    :return float: Probability of a win
    """
    retval = 1
    for n in range(8):
        retval *= hypogeo(60, n, x, 0)
    return 1 - retval
    # return 1 - reduce(lambda x, y: x * y, [hypogeo(60, n, x, 0) for n in range(8)])


def level_2_hand_odds_play(n, x):
    """
    Probability of an n-card hand winning on the play based on level 2 reasoning.
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :return float:
    """
    return sum([hypogeo(60, n, x, i) * hand_will_win_play(n, x, i) for i in range(n)])


def level_2_win_play(x):
    """
    Probability that a deck with x SSGs will win on the play using level two reasoning
    :param int x: SSGs in deck
    :return float:
    """
    return sum([level_2_hand_odds_play(i, x) * mull_to_play(i, x) for i in range(0, 8)])


def level_2_hand_odds_draw(n, x):
    """
    Probability of an n-card hand winning on the draw based on level 2 reasoning.
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :return float:
    """
    return sum([hypogeo(60, n, x, i) * hand_will_win_draw(n, x, i) for i in range(n)])


def level_2_win_draw(x):
    """
    Probability that a deck with x SSGs will win on the draw using level two reasoning
    :param int x: SSGs in deck
    :return float:
    """
    return sum([mull_to_draw(i, x) * level_2_hand_odds_draw(i, x) for i in range(8)])


@memoize
def surge_odds(N, x, T, C, topcard=None):
    """
    Recursively computes probability of a selection having successes and leading to more selections
    :param int N: Cards in deck
    :param int x: Successes in deck
    :param int T: How many tries left
    :param int C: How many hits thus far
    :param int topcard: Tells us whether we know the top card, is either 1 (SSG) or 0 (SF). Defaults to None
    :return float: Probability of success
    """
    if C > 9:
        return 1
    if T == 0:
        return 0
    if topcard is not None:
        if topcard == 1:
            return sum([hypogeo(N - 1, 3, x - 1, 3 - i) *
                        surge_odds(N - 4, x - (4 - i), T - 1 + i, C + i) for i in range(4)])
        if topcard == 0:
            return sum([hypogeo(N - 1, 3, x, 3 - i) *
                        surge_odds(N - 4, x - (3 - i), T - 1 + i, C + i + 1) for i in range(4)])
    else:
        return sum([hypogeo(N, 4, x, 4 - i) *
                surge_odds(N - 4, x - (4 - i), T - 1 + i, C + i) for i in range(5)])


def keep_on_top(n, x, k, topcard, N=60):
    """
    Probability that a hand will win if a card is left on top.
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :param int topcard: Card on top, 1 for SSG or 0 for SF.
    :param int N: Cards in deck, 60 by default
    :return float:
    """
    return surge_odds(N - n, x - k, plays_in_hand(n, k), plays_in_hand(n, k), topcard)


def push_to_bottom(n, x, k, topcard, N=60):
    """
    Probability that a hand will win if a card is put on the bottom.
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :param int topcard: Card that was pushed to bottom, 1 for SSG or 0 for SF
    :param int N: Cards in deck, 60 by default
    :return float:
    """
    return surge_odds(N - 1 - n, x - topcard - k, plays_in_hand(n, k), plays_in_hand(n, k))


def hand_will_win_play(n, x, k, scry=True, N=60):
    """
    Probability that a hand will win on the play
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :param boolean scry: Whether there will be a scry. True by default
    :param int N: Cards in deck, 60 by default
    :return float:
    """
    if n < 7 and scry:
        retval = 0
        retval += (hypogeo(N - n, 1, x - k, 1) *
                   max(keep_on_top(n, x, k, 1, N),
                       push_to_bottom(n, x, k, 1, N)))
        retval += (hypogeo(N - n, 1, x - k, 0) *
                   max(keep_on_top(n, x, k, 0),
                       push_to_bottom(n, x, k, 0, N)))
        return retval
    else:
        return keep_on_top(n, x, k, None, N)


def hand_will_win_play_scry_bottom(n, x, k, N=60):
    """
    Probability that a hand will win on the play after scrying to the bottom
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :param int N: Cards in deck, 60 by default
    :return float:
    """
    retval = 0
    retval += hypogeo(N - n, 1, x - k, 1) * hand_will_win_play(n + 1, x - 1, k + 1, False, N)
    retval += hypogeo(N - n, 1, x - k, 0) * hand_will_win_play(n + 1, x, k, False, N)
    return retval


def hand_will_win_draw(n, x, k, N=60):
    """
    Probability that a hand will win on the draw
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :param int N: Cards in deck, 60 by default
    :return float:
    """
    if n < 7:
        retval = 0
        # First we assume card a is on top
        retval += (hypogeo(N - n, 1, x - k, 1) *
                   max(hand_will_win_play(n + 1, x - k, k + 1, False),  # probability if kept on top
                       hand_will_win_play_scry_bottom(n, x - 1, k, 59)))  # probability if put on bottom
        # Next we assume card b is top
        retval += (hypogeo(N - n, 1, x - k, 0) *
                   max(hand_will_win_play(n + 1, x, k, False),  # probability if kept on top
                       hand_will_win_play_scry_bottom(n, x, k, 59)))  # probability if put on bottom
        return retval
    else:
        return (hypogeo(N - n, 1, x - k, 0) * hand_will_win_play(n + 1, x, k) +
                hypogeo(N - n, 1, x - k, 1) * hand_will_win_play(n + 1, x, k + 1))


@memoize
def level_3_mull_odds_play(n, x, k):
    """
    Probability that a hand will win if it mulligans on the play using level three reasoning
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return float:
    """
    return sum([level_3_hand_odds_play(n - 1, x, i) * hypogeo(60, n - 1, x, i) for i in range(0, n)])


@memoize
def level_3_hand_odds_play(n, x, k):
    """
    Probability that a player will win on the play with a given hand using level three reasoning
    Finds the better choice between a keep or a mulligan
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return float:
    """
    if n < 3:
        return 0
    return max(hand_will_win_play(n, x, k), level_3_mull_odds_play(n, x, k))


@memoize
def level_3_mull_odds_draw(n, x, k):
    """
    Probability that a hand will win if it mulligans on the draw using level three reasoning
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return float:
    """
    return sum([level_3_hand_odds_draw(n - 1, x, i) * hypogeo(60, n - 1, x, i) for i in range(n)])


@memoize
def level_3_hand_odds_draw(n, x, k):
    """
    Probability that a player will win on the draw with a given hand using level three reasoning
    Finds the better choice between a keep or a mulligan
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return float:
    """
    if n < 1:
        return 0
    return max(hand_will_win_draw(n, x, k), level_3_mull_odds_play(n, x, k))


def level_3_win_play(x):
    """
    Probability that a deck with x SSGs will win on the play
    :param int x: SSGs in deck
    :return float:
    """
    return sum([level_3_hand_odds_play(7, x, k) * hypogeo(60, 7, x, k) for k in range(8)])


def level_3_win_draw(x):
    """
    Probability that a deck with x SSGs will win on the draw
    :param int x: SSGs in deck
    :return float:
    """
    return sum([level_3_hand_odds_draw(7, x, k) * hypogeo(60, 7, x, k) for k in range(8)])


def best_choice(func):
    """
    Given a function, finds the input that gives the maximum output
    :param func: The function that will be used
    :return tuple:
    """
    results = [func(x) for x in range(61)]
    l, m = 0, 0
    for i in range(61):
        if results[i] > m:
            m = results[i]
            l = i
    return l, m


def should_i_keep_play(n, x, k):
    """
    Given a hand, determines whether the hand should be kept and if so how to scry
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return list:
    """
    retval = [n, k]
    if hand_will_win_play(n, x, k) >= level_3_mull_odds_play(n, x, k):
        retval += ['keep']
        if n < 7:
            if keep_on_top(n, x, k, 1) >= push_to_bottom(n, x, k, 1):
                retval += ['top']
            else:
                retval += ['bottom']
            if keep_on_top(n, x, k, 0) >= push_to_bottom(n, x, k, 0):
                retval += ['top']
            else:
                retval += ['bottom']
    else:
        retval += ['mulligan']
    return retval


def should_i_keep_draw(n, x, k):
    """
    Given a hand, determines whether the hand should be kept and if so how to scry
    :param int n: Cards in hand
    :param int x: SSGs in deck
    :param int k: SSGs in hand
    :return list: Returns a list with n and k as well as "keep" or "mulligan" and "top"/"bottom" twice
    """
    retval = [n, k]
    if hand_will_win_play(n, x, k, False) >= level_3_mull_odds_play(n, x, k):
        retval += ['keep']
        if n < 7:
            if hand_will_win_play(n + 1, x - k, k + 1, False) >= hand_will_win_play_scry_bottom(n, x - 1, k, 59):
                retval += ['top']
            else:
                retval += ['bottom']
            if hand_will_win_play(n + 1, x, k, False) >= hand_will_win_play_scry_bottom(n, x, k, 59):
                retval += ['top']
            else:
                retval += ['bottom']
    else:
        retval += ['mulligan']
    return retval


def mull_thing(n, x, k, draw=False):
    if draw:
        temp = should_i_keep_draw(n, x, k)
        hand_str = 'If you\'re on the draw and you have '
    else:
        temp = should_i_keep_play(n, x, k)
        hand_str = 'If you\'re on the play and you have '
    hand_str += str(k)
    hand_str += ' Spirit Guide and '
    hand_str += str(n - k)
    hand_str += ' Surging Flame, you should '
    hand_str += temp[2]
    if len(temp) == 5:
        hand_str += ', scry a Spirit Guide to the '
        hand_str += temp[3]
        hand_str += ' and scry a Surging Flame to the '
        hand_str += temp[4]
    hand_str += '.'
    return hand_str


def mull_guide(x, draw=False):
    """
    Generates each hand's mulligan recommendation
    :param int x: SSGs in deck
    :param boolean draw: Specifies whether the hand is on the draw, assumes that it is not
    :return string: A recommendation in plan English
    """
    for h in hand_gen():
        n = h[0]
        k = h[1]
        # hand_str = ''
        yield mull_thing(n, x, k, draw)


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
