from dataclasses import dataclass

@dataclass
class Config:
    # Number of preparation rooms
    P: int
    # Number of recovery rooms
    R: int

    # Number of operating theatres (default: 1)
    OP: int = 1
    # Simulation time (observation length after warm-up)
    sim_time: float = 1000.0
    # Warm-up period before starting observation
    warmup: float = 200.0
    # Monitoring interval for periodic sampling
    monitor_dt: float = 1.0

    # Random seed for reproducibility
    seed: int = 123

    # Mean values for exponential distributions
    interarrival_mean: float = 25.0   # mean interarrival time
    prep_mean: float = 40.0           # mean preparation time
    op_mean: float = 20.0             # mean operation time
    rec_mean: float = 40.0            # mean recovery time

    # Scenario type: "original" or "twisted"
    scenario: str = "original"

    # Parameters for twisted scenario (mixture of severe/mild cases)
    severe_prob: float = 0.3          # probability of severe case
    severe_op_mean: float = 35.0      # mean operation time for severe case
    mild_op_mean: float = 15.0        # mean operation time for mild case

    # Verbose flag for additional logging
    verbose: bool = False
