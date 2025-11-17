import simpy

class Monitor:
    """
    Monitoring process by sampling:
    - Takes snapshots of the preparation queue length every Δt.
    - Also prints the current state of the operating theatre for debugging.
    """
    def __init__(self, env: simpy.Environment, prep_res: simpy.Resource, metrics, dt: float):
        self.env = env
        self.prep_res = prep_res
        self.metrics = metrics
        self.dt = dt
        self.proc = env.process(self.run())
        print(f"[Monitor] Started with sampling interval={dt}")

    def run(self):
        while True:
            # Length of the preparation queue
            qlen = len(self.prep_res.queue)
            self.metrics.record_prep_queue_sample(qlen)
            # Debug: print snapshot
            print(f"[Monitor] t={self.env.now:.1f}: preparation queue={qlen}, theatre state={self.metrics.theatre_state}")
            yield self.env.timeout(self.dt)
