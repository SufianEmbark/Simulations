import simpy, random, math
import logging
from typing import Dict, List

from config import Config
from metrics import Metrics
from model import Monitor, source_process

logger = logging.getLogger("hospital_sim")


def run_once(cfg: Config) -> Dict[str, float]:
    logger.debug(
        "Running one replication: P=%d, R=%d, OP=%d, sim_time=%.3f, warmup=%.3f, seed=%d, scenario=%s",
        cfg.P, cfg.R, cfg.OP, cfg.sim_time, cfg.warmup, cfg.seed, cfg.scenario
    )

    # Separate RNGs to maintain CRN across configurations
    rng_arr = random.Random(cfg.seed + 100)  # arrivals
    rng_prep = random.Random(cfg.seed + 200)  # preparation
    rng_op = random.Random(cfg.seed + 300)    # operation
    rng_rec = random.Random(cfg.seed + 400)   # recovery

    env = simpy.Environment()

    prep_res = simpy.Resource(env, capacity=cfg.P)
    theatre_res = simpy.Resource(env, capacity=cfg.OP)
    rec_res = simpy.Resource(env, capacity=cfg.R)

    metrics = Metrics(rec_capacity=cfg.R, verbose=cfg.verbose)

    Monitor(env, prep_res, metrics, cfg.monitor_dt)

    # Pass separate RNGs to the arrival process
    env.process(source_process(
        env, cfg, prep_res, theatre_res, rec_res, metrics,
        rng_arr, rng_prep, rng_op, rng_rec
    ))

    def do_warmup(env: simpy.Environment, metrics: Metrics, warmup: float):
        logger.debug("Starting warm-up period of length %.3f", warmup)
        yield env.timeout(warmup)
        logger.debug("Warm-up finished at time %.3f, starting observation", env.now)
        metrics.start_observation(env.now)

        # --- Synchronize real state after warm-up ---
        metrics.rec_count = rec_res.count
        if theatre_res.count > 0:
            metrics.theatre_state = "busy"
            metrics.last_state_change = env.now
        else:
            metrics.theatre_state = "idle"

        logger.debug(
            "Post-warmup sync: theatre_state=%s, rec_count=%d (cap=%d)",
            metrics.theatre_state, metrics.rec_count, metrics.rec_capacity
        )

    env.process(do_warmup(env, metrics, cfg.warmup))
    env.run(until=cfg.warmup + cfg.sim_time)

    res = metrics.summarize(env.now)
    res.update({"P": cfg.P, "R": cfg.R, "scenario": cfg.scenario})

    logger.debug(
        "Replication finished: P=%d, R=%d, scenario=%s, block_rate=%.6f, avg_qprep=%.6f, avg_prep_idle=%.6f, prob_rec_full=%.6f, avg_rec_wait=%.6f",
        cfg.P, cfg.R, cfg.scenario,
        res["theatre_block_rate"],
        res["avg_prep_queue_length"],
        res["avg_prep_idle_capacity"],
        res["prob_recovery_all_busy"],
        res["avg_rec_wait"]
    )

    return res


def mean_ci_95(samples: List[float]):
    """Compute mean and 95% CI using fixed t_crit=2.093 (df=19)."""
    n = len(samples)
    if n == 0:
        return float("nan"), float("nan"), (float("nan"), float("nan"))

    mean = sum(samples) / n
    if n == 1:
        return mean, float("nan"), (mean, mean)

    var = sum((x - mean) ** 2 for x in samples) / (n - 1)
    s = math.sqrt(var)
    t_crit = 2.093  # critical t-value for df=19
    half = t_crit * s / math.sqrt(n)

    return mean, half, (mean - half, mean + half)


def print_metric(label: str, samples: List[float]):
    """Print mean, 95% CI and relative half-width for a metric."""
    m, h, (lo, hi) = mean_ci_95(samples)

    if math.isnan(m):
        print(f"{label}: mean=nan, 95%CI=(nan,nan)")
        logger.info("%s: mean=nan, CI undefined", label)
        return

    print(f"{label}: mean={m:.4f}, 95%CI=({lo:.4f},{hi:.4f})")
    if m > 0:
        rel = h / m
        print(f" relative half-width = {rel:.2%}")
        logger.info(
            "%s: mean=%.6f, 95%%CI=(%.6f,%.6f), rel_half_width=%.4f",
            label, m, lo, hi, rel
        )
    else:
        print(" relative half-width = n/a (mean=0)")
        logger.info(
            "%s: mean=%.6f, 95%%CI=(%.6f,%.6f), mean is zero (relative width not defined)",
            label, m, lo, hi
        )

def run_independent_experiments():
    print("=== Independent experiments (different seeds) ===")
    logger.info("Starting independent experiments with different seeds")

    base_seed = 10_000
    n_rep = 20

    configs = {
        "3P4R": Config(P=3, R=4),
        "3P5R": Config(P=3, R=5),
        "4P5R": Config(P=4, R=5),
    }

    results = {
        name: {"block": [], "qprep": [], "recfull": [], "idle": []}
        for name in configs.keys()
    }

    for idx, (name, cfg) in enumerate(configs.items()):
        print(f"\n--- Config {name} ---")
        logger.info("Running config %s with %d replications", name, n_rep)

        for r in range(n_rep):
            cfg.seed = base_seed + 1000 * idx + r
            logger.debug("Replication %d for config %s with seed %d", r + 1, name, cfg.seed)

            res = run_once(cfg)
            results[name]["block"].append(res["theatre_block_rate"])
            results[name]["qprep"].append(res["avg_prep_queue_length"])
            results[name]["recfull"].append(res["prob_recovery_all_busy"])
            results[name]["idle"].append(res["avg_prep_idle_capacity"])

        print_metric("P(block OR)", results[name]["block"])
        print_metric("avg queue before prep", results[name]["qprep"])
        print_metric("avg idle capacity in prep", results[name]["idle"])
        print_metric("P(all recovery busy)", results[name]["recfull"])

    return results


def run_crn_experiments():
    print("\n\n=== Experiments with Common Random Numbers (CRN) ===")
    logger.info("Starting CRN experiments")

    base_seed = 20_000
    n_rep = 20

    cfg_3P4R = Config(P=3, R=4)
    cfg_3P5R = Config(P=3, R=5)
    cfg_4P5R = Config(P=4, R=5)

    diff_block_3P5R_4P5R = []
    diff_block_3P5R_3P4R = []
    diff_q_3P5R_4P5R = []
    diff_q_3P5R_3P4R = []

    for r in range(n_rep):
        seed = base_seed + r
        cfg_3P4R.seed = seed
        cfg_3P5R.seed = seed
        cfg_4P5R.seed = seed

        logger.debug("CRN replication %d with shared seed %d", r + 1, seed)

        res_3P4R = run_once(cfg_3P4R)
        res_3P5R = run_once(cfg_3P5R)
        res_4P5R = run_once(cfg_4P5R)

        diff_block_3P5R_4P5R.append(res_3P5R["theatre_block_rate"] - res_4P5R["theatre_block_rate"])
        diff_block_3P5R_3P4R.append(res_3P5R["theatre_block_rate"] - res_3P4R["theatre_block_rate"])
        diff_q_3P5R_4P5R.append(res_3P5R["avg_prep_queue_length"] - res_4P5R["avg_prep_queue_length"])
        diff_q_3P5R_3P4R.append(res_3P5R["avg_prep_queue_length"] - res_3P4R["avg_prep_queue_length"])

    def print_diff(label: str, diffs: List[float]):
        m, h, (lo, hi) = mean_ci_95(diffs)
        print(f"{label}: mean diff={m:.6f}, 95%CI=({lo:.6f},{hi:.6f})")
        logger.info("%s: mean_diff=%.6f, 95%%CI=(%.6f,%.6f)", label, m, lo, hi)

    print("\n--- Differences in P(block OR) ---")
    print_diff("3P5R - 4P5R (block)", diff_block_3P5R_4P5R)
    print_diff("3P5R - 3P4R (block)", diff_block_3P5R_3P4R)

    print("\n--- Differences in avg queue before prep ---")
    print_diff("3P5R - 4P5R (q_prep)", diff_q_3P5R_4P5R)
    print_diff("3P5R - 3P4R (q_prep)", diff_q_3P5R_3P4R)


def compare_block_vs_recfull_ci():
    print("\n\n=== Comparison of CI widths: blocking OR vs all recovery busy ===")
    logger.info("Comparing CI widths for blocking vs recovery-full probabilities")

    base_seed = 30_000
    n_rep = 20

    configs = {
        "3P4R": Config(P=3, R=4),
        "3P5R": Config(P=3, R=5),
        "4P5R": Config(P=4, R=5),
    }

    for idx, (name, cfg) in enumerate(configs.items()):
        blocks = []
        recfulls = []

        logger.info("Config %s: computing CI for block and recovery-full", name)

        for r in range(n_rep):
            cfg.seed = base_seed + 1000 * idx + r
            logger.debug("CI replication %d for config %s with seed %d", r + 1, name, cfg.seed)

            res = run_once(cfg)
            blocks.append(res["theatre_block_rate"])
            recfulls.append(res["prob_recovery_all_busy"])

        m_b, h_b, _ = mean_ci_95(blocks)
        m_r, h_r, _ = mean_ci_95(recfulls)

        rel_b = h_b / m_b if m_b > 0 else float("nan")
        rel_r = h_r / m_r if m_r > 0 else float("nan")

        print(f"\nConfig {name}:")
        if m_b > 0:
            print(f" P(block OR): mean={m_b:.6f}, half={h_b:.6f}, relative half-width={rel_b:.2%}")
        else:
            print(f" P(block OR): mean={m_b:.6f}, half={h_b:.6f}, relative half-width=n/a")

        if m_r > 0:
            print(f" P(all recovery busy): mean={m_r:.6f}, half={h_r:.6f}, relative half-width={rel_r:.2%}")
        else:
            print(f" P(all recovery busy): mean={m_r:.6f}, half={h_r:.6f}, relative half-width=n/a")

        logger.info(
            "Config %s: block mean=%.6f, half=%.6f, rel=%.4f; rec_full mean=%.6f, half=%.6f, rel=%.4f",
            name, m_b, h_b, rel_b if not math.isnan(rel_b) else -1.0,
            m_r, h_r, rel_r if not math.isnan(rel_r) else -1.0
        )


def twisted_scenario_experiment():
    print("\n\n=== Twisted scenario: same expected OR utilization (3P5R) ===")
    logger.info("Starting twisted scenario experiment for 3P5R")

    n_rep = 20
    base_seed = 40_000

    cfg_orig = Config(P=3, R=5, interarrival_mean=25.0, scenario="original")
    cfg_twist = Config(
        P=3, R=5,
        interarrival_mean=26.25,
        scenario="twisted",
        severe_prob=0.3,
        severe_op_mean=35.0,
        mild_op_mean=15.0
    )

    diff_block = []
    diff_qprep = []
    diff_recfull = []

    for r in range(n_rep):
        seed = base_seed + r
        cfg_orig.seed = seed
        cfg_twist.seed = seed

        logger.debug("Twisted replication %d with shared seed %d", r + 1, seed)

        res_o = run_once(cfg_orig)
        res_t = run_once(cfg_twist)

        diff_block.append(res_t["theatre_block_rate"] - res_o["theatre_block_rate"])
        diff_qprep.append(res_t["avg_prep_queue_length"] - res_o["avg_prep_queue_length"])
        diff_recfull.append(res_t["prob_recovery_all_busy"] - res_o["prob_recovery_all_busy"])

    def print_diff(label: str, diffs: List[float]):
        m, h, (lo, hi) = mean_ci_95(diffs)
        print(f"{label}: mean diff={m:.6f}, 95%CI=({lo:.6f},{hi:.6f})")
        logger.info("%s: mean_diff=%.6f, 95%%CI=(%.6f,%.6f)", label, m, lo, hi)

    print("\nDifferences (twisted - original) for 3P5R:")
    print_diff("P(block OR)", diff_block)
    print_diff("avg queue before prep", diff_qprep)
    print_diff("P(all recovery busy)", diff_recfull)