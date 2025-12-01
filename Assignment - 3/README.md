# Assignment 3 – Hospital Operating Theatre Simulation

## Overview
This assignment extends the hospital operating theatre simulation.  
Patients flow through three stages:
1. Preparation  
2. Operation (Operating Theatre)  
3. Recovery  

The simulation tracks arrivals, service times, and resource usage.  
Metrics collected include throughput, utilization, blocking probability, queue lengths, recovery bed usage, and average waiting time for recovery.  
Experiments include independent replications, Common Random Numbers (CRN), comparison of confidence interval widths, and a twisted scenario.

---

## Configuration Parameters
Simulation parameters are defined in the `Config` class:

- **P** → Number of preparation rooms  
- **OP** → Number of operating theatres  
- **R** → Number of recovery rooms  
- **sim_time** → Simulation time after warm-up  
- **warmup** → Warm-up period before observation  
- **monitor_dt** → Monitoring interval for queue/beds sampling  
- **seed** → Random seed for reproducibility  

### Distributions (baseline exponential):
- Interarrival time ~ Exp(25)  
- Preparation time ~ Exp(40)  
- Operation time ~ Exp(20)  
- Recovery time ~ Exp(40)  

Twisted scenario: mixture of severe/mild cases with different operation times.

---

## How to Run
From the `Assignment - 3` folder:
```
python main.py
```

## Output
Console → Summaries of experiments and confidence intervals.

results.txt → Formatted results of all experiments.

simulation.log → Detailed event logs (arrivals, preparation, operation, recovery, departures).

Example console output:
```
=== Independent experiments (different seeds) ===
--- Config 3P4R ---
P(block OR): mean=0.0000, 95%CI=(0.0000,0.0000)
avg queue before prep: mean=0.2361, 95%CI=(0.1202,0.3520)
avg idle capacity in prep: mean=1.3803, 95%CI=(1.1797,1.5810)
P(all recovery busy): mean=0.0157, 95%CI=(0.0029,0.0285)
...
=== Twisted scenario: same expected OR utilization (3P5R) ===
Differences (twisted - original) for 3P5R:
P(block OR): mean diff=0.000000, 95%CI=(0.000000,0.000000)
avg queue before prep: mean diff=-0.060300, 95%CI=(-0.101449,-0.019151)
P(all recovery busy): mean diff=0.000633, 95%CI=(-0.006685,0.007951)
```
---
## Requirements
Python 3.10+  

SimPy library:  
```
pip install simpy
```
---

## Files
config.py → Simulation parameters

model.py → Patient processes and monitoring

metrics.py → Metrics collection and logging

analysis.py → Experiment definitions and statistical analysis

main.py → Entry point, sets up logging and runs experiments

results.txt → Experiment results

simulation.log → Detailed logs