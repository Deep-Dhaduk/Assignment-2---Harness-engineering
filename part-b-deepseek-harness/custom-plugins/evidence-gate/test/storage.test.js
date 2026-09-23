import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { apply } from '../index.js';
import { handleEvidence } from '../storage.js';

test('gate becomes ready when every claim has passing evidence', async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'evidence-gate-'));
  const store = path.join(directory, 'evidence.json');
  try {
    let result = await handleEvidence({
      action: 'record', claim: 'Part A works', evidence: 'unit tests exit 0', kind: 'test', status: 'passed'
    }, store);
    assert.equal(result.summary.ready, true);
    result = await handleEvidence({
      action: 'record', claim: 'Part B works', evidence: 'not installed yet', kind: 'demo', status: 'failed'
    }, store);
    assert.equal(result.summary.ready, false);
    result = await handleEvidence({
      action: 'record', claim: 'Part B works', evidence: 'tool visible in Creator mode', kind: 'demo', status: 'passed'
    }, store);
    assert.equal(result.summary.ready, true);
    assert.equal(result.summary.failedItems, 1);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('rejects unknown evidence kinds', async () => {
  await assert.rejects(() => handleEvidence({
    action: 'record', claim: 'x', evidence: 'y', kind: 'guess', status: 'passed'
  }, 'unused.json'), /Unsupported evidence kind/);
});

test('Cordis apply registers an executable evidence_gate tool', async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'evidence-gate-registration-'));
  const previous = process.env.DSH_PROFILE_DIR;
  process.env.DSH_PROFILE_DIR = directory;
  let definition;
  try {
    apply({ tools: { register(tool) { definition = tool; } } });
    assert.equal(definition.name, 'evidence_gate');
    const result = await definition.execute({
      action: 'record', claim: 'Registration works', evidence: 'execute returned', kind: 'test', status: 'passed'
    });
    assert.equal(result.summary.ready, true);
  } finally {
    if (previous === undefined) delete process.env.DSH_PROFILE_DIR;
    else process.env.DSH_PROFILE_DIR = previous;
    await rm(directory, { recursive: true, force: true });
  }
});
