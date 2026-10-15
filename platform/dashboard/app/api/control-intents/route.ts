import { submitControl } from '../../../lib/controls.ts';
export const dynamic = 'force-dynamic';
export async function POST(request: Request) { return submitControl(request,'/v1/intents'); }
