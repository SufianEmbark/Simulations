# Assignment 2 – Hospital Operating Theatre Simulation

## Overview
This assignment models the flow of patients through a hospital system with three stages:
1. Preparation  
2. Operation (Operating Theatre)  
3. Recovery  

The simulation tracks patient arrivals, service times, and resource usage.  
Metrics such as throughput, utilization, and queue lengths are collected.

---

## Configuration Parameters
The simulation is controlled via the `Config` class:

- **P** → Number of preparation rooms (default: 3)  
- **OP** → Number of operating theatres (default: 1)  
- **R** → Number of recovery rooms (default: 3)  
- **sim_time** → Total simulation time (default: 10,000)  
- **monitor_dt** → Monitoring interval for queue snapshots (default: 1.0)  
- **seed** → Random seed for reproducibility (default: 123)  

### Distributions (baseline exponential):
- Interarrival time ~ Exp(25)  
- Preparation time ~ Exp(40)  
- Operation time ~ Exp(20)  
- Recovery time ~ Exp(40)  

---

## How to Run
From the `Assignment2` folder:
```
python main.py
```


## Output
Console → Prints a summary of parameters at the start and results at the end.  

File → Detailed logs and metrics are saved in `simulation_output.txt`.  

Example console output:

=== Simulation start ===  
Parameters: P=3, R=3, OP=1, sim_time=10000, monitor_dt=1.0, seed=123  
Distributions: interarrival=25, prep=40, op=20, rec=40 (exponential)  
------------------------------------------------------------  
=== Simulation end ===  
Simulation results (baseline exponential):  
- patients_done: 392  
- theatre_utilization: 0.7552  
- theatre_block_rate: 0.0878  
- avg_throughput_time: 218.7469  
- avg_prep_queue_length: 0.3625  
(All logs and details are saved in simulation_output.txt)  

---

## Requirements
Python 3.10+  

SimPy library:  
```
pip install simpy
```
