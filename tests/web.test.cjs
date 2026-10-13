"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluateTask } = require("../web/app.js");

function sample(overrides = {}) {
  return Object.assign({ task_id: "T1", target_identifier: "KEY-01", primary_metric: 10, secondary_metric: 2, status_descriptor: "NOMINAL", is_critical_flag: false }, overrides);
}

test("nominal values have no alerts", () => {
  const output = evaluateTask(sample());
  assert.equal(output.overall_urgency, "ROUTINE");
  assert.equal(output.total_alerts, 0);
});
test("primary and secondary thresholds match Python worker logic", () => {
  const output = evaluateTask(sample({ primary_metric: 26, secondary_metric: 13 }));
  assert.equal(output.overall_urgency, "ELEVATED_RISK");
  assert.equal(output.total_alerts, 2);
});
test("critical flag escalates and descriptor is evaluated", () => {
  const output = evaluateTask(sample({ is_critical_flag: true, status_descriptor: "DISCORDANT" }));
  assert.equal(output.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(output.critical_alerts_count, 1);
  assert.equal(output.total_alerts, 2);
});
test("invalid numeric values are rejected", () => {
  assert.throws(() => evaluateTask(sample({ primary_metric: "Infinity" })), /finite/);
  assert.throws(() => evaluateTask(sample({ secondary_metric: "NaN" })), /finite/);
});
test("no fabricated HMAC signature is produced", () => {
  assert.equal("audit_hash" in evaluateTask(sample()), false);
});
