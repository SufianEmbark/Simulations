# Assignment 4 – Hospital Operating Theatre Simulation (Extension of Assignment 3)

## Overview
This assignment extends Assignment 3 by adding new experimental design and analysis features.
Patients still flow through three stages:
1. Preparation
2. Operation (Operating Theatre)
3. Recovery

The simulation tracks arrivals, service times, and resource usage.
Metrics collected include throughput, utilization, blocking probability, queue lengths, recovery bed usage, and average waiting time for recovery.

New in Assignment 4:
- Support for exponential or uniform distributions for interarrival, preparation, and recovery times
- Serial correlation analysis in high-utilisation settings
- A 2^4 full factorial design (16 configurations × 20 replications)
- A regression metamodel to quantify factor effects and interactions

Experiments now include independent replications, Common Random Numbers (CRN), CI width comparison, twisted scenario, serial correlation study, factorial design, and regression modelling.

---

## Configuration Parameters
Simulation parameters are defined in the Config class:

- P → Number of preparation rooms
- OP → Number of operating theatres
- R → Number of recovery rooms
- sim_time → Simulation time after warm-up
- warmup → Warm-up period before observation
- monitor_dt → Monitoring interval for queue/beds sampling
- seed → Random seed for reproducibility

### Distributions
Each stage can now use either exponential or uniform distributions. The following parameters are available in the Config class:

Interarrival time:
- interarrival_dist: "exp" or "unif"
- Exponential: interarrival_mean
- Uniform: interarrival_low, interarrival_high

Preparation time:
- prep_dist: "exp" or "unif"
- Exponential: prep_mean
- Uniform: prep_low, prep_high

Operation time:
- Baseline: exponential (op_mean)
- Twisted scenario: mixture of severe/mild cases with different operation-time means

Recovery time:
- rec_dist: "exp" or "unif"
- Exponential: rec_mean
- Uniform: rec_low, rec_high

---

## How to Run
From the assignment folder:
python main.py

---

## Output
All printed output is redirected to results.txt.
Detailed logs are written to simulation.log.

results.txt includes:
- Independent experiments
- CRN comparisons
- CI width comparison
- Twisted scenario differences
- Serial correlation results
- Full factorial table (16 runs)
- Regression model coefficients

simulation.log includes:
- Detailed event logs (arrivals, preparation, operation, recovery, departures)

---

## Requirements
Python 3.10+

SimPy library:
```
pip install simpy
```

Numpy library:
```
pip install numpy
```
---

## Files
config.py → Simulation parameters and distribution settings
model.py → Patient processes and monitoring
metrics.py → Metrics collection and logging
analysis.py → Experiment definitions, factorial design, regression model
main.py → Entry point, sets up logging and runs experiments
results.txt → Experiment results
simulation.log → Detailed logs

Additionally, the written analysis for Assignment 4 is provided in the file:
Analysis.pdf
This document contains the full explanation of the serial correlation study, the 2^4 factorial design, the regression metamodel, and the conclusions.
