import logging

logger = logging.getLogger("hospital_sim")


class Metrics:
    def __init__(self, rec_capacity: int, verbose: bool = False):
        self.verbose = verbose

        # Observation state
        self.observing = False
        self.obs_start_time = 0.0

        # Throughput & departures
        self.n_done = 0
        self.throughput_sum = 0.0

        # Operating theatre state
        self.theatre_state = "idle"  # idle / busy / blocked
        self.last_state_change = 0.0
        self.theatre_busy_time = 0.0
        self.theatre_blocked_time = 0.0

        # Preparation queue samples
        self.prep_queue_samples_sum = 0.0
        self.prep_queue_samples_n = 0

        # Preparation idle capacity samples
        self.prep_idle_samples_sum = 0.0
        self.prep_idle_samples_n = 0

        # Recovery beds
        self.rec_capacity = rec_capacity
        self.rec_count = 0
        self.rec_last_change = 0.0
        self.rec_full_time = 0.0

        # --- New metric: waiting time for recovery bed ---
        self.rec_wait_sum = 0.0
        self.rec_wait_n = 0

    # -------------------------
    # Observation control
    # -------------------------

    def start_observation(self, now: float):
        """Start observation period and reset all counters."""
        self.observing = True
        self.obs_start_time = now

        # Reset counters
        self.n_done = 0
        self.throughput_sum = 0.0
        self.theatre_busy_time = 0.0
        self.theatre_blocked_time = 0.0

        self.prep_queue_samples_sum = 0.0
        self.prep_queue_samples_n = 0
        self.prep_idle_samples_sum = 0.0
        self.prep_idle_samples_n = 0

        self.rec_full_time = 0.0
        self.rec_wait_sum = 0.0
        self.rec_wait_n = 0

        self.last_state_change = now
        self.rec_last_change = now

    # -------------------------
    # Operating theatre tracking
    # -------------------------

    def _flush_theatre(self, now: float):
        """Update accumulated times for theatre states up to 'now'."""
        if not self.observing:
            self.last_state_change = now
            return

        dur = now - self.last_state_change
        if dur > 0:
            if self.theatre_state == "busy":
                self.theatre_busy_time += dur
            elif self.theatre_state == "blocked":
                self.theatre_blocked_time += dur

        self.last_state_change = now

    def set_theatre_state(self, now: float, new_state: str):
        """Change theatre state and flush previous duration."""
        self._flush_theatre(now)
        self.theatre_state = new_state

    # -------------------------
    # Recovery beds tracking
    # -------------------------

    def _flush_rec(self, now: float):
        """Update accumulated time when all recovery beds are full."""
        if not self.observing:
            self.rec_last_change = now
            return

        dur = now - self.rec_last_change
        if dur > 0 and self.rec_count == self.rec_capacity:
            self.rec_full_time += dur

        self.rec_last_change = now

    def rec_enter(self, now: float):
        """Record patient entering recovery bed."""
        self._flush_rec(now)
        self.rec_count += 1
        logger.debug(
            "Recovery enter at %.3f, count=%d/%d",
            now, self.rec_count, self.rec_capacity
        )

    def rec_leave(self, now: float):
        """Record patient leaving recovery bed."""
        self._flush_rec(now)
        self.rec_count -= 1
        logger.debug(
            "Recovery leave at %.3f, count=%d/%d",
            now, self.rec_count, self.rec_capacity
        )

    # -------------------------
    # Sampling
    # -------------------------

    def record_prep_queue_sample(self, qlen: int):
        """Record a sample of preparation queue length."""
        if not self.observing:
            return
        self.prep_queue_samples_sum += qlen
        self.prep_queue_samples_n += 1

    def record_prep_idle_sample(self, idle: int):
        """Record a sample of idle preparation capacity."""
        if not self.observing:
            return
        self.prep_idle_samples_sum += idle
        self.prep_idle_samples_n += 1

    # -------------------------
    # New metric: recovery waiting time
    # -------------------------

    def record_rec_wait(self, wait_time: float):
        """Record waiting time for recovery bed."""
        if self.observing:
            self.rec_wait_sum += wait_time
            self.rec_wait_n += 1

    # -------------------------
    # Departures and throughput
    # -------------------------

    def record_patient_departure(self, t_exit: float, t_arrival: float):
        """Record patient departure and total time in system."""
        if not self.observing:
            return
        self.n_done += 1
        self.throughput_sum += (t_exit - t_arrival)

    # -------------------------
    # Final summary
    # -------------------------

    def summarize(self, now: float):
        """Summarize all metrics at the end of observation."""
        self._flush_theatre(now)
        self._flush_rec(now)

        total_time = (now - self.obs_start_time) if self.observing else 0.0

        util = self.theatre_busy_time / total_time if total_time > 0 else float("nan")
        block_rate = self.theatre_blocked_time / total_time if total_time > 0 else float("nan")
        prob_rec_full = self.rec_full_time / total_time if total_time > 0 else float("nan")

        avg_thr = self.throughput_sum / self.n_done if self.n_done > 0 else float("nan")
        avg_qprep = (
            self.prep_queue_samples_sum / self.prep_queue_samples_n
            if self.prep_queue_samples_n > 0 else float("nan")
        )
        avg_prep_idle = (
            self.prep_idle_samples_sum / self.prep_idle_samples_n
            if self.prep_idle_samples_n > 0 else float("nan")
        )

        avg_rec_wait = (
            self.rec_wait_sum / self.rec_wait_n
            if self.rec_wait_n > 0 else float("nan")
        )

        return {
            "patients_done": self.n_done,
            "theatre_utilization": util,
            "theatre_block_rate": block_rate,
            "avg_throughput_time": avg_thr,
            "avg_prep_queue_length": avg_qprep,
            "avg_prep_idle_capacity": avg_prep_idle,
            "prob_recovery_all_busy": prob_rec_full,
            "avg_rec_wait": avg_rec_wait,
        }
