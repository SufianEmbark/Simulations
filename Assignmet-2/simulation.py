import simpy
from config import Config
from patient import Patient
from metrics import Metrics
from monitor import Monitor

def patient_process(env, pat: Patient, prep_res: simpy.Resource, theatre_res: simpy.Resource, rec_res: simpy.Resource, metrics: Metrics):
    # PREPARATION
    with prep_res.request() as req_prep:
        yield req_prep
        yield env.timeout(pat.prep_time)

    # OPERATION
    with theatre_res.request() as req_op:
        yield req_op
        # operating theatre busy
        metrics.set_theatre_state(env.now, 'busy')
        yield env.timeout(pat.op_time)
        # try recovery before releasing the theatre
        rec_req = rec_res.request()
        blocked_start = env.now
        # at this yield, if no bed is available, it will wait -> state 'blocked'
        # explicitly change the state to blocked at the end of the operation
        metrics.set_theatre_state(blocked_start, 'blocked')
        yield rec_req
        # recovery bed granted: theatre returns to 'idle'
        metrics.set_theatre_state(env.now, 'idle')

    # RECOVERY
    yield env.timeout(pat.rec_time)
    rec_res.release(rec_req)

    # TERMINATION
    pat.t_exit = env.now
    metrics.record_patient_departure(pat.t_exit, pat.t_arrival)

def generator(env, cfg: Config, prep_res: simpy.Resource, theatre_res: simpy.Resource, rec_res: simpy.Resource, metrics: Metrics):
    pid = 0
    while True:
        # wait for the next interarrival
        ia = cfg.interarrival_fn()
        yield env.timeout(ia)

        # create patient with personal service times (carries their times)
        times = cfg.sample_patient_times('base')  # future: use different ptypes
        pat = Patient(
            pid=pid,
            ptype='base',
            t_arrival=env.now,
            prep_time=times['prep'],
            op_time=times['op'],
            rec_time=times['rec'],
        )
        env.process(patient_process(env, pat, prep_res, theatre_res, rec_res, metrics))
        pid += 1

def run_once(cfg: Config):
    env = simpy.Environment()

    # Resources (pools)
    prep_res = simpy.Resource(env, capacity=cfg.P)
    theatre_res = simpy.Resource(env, capacity=cfg.OP)
    rec_res = simpy.Resource(env, capacity=cfg.R)

    # Metrics and monitor
    metrics = Metrics()
    monitor = Monitor(env, prep_res, metrics, cfg.monitor_dt)

    # Main processes
    env.process(generator(env, cfg, prep_res, theatre_res, rec_res, metrics))

    # Run
    env.run(until=cfg.sim_time)

    # Summary
    return metrics.summarize(cfg.sim_time)
