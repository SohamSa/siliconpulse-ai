/* SiliconPulse local demo UI */

const state = {
  selected: "GPU-042",
  polling: null,
  busy: false,
};

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function pct(n) {
  return `${Math.round((n || 0) * 100)}%`;
}

function setStatus(msg) {
  document.getElementById("demo-status").textContent = msg;
}

function renderKpis(summary) {
  const items = [
    ["Devices", summary.device_count],
    ["Healthy", summary.healthy],
    ["Warning", summary.warning],
    ["Critical", summary.critical],
    ["Avg temp °C", summary.avg_temperature_c.toFixed(1)],
    ["Events", summary.events_generated],
    ["Top risk", summary.highest_risk_device],
    ["Risk P", pct(summary.highest_risk_prob)],
  ];
  document.getElementById("kpi-grid").innerHTML = items
    .map(
      ([label, value]) => `
      <div class="kpi">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
      </div>`,
    )
    .join("");
}

function renderDevices(rows) {
  const body = document.getElementById("device-rows");
  body.innerHTML = rows
    .slice(0, 12)
    .map((d) => {
      const active = d.device_id === state.selected ? "active" : "";
      return `<tr class="${active}" data-id="${d.device_id}">
        <td>${d.device_id}</td>
        <td>${d.rack_id}</td>
        <td>${d.temperature_c.toFixed(1)}</td>
        <td>${d.twin_deviation.toFixed(2)}</td>
        <td>${d.anomaly_score.toFixed(2)}</td>
        <td>${pct(d.failure_probability)}</td>
        <td>${d.health_score.toFixed(0)}</td>
        <td>${d.rul_hours.toFixed(0)}</td>
      </tr>`;
    })
    .join("");
  body.querySelectorAll("tr").forEach((tr) => {
    tr.addEventListener("click", () => {
      state.selected = tr.dataset.id;
      refreshDetail();
      refresh();
    });
  });
}

async function refreshDetail() {
  document.getElementById("selected-device").textContent = state.selected;
  const d = await api(`/api/v1/devices/${state.selected}`);
  const i = d.intelligence;
  const t = d.telemetry;
  document.getElementById("device-detail").innerHTML = `
    <div class="row"><span class="k">Model / FW</span><span>${d.model_name} · ${d.firmware_version}</span></div>
    <div class="row"><span class="k">Lifecycle</span><span class="badge ${i.lifecycle === "healthy" ? "ok" : "warning"}">${i.lifecycle}</span></div>
    <div class="row"><span class="k">Temp actual / twin expected</span><span>${t.temperature_c.toFixed(1)}°C / ${i.twin_expected_temperature_c.toFixed(1)}°C</span></div>
    <div class="row"><span class="k">Twin deviation</span><span>${i.twin_deviation_score.toFixed(2)} (conf ${i.twin_confidence.toFixed(2)})</span></div>
    <div class="row"><span class="k">Anomaly</span><span>${i.anomaly_score.toFixed(2)}</span></div>
    <div class="row"><span class="k">Predicted failure</span><span>${i.predicted_failure_type} (${pct(i.failure_probability)})</span></div>
    <div class="row"><span class="k">RUL / health</span><span>${i.remaining_useful_life_hours.toFixed(0)}h · ${i.health_score.toFixed(0)}</span></div>
    <div class="row"><span class="k">Power / util / fan</span><span>${t.power_watts.toFixed(0)}W · ${t.utilization_pct.toFixed(0)}% · ${t.fan_speed_rpm.toFixed(0)} RPM</span></div>
    <div class="row"><span class="k">True cooling efficiency</span><span>${d.true_internal.cooling_efficiency.toFixed(2)} <em>(eval only)</em></span></div>
  `;
}

function renderIncidents(incidents) {
  const el = document.getElementById("incidents");
  if (!incidents.length) {
    el.innerHTML = `<div class="cardish"><p>No open incidents. Inject a scenario to begin.</p></div>`;
    return;
  }
  el.innerHTML = incidents
    .map((inc) => {
      const cause = inc.likely_root_cause || "not investigated";
      return `<div class="cardish" data-incident="${inc.incident_id}">
        <h4>${inc.title} <span class="badge ${inc.severity}">${inc.severity}</span></h4>
        <p>Status: <strong>${inc.status}</strong> · Devices: ${inc.affected_devices.join(", ")}</p>
        <p>Root cause: <strong>${cause}</strong>${inc.confidence ? ` (${pct(inc.confidence)})` : ""}</p>
        <div class="cta-row">
          <button class="btn ghost" data-act="investigate">Investigate</button>
          <button class="btn ghost" data-act="maintenance">Maintenance agent</button>
          <button class="btn ghost" data-act="report">Generate report</button>
        </div>
      </div>`;
    })
    .join("");

  el.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const card = btn.closest("[data-incident]");
      const id = card.dataset.incident;
      const act = btn.dataset.act;
      try {
        state.busy = true;
        if (act === "investigate") {
          setStatus("Running Root-Cause Investigation Agent…");
          const out = await api(`/api/v1/incidents/${id}/investigate`, { method: "POST", body: "{}" });
          setStatus(`RCA: ${out.result.most_likely_cause} (${pct(out.result.confidence)})`);
        } else if (act === "maintenance") {
          setStatus("Predictive Maintenance Agent proposing plan…");
          await api(`/api/v1/incidents/${id}/maintenance`, { method: "POST", body: "{}" });
          setStatus("Approval requested — review Approvals panel.");
        } else if (act === "report") {
          setStatus("Reporting Agent compiling evidence…");
          const report = await api(`/api/v1/incidents/${id}/report`, { method: "POST", body: "{}" });
          document.getElementById("report").textContent = JSON.stringify(report, null, 2);
          setStatus("Report generated.");
        }
        await refresh();
      } catch (err) {
        setStatus(`Error: ${err.message}`);
      } finally {
        state.busy = false;
      }
    });
  });
}

function renderApprovals(approvals) {
  const el = document.getElementById("approvals");
  const pending = approvals.filter((a) => a.status === "pending");
  if (!pending.length) {
    el.innerHTML = `<div class="cardish"><p>No pending approvals.</p></div>`;
    return;
  }
  el.innerHTML = pending
    .map(
      (a) => `<div class="cardish">
        <h4>Approval ${a.approval_id.slice(0, 8)}</h4>
        <p><strong>${a.action}</strong></p>
        <p>${a.reason}</p>
        <p>Expected: ${a.expected_impact}</p>
        <p>Risk: ${a.risk}</p>
        <div class="cta-row">
          <button class="btn primary" data-id="${a.approval_id}" data-act="approve">Approve</button>
          <button class="btn ghost" data-id="${a.approval_id}" data-act="reject">Reject</button>
        </div>
      </div>`,
    )
    .join("");

  el.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const act = btn.dataset.act;
      try {
        await api(`/api/v1/approvals/${id}/${act}`, {
          method: "POST",
          body: JSON.stringify({ comments: act === "approve" ? "Approved in demo UI" : "Rejected in demo UI" }),
        });
        setStatus(act === "approve" ? "Action approved — recovery injected. Watch temp stabilize." : "Action rejected.");
        await refresh();
      } catch (err) {
        setStatus(`Error: ${err.message}`);
      }
    });
  });
}

function renderAgents(runs) {
  const el = document.getElementById("agents");
  if (!runs.length) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML = `<h4 style="margin:0 0 .5rem;color:var(--muted)">Recent agent runs</h4>` +
    runs
      .slice(0, 5)
      .map(
        (r) => `<div class="cardish">
          <h4>${r.agent_type} · ${r.status}</h4>
          <p>${r.current_step}${r.confidence ? ` · conf ${pct(r.confidence)}` : ""}</p>
          <p>${(r.decisions || []).join(" · ")}</p>
        </div>`,
      )
      .join("");
}

async function refreshHealthcare() {
  const data = await api("/api/v1/healthcare/devices");
  document.getElementById("hc-disclaimer").textContent = data.disclaimer;
  document.getElementById("healthcare").innerHTML = data.devices
    .map(
      (d) => `<div class="cardish">
        <h4>${d.device_id} · ${d.device_health}</h4>
        <p>Signal quality ${d.signal_quality}</p>
        <p>Battery ${d.battery_voltage}V · packet loss ${d.packet_loss}</p>
        <p>Drift ${d.calibration_drift} · device temp ${d.device_temperature_c}°C</p>
        <p>${d.note}</p>
      </div>`,
    )
    .join("");
}

async function refresh() {
  const overview = await api("/api/v1/overview");
  renderKpis(overview.summary);
  renderDevices(overview.top_anomalies);
  renderIncidents(overview.open_incidents);
  renderApprovals(overview.pending_approvals);
  document.getElementById("pitch-points").innerHTML = overview.value_proposition.differentiation
    .map((x) => `<li>${x}</li>`)
    .join("");
  const agents = await api("/api/v1/agents/runs");
  renderAgents(agents.runs);
  await refreshDetail();
}

async function injectCooling() {
  setStatus("Injecting cooling_degradation on GPU-042…");
  await api("/api/v1/scenarios/inject", {
    method: "POST",
    body: JSON.stringify({
      scenario: "cooling_degradation",
      device_id: "GPU-042",
      severity: 0.8,
    }),
  });
  state.selected = "GPU-042";
  setStatus("Scenario active. Twin deviation and anomaly should rise before critical static threshold.");
}

async function resetFleet() {
  await api("/api/v1/scenarios/reset", { method: "POST", body: "{}" });
  document.getElementById("report").textContent =
    "No report yet. Complete investigate → approve → generate report.";
  setStatus("Fleet reset to healthy baseline.");
  await refresh();
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function guidedDemo() {
  if (state.busy) return;
  state.busy = true;
  const buttons = ["btn-inject", "btn-auto", "btn-reset"].map((id) => document.getElementById(id));
  buttons.forEach((b) => (b.disabled = true));
  try {
    await resetFleet();
    setStatus("Baseline collecting…");
    await sleep(2500);
    await injectCooling();
    // Wait for alert/incident
    let incidentId = null;
    for (let i = 0; i < 40; i++) {
      await sleep(1000);
      await refresh();
      const overview = await api("/api/v1/overview");
      const hit = overview.open_incidents.find((x) => x.affected_devices.includes("GPU-042"));
      const d = overview.top_anomalies.find((x) => x.device_id === "GPU-042");
      if (d) {
        setStatus(
          `GPU-042 twinΔ=${d.twin_deviation.toFixed(2)} anomaly=${d.anomaly_score.toFixed(2)} failP=${pct(d.failure_probability)} — waiting for incident…`,
        );
      }
      if (hit) {
        incidentId = hit.incident_id;
        break;
      }
    }
    if (!incidentId) {
      setStatus("No incident yet — keep waiting or increase severity manually.");
      return;
    }
    setStatus("Incident created. Running RCA agent…");
    const rca = await api(`/api/v1/incidents/${incidentId}/investigate`, { method: "POST", body: "{}" });
    setStatus(`RCA ranked: ${rca.result.most_likely_cause}`);
    await sleep(800);
    setStatus("Launching Predictive Maintenance Agent…");
    const maint = await api(`/api/v1/incidents/${incidentId}/maintenance`, { method: "POST", body: "{}" });
    const approvalId = maint.approval.approval_id;
    await refresh();
    setStatus("Auto-approving simulated remediation (human gate in real ops)…");
    await sleep(1000);
    await api(`/api/v1/approvals/${approvalId}/approve`, {
      method: "POST",
      body: JSON.stringify({ comments: "Guided demo approval", user: "demo-operator" }),
    });
    setStatus("Recovery applied — monitoring stabilization…");
    for (let i = 0; i < 12; i++) {
      await sleep(1000);
      await refresh();
    }
    const report = await api(`/api/v1/incidents/${incidentId}/report`, { method: "POST", body: "{}" });
    document.getElementById("report").textContent = JSON.stringify(report, null, 2);
    setStatus("Guided demo complete — review RCA, approval trail, and report.");
    await refresh();
  } catch (err) {
    setStatus(`Guided demo error: ${err.message}`);
  } finally {
    state.busy = false;
    buttons.forEach((b) => (b.disabled = false));
  }
}

function boot() {
  document.getElementById("btn-inject").addEventListener("click", async () => {
    try {
      await injectCooling();
      await refresh();
    } catch (err) {
      setStatus(err.message);
    }
  });
  document.getElementById("btn-reset").addEventListener("click", () => resetFleet());
  document.getElementById("btn-auto").addEventListener("click", () => guidedDemo());
  refreshHealthcare().catch(() => {});
  refresh()
    .then(() => setStatus("Fleet live. Ready to inject cooling degradation on GPU-042."))
    .catch((err) => setStatus(`API error: ${err.message}`));
  state.polling = setInterval(() => {
    if (!state.busy) refresh().catch(() => {});
  }, 2000);
}

boot();
