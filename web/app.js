"use strict";

/* Pure evaluator intentionally mirrors agents/workers.py, not a biological model. */
function evaluateTask(payload) {
  const primary = Number(payload.primary_metric);
  const secondary = Number(payload.secondary_metric);
  if (!Number.isFinite(primary) || !Number.isFinite(secondary)) {
    throw new Error("Both metrics must be finite numbers.");
  }
  const taskId = String(payload.task_id || "").trim();
  const target = String(payload.target_identifier || "").trim();
  const descriptor = String(payload.status_descriptor || "").trim();
  if (!taskId || !target || !descriptor) {
    throw new Error("Task ID, target identifier and status descriptor are required.");
  }
  const critical = payload.is_critical_flag === true;
  const alerts = [];
  if (primary > 25) {
    alerts.push({ worker: "InvariantQCWorker", urgency: "ELEVATED_RISK", summary: "Primary Metric Threshold Exceeded" });
  }
  if (critical || secondary > 12) {
    alerts.push({ worker: "SafetyEscalationWorker", urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK", summary: "Critical Safety Interlock Triggered" });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(token => descriptor.toUpperCase().includes(token))) {
    alerts.push({ worker: "ProtocolConformanceWorker", urgency: "ELEVATED_RISK", summary: "Protocol Conformance Discordance Detected" });
  }
  const urgency = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    task_id: taskId,
    target_identifier: target,
    overall_urgency: urgency,
    integrity_status: urgency === "CRITICAL_STAT_PANIC" ? "RECALIBRATION_REQUIRED" : urgency === "ELEVATED_RISK" ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length,
    alerts,
    evaluation_mode: "local-rule-demo",
    warning: "Not a promoter model, sequence generator, safety certification, or cryptographically signed audit."
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { evaluateTask };
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("audit-form");
    const result = document.getElementById("result");
    const output = document.getElementById("json-output");
    const error = document.getElementById("form-error");
    const exportButton = document.getElementById("export");
    let lastResult = null;

    function value(id) { return document.getElementById(id).value; }

    form.addEventListener("submit", event => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      try {
        const payload = {
          task_id: value("task_id"),
          target_identifier: value("target_identifier"),
          primary_metric: value("primary_metric"),
          secondary_metric: value("secondary_metric"),
          status_descriptor: value("status_descriptor"),
          is_critical_flag: document.getElementById("is_critical_flag").checked
        };
        if (!payload.primary_metric.trim() || !payload.secondary_metric.trim()) {
          throw new Error("Both metrics are required.");
        }
        lastResult = evaluateTask(payload);
        error.textContent = "";
        exportButton.disabled = false;
        result.replaceChildren();
        const status = document.createElement("span");
        status.className = "pill " + (lastResult.overall_urgency === "ROUTINE" ? "routine" : lastResult.overall_urgency === "ELEVATED_RISK" ? "elevated" : "critical");
        status.textContent = lastResult.overall_urgency;
        result.append(status);
        const facts = document.createElement("div");
        facts.className = "facts";
        for (const [label, data] of [["Alerts", lastResult.total_alerts], ["Integrity classification", lastResult.integrity_status]]) {
          const wrapper = document.createElement("div");
          const caption = document.createElement("small");
          caption.textContent = label;
          const number = document.createElement("strong");
          number.textContent = String(data);
          wrapper.append(caption, number);
          facts.append(wrapper);
        }
        result.append(facts);
        const heading = document.createElement("p");
        heading.textContent = "Triggered rules:";
        result.append(heading);
        const list = document.createElement("ul");
        list.className = "alerts";
        if (!lastResult.alerts.length) {
          const item = document.createElement("li");
          item.textContent = "No configured rules were triggered.";
          list.append(item);
        }
        for (const alert of lastResult.alerts) {
          const item = document.createElement("li");
          item.textContent = alert.worker + ": " + alert.summary;
          list.append(item);
        }
        result.append(list);
        output.textContent = JSON.stringify(lastResult, null, 2);
      } catch (exc) {
        error.textContent = exc.message || "Unable to evaluate the input.";
        lastResult = null;
        exportButton.disabled = true;
      }
    });

    exportButton.addEventListener("click", () => {
      if (!lastResult) return;
      const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "evaluation-result.json";
      anchor.click();
      URL.revokeObjectURL(url);
    });
  });
}
