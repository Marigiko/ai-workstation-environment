"""Fibonacci number calculation using dynamic programming."""


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number using bottom-up dynamic programming.

    The Fibonacci sequence is defined as:
        F(0) = 0, F(1) = 1
        F(n) = F(n-1) + F(n-2) for n > 1

    Args:
        n: A non-negative integer index into the Fibonacci sequence.

    Returns:
        The nth Fibonacci number.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    if n <= 1:
        return n

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


if __name__ == "__main__":
    for i in range(15):
        print(f"F({i}) = {fibonacci(i)}")
