import { defaultStorePath, handleEvidence } from './storage.js';

export const name = 'assignment-evidence-gate';
export const inject = ['tools'];

export function apply(ctx) {
  ctx.tools.register({
    name: 'evidence_gate',
    description: 'Record or inspect concrete evidence for completion claims. A gate passes only when every recorded claim has passing evidence.',
    parameters: {
      type: 'object',
      additionalProperties: false,
      properties: {
        action: { type: 'string', enum: ['record', 'list', 'check'] },
        claim: { type: 'string', description: 'Claim being supported; required by record.' },
        evidence: { type: 'string', description: 'Specific result, command output, file, metric, citation, or demo; required by record.' },
        kind: { type: 'string', enum: ['test', 'file', 'metric', 'citation', 'demo'] },
        status: { type: 'string', enum: ['passed', 'failed'] }
      },
      required: ['action']
    },
    output: {
      schema: { type: 'object' },
      render: (_args, value) => [{
        type: 'text',
        text: `${value.message} Claims: ${value.summary.supportedClaims}/${value.summary.totalClaims} supported; ready=${value.summary.ready}.`
      }]
    },
    execute(args) {
      return handleEvidence(args, defaultStorePath());
    },
    presentCall: args => ({ card: 'generic', title: `Evidence gate: ${args.action}`, kind: 'other', rawInput: args })
  });
}
