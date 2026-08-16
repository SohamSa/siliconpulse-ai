// Browser-safe companion demonstrations for lifecycle survival, wafer triage,
// and an evidence-grounded engineering copilot. All data are synthetic.

function mulberry32(seed) {
  return function rng() {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function lifecycleAssessment(device) {
  const stress = Math.min(1, 0.42 * device.twin_deviation + 0.33 * device.anomaly_score + 0.25 * device.failure_probability);
  const hazards = Array.from({ length: 12 }, (_, interval) =>
    Math.min(0.72, 0.018 + stress * 0.19 + interval * 0.006 * (0.3 + stress)),
  );
  let survival = 1;
  const curve = hazards.map((hazard, interval) => {
    survival *= 1 - hazard;
    return { interval: interval + 1, survival: Number(survival.toFixed(3)), hazard: Number(hazard.toFixed(3)) };
  });
  const median = curve.find((point) => point.survival <= 0.5)?.interval ?? ">12";
  return {
    device_id: device.device_id,
    current_stress_index: Number(stress.toFixed(3)),
    median_remaining_intervals: median,
    survival_curve: curve,
    interpretation: "A calibrated production model would map intervals to real time and include uncertainty by product and workload.",
    boundary: "Illustrative browser score. The committed Python benchmark uses device-separated synthetic survival data.",
  };
}

export function waferAssessment(seed = 904, pattern = "edge_ring") {
  const rng = mulberry32(seed);
  const size = 15;
  const cells = [];
  let failed = 0;
  let edgeFailed = 0;
  let centerFailed = 0;
  let lineFailed = 0;
  for (let row = 0; row < size; row++) {
    for (let col = 0; col < size; col++) {
      const x = (col - 7) / 7.5;
      const y = (row - 7) / 7.5;
      const radius = Math.sqrt(x * x + y * y);
      if (radius > 1) continue;
      let probability = 0.015;
      if (pattern === "edge_ring" && radius > 0.72) probability += 0.58;
      if (pattern === "center_cluster" && radius < 0.34) probability += 0.66;
      if (pattern === "scratch" && Math.abs(y - 0.42 * x) < 0.1) probability += 0.72;
      const bad = rng() < probability;
      cells.push({ row, col, bad });
      if (bad) {
        failed++;
        if (radius > 0.72) edgeFailed++;
        if (radius < 0.34) centerFailed++;
        if (Math.abs(y - 0.42 * x) < 0.1) lineFailed++;
      }
    }
  }
  const denom = Math.max(failed, 1);
  const scores = {
    normal: Math.max(0, 1 - (failed / cells.length) * 7),
    edge_ring: edgeFailed / denom,
    center_cluster: centerFailed / denom,
    scratch: lineFailed / denom,
  };
  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  return {
    wafer_id: `WAFER-${seed}`,
    cells,
    yield_pct: ((1 - failed / cells.length) * 100).toFixed(1),
    predicted_pattern: ranked[0][0],
    ranked_patterns: ranked,
    next_step: "Correlate the spatial signature with lot genealogy, tool/chamber history, metrology, and electrical test before assigning physical cause.",
  };
}

export function copilotAssessment(device) {
  const evidence = [
    { id: "E-TWIN", source: "operational_twin", statement: `Observed twin deviation ${device.twin_deviation.toFixed(2)}` },
    { id: "E-ANOM", source: "anomaly_service", statement: `Multivariate anomaly ${device.anomaly_score.toFixed(2)}` },
    { id: "E-PEER", source: "peer_group", statement: "Rack peers do not share the same thermal excursion" },
    { id: "E-FAN", source: "functional_monitor", statement: `Cooling efficiency proxy ${device.cooling_eff}` },
  ];
  return {
    question: `Why is ${device.device_id} degrading?`,
    leading_hypothesis: "device_local_cooling_degradation",
    supporting_evidence_ids: ["E-TWIN", "E-ANOM", "E-FAN"],
    contradicting_alternative: { hypothesis: "rack_cooling_failure", evidence_ids: ["E-PEER"] },
    missing_evidence: ["Physical inspection", "Maintenance history", "Calibrated monitor uncertainty"],
    evidence,
    proposed_action: "Schedule cooling-path inspection and temporarily redistribute non-critical workload",
    approval_status: "required",
    grounding_boundary: "The explanation references structured evidence IDs; no physical cause is asserted as fact.",
  };
}
