import sys
from config import Config
from simulation import run_once

def main():
    # Redirect all output to simulation_output.txt
    log_file = open("simulation_output.txt", "w", encoding="utf-8")
    sys.stdout = log_file
    console = sys.__stdout__  # keep console reference

    # Initial configuration
    cfg = Config(
        P=3,
        R=3,
        OP=1,
        sim_time=10_000,
        monitor_dt=1.0,
        seed=123
    )

    # Initial debug (printed to file and console)
    init_text = (
        "[Config] Initialized with parameters:\n"
        f"  P={cfg.P}, R={cfg.R}, OP={cfg.OP}, sim_time={cfg.sim_time}, monitor_dt={cfg.monitor_dt}, seed={cfg.seed}\n"
        "  Distributions: interarrival=Exp(25), prep=Exp(40), op=Exp(20), rec=Exp(40)\n"
        "=== Simulation start ===\n"
        f"Parameters: P={cfg.P}, R={cfg.R}, OP={cfg.OP}, sim_time={cfg.sim_time}, monitor_dt={cfg.monitor_dt}, seed={cfg.seed}\n"
        "Distributions: interarrival=25, prep=40, op=20, rec=40 (exponential)\n"
        "------------------------------------------------------------"
    )
    print(init_text)
    console.write(init_text + "\n")

    # Run simulation
    results = run_once(cfg)

    # Final debug (printed to file and console)
    end_text = (
        "=== Simulation end ===\n"
        "Simulation results (baseline exponential):\n"
        + "\n".join(
            f"- {k}: {v:.4f}" if isinstance(v, float) else f"- {k}: {v}"
            for k, v in results.items()
        )
        + "\n(All logs and details are saved in simulation_output.txt)"
    )
    print(end_text)
    console.write(end_text + "\n")

    log_file.close()

if __name__ == '__main__':
    main()
