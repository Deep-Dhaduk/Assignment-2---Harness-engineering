import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

export function defaultStorePath() {
  const root = process.env.DSH_PROFILE_DIR || process.cwd();
  return path.join(root, 'assignment-project-memory.json');
}

export async function loadNotes(filePath) {
  try {
    const parsed = JSON.parse(await readFile(filePath, 'utf8'));
    return Array.isArray(parsed.notes) ? parsed.notes : [];
  } catch (error) {
    if (error && error.code === 'ENOENT') return [];
    throw error;
  }
}

async function saveNotes(filePath, notes) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, JSON.stringify({ version: 1, notes }, null, 2), 'utf8');
}

function text(value, field) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${field} must be a non-empty string`);
  return value.trim();
}

export async function handleMemory(args, filePath = defaultStorePath()) {
  const action = text(args.action, 'action');
  let notes = await loadNotes(filePath);
  let message;
  if (action === 'add') {
    const title = text(args.title, 'title');
    const content = text(args.content, 'content');
    const tag = typeof args.tag === 'string' && args.tag.trim() ? args.tag.trim() : 'general';
    const now = new Date().toISOString();
    const existing = notes.find(note => note.title.toLowerCase() === title.toLowerCase());
    if (existing) {
      Object.assign(existing, { title, content, tag, updatedAt: now });
      message = `Updated note: ${title}`;
    } else {
      notes.push({ id: randomUUID(), title, content, tag, createdAt: now, updatedAt: now });
      message = `Added note: ${title}`;
    }
    await saveNotes(filePath, notes);
  } else if (action === 'list') {
    message = `Found ${notes.length} note(s).`;
  } else if (action === 'search') {
    const query = text(args.query, 'query').toLowerCase();
    notes = notes.filter(note => [note.title, note.content, note.tag].some(value => value.toLowerCase().includes(query)));
    message = `Found ${notes.length} matching note(s).`;
  } else if (action === 'remove') {
    const title = text(args.title, 'title');
    const before = notes.length;
    notes = notes.filter(note => note.title.toLowerCase() !== title.toLowerCase());
    if (notes.length === before) throw new Error(`No note titled: ${title}`);
    await saveNotes(filePath, notes);
    message = `Removed note: ${title}`;
  } else {
    throw new Error(`Unsupported action: ${action}`);
  }
  return { message, notes };
}
