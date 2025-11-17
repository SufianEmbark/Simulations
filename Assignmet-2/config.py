import random
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class Config:
    # Capacities
    P: int = 3
    R: int = 3
    OP: int = 1  # operating theatre
    # Simulation duration and monitor sampling interval
    sim_time: float = 10_000.0
    monitor_dt: float = 1.0
    seed: int = 42

    # Patient types (future-proofing)
    # ptype -> time sampling functions
    time_fns: Dict[str, Dict[str, Callable[[], float]]] = None
    interarrival_fn: Callable[[], float] = None

    def __post_init__(self):
        random.seed(self.seed)
        # Base distributions (exponentials)
        if self.interarrival_fn is None:
            self.interarrival_fn = lambda: random.expovariate(1/25)
        if self.time_fns is None:
            # Single 'base' type for now; easy to extend with more types
            self.time_fns = {
                'base': {
                    'prep': lambda: random.expovariate(1/40),
                    'op':   lambda: random.expovariate(1/20),
                    'rec':  lambda: random.expovariate(1/40),
                }
            }

        # Initial configuration debug
        print("[Config] Initialized with parameters:")
        print(f"  P={self.P}, R={self.R}, OP={self.OP}, sim_time={self.sim_time}, monitor_dt={self.monitor_dt}, seed={self.seed}")
        print("  Distributions: interarrival=Exp(25), prep=Exp(40), op=Exp(20), rec=Exp(40)")

    # Helper to create new patients carrying personal service times by type
    def sample_patient_times(self, ptype: str = 'base') -> Dict[str, float]:
        f = self.time_fns[ptype]
        times = {
            'prep': f['prep'](),
            'op':   f['op'](),
            'rec':  f['rec'](),
        }
        # Debug: show sampled times assigned to the patient
        print(f"[Config] Assigned times for patient type '{ptype}': prep={times['prep']:.2f}, op={times['op']:.2f}, rec={times['rec']:.2f}")
        return times
