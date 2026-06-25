# Si Powder Bed Nitridation Simulation Plan

## 1. 목표

첨부 experimental configuration에서 Ar + N2 혼합가스가 공급될 때 Si powder bed의 질화 반응, 반응열에 의한 bed self-heating, 그리고 주요 열손실/열전달 경로를 포함하는 시뮬레이션 코드를 작성한다.

최종 코드는 다음 질문에 답할 수 있어야 한다.

- furnace setting 온도 스케줄에 따라 Si powder bed 온도가 어떻게 변하는가?
- 질화 반응열이 powder bed 온도 상승에 얼마나 기여하는가?
- N2 공급 비율, 총 유량, bed porosity, Si mass, crucible/graphite/refractory 조건이 질화율과 peak bed temperature에 어떤 영향을 주는가?
- 실제 질화율 데이터가 있을 때 그 데이터를 반영하고, 없을 때는 명시적인 mock kinetics로 계산할 수 있는가?

## 2. 실험 구성 해석

그림과 설명을 기준으로 모델에 반영할 구조는 다음과 같다.

- Ar + N2 혼합가스 공급:
  - N2 mol fraction: 0.05 to 1.00
  - 총 유량: 300 to 3000 ml/min
  - 압력: 약 1.02 bar
  - inlet pipe diameter: 10 mm
- outlet:
  - back-side center
  - outlet pipe diameter: 50 mm
- 내부 구조:
  - carbon felt refractory structure: 직육면체, 약 95% porosity
  - furnace door가 닫히면 heating element와 crucible이 refractory structure 내부에 갇힘
  - heating elements는 crucible 좌우에 위치
  - Si powder bed: BN crucible 안에 위치, 약 85% porosity
  - bed 표면 폭은 그림 기준 약 150 mm
  - heating zone 폭은 그림 기준 약 250 mm
  - graphite block 위에 BN crucible이 놓임
- thermal boundary:
  - furnace setpoint 또는 thermocouple 온도는 refractory inside surface temperature `T_s,refract`의 proxy로 취급 가능
  - bed surface temperature `T_s,bed`는 반응열과 열손실의 결과로 계산

주의: 그림만으로는 bed depth, crucible wall thickness, bed mass, particle size, graphite dimensions, gas 실제 유동 경로가 확정되지 않는다. 따라서 초기 코드는 parameterized model이어야 하고, hard-coded geometry를 피해야 한다.

## 3. 모델링 철학

이 문제를 처음부터 full CFD/reactive porous media로 구현하면 실험 데이터 없이 검증이 어렵고, 불확실한 파라미터가 너무 많다. 따라서 단계별로 모델 충실도를 올린다.

### Level 0: Lumped Thermal Reactor Model

목적: 빠르게 실행되고, 에너지 보존과 질화율 데이터 반영이 확실한 기준 모델.

구성:

- powder bed를 하나의 thermal node로 취급
- BN crucible, graphite block, refractory inside surface를 boundary 또는 별도 thermal node로 선택 가능
- 질화율 `X(t)`는 실제 데이터가 있으면 interpolation으로 사용
- 실제 데이터가 없으면 mock kinetics로 `X(t)` 생성
- 반응열, radiation, gas convection, conduction/contact heat transfer를 ODE에 포함

대표 energy balance:

```text
C_bed dT_bed/dt =
    Q_from_refractory
  + Q_from_graphite_or_crucible
  + Q_reaction
  - Q_radiation_to_refractory
  - Q_gas_convection
  - Q_other_losses
```

Level 0은 설계 sweep, 실험 조건 비교, parameter sensitivity에 가장 유용하다.

### Level 1: 1D Porous Bed Finite Volume Model

목적: powder bed 내부 temperature gradient와 N2 diffusion/convection limitation을 보기 위한 모델.

권장 첫 방향:

- 1D vertical model: bed depth 방향
- optional 1D radial/width direction은 후속 단계
- local thermal equilibrium 가정: solid Si/Si3N4와 pore gas가 같은 온도 `T(z,t)`를 가짐
- finite volume discretization
- 각 cell에서 conversion `X_i(t)`, temperature `T_i(t)`, gas N2 concentration `C_N2,i(t)` 계산

대표 governing equations:

```text
(rho Cp)_eff dT/dt
  = div(k_eff grad T)
  - (rho_g Cp_g u) grad T
  + q_rxn

epsilon dC_N2/dt
  = - div(u C_N2)
    + div(D_eff grad C_N2)
    - nu_N2 r_rxn

dX/dt = r_X(T, p_N2, X)
```

Level 1은 bed 내부의 hot spot과 N2 starvation 가능성을 평가하는 데 사용한다.

### Level 2: Reactor Network / Chamber Coupled Model

목적: inlet/outlet 위치와 refractory 내부 gas residence를 더 현실적으로 반영.

구성:

- chamber gas를 well-mixed node 또는 plug-flow network로 표현
- bed 위 gas boundary의 `T_gas`, `p_N2`, velocity를 chamber model에서 전달
- outlet flow 및 gas sensible heat loss 계산

주의: gas가 실제로 powder bed를 얼마나 통과하는지는 geometry와 유동장에 크게 의존한다. 초기에는 empirical gas-bed contact factor를 두고, tracer/flow 실험 또는 CFD 결과로 보정한다.

## 4. 화학 반응 모델

기본 반응:

```text
3Si(s) + 2N2(g) -> Si3N4(s)
```

열화학:

```text
Delta H_rxn ~= -828.9 kJ/mol Si3N4
q_release_per_mol_Si = 828.9 / 3 kJ/mol Si = 276.3 kJ/mol Si
```

반응열:

```text
Q_reaction_dot = n_Si0 * q_release_per_mol_Si * dX/dt
```

여기서:

- `n_Si0`: 초기 Si mol 수
- `X`: 초기 Si 기준 질화 전환율
- `dX/dt`: 1/s 단위
- `Q_reaction_dot`: W

N2 소비량:

```text
n_N2_consumed = (2/3) * n_Si0 * X
N2_consumption_rate = (2/3) * n_Si0 * dX/dt
```

N2 supply와 비교하여 반응이 공급량보다 많은 N2를 소비하지 않는지 검증해야 한다.

## 5. 질화율 데이터 반영 방식

### 실제 데이터가 있는 경우

입력 CSV schema:

```text
time_s,setpoint_C,measured_bed_C,measured_refractory_C,n2_fraction,flow_sccm,conversion_fraction
```

필수 컬럼:

- `time_s`
- `conversion_fraction`

권장 컬럼:

- `setpoint_C`
- `measured_bed_C`
- `measured_refractory_C`
- `n2_fraction`
- `flow_sccm`

처리:

- `X(t)`는 monotonic correction 전 raw data를 보존
- corrected `X(t)`를 PCHIP 또는 monotone spline으로 보간
- `dX/dt`를 계산하여 reaction heat source로 사용
- raw/corrected conversion 차이는 audit CSV로 저장

한계:

- 실제 conversion data를 직접 입력하는 방식은 해당 실험 조건의 재현에는 강하지만, 새로운 조건 예측력은 제한적이다.
- 새로운 온도/유량/N2 fraction 조건을 예측하려면 kinetic parameter fitting이 필요하다.

### 실제 데이터가 없는 경우

명시적인 mock kinetics를 사용한다. 이 결과는 물리적으로 가능한 demonstration일 뿐, 예측값으로 해석하면 안 된다.

권장 mock rate law:

```text
dX/dt = k0 exp(-Ea / R T) * (p_N2 / p_ref)^n * (1 - X)^m * f_diffusion(X)
```

예시 diffusion limitation:

```text
f_diffusion(X) = max(1 - X / X_max, 0)^a
```

또는 isothermal placeholder:

```text
X(t) = X_max * (1 - exp(-(K t)^n_avrami))
```

Mock parameter는 반드시 config에 `source: synthetic`으로 표시하고, output manifest에 경고를 남긴다.

## 6. 열전달 모델

### 6.1 Porous Bed Effective Properties

초기 LTE 모델에서:

```text
rhoCp_eff = (1 - epsilon) * rho_solid * Cp_solid + epsilon * rho_gas * Cp_gas
k_eff = k_static + k_radiative + k_gas_dispersion
```

초기 구현은 단순 mixing rule을 사용하되, 나중에 보정 가능하게 한다.

필요 입력:

- bed porosity: 기본 0.85
- Si/Si3N4 density and Cp
- gas Cp, viscosity, thermal conductivity
- particle diameter
- bed dimensions
- tortuosity

### 6.2 Conduction / Contact Heat Transfer

경로:

- refractory/heating zone to crucible/bed
- bed to BN crucible
- crucible to graphite block
- graphite block to refractory/furnace environment

Level 0에서는 thermal resistance network로 표현:

```text
Q_cond = (T_source - T_bed) / R_th
```

Level 1에서는 boundary condition으로 표현:

```text
-k_eff dT/dn = h_contact (T_bed_surface - T_wall)
```

### 6.3 Radiation Loss/Gain

bed surface와 carbon felt inside surface 사이:

```text
Q_rad = epsilon_eff * sigma * A_view * F_view * (T_bed_K^4 - T_refract_K^4)
```

부호 규칙:

- `Q_rad_loss_from_bed > 0` if `T_bed > T_refract`
- `T_refract > T_bed`이면 radiation은 bed heating term이 될 수 있음

필수 주의:

- 모든 radiation 계산은 Kelvin 사용
- emissivity와 view factor는 실험 fitting 대상

### 6.4 Gas Convection Heat Loss

혼합가스 공급/배출에 의한 sensible heat loss:

간단 모델:

```text
Q_gas = eta_contact * m_dot_gas * Cp_gas * (T_bed - T_inlet_or_chamber)
```

또는 boundary heat transfer:

```text
Q_gas = h_gas * A_exposed * (T_bed - T_gas)
```

초기에는 두 방식을 모두 지원하되, 하나를 config로 선택한다.

중요:

- 300 to 3000 ml/min은 입력 조건 기준 부피 유량이다.
- 실제 furnace temperature에서 volumetric flow와 gas density가 크게 변하므로 mass flow는 pressure, inlet temperature, composition으로 계산해야 한다.
- 유량 단위는 `sccm`인지 actual ml/min인지 명확히 해야 한다.

## 7. Gas Transport / N2 Availability

초기 mass balance:

```text
N2_supply_mol_s = y_N2 * P * Q_vol / (R * T_flow_reference)
N2_consumption_mol_s = (2/3) * n_Si0 * dX/dt
```

검증:

- `N2_consumption_mol_s <= N2_supply_mol_s * eta_available`
- 위 조건이 깨지면 rate를 supply-limited로 제한하거나 warning/fail 처리

Level 1에서는 bed 내 species equation으로 N2 depletion을 계산한다.

## 8. 코드 구조 계획

권장 파일 구조:

```text
powder_bed_nitridation/
  __init__.py
  cli.py
  config.py
  geometry.py
  gas.py
  reactions.py
  kinetics.py
  thermal.py
  porous_bed.py
  reactor_network.py
  data_io.py
  simulation.py
  validation.py
  plotting.py
tests/
  test_reactions.py
  test_gas.py
  test_energy_balance.py
  test_lumped_model.py
  test_cli_smoke.py
configs/
  example_lumped.yaml
  example_1d_bed.yaml
examples/
  synthetic_conversion_data.csv
```

초기 구현은 현재 단일 스크립트에서 시작해도 되지만, 새 모델은 위 구조로 분리하는 것을 권장한다.

## 9. Config 설계

예시 YAML:

```yaml
experiment:
  pressure_bar: 1.02
  flow_basis: standard        # standard or actual
  flow_reference_temperature_K: 298.15
  flow_reference_pressure_bar: 1.01325
  gas_flow_sccm: 1000
  n2_fraction: 0.75
  ar_fraction: 0.25

furnace_schedule:
  initial_C: 25
  ramps:
    - rate_C_per_min: 10
      target_C: 1000
    - rate_C_per_min: 5
      target_C: 1400
  hold_time_min: 600
  refractory_temperature_mode: setpoint

geometry:
  bed_width_m: 0.150
  bed_depth_m: null
  bed_height_m: null
  crucible_material: BN
  refractory_inner_width_m: 0.250

bed:
  si_mass_g: 10
  porosity: 0.85
  particle_diameter_m: null
  initial_conversion: 0

thermal:
  model_level: lumped
  bed_heat_capacity_J_per_K: null
  effective_k_W_m_K: null
  radiation_emissivity_eff: 0.8
  radiation_view_factor: 0.5
  gas_contact_efficiency: 0.2

kinetics:
  mode: synthetic
  k0_1_s: 1.0e5
  activation_energy_J_mol: 250000
  n2_order: 1.0
  conversion_order: 1.0
  x_max: 0.92
```

`null` 값은 code가 default를 임의로 넣어 조용히 진행하면 안 된다. 반드시 explicit fallback 또는 warning을 출력해야 한다.

## 10. Solver 계획

### Level 0 ODE

- `scipy.integrate.solve_ivp` 사용
- stiff 가능성이 있으므로 `BDF` 또는 `Radau` option 제공
- 빠른 sweep용으로 `RK45`도 허용
- state:
  - `T_bed`
  - optional `T_crucible`
  - optional `T_graphite`
  - `X`
  - optional chamber gas `T_gas`, `y_N2`

### Level 1 Finite Volume

- method of lines
- state per cell:
  - `T_i`
  - `X_i`
  - `C_N2_i`
- upwind advection for gas
- central difference conduction/diffusion
- adaptive time integrator

### Numerical Safety

- temperature in Kelvin for radiation and Arrhenius
- conversion clipped to `[0, 1]`
- N2 concentration nonnegative
- reaction rate nonnegative
- fail if energy residual exceeds tolerance
- fail if N2 consumption exceeds available supply without supply-limited mode enabled
- state clipping must be reported; clipping cannot silently hide solver failure

Recommended default tolerances:

```yaml
validation:
  energy_balance_relative_tolerance: 1.0e-3
  n2_balance_relative_tolerance: 1.0e-3
  timestep_peak_temperature_tolerance_C: 1.0
  timestep_final_conversion_tolerance: 1.0e-3
  mesh_peak_temperature_tolerance_C: 1.0
  mesh_final_conversion_tolerance: 1.0e-3
```

## 11. Calibration Strategy

실제 데이터가 생기면 다음 순서로 보정한다.

1. No-reaction 또는 inert Ar run으로 thermal parameters 보정
   - radiation emissivity/view factor
   - gas contact efficiency
   - conduction/contact resistance
   - effective heat capacity
2. 질화 run에서 reaction/kinetic parameters 보정
   - `k0`
   - `Ea`
   - N2 pressure order
   - diffusion limitation exponent
   - maximum conversion `X_max`
3. 보정된 parameter로 다른 N2 fraction/flow/furnace schedule validation

실제 bed temperature data가 있으면 thermal parameter 식별력이 크게 좋아진다.

## 12. 필수 Output

각 run마다 다음을 저장한다.

- `run_manifest.json`
- `config_resolved.yaml`
- `time_series.csv`
- `bed_profile.csv` for Level 1
- `energy_balance.csv`
- `n2_balance.csv`
- `conversion_audit.csv`
- `summary.csv`
- plots:
  - bed temperature vs time
  - conversion vs time
  - heat generation vs time
  - heat loss decomposition
  - N2 supply vs consumption
  - Level 1 temperature/conversion profile

## 13. Verification And Pass Criteria

### Physics Checks

- Integrated reaction heat equals `n_Si0 * q_release * delta_X` within tolerance.
- N2 consumption equals `(2/3) * n_Si0 * delta_X`.
- Radiation is zero when `T_bed == T_refract`.
- Gas convection loss is zero when gas contact efficiency or flow is zero.
- No-reaction run has no reaction heat and no conversion increase.
- Adiabatic run temperature rise matches `Q_rxn / C_bed`.

### Numerical Checks

- timestep convergence: halve max step and compare peak bed temperature and final conversion.
- mesh convergence for Level 1: double cell count and compare.
- nonnegative species concentration.
- conversion remains in `[0, 1]`.
- all terms use SI units internally.

### Practicality Checks

- Model can run with only minimal geometry and synthetic kinetics.
- Model can run with real conversion CSV.
- Missing high-impact parameters produce explicit warnings.
- Output explains whether result is calibrated, data-driven, or synthetic.
- Output labels each high-impact parameter as `measured`, `assumed`, `synthetic`, or `calibrated`.
- Runtime for Level 0 is seconds; Level 1 should be practical for parameter sweeps after configuration.

## 14. Implementation Phases

### Phase 1: Requirements And Data Schema

- Finalize config schema.
- Define required/optional measured data columns.
- Create example config from current experimental setup.
- Create synthetic conversion data example.

### Phase 2: Level 0 Lumped Model

- Implement gas property and flow conversion utilities.
- Implement N2 supply/consumption balance.
- Implement signed thermochemistry and reaction heat.
- Implement data-driven conversion mode.
- Implement synthetic kinetics mode.
- Implement lumped thermal ODE with radiation, gas convection, and conduction/contact terms.
- Generate energy and N2 balance outputs.

### Phase 3: Validation Harness

- Add unit tests for thermochemistry, gas flow conversion, heat losses, reaction heat integration.
- Add smoke test with synthetic config.
- Add limiting-case tests.
- Add manifest and warning system.

### Phase 4: Level 1 Porous Bed Model

- Implement 1D finite-volume bed model.
- Add thermal conduction and gas advection/diffusion.
- Couple reaction rate to local `T` and `p_N2`.
- Add mesh convergence tests.

### Phase 5: Calibration Workflow

- Implement parameter fitting against measured conversion and bed temperature data.
- Add confidence intervals or sensitivity ranking.
- Separate fitted parameters from assumed parameters in output.

### Phase 6: Experiment Planning Tools

- Add sweep runner for N2 fraction and flow rate.
- Add peak temperature and final conversion maps.
- Add safe operating envelope warnings.

## 15. Major Risks

- Gas flow around the bed may not equal gas flow through the bed. Treating inlet flow as bed-through-flow can overstate convection and N2 availability.
- Refractory inside surface temperature may differ from furnace setpoint or thermocouple temperature.
- Radiation view factor and emissivity are uncertain and can dominate high-temperature heat transfer.
- Powder bed effective thermal conductivity and contact resistance are hard to know without calibration.
- Synthetic kinetics can look plausible but should not be used for prediction.
- Si melting, sintering, pore closure, Si3N4 product-layer diffusion, and local runaway may require more detailed physics if observed experimentally.

## 16. Definition Of Done

- A documented config-driven simulation can run Level 0 with synthetic data.
- The same code can accept measured conversion data.
- Energy balance and N2 balance are saved and pass strict checks.
- The code explicitly labels synthetic, data-driven, and calibrated modes.
- A strict review agent gives `PASS` on physical validity, numerical sanity, and practical implementation scope.
