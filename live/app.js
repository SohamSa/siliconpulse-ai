import { SiliconPulseEngine } from "./engine.js";
import { copilotAssessment, lifecycleAssessment, waferAssessment } from "./semiconductor_ai.js";

const engine = new SiliconPulseEngine({ deviceCount: 50, rackCount: 5, seed: 42 });
engine.reset();

const state = { selected: "GPU-042", busy: false };

function pct(n) {
  return `${Math.round((n || 0) * 100)}%`;
}

function setStatus(msg) {
  document.getElementById("demo-status").textContent = msg;
}

function render() {
  const o = engine.overview();
  const s = o.summary;
  const items = [
    ["Devices", s.device_count],
    ["Healthy", s.healthy],
    ["Warning", s.warning],
    ["Critical", s.critical],
    ["Avg temp °C", s.avg_temperature_c.toFixed(1)],
    ["Events", s.events_generated],
    ["Top risk", s.highest_risk_device],
    ["Top risk score", pct(s.highest_risk_prob)],
  ];
  document.getElementById("kpi-grid").innerHTML = items
    .map(
      ([label, value]) => `<div class="kpi"><div class="label">${label}</div><div class="value">${value}</div></div>`,
    )
    .join("");

  const body = document.getElementById("device-rows");
  body.innerHTML = o.top_anomalies
    .map((d) => {
      const active = d.device_id === state.selected ? "active" : "";
      return `<tr class="${active}" data-id="${d.device_id}">
        <td>${d.device_id}</td><td>${d.rack_id}</td><td>${d.temperature_c.toFixed(1)}</td>
        <td>${d.twin_deviation.toFixed(2)}</td><td>${d.anomaly_score.toFixed(2)}</td>
        <td>${pct(d.failure_probability)}</td><td>${d.health_score.toFixed(0)}</td>
        <td>${d.rul_hours.toFixed(0)}</td></tr>`;
    })
    .join("");
  body.querySelectorAll("tr").forEach((tr) => {
    tr.onclick = () => {
      state.selected = tr.dataset.id;
      render();
    };
  });

  const d = engine.deviceRows().find((x) => x.device_id === state.selected) || o.top_anomalies[0];
  document.getElementById("selected-device").textContent = d.device_id;
  document.getElementById("device-detail").innerHTML = `
    <div class="row"><span class="k">Model / FW</span><span>${d.model_name} · ${d.firmware_version}</span></div>
    <div class="row"><span class="k">Lifecycle</span><span class="badge ${d.status === "healthy" ? "ok" : "warning"}">${d.status}</span></div>
    <div class="row"><span class="k">Temp / twin expected</span><span>${d.temperature_c.toFixed(1)}°C / ${d.twin_expected_temp.toFixed(1)}°C</span></div>
    <div class="row"><span class="k">Twin deviation</span><span>${d.twin_deviation.toFixed(2)} (conf ${d.twin_confidence})</span></div>
    <div class="row"><span class="k">Anomaly</span><span>${d.anomaly_score.toFixed(2)}</span></div>
    <div class="row"><span class="k">Failure risk score</span><span>${d.failure_type} (${pct(d.failure_probability)})</span></div>
    <div class="row"><span class="k">Demo RUL / health</span><span>${d.rul_hours.toFixed(0)}h · ${d.health_score.toFixed(0)}</span></div>
    <div class="row"><span class="k">Power / util / fan</span><span>${d.power_watts}W · ${d.utilization_pct}% · ${d.fan_rpm} RPM</span></div>
    <div class="row"><span class="k">True cooling efficiency</span><span>${d.cooling_eff} <em>(eval only)</em></span></div>`;

  const incEl = document.getElementById("incidents");
  if (!o.open_incidents.length) {
    incEl.innerHTML = `<div class="cardish"><p>No open incidents. Inject a scenario to begin.</p></div>`;
  } else {
    incEl.innerHTML = o.open_incidents
      .map((inc) => {
        const cause = inc.likely_root_cause || "not investigated";
        return `<div class="cardish" data-incident="${inc.incident_id}">
          <h4>${inc.title} <span class="badge ${inc.severity}">${inc.severity}</span></h4>
          <p>Status: <strong>${inc.status}</strong> · ${inc.affected_devices.join(", ")}</p>
          <p>Root cause: <strong>${cause}</strong>${inc.confidence ? ` (${pct(inc.confidence)})` : ""}</p>
          <div class="cta-row">
            <button class="btn ghost" data-act="investigate" type="button">Investigate</button>
            <button class="btn ghost" data-act="maintenance" type="button">Maintenance agent</button>
            <button class="btn ghost" data-act="report" type="button">Generate report</button>
          </div>
        </div>`;
      })
      .join("");
    incEl.querySelectorAll("button").forEach((btn) => {
      btn.onclick = () => {
        const id = btn.closest("[data-incident]").dataset.incident;
        try {
          if (btn.dataset.act === "investigate") {
            const out = engine.investigate(id);
            setStatus(`RCA: ${out.result.most_likely_cause} (${pct(out.result.confidence)})`);
          } else if (btn.dataset.act === "maintenance") {
            engine.requestMaintenance(id);
            setStatus("Approval requested — review Approvals panel.");
          } else {
            const report = engine.generateReport(id);
            document.getElementById("report").textContent = JSON.stringify(report, null, 2);
            setStatus("Report generated.");
          }
          render();
        } catch (err) {
          setStatus(`Error: ${err.message}`);
        }
      };
    });
  }

  const apEl = document.getElementById("approvals");
  if (!o.pending_approvals.length) {
    apEl.innerHTML = `<div class="cardish"><p>No pending approvals.</p></div>`;
  } else {
    apEl.innerHTML = o.pending_approvals
      .map(
        (a) => `<div class="cardish">
          <h4>Approval ${a.approval_id.slice(0, 8)}</h4>
          <p><strong>${a.action}</strong></p>
          <p>${a.reason}</p>
          <p>Expected: ${a.expected_impact}</p>
          <div class="cta-row">
            <button class="btn primary" data-id="${a.approval_id}" data-act="approve" type="button">Approve</button>
            <button class="btn ghost" data-id="${a.approval_id}" data-act="reject" type="button">Reject</button>
          </div>
        </div>`,
      )
      .join("");
    apEl.querySelectorAll("button").forEach((btn) => {
      btn.onclick = () => {
        engine.decideApproval(btn.dataset.id, btn.dataset.act === "approve", btn.dataset.act);
        setStatus(
          btn.dataset.act === "approve"
            ? "Action approved — recovery injected. Watch temp stabilize."
            : "Action rejected.",
        );
        render();
      };
    });
  }

  const agEl = document.getElementById("agents");
  agEl.innerHTML = o.agent_runs.length
    ? `<h4 style="margin:0 0 .5rem;color:var(--muted)">Recent agent runs</h4>` +
      o.agent_runs
        .map(
          (r) => `<div class="cardish"><h4>${r.agent_type} · ${r.status}</h4>
          <p>${r.current_step}${r.confidence ? ` · conf ${pct(r.confidence)}` : ""}</p>
          <p>${(r.decisions || []).join(" · ")}</p></div>`,
        )
        .join("")
    : "";
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function guidedDemo() {
  if (state.busy) return;
  state.busy = true;
  ["btn-inject", "btn-auto", "btn-reset"].forEach((id) => (document.getElementById(id).disabled = true));
  try {
    engine.reset();
    state.selected = "GPU-042";
    setStatus("Baseline collecting…");
    render();
    await sleep(2000);
    engine.inject("cooling_degradation", "GPU-042", 0.9);
    setStatus("Cooling degradation active on GPU-042…");
    let incidentId = null;
    for (let i = 0; i < 40; i++) {
      await sleep(500);
      engine.tick();
      render();
      const d = engine.deviceRows().find((x) => x.device_id === "GPU-042");
      const hit = engine.overview().open_incidents.find((x) => x.affected_devices.includes("GPU-042"));
      if (d) {
        setStatus(
          `GPU-042 twinΔ=${d.twin_deviation.toFixed(2)} anomaly=${d.anomaly_score.toFixed(2)} risk=${pct(d.failure_probability)}`,
        );
      }
      if (hit) {
        incidentId = hit.incident_id;
        break;
      }
    }
    if (!incidentId) {
      setStatus("No incident yet — try inject again.");
      return;
    }
    const rca = engine.investigate(incidentId);
    setStatus(`RCA ranked: ${rca.result.most_likely_cause}`);
    render();
    await sleep(700);
    const maint = engine.requestMaintenance(incidentId);
    render();
    await sleep(700);
    engine.decideApproval(maint.approval.approval_id, true, "Guided demo approval");
    setStatus("Recovery applied — monitoring stabilization…");
    for (let i = 0; i < 10; i++) {
      await sleep(400);
      engine.tick();
      render();
    }
    const report = engine.generateReport(incidentId);
    document.getElementById("report").textContent = JSON.stringify(report, null, 2);
    setStatus("Guided demo complete — share this live link with your audience.");
    render();
  } catch (err) {
    setStatus(`Guided demo error: ${err.message}`);
  } finally {
    state.busy = false;
    ["btn-inject", "btn-auto", "btn-reset"].forEach((id) => (document.getElementById(id).disabled = false));
  }
}

document.getElementById("btn-reset").onclick = () => {
  engine.reset();
  document.getElementById("report").textContent =
    "No report yet. Complete investigate → approve → generate report.";
  setStatus("Fleet reset to healthy baseline.");
  render();
};

document.getElementById("btn-inject").onclick = () => {
  engine.inject("cooling_degradation", "GPU-042", 0.85);
  state.selected = "GPU-042";
  setStatus("Scenario active. Twin deviation and anomaly should rise in real time.");
  render();
};

document.getElementById("btn-auto").onclick = () => guidedDemo();

function showLab(title, data, extra = "") {
  document.getElementById("ai-lab-output").innerHTML = `<h4>${title}</h4>${extra}<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

document.getElementById("btn-survival").onclick = () => {
  const device = engine.deviceRows().find((item) => item.device_id === "GPU-042");
  showLab("GPU-042 survival assessment", lifecycleAssessment(device));
};

document.getElementById("btn-wafer").onclick = () => {
  const assessment = waferAssessment(904, "edge_ring");
  const cells = assessment.cells
    .map((cell) => `<i class="${cell.bad ? "fail" : "pass"}" style="grid-column:${cell.col + 1};grid-row:${cell.row + 1}" title="${cell.bad ? "defect" : "pass"}"></i>`)
    .join("");
  const view = { ...assessment };
  delete view.cells;
  showLab("Synthetic wafer spatial triage", view, `<div class="wafer-map">${cells}</div>`);
};

document.getElementById("btn-copilot").onclick = () => {
  const device = engine.deviceRows().find((item) => item.device_id === "GPU-042");
  showLab("Evidence-grounded engineering case", copilotAssessment(device));
};

// Real-time loop: tick + paint while the page is open
setInterval(() => {
  if (!state.busy) {
    engine.tick();
    render();
  }
}, 1000);

setStatus("Fleet live. Ready to inject cooling degradation on GPU-042.");
render();
