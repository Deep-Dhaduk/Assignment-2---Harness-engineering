import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { apply } from '../index.js';
import { handleMemory, loadNotes } from '../storage.js';

test('adds, updates, searches, and removes persistent notes', async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'project-memory-'));
  const store = path.join(directory, 'notes.json');
  try {
    await handleMemory({ action: 'add', title: 'Architecture', content: 'Bounded loop', tag: 'design' }, store);
    await handleMemory({ action: 'add', title: 'Architecture', content: 'Bounded tool loop', tag: 'design' }, store);
    assert.equal((await loadNotes(store)).length, 1);
    const found = await handleMemory({ action: 'search', query: 'tool loop' }, store);
    assert.equal(found.notes[0].title, 'Architecture');
    await handleMemory({ action: 'remove', title: 'Architecture' }, store);
    assert.deepEqual(await loadNotes(store), []);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('rejects unsupported actions', async () => {
  await assert.rejects(() => handleMemory({ action: 'erase-everything' }, 'unused.json'), /Unsupported action/);
});

test('Cordis apply registers an executable project_memory tool', async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'project-memory-registration-'));
  const previous = process.env.DSH_PROFILE_DIR;
  process.env.DSH_PROFILE_DIR = directory;
  let definition;
  try {
    apply({ tools: { register(tool) { definition = tool; } } });
    assert.equal(definition.name, 'project_memory');
    const result = await definition.execute({ action: 'add', title: 'Registered', content: 'Tool works' });
    assert.equal(result.notes.length, 1);
  } finally {
    if (previous === undefined) delete process.env.DSH_PROFILE_DIR;
    else process.env.DSH_PROFILE_DIR = previous;
    await rm(directory, { recursive: true, force: true });
  }
});
