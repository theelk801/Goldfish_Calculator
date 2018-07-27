from math import factorial as fac


def memoize(f):
    """
    Memoization decorator for functions taking one or more arguments.
    """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
            super().__init__()

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