# Evaluación de La Bardera

**Estado:** VERIFICADO / en calibración real.

La batería ejecutable es [`scripts/eval_modismos.py`](../../../scripts/eval_modismos.py) y el contrato está en [`scripts/modismo_battery.md`](../../../scripts/modismo_battery.md). Debe separar `PASS`, `HARD_FAIL`, `CAPABILITY_BOUNDARY` e `INFRA_FAILURE`.

Un proveedor/configuración pasa cuando completa la batería sin bloqueos indebidos de voz, sin fuga de identidad y con límites preservados. El resultado debe registrar modelo, proveedor, parámetros, commit, fecha y muestra de salida sanitizada. Este resultado sólo habilita a Bardera.
