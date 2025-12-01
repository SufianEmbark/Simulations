import simpy
import random
import logging
from dataclasses import dataclass

from metrics import Metrics
from config import Config

logger = logging.getLogger("hospital_sim")


# -------------------------
# Patient dataclass
# -------------------------

@dataclass
class Patient:
    pid: int
    ptype: str
    t_arrival: float
    prep_time: float
    op_time: float
    rec_time: float
    t_exit: float = None


# -------------------------
# Sampling helpers
# -------------------------

def exp_sample(rng: random.Random, mean: float) -> float:
    """Sample from an exponential distribution with given mean."""
    return rng.expovariate(1.0 / mean)


def sample_op_time(cfg: Config, rng: random.Random):
    """Return sampled operation time and patient type label."""
    if cfg.scenario == "original":
        return exp_sample(rng, cfg.op_mean), "base"
    else:
        if rng.random() < cfg.severe_prob:
            return exp_sample(rng, cfg.severe_op_mean), "severe"
        else:
            return exp_sample(rng, cfg.mild_op_mean), "mild"


# -------------------------
# Patient flow process
# -------------------------

def patient_process(env, patient, cfg, prep_res, theatre_res, rec_res, metrics: Metrics):
    # ---- Preparation ----
    logger.debug("Patient %d enters prep queue at t=%.3f", patient.pid, env.now)
    with prep_res.request() as req_prep:
        yield req_prep
        logger.debug("Patient %d starts preparation at t=%.3f (dur=%.3f)", patient.pid, env.now, patient.prep_time)
        yield env.timeout(patient.prep_time)
        logger.debug("Patient %d finishes preparation at t=%.3f", patient.pid, env.now)

    # ---- Operation ----
    with theatre_res.request() as req_theatre:
        yield req_theatre
        metrics.set_theatre_state(env.now, "busy")
        logger.debug("Patient %d starts operation at t=%.3f (dur=%.3f)", patient.pid, env.now, patient.op_time)
        yield env.timeout(patient.op_time)
        logger.debug("Patient %d finishes operation at t=%.3f", patient.pid, env.now)

        # --- Operating room blocked while waiting for recovery bed ---
        with rec_res.request() as req_rec:
            metrics.set_theatre_state(env.now, "blocked")
            t_start_wait = env.now
            logger.debug("Patient %d blocks OR at t=%.3f waiting for recovery bed", patient.pid, env.now)
            yield req_rec
            wait_time = env.now - t_start_wait
            metrics.record_rec_wait(wait_time)
            metrics.rec_enter(env.now)
            logger.debug("Patient %d gets recovery bed at t=%.3f (wait=%.3f)", patient.pid, env.now, wait_time)

        # Once bed is obtained, operating room becomes idle
        metrics.set_theatre_state(env.now, "idle")
        logger.debug("Operating room idle at t=%.3f after patient %d moved to recovery", env.now, patient.pid)

    # ---- Recovery ----
    logger.debug("Patient %d starts recovery at t=%.3f (dur=%.3f)", patient.pid, env.now, patient.rec_time)
    yield env.timeout(patient.rec_time)
    metrics.rec_leave(env.now)
    logger.debug("Patient %d finishes recovery and releases bed at t=%.3f", patient.pid, env.now)

    # ---- Departure ----
    patient.t_exit = env.now
    metrics.record_patient_departure(patient.t_exit, patient.t_arrival)
    logger.debug("Patient %d leaves system at t=%.3f (total time=%.3f)", patient.pid, patient.t_exit, patient.t_exit - patient.t_arrival)


# -------------------------
# Patient arrival process
# -------------------------

def source_process(env, cfg, prep_res, theatre_res, rec_res, metrics: Metrics,
                   rng_arr: random.Random, rng_prep: random.Random,
                   rng_op: random.Random, rng_rec: random.Random):
    pid = 0

    while True:
        # Interarrival time
        ia = exp_sample(rng_arr, cfg.interarrival_mean)
        yield env.timeout(ia)

        pid += 1
        op_time, ptype = sample_op_time(cfg, rng_op)
        prep_time = exp_sample(rng_prep, cfg.prep_mean)
        rec_time = exp_sample(rng_rec, cfg.rec_mean)

        p = Patient(
            pid=pid,
            ptype=ptype,
            t_arrival=env.now,
            prep_time=prep_time,
            op_time=op_time,
            rec_time=rec_time,
        )

        logger.debug(
            "Patient %d arrival at t=%.3f: prep=%.3f, op=%.3f, rec=%.3f, type=%s",
            pid, p.t_arrival, prep_time, op_time, rec_time, p.ptype
        )

        env.process(
            patient_process(env, p, cfg, prep_res, theatre_res, rec_res, metrics)
        )


# -------------------------
# Continuous monitoring of prep queue
# -------------------------

class Monitor:
    def __init__(self, env: simpy.Environment, prep_res: simpy.Resource, metrics: Metrics, dt: float):
        self.env = env
        self.prep_res = prep_res
        self.metrics = metrics
        self.dt = dt
        env.process(self.run())

    def run(self):
        while True:
            qlen = len(self.prep_res.queue)
            idle = self.prep_res.capacity - self.prep_res.count

            self.metrics.record_prep_queue_sample(qlen)
            self.metrics.record_prep_idle_sample(idle)

            # Optional periodic sampling log (commented to avoid log flooding):
            # logger.debug("Prep sampling at t=%.3f: qlen=%d, idle=%d", self.env.now, qlen, idle)

            yield self.env.timeout(self.dt)
