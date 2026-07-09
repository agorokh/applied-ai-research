# Targets

Eleven targets covering the paper's core low-dimensional computational claims.
Full inventory with locators, acceptance modes, and tolerances: `spec/reproduction_matrix.csv`.

## Example 1: simple illustrative systems (arxiv.tex:507-650)

- `tab_ex1_2d_linear` -- Tab:Ex1_2dLin coefficient recovery, 2D damped linear oscillator, poly library order 5.
- `tab_ex1_2d_cubic` -- Tab:Ex1_2dCub coefficient recovery, cubic dynamics.
- `fig_ex1_2d` -- Fig:Ex1: trajectories + phase portraits reproduced by the identified models.
- `tab_ex1_3d` -- Tab:Ex1_3d coefficient recovery, 3D linear system, poly order 3 (paper: "second or third").

## Example 2: Lorenz system (arxiv.tex:652-935)

- `tab_lorenz_coefficients` -- appendix Lorenz table at eta=1.0: 7-term support, coefficients near (10, 28, 8/3).
- `fig_lorenz_attractor` -- attractor geometry reproduced (bounded, two-lobed butterfly).
- `fig_lorenz_error` -- short-term tracking accurate; long-term forecast diverges (chaos) while attractor form is preserved.

## Example 3: fluid wake behind a cylinder -- NOT PLANNED

Excluded from the target plan (laptop-only scope: no DNS compute). Recorded in
`spec/assumptions_and_unknowns.md`. The release bundle's own runs cover it; ours deliberately does not.

## Example 4: bifurcations and normal forms (arxiv.tex:1199-1372)

- `tab_logistic_coefficients` -- Tab:Logistic: discrete-time SINDy recovers mu*x*(1-x) with r_{k+1}=r.
- `fig_logistic_bifurcation` -- Fig:Logistic: attracting sets vs mu reproduced by the identified map.
- `tab_hopf_coefficients` -- Tab:Hopf: support recovery under sensor noise + TV derivative; paper's own cubic coefficients deviate ~8% from truth.
- `fig_hopf_reconstruction` -- Fig:HopfReconstruct: fixed point for mu<0, limit cycle radius sqrt(mu) for mu>0.

## Target-specific ambiguities

- Ex1/Lorenz noise magnitudes and thresholds not stated exactly for every case; see assumptions.
- Hopf omega sign: the displayed equation (arxiv.tex:1297-1301) leaves omega unstated; Tab:Hopf signs
  (xdot 'y' negative, ydot 'x' positive) imply the omega=-1 rotation sense. We match the table.
