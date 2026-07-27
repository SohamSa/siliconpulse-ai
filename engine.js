/**
 * SiliconPulse AI — in-browser fleet intelligence engine.
 * Runs entirely client-side so a static host can serve a live demo link.
 */

const MODELS = {
  "SP-H100-80G": { tdp: 700, baseClock: 1410, idle: 70, maxTps: 400 },
  "SP-A100-40G": { tdp: 400, baseClock: 1410, idle: 50, maxTps: 250 },
  "SP-L40S": { tdp: 350, baseClock: 2520, idle: 40, maxTps: 220 },
};

const SCENARIOS = {
  cooling_degradation: "Gradual loss of cooling effectiveness",
  fan_failure: "Fan collapse and thermal rise",
  memory_degradation: "Rising ECC errors",
  rack_cooling_failure: "Shared rack cooling impact",
  sensor_drift: "Reported sensors diverge from truth",
  recovery: "Post-intervention stabilization",
  normal: "Nominal operation",
};

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function uid() {
  return crypto.randomUUID();
}

function gpuId(i) {
  return `GPU-${String(i).padStart(3, "0")}`;
}

function rackId(i) {
  return `RACK-${String(i).padStart(2, "0")}`;
}

export class SiliconPulseEngine {
  constructor({ deviceCount = 50, rackCount = 5, seed = 42 } = {}) {
    this.deviceCount = deviceCount;
    this.rackCount = rackCount;
    this.seed = seed;
    this.rng = mulberry32(seed);
    this.devices = new Map();
    this.baselines = new Map();
    this.history = new Map();
    this.scenarios = new Map();
    this.deviceScenario = new Map();
    this.alerts = [];
    this.incidents = [];
    this.approvals = [];
    this.agentRuns = [];
    this.reports = [];
    this.eventsGenerated = 0;
    this.dedupeUntil = new Map();
    this._buildFleet();
  }

  _buildFleet() {
    const models = Object.keys(MODELS);
    const firmwares = ["1.8.2", "2.1.0", "2.3.1", "2.4.0"];
    for (let i = 1; i <= this.deviceCount; i++) {
      const id = gpuId(i);
      const ridx = ((i - 1) % this.rackCount) + 1;
      const rid = rackId(ridx);
      const model = models[(i - 1) % models.length];
      const profile = MODELS[model];
      this.devices.set(id, {
        device_id: id,
        rack_id: rid,
        server_id: `${rid}-SRV-${String(Math.floor((i - 1) / this.rackCount) + 1).padStart(2, "0")}`,
        model_name: model,
        firmware_version: firmwares[(i + this.seed) % firmwares.length],
        batch: ["BATCH-2023-A", "BATCH-2024-B", "BATCH-2025-A"][i % 3],
        age_hours: 500 + this.rng() * 11000,
        utilization: 40 + this.rng() * 30,
        memory_util: 40,
        power_w: profile.idle + 80 + this.rng() * 100,
        voltage: 12,
        temp_c: 50 + this.rng() * 12,
        ambient_c: 22,
        fan_rpm: 3000,
        fan_eff: 1,
        cooling_eff: 1,
        clock_mhz: profile.baseClock,
        throughput: 180,
        latency_ms: 1.2,
        ecc_c: 0,
        ecc_u: 0,
        sensor_quality: 1,
        workload: "inference",
        seq: 0,
        temp_bias: 0,
        power_bias: 0,
        anomaly_score: 0.05,
        failure_prob: 0.05,
        failure_type: "normal",
        rul_hours: 720,
        health_score: 92,
        lifecycle: "healthy",
        twin_expected_temp: 58,
        twin_deviation: 0,
        twin_confidence: 0.7,
      });
      this.history.set(id, []);
    }
  }

  reset() {
    this.scenarios.clear();
    this.deviceScenario.clear();
    this.alerts = [];
    this.incidents = [];
    this.approvals = [];
    this.agentRuns = [];
    this.reports = [];
    this.dedupeUntil.clear();
    this.baselines.clear();
    this.rng = mulberry32(this.seed);
    this._buildFleet();
    // Warm device-specific residual baselines before alerts are eligible.
    for (let i = 0; i < 35; i++) this.tick();
  }

  inject(scenario, deviceId = "GPU-042", severity = 0.85, rack = null) {
    if (!SCENARIOS[scenario]) throw new Error(`Unknown scenario: ${scenario}`);
    let targets;
    let rackIdValue = rack;
    if (scenario === "rack_cooling_failure") {
      if (!rackIdValue) {
        const d = this.devices.get(deviceId);
        if (!d) throw new Error("device not found");
        rackIdValue = d.rack_id;
      }
      targets = [...this.devices.values()].filter((d) => d.rack_id === rackIdValue).map((d) => d.device_id);
    } else {
      if (!this.devices.has(deviceId)) throw new Error("device not found");
      targets = [deviceId];
      rackIdValue = this.devices.get(deviceId).rack_id;
    }
    const sc = {
      scenario_id: uid(),
      scenario,
      device_ids: targets,
      rack_id: rackIdValue,
      severity: clamp(severity, 0, 1),
      progress: 0.08,
      stopped: false,
      started_at: new Date().toISOString(),
    };
    this.scenarios.set(sc.scenario_id, sc);
    targets.forEach((id) => this.deviceScenario.set(id, sc.scenario_id));
    return sc;
  }

  applyRecovery(deviceId) {
    return this.inject("recovery", deviceId, 0.95);
  }

  tick() {
    for (const st of this.devices.values()) {
      let active = null;
      const sid = this.deviceScenario.get(st.device_id);
      if (sid) {
        active = this.scenarios.get(sid);
        if (active && !active.stopped) {
          active.progress = Math.min(1, active.progress + 0.028 * Math.max(active.severity, 0.15));
        } else active = null;
      }
      this._step(st, active);
      this._intelligence(st);
      this.eventsGenerated += 1;
    }
  }

  _step(st, active) {
    const profile = MODELS[st.model_name];
    const scenario = active && !active.stopped ? active.scenario : "normal";
    const severity = active && !active.stopped ? active.severity * active.progress : 0;
    let ambient = 22;

    if (scenario === "cooling_degradation") st.cooling_eff = clamp(1 - 0.55 * severity, 0.35, 1);
    else if (scenario === "fan_failure") st.fan_eff = clamp(1 - 0.9 * severity, 0.05, 1);
    else if (scenario === "rack_cooling_failure") {
      ambient = 22 + 8 * severity;
      st.cooling_eff = clamp(1 - 0.35 * severity, 0.45, 1);
    } else if (scenario === "recovery") {
      st.cooling_eff += (1 - st.cooling_eff) * 0.2;
      st.fan_eff += (1 - st.fan_eff) * 0.2;
      st.temp_bias *= 0.85;
      st.power_bias *= 0.85;
    }

    if (scenario === "sensor_drift") {
      st.temp_bias = 6 * severity;
      st.power_bias = 40 * severity;
      st.sensor_quality = clamp(1 - 0.5 * severity, 0.3, 1);
    } else st.sensor_quality = Math.min(1, st.sensor_quality + 0.02);

    let targetUtil = 45 + this.rng() * 30;
    if (scenario === "heavy_workload") targetUtil = 88 + this.rng() * 10;
    st.utilization += (targetUtil - st.utilization) * 0.25;
    st.utilization = clamp(st.utilization, 0, 100);
    st.memory_util = clamp(st.utilization * 0.75 + (this.rng() - 0.5) * 10, 5, 98);

    const util = st.utilization / 100;
    let targetPower = profile.idle + (profile.tdp - profile.idle) * (0.85 * util + 0.15 * util * util);
    st.voltage = 12 + (this.rng() - 0.5) * 0.1;
    st.power_w += (targetPower - st.power_w) * 0.35;
    st.power_w = clamp(st.power_w, profile.idle * 0.8, profile.tdp * 1.05);

    st.ambient_c = ambient;
    const cooling = st.cooling_eff * st.fan_eff;
    const dt = 1;
    const heatIn = 0.045 * st.power_w * dt;
    const heatOut = (0.08 + 0.22 * cooling) * Math.max(st.temp_c - ambient, 0) * dt;
    st.temp_c += heatIn - heatOut + (this.rng() - 0.5) * 0.1;
    st.temp_c = clamp(st.temp_c, ambient + 5, 105);

    let targetFan = (1800 + (st.temp_c - 40) * 55) * st.fan_eff;
    if (scenario === "fan_failure") targetFan *= Math.max(0.05, 1 - 0.95 * severity);
    st.fan_rpm += (targetFan - st.fan_rpm) * 0.4;
    st.fan_rpm = clamp(st.fan_rpm, 0, 7500);

    let throttle = 0;
    if (st.temp_c > 85) throttle = clamp((st.temp_c - 85) / 15, 0, 0.55);
    st.clock_mhz = profile.baseClock * (1 - throttle);
    st.latency_ms = 1 + this.rng() * 0.8;
    const netPenalty = 1 / (1 + Math.max(st.latency_ms - 2, 0) / 20);
    st.throughput =
      profile.maxTps * util * (st.clock_mhz / profile.baseClock) * netPenalty * (0.97 + this.rng() * 0.06);

    if (scenario === "memory_degradation" && this.rng() < 0.35 * severity) {
      st.ecc_c += 1 + Math.floor(this.rng() * 5 * severity);
    }

    st.age_hours += dt / 3600;
    st.seq += 1;
  }

  _intelligence(st) {
    const reportedTemp = st.temp_c + st.temp_bias;
    const peers = [...this.devices.values()].filter((d) => d.rack_id === st.rack_id && d.device_id !== st.device_id);
    const peerAvg = peers.length ? peers.reduce((s, p) => s + p.temp_c, 0) / peers.length : st.temp_c;
    const util = st.utilization / 100;
    let expected = 28 + 22 * util + 0.02 * st.power_w + (peerAvg - 55) * 0.15;

    if (!this.baselines.has(st.device_id)) {
      this.baselines.set(st.device_id, { residual: reportedTemp - expected, n: 1 });
    }
    const baseline = this.baselines.get(st.device_id);
    if (baseline.n < 30 || (st.anomaly_score < 0.35 && st.cooling_eff > 0.9)) {
      const observedResidual = reportedTemp - expected;
      const alpha = baseline.n < 30 ? 0.3 : 0.02;
      baseline.residual = (1 - alpha) * baseline.residual + alpha * observedResidual;
      baseline.n += 1;
    }
    expected += baseline.residual;
    const deviation = Math.abs(reportedTemp - expected);
    st.twin_expected_temp = expected;
    st.twin_deviation = Math.min(1, deviation / 12 + deviation / Math.max(expected, 1) * 0.5);
    st.twin_confidence = Math.min(0.95, 0.55 + Math.min(baseline.n, 40) / 80);

    const hist = this.history.get(st.device_id);
    hist.push(reportedTemp);
    if (hist.length > 30) hist.shift();
    let z = 0;
    if (hist.length >= 5) {
      const mean = hist.reduce((a, b) => a + b, 0) / hist.length;
      const std = Math.sqrt(hist.reduce((a, b) => a + (b - mean) ** 2, 0) / hist.length) || 0.5;
      z = Math.abs(reportedTemp - mean) / std;
    }
    const fanProxy = st.fan_rpm / Math.max(1800 + (reportedTemp - 40) * 55, 1);
    let score = st.twin_deviation * 0.45 + Math.min(1, z / 4) * 0.25 + Math.max(0, 1 - fanProxy) * 0.15;
    score += Math.min(1, st.ecc_c / 10) * 0.1 + (1 - st.sensor_quality) * 0.05;
    st.anomaly_score = clamp(0.7 * st.anomaly_score + 0.3 * score, 0, 1);

    const scores = {
      normal: 0.35,
      cooling_degradation: st.twin_deviation * 1.3 + (1 - st.cooling_eff) * 0.8,
      fan_failure: (1 - st.fan_eff) * 1.4 + (st.fan_rpm < 1500 ? 1 : 0),
      memory_degradation: Math.min(1.5, st.ecc_c / 8 + st.ecc_u * 0.8),
      rack_cooling_failure: 0,
      sensor_drift: (1 - st.sensor_quality) * 1.2,
    };
    const hotPeers = peers.filter((p) => p.twin_deviation > 0.4 || p.anomaly_score > 0.45).length;
    if (hotPeers >= Math.max(2, Math.floor(peers.length / 3))) {
      scores.rack_cooling_failure += 0.9;
      scores.cooling_degradation *= 0.6;
    } else {
      scores.cooling_degradation += 0.35 * st.twin_deviation;
      scores.rack_cooling_failure *= 0.3;
    }
    const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
    const total = Object.values(scores).reduce((a, b) => a + Math.max(0.01, b), 0);
    st.failure_type = best[1] > 0.45 ? best[0] : "normal";
    st.failure_prob = clamp(best[1] / (total * 0.35), 0.02, 0.98);
    if (st.failure_type === "normal") st.failure_prob = Math.min(st.failure_prob, 0.15);
    st.rul_hours = Math.max(4, 720 * (1 - 0.85 * st.failure_prob) * (1 - 0.5 * st.anomaly_score));

    const thermal = clamp((st.temp_c - 55) / 35, 0, 1);
    let health = 100 - thermal * 25 - st.anomaly_score * 20 - st.failure_prob * 25 - st.twin_deviation * 12;
    st.health_score = clamp(health, 0, 100);
    st.lifecycle =
      st.health_score >= 85
        ? "healthy"
        : st.health_score >= 70
          ? "stressed"
          : st.health_score >= 55
            ? "degraded"
            : st.health_score >= 40
              ? "maintenance_recommended"
              : "critical";

    this._alerts(st, reportedTemp);
  }

  _alerts(st, reportedTemp) {
    const now = Date.now();
    if ((this.baselines.get(st.device_id)?.n || 0) < 20) return;
    if (st.twin_deviation < 0.35 || reportedTemp >= 95) return;
    const key = `${st.device_id}:twin_temperature_deviation`;
    if ((this.dedupeUntil.get(key) || 0) > now) return;
    this.dedupeUntil.set(key, now + 45000);
    const alert = {
      alert_id: uid(),
      device_id: st.device_id,
      alert_type: "twin_temperature_deviation",
      severity: st.twin_deviation > 0.7 ? "critical" : "warning",
      status: "open",
      detected_at: new Date().toISOString(),
      current_value: reportedTemp,
      expected_value: st.twin_expected_temp,
      evidence: [
        `Twin expected ${st.twin_expected_temp.toFixed(1)}°C, observed ${reportedTemp.toFixed(1)}°C`,
        `Twin deviation ${st.twin_deviation.toFixed(2)}`,
        `Anomaly ${st.anomaly_score.toFixed(2)}`,
      ],
      recommendation: "Inspect cooling path and compare with rack peers.",
      confidence: Math.min(0.95, 0.55 + st.anomaly_score * 0.4),
      incident_id: null,
    };
    this.alerts.unshift(alert);
    const existing = this.incidents.find(
      (i) => i.status !== "resolved" && i.affected_devices.includes(st.device_id),
    );
    if (existing) {
      alert.incident_id = existing.incident_id;
      existing.timeline.push({ at: new Date().toISOString(), type: "alert", message: alert.alert_type });
      return;
    }
    const inc = {
      incident_id: uid(),
      title: `Device anomaly on ${st.device_id}`,
      status: "open",
      severity: alert.severity,
      started_at: new Date().toISOString(),
      affected_devices: [st.device_id],
      affected_racks: [st.rack_id],
      likely_root_cause: null,
      confidence: 0,
      timeline: [{ at: new Date().toISOString(), type: "created", message: `Incident for ${st.device_id}` }],
      approved_actions: [],
      outcome: null,
      resolved_at: null,
    };
    alert.incident_id = inc.incident_id;
    this.incidents.unshift(inc);
  }

  investigate(incidentId) {
    const inc = this.incidents.find((i) => i.incident_id === incidentId);
    if (!inc) throw new Error("incident not found");
    const deviceId = inc.affected_devices[0];
    const st = this.devices.get(deviceId);
    const peers = [...this.devices.values()].filter((d) => d.rack_id === st.rack_id && d.device_id !== deviceId);
    const peerHot = peers.filter((p) => p.twin_deviation > 0.4).length;

    const hypotheses = [
      {
        cause: "device_cooling_degradation",
        score: 0.35 + st.twin_deviation * 0.5 + (peerHot <= 1 ? 0.2 : -0.2),
        supporting_evidence: [
          st.twin_deviation > 0.4 ? `Twin deviation ${st.twin_deviation.toFixed(2)}` : null,
          peerHot <= 1 ? "Rack peers mostly normal — device-local issue" : null,
          st.fan_eff > 0.7 ? "Fan still responding" : null,
        ].filter(Boolean),
        contradicting_evidence: peerHot > 1 ? [`${peerHot} peers also abnormal`] : [],
      },
      {
        cause: "rack_cooling_failure",
        score: 0.15 + (peerHot >= 2 ? 0.5 : 0),
        supporting_evidence: peerHot >= 2 ? [`Multiple peers hot in ${st.rack_id}`] : [],
        contradicting_evidence: peerHot < 2 ? ["Peers near normal"] : [],
      },
      {
        cause: "fan_failure",
        score: 0.1 + (st.fan_eff < 0.5 ? 0.6 : 0),
        supporting_evidence: st.fan_eff < 0.5 ? [`Fan efficiency ${st.fan_eff.toFixed(2)}`] : [],
        contradicting_evidence: st.fan_eff >= 0.5 ? [`Fan RPM ${st.fan_rpm.toFixed(0)} tracking temp`] : [],
      },
    ].sort((a, b) => b.score - a.score);

    const top = hypotheses[0];
    const confidence = Math.min(0.93, 0.45 + top.score * 0.4);
    inc.likely_root_cause = top.cause;
    inc.confidence = confidence;
    inc.status = "investigating";
    const result = {
      most_likely_cause: top.cause,
      confidence,
      hypotheses,
      note: "Ranked from observed telemetry/twin/peer evidence only — not hidden simulation labels.",
    };
    const run = {
      agent_run_id: uid(),
      agent_type: "root_cause_investigation",
      status: "completed",
      device_id: deviceId,
      incident_id: incidentId,
      confidence,
      decisions: [`Ranked cause: ${top.cause}`],
      current_step: "complete",
      started_at: new Date().toISOString(),
    };
    this.agentRuns.unshift(run);
    inc.timeline.push({
      at: new Date().toISOString(),
      type: "investigation",
      message: `RCA: ${top.cause} (${Math.round(confidence * 100)}%)`,
    });
    return { agent_run: run, result };
  }

  requestMaintenance(incidentId) {
    const inc = this.incidents.find((i) => i.incident_id === incidentId);
    if (!inc) throw new Error("incident not found");
    const deviceId = inc.affected_devices[0];
    const st = this.devices.get(deviceId);
    const approval = {
      approval_id: uid(),
      action: "simulate_workload_redistribution+fan_inspection",
      reason: "Reduce thermal stress while validating cooling degradation hypothesis",
      expected_impact: "Temperature should stabilize; anomaly and twin deviation should fall",
      risk: "medium — simulated only",
      requested_by: "predictive_maintenance_agent",
      device_id: deviceId,
      incident_id: incidentId,
      status: "pending",
      requested_at: new Date().toISOString(),
      decided_at: null,
      comments: "",
    };
    this.approvals.unshift(approval);
    const run = {
      agent_run_id: uid(),
      agent_type: "predictive_maintenance",
      status: "awaiting_approval",
      device_id: deviceId,
      incident_id: incidentId,
      confidence: Math.min(0.9, 0.5 + st.failure_prob * 0.4),
      decisions: ["Proposed simulated remediation; waiting for human approval"],
      current_step: "awaiting_approval",
      approval_id: approval.approval_id,
      started_at: new Date().toISOString(),
    };
    this.agentRuns.unshift(run);
    inc.timeline.push({
      at: new Date().toISOString(),
      type: "approval_requested",
      message: `Maintenance plan awaiting approval (${approval.approval_id.slice(0, 8)})`,
    });
    return { approval, agent_run: run };
  }

  decideApproval(approvalId, approve, comments = "") {
    const ap = this.approvals.find((a) => a.approval_id === approvalId);
    if (!ap || ap.status !== "pending") throw new Error("approval not available");
    ap.status = approve ? "approved" : "rejected";
    ap.decided_at = new Date().toISOString();
    ap.comments = comments;
    const inc = this.incidents.find((i) => i.incident_id === ap.incident_id);
    if (approve) {
      this.applyRecovery(ap.device_id);
      if (inc) {
        inc.approved_actions.push({ ...ap });
        inc.status = "remediating";
        inc.timeline.push({
          at: new Date().toISOString(),
          type: "action_applied",
          message: "Approved simulated remediation applied",
        });
      }
    } else if (inc) {
      inc.timeline.push({ at: new Date().toISOString(), type: "approval_rejected", message: comments || "Rejected" });
    }
    const run = this.agentRuns.find((r) => r.approval_id === approvalId);
    if (run) {
      run.status = "completed";
      run.current_step = approve ? "monitor_post_action" : "complete";
      run.decisions.push(approve ? "Human approved; recovery injected" : "Human rejected");
    }
    return ap;
  }

  generateReport(incidentId) {
    const inc = this.incidents.find((i) => i.incident_id === incidentId);
    if (!inc) throw new Error("incident not found");
    const st = this.devices.get(inc.affected_devices[0]);
    const report = {
      report_id: uid(),
      incident_id: incidentId,
      title: inc.title,
      generated_at: new Date().toISOString(),
      executive_summary: `${inc.affected_devices[0]} developed abnormal thermal behavior vs its statistical digital twin. Investigation ranked '${inc.likely_root_cause || "pending"}' at ${Math.round((inc.confidence || 0) * 100)}% confidence. ${inc.approved_actions.length ? "Human-approved remediation was applied." : "No remediation approved yet."}`,
      technical_summary: {
        device_id: st.device_id,
        health_score: +st.health_score.toFixed(1),
        anomaly_score: +st.anomaly_score.toFixed(3),
        twin_deviation: +st.twin_deviation.toFixed(3),
        failure_probability: +st.failure_prob.toFixed(3),
        predicted_failure_type: st.failure_type,
        rul_hours: +st.rul_hours.toFixed(1),
        likely_root_cause: inc.likely_root_cause,
        confidence: inc.confidence,
      },
      timeline: [...inc.timeline],
      approvals: [...inc.approved_actions],
      limitations: [
        "Telemetry and models are synthetic / demonstration-grade",
        "Digital twin is statistical, not transistor-level",
        "Not validated on real semiconductor production fleets",
      ],
    };
    if (st.twin_deviation < 0.35 && st.anomaly_score < 0.35 && inc.status !== "resolved") {
      inc.status = "resolved";
      inc.resolved_at = new Date().toISOString();
      inc.outcome = "stabilized_after_approved_action";
      inc.timeline.push({ at: new Date().toISOString(), type: "resolved", message: "Incident resolved after stabilization" });
    }
    this.reports.unshift(report);
    return report;
  }

  overview() {
    const list = this.deviceRows();
    const critical = list.filter((d) => d.status === "critical").length;
    const warning = list.filter((d) =>
      ["stressed", "degraded", "maintenance_recommended"].includes(d.status),
    ).length;
    const healthy = this.deviceCount - critical - warning;
    const riskiest = [...list].sort((a, b) => b.failure_probability - a.failure_probability)[0];
    return {
      summary: {
        device_count: this.deviceCount,
        healthy,
        warning,
        critical,
        avg_temperature_c: list.reduce((s, d) => s + d.temperature_c, 0) / list.length,
        avg_utilization_pct: list.reduce((s, d) => s + d.utilization_pct, 0) / list.length,
        events_generated: this.eventsGenerated,
        highest_risk_device: riskiest?.device_id,
        highest_risk_prob: riskiest?.failure_probability || 0,
      },
      top_anomalies: list.slice(0, 12),
      open_alerts: this.alerts.filter((a) => a.status === "open").slice(0, 10),
      open_incidents: this.incidents.filter((i) => i.status !== "resolved"),
      pending_approvals: this.approvals.filter((a) => a.status === "pending"),
      agent_runs: this.agentRuns.slice(0, 8),
    };
  }

  deviceRows() {
    return [...this.devices.values()]
      .map((st) => ({
        device_id: st.device_id,
        model_name: st.model_name,
        rack_id: st.rack_id,
        status: st.lifecycle,
        temperature_c: +(st.temp_c + st.temp_bias).toFixed(1),
        utilization_pct: +st.utilization.toFixed(1),
        power_watts: +st.power_w.toFixed(0),
        throughput: +st.throughput.toFixed(0),
        anomaly_score: +st.anomaly_score.toFixed(3),
        failure_probability: +st.failure_prob.toFixed(3),
        health_score: +st.health_score.toFixed(1),
        rul_hours: +st.rul_hours.toFixed(1),
        twin_deviation: +st.twin_deviation.toFixed(3),
        failure_type: st.failure_type,
        twin_expected_temp: +st.twin_expected_temp.toFixed(1),
        twin_confidence: +st.twin_confidence.toFixed(2),
        firmware_version: st.firmware_version,
        fan_rpm: +st.fan_rpm.toFixed(0),
        cooling_eff: +st.cooling_eff.toFixed(3),
      }))
      .sort((a, b) => b.anomaly_score - a.anomaly_score || b.failure_probability - a.failure_probability);
  }
}

function mulberry32(a) {
  return function rand() {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
