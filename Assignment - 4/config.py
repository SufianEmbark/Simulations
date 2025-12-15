from dataclasses import dataclass

@dataclass
class Config:
    # -------------------------
    # System capacities
    # -------------------------

    # Number of preparation rooms
    P: int
    # Number of recovery rooms
    R: int
    # Number of operating theatres (default: 1)
    OP: int = 1

    # -------------------------
    # Simulation control
    # -------------------------

    # Simulation time (observation length after warm-up)
    sim_time: float = 1000.0
    # Warm-up period before starting observation
    warmup: float = 200.0
    # Monitoring interval for periodic sampling
    monitor_dt: float = 1.0

    # Random seed for reproducibility
    seed: int = 123

    # -------------------------
    # Interarrival time distribution
    # -------------------------
    # interarrival_dist ∈ {"exp", "unif"}
    interarrival_dist: str = "exp"
    # Parameters for exponential arrivals
    interarrival_mean: float = 25.0
    # Parameters for uniform arrivals
    interarrival_low: float = 20.0
    interarrival_high: float = 30.0

    # -------------------------
    # Preparation time distribution
    # -------------------------
    # prep_dist ∈ {"exp", "unif"}
    prep_dist: str = "exp"
    # Parameters for exponential preparation
    prep_mean: float = 40.0
    # Parameters for uniform preparation
    prep_low: float = 30.0
    prep_high: float = 50.0

    # -------------------------
    # Operation time distribution
    # -------------------------
    # For Assignment 3, operation time is always exponential with mean 20
    op_mean: float = 20.0

    # -------------------------
    # Twisted scenario (optional)
    # -------------------------
    # Scenario type: "original" or "twisted"
    scenario: str = "original"

    # Parameters for twisted scenario (mixture of severe/mild cases)
    severe_prob: float = 0.3          # probability of severe case
    severe_op_mean: float = 35.0      # mean operation time for severe case
    mild_op_mean: float = 15.0        # mean operation time for mild case

    # -------------------------
    # Recovery time distribution
    # -------------------------
    # rec_dist ∈ {"exp", "unif"}
    rec_dist: str = "exp"
    # Parameters for exponential recovery
    rec_mean: float = 40.0
    # Parameters for uniform recovery
    rec_low: float = 30.0
    rec_high: float = 50.0

    # Verbose flag for additional logging
    verbose: bool = False
