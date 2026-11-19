
### free slip, sigma_rr

| wall | route | L2 h=1/8 | L2 h=1/16 | L2 h=1/32 | order | max h=1/32 | L2 midpoints h=1/32 | cost / solve h=1/32 |
|---|---|---|---|---|---|---|---|---|
| Lower | 857 CBF + reconstruction | 5.61e-04 | 4.55e-05 | 5.52e-06 | 3.33 | 2.12e-05 | 4.97e-06 | 0.028 |
| Lower | 857 circular CBF | 3.19e-03 | 4.97e-04 | 1.58e-04 | 2.17 | 4.87e-04 | 1.09e-04 | 0.004 |
| Lower | raw FE stress at nodes [857 solve] | 1.28e-02 | 3.26e-03 | 7.70e-04 | 2.03 | 1.75e-03 | 3.55e-04 | 0.215 |
| Lower | raw FE stress at nodes [development solve] | 1.08e-02 | 2.68e-03 | 6.97e-04 | 1.98 | 1.29e-03 | 7.83e-04 | 0.288 |
| Lower | rotated reaction (consistent) [857 solve] | 6.59e-03 | 1.54e-03 | 4.46e-04 | 1.94 | 9.05e-04 | 4.33e-04 | 0.003 |
| Lower | rotated reaction (consistent) [development solve] | 2.03e-02 | 1.22e-02 | 6.50e-03 | 0.82 | 1.17e-02 | 4.45e-03 | 0.004 |
| Lower | rotated reaction (lumped) [857 solve] | 4.67e-03 | 1.25e-03 | 3.18e-04 | 1.94 | 7.54e-04 | 5.16e-05 | 0.003 |
| Lower | rotated reaction (lumped) [development solve] | 1.45e-02 | 6.42e-03 | 2.99e-03 | 1.14 | 5.26e-03 | 2.22e-03 | 0.004 |
| Upper | 857 CBF + reconstruction | 2.94e-04 | 5.11e-05 | 1.12e-05 | 2.36 | 3.42e-05 | 1.08e-05 | 0.034 |
| Upper | 857 circular CBF | 3.01e-03 | 8.11e-04 | 2.10e-04 | 1.92 | 7.71e-04 | 1.50e-04 | 0.006 |
| Upper | raw FE stress at nodes [857 solve] | 1.34e-02 | 4.12e-03 | 1.57e-03 | 1.55 | 2.73e-03 | 1.73e-03 | 0.132 |
| Upper | raw FE stress at nodes [development solve] | 1.06e-02 | 3.36e-03 | 1.37e-03 | 1.48 | 2.45e-03 | 1.52e-03 | 0.227 |
| Upper | rotated reaction (consistent) [857 solve] | 6.51e-03 | 1.76e-03 | 4.59e-04 | 1.91 | 1.28e-03 | 6.29e-04 | 0.003 |
| Upper | rotated reaction (consistent) [development solve] | 3.03e-03 | 2.24e-03 | 1.37e-03 | 0.57 | 2.87e-03 | 6.68e-04 | 0.009 |
| Upper | rotated reaction (lumped) [857 solve] | 5.65e-03 | 1.52e-03 | 3.95e-04 | 1.92 | 1.01e-03 | 5.50e-04 | 0.003 |
| Upper | rotated reaction (lumped) [development solve] | 2.45e-03 | 8.84e-04 | 5.00e-04 | 1.15 | 1.15e-03 | 1.21e-04 | 0.007 |

### zero slip, sigma_rr

| wall | route | L2 h=1/8 | L2 h=1/16 | L2 h=1/32 | order | max h=1/32 | L2 midpoints h=1/32 | cost / solve h=1/32 |
|---|---|---|---|---|---|---|---|---|
| Lower | 857 CBF + reconstruction | 1.33e-03 | 2.19e-04 | 4.32e-05 | 2.47 | 8.81e-05 | 4.12e-05 | 0.210 |
| Lower | 857 circular CBF | 7.99e-03 | 2.86e-03 | 6.58e-04 | 1.80 | 1.86e-03 | 3.85e-04 | 0.210 |
| Lower | boundary_flux CBF (consistent) [857 solve] | 2.28e-02 | 6.93e-03 | 1.74e-03 | 1.86 | 3.93e-03 | 1.02e-03 | 0.027 |
| Lower | boundary_flux CBF (consistent) [development solve] | 1.14e-02 | 4.58e-03 | 1.42e-03 | 1.51 | 3.40e-03 | 4.15e-04 | 0.045 |
| Lower | boundary_flux CBF (lumped) [857 solve] | 5.64e-03 | 1.61e-03 | 3.77e-04 | 1.95 | 1.01e-03 | 1.72e-04 | 0.027 |
| Lower | boundary_flux CBF (lumped) [development solve] | 6.72e-03 | 1.78e-03 | 5.04e-04 | 1.87 | 1.25e-03 | 3.48e-04 | 0.046 |
| Lower | raw FE stress at nodes [857 solve] | 2.81e-02 | 7.38e-03 | 1.89e-03 | 1.95 | 4.38e-03 | 1.09e-03 | 0.282 |
| Lower | raw FE stress at nodes [development solve] | 2.21e-02 | 5.99e-03 | 1.57e-03 | 1.91 | 4.21e-03 | 7.46e-04 | 0.369 |
| Upper | 857 CBF + reconstruction | 7.35e-04 | 1.06e-04 | 1.56e-05 | 2.78 | 4.44e-05 | 1.60e-05 | 0.355 |
| Upper | 857 circular CBF | 2.56e-03 | 7.02e-04 | 1.87e-04 | 1.89 | 7.04e-04 | 1.39e-04 | 0.355 |
| Upper | boundary_flux CBF (consistent) [857 solve] | 5.76e-03 | 1.52e-03 | 3.91e-04 | 1.94 | 1.10e-03 | 5.39e-04 | 0.030 |
| Upper | boundary_flux CBF (consistent) [development solve] | 3.97e-03 | 1.07e-03 | 3.03e-04 | 1.86 | 1.10e-03 | 3.35e-04 | 0.053 |
| Upper | boundary_flux CBF (lumped) [857 solve] | 5.64e-03 | 1.47e-03 | 3.77e-04 | 1.95 | 9.45e-04 | 5.27e-04 | 0.029 |
| Upper | boundary_flux CBF (lumped) [development solve] | 3.76e-03 | 1.01e-03 | 2.73e-04 | 1.89 | 7.43e-04 | 3.26e-04 | 0.048 |
| Upper | raw FE stress at nodes [857 solve] | 1.29e-02 | 3.88e-03 | 1.46e-03 | 1.57 | 2.60e-03 | 1.61e-03 | 0.175 |
| Upper | raw FE stress at nodes [development solve] | 1.01e-02 | 3.14e-03 | 1.26e-03 | 1.50 | 2.24e-03 | 1.42e-03 | 0.285 |

### zero slip, sigma_rt

| wall | route | L2 h=1/8 | L2 h=1/16 | L2 h=1/32 | order | max h=1/32 | L2 midpoints h=1/32 | cost / solve h=1/32 |
|---|---|---|---|---|---|---|---|---|
| Lower | 857 CBF + reconstruction | 1.12e-02 | 1.61e-03 | 2.93e-04 | 2.63 | 8.01e-04 | 3.42e-04 | 0.210 |
| Lower | 857 circular CBF | 1.61e-01 | 5.07e-02 | 1.31e-02 | 1.81 | 2.64e-02 | 8.65e-03 | 0.210 |
| Lower | boundary_flux CBF (consistent) [857 solve] | 1.24e-01 | 4.08e-02 | 1.06e-02 | 1.78 | 2.04e-02 | 8.67e-03 | 0.027 |
| Lower | boundary_flux CBF (consistent) [development solve] | 1.40e-01 | 1.11e-01 | 6.63e-02 | 0.54 | 1.21e-01 | 4.21e-02 | 0.045 |
| Lower | boundary_flux CBF (lumped) [857 solve] | 6.21e-02 | 1.91e-02 | 4.92e-03 | 1.83 | 8.83e-03 | 5.00e-03 | 0.027 |
| Lower | boundary_flux CBF (lumped) [development solve] | 5.06e-02 | 4.26e-02 | 2.59e-02 | 0.48 | 4.80e-02 | 1.65e-02 | 0.046 |
| Lower | raw FE stress at nodes [857 solve] | 6.02e-02 | 2.09e-02 | 6.45e-03 | 1.61 | 1.12e-02 | 7.05e-03 | 0.282 |
| Lower | raw FE stress at nodes [development solve] | 8.49e-02 | 2.81e-02 | 8.47e-03 | 1.66 | 1.39e-02 | 9.09e-03 | 0.369 |
| Upper | 857 CBF + reconstruction | 2.73e-03 | 4.92e-04 | 9.16e-05 | 2.45 | 2.60e-04 | 7.63e-05 | 0.355 |
| Upper | 857 circular CBF | 5.21e-02 | 1.51e-02 | 4.17e-03 | 1.82 | 1.01e-02 | 2.65e-03 | 0.355 |
| Upper | boundary_flux CBF (consistent) [857 solve] | 7.48e-02 | 2.10e-02 | 5.66e-03 | 1.86 | 1.31e-02 | 2.80e-03 | 0.030 |
| Upper | boundary_flux CBF (consistent) [development solve] | 2.06e-01 | 9.35e-02 | 4.36e-02 | 1.12 | 8.91e-02 | 2.76e-02 | 0.053 |
| Upper | boundary_flux CBF (lumped) [857 solve] | 2.20e-02 | 6.38e-03 | 1.72e-03 | 1.84 | 4.78e-03 | 5.55e-04 | 0.029 |
| Upper | boundary_flux CBF (lumped) [development solve] | 7.10e-02 | 3.42e-02 | 1.66e-02 | 1.05 | 3.59e-02 | 1.05e-02 | 0.048 |
| Upper | raw FE stress at nodes [857 solve] | 4.18e-02 | 1.20e-02 | 4.11e-03 | 1.67 | 7.55e-03 | 4.26e-03 | 0.175 |
| Upper | raw FE stress at nodes [development solve] | 3.30e-02 | 9.74e-03 | 3.54e-03 | 1.61 | 6.24e-03 | 3.69e-03 | 0.285 |
