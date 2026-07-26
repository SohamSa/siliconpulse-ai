# Simulation Scenarios

The telemetry generator publishes only to Redpanda topic `telemetry.raw`.

## Control API

Base URL (local Compose): `http://localhost:8100`

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/api/v1/scenarios` | List scenario types + active runs |
| POST | `/api/v1/scenarios/inject` | Inject failure |
| POST | `/api/v1/scenarios/{id}/stop` | Stop scenario |
| POST | `/api/v1/scenarios/{id}/severity/increase` | Increase severity |
| POST | `/api/v1/scenarios/{id}/severity/decrease` | Decrease severity |
| POST | `/api/v1/scenarios/reset` | Reset entire fleet |
| POST | `/api/v1/devices/{id}/reset` | Reset one device |
| POST | `/api/v1/devices/{id}/recovery` | Simulated approved intervention |
| GET | `/api/v1/devices/{id}` | True vs reported snapshot |
| GET | `/api/v1/fleet` | Fleet summary |

### Inject cooling degradation (primary demo)

```bash
curl -X POST http://localhost:8100/api/v1/scenarios/inject \
  -H "Content-Type: application/json" \
  -d "{\"scenario\":\"cooling_degradation\",\"device_id\":\"GPU-042\",\"severity\":0.7}"
```

## Scenario catalog

| Scenario | Effect |
| --- | --- |
| `normal` | Nominal operation |
| `heavy_workload` | High utilization / power |
| `idle` | Low utilization |
| `cooling_degradation` | Cooling efficiency falls; temperature rises gradually |
| `fan_failure` | Fan efficiency collapses |
| `memory_degradation` | ECC errors accumulate |
| `voltage_instability` | Voltage/power variance |
| `firmware_regression` | Errors + mild clock impact |
| `rack_cooling_failure` | Affects all devices in a rack |
| `sensor_drift` | Reported sensors diverge from true state |
| `network_bottleneck` | Latency rises; throughput falls |
| `cascading_workload_overload` | Heavy workload pattern |
| `intermittent_device_reset` | Brief zero-throughput resets |
| `recovery` | Post-intervention stabilization |

## Important

- True internal state is **not** published on the wire.
- `simulation_scenario` on events is for demo/evaluation tooling only and must **not** be used as root-cause evidence in later phases.
