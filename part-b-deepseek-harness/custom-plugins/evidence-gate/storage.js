import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

const KINDS = new Set(['test', 'file', 'metric', 'citation', 'demo']);
const STATUSES = new Set(['passed', 'failed']);

export function defaultStorePath() {
  const root = process.env.DSH_PROFILE_DIR || process.cwd();
  return path.join(root, 'assignment-evidence-gate.json');
}

export async function loadEvidence(filePath) {
  try {
    const parsed = JSON.parse(await readFile(filePath, 'utf8'));
    return Array.isArray(parsed.items) ? parsed.items : [];
  } catch (error) {
    if (error && error.code === 'ENOENT') return [];
    throw error;
  }
}

async function saveEvidence(filePath, items) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, JSON.stringify({ version: 1, items }, null, 2), 'utf8');
}

function requiredText(value, field) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${field} must be a non-empty string`);
  return value.trim();
}

export function summarize(items) {
  const claims = [...new Set(items.map(item => item.claim))];
  const supported = claims.filter(claim => items.some(item => item.claim === claim && item.status === 'passed'));
  return {
    totalItems: items.length,
    totalClaims: claims.length,
    supportedClaims: supported.length,
    failedItems: items.filter(item => item.status === 'failed').length,
    ready: claims.length > 0 && supported.length === claims.length
  };
}

export async function handleEvidence(args, filePath = defaultStorePath()) {
  const action = requiredText(args.action, 'action');
  const items = await loadEvidence(filePath);
  let message;
  if (action === 'record') {
    const claim = requiredText(args.claim, 'claim');
    const evidence = requiredText(args.evidence, 'evidence');
    const kind = requiredText(args.kind, 'kind');
    const status = requiredText(args.status, 'status');
    if (!KINDS.has(kind)) throw new Error(`Unsupported evidence kind: ${kind}`);
    if (!STATUSES.has(status)) throw new Error(`Unsupported evidence status: ${status}`);
    items.push({ id: randomUUID(), claim, evidence, kind, status, recordedAt: new Date().toISOString() });
    await saveEvidence(filePath, items);
    message = `Recorded ${status} ${kind} evidence for: ${claim}`;
  } else if (action === 'list') {
    message = `Found ${items.length} evidence item(s).`;
  } else if (action === 'check') {
    message = summarize(items).ready ? 'Evidence gate passed.' : 'Evidence gate is not ready.';
  } else {
    throw new Error(`Unsupported action: ${action}`);
  }
  return { message, summary: summarize(items), items };
}
