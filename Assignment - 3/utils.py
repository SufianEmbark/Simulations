import math


def mean_ci_95(samples):
    """
    Compute the mean and the 95% confidence interval assuming a t-distribution with df = n-1.
    Uses a fixed critical t-value t_crit = 2.093 (df=19), consistent with 20 replications.
    Returns:
        mean: sample mean
        half: half-width of the confidence interval
        (lo, hi): lower and upper bounds of the confidence interval
    """
    n = len(samples)
    if n == 0:
        return float("nan"), float("nan"), (float("nan"), float("nan"))

    mean = sum(samples) / n

    if n == 1:
        return mean, float("nan"), (mean, mean)

    # Sample variance
    var = sum((x - mean) ** 2 for x in samples) / (n - 1)
    s = math.sqrt(var)

    # Critical t-value for 95% CI with df ~ 19
    t_crit = 2.093

    half = t_crit * s / math.sqrt(n)

    return mean, half, (mean - half, mean + half)


def print_metric(label, samples):
    """
    Print the mean and 95% confidence interval for a given set of samples.
    Also prints the relative half-width if the mean is greater than zero.
    """
    m, h, (lo, hi) = mean_ci_95(samples)

    if math.isnan(m):
        print(f"{label}: mean=nan, 95%CI=(nan,nan)")
        return

    print(f"{label}: mean={m:.4f}, 95%CI=({lo:.4f},{hi:.4f})")

    if m > 0:
        rel = h / m
        print(f"  relative half-width = {rel:.2%}")
