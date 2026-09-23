# Autoresearch Report — synthetic-polynomial-regression

## Objective

Minimize held-out mean squared error on a noisy nonlinear regression problem.

## Hypothesis

A quadratic model will improve on the linear baseline without the variance of higher degrees.

## Method

Planner: `deterministic-heuristic`. Budget: 8 experiments. Selection metric: `mean_squared_error` (lower is better).

## Leaderboard

| Rank | Experiment | Degree | Ridge | Train MSE | Validation MSE |
|---:|---|---:|---:|---:|---:|
| 1 | exp-06 | 2 | 0.1 | 0.144051 | 0.133288 |
| 2 | exp-05 | 2 | 0.01 | 0.144045 | 0.133899 |
| 3 | exp-04 | 2 | 0.0 | 0.144045 | 0.133968 |
| 4 | exp-07 | 3 | 0.0 | 0.143836 | 0.136273 |
| 5 | exp-10 | 4 | 0.0 | 0.142534 | 0.137364 |
| 6 | exp-03 | 1 | 0.1 | 3.972408 | 4.147926 |
| 7 | exp-02 | 1 | 0.01 | 3.972403 | 4.148990 |
| 8 | exp-01 | 1 | 0.0 | 3.972403 | 4.149109 |

## Selected model

- Experiment: `exp-06`
- Parameters: `{"degree": 2, "ridge": 0.1}`
- Validation MSE: `0.133288`
- Held-out test MSE: `0.166747`
- Reproduction delta: `0.000000000000`
- Failed experiments: `0`

## Evidence gate

- [x] at least one experiment
- [x] best reproduced
- [x] test metric is finite

Overall: **PASS**

## Conclusion

The winning configuration was selected only on validation performance and evaluated once on the held-out test split. The exact event stream, all candidates, and serialized coefficients are saved beside this report.
