import logging
import sys

from analysis import (
    run_independent_experiments,
    run_crn_experiments,
    compare_block_vs_recfull_ci,
    twisted_scenario_experiment,
    run_factorial_experiments,
    regression_from_factorial
)

# Redirect all printed output to a text file
sys.stdout = open("results.txt", "w", encoding="utf-8")

logger = logging.getLogger("hospital_sim")


def setup_logging():
    """Configure logging to both file and console."""
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # File handler (writes detailed logs to simulation.log)
    fh = logging.FileHandler("simulation.log", mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # Console handler (prints INFO level and above to console)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # Clear existing handlers and add the new ones
    logger.handlers.clear()
    logger.addHandler(fh)
    logger.addHandler(ch)


if __name__ == "__main__":
    setup_logging()
    logger.info("Starting hospital simulation experiments")

    run_independent_experiments()
    run_crn_experiments()
    compare_block_vs_recfull_ci()
    twisted_scenario_experiment()
    results = run_factorial_experiments()
    betas = regression_from_factorial(results)

    logger.info("All experiments completed")
