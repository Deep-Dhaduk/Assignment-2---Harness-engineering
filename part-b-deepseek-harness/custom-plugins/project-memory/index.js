import { defaultStorePath, handleMemory } from './storage.js';

export const name = 'assignment-project-memory';
export const inject = ['tools'];

export function apply(ctx) {
  ctx.tools.register({
    name: 'project_memory',
    description: 'Persist and retrieve durable notes about the current project. Use add, list, search, or remove.',
    parameters: {
      type: 'object',
      additionalProperties: false,
      properties: {
        action: { type: 'string', enum: ['add', 'list', 'search', 'remove'] },
        title: { type: 'string', description: 'Required by add and remove.' },
        content: { type: 'string', description: 'Required by add.' },
        tag: { type: 'string', description: 'Optional category for an added note.' },
        query: { type: 'string', description: 'Required by search.' }
      },
      required: ['action']
    },
    output: {
      schema: { type: 'object' },
      render: (_args, value) => [{ type: 'text', text: `${value.message}\n${value.notes.map(note => `- ${note.title} [${note.tag}]: ${note.content}`).join('\n')}`.trim() }]
    },
    execute(args) {
      return handleMemory(args, defaultStorePath());
    },
    presentCall: args => ({ card: 'generic', title: `Project memory: ${args.action}`, kind: 'other', rawInput: args })
  });
}
