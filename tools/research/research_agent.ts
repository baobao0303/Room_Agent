import { writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { execSync } from 'child_process';

interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

const GATEWAY_URL = process.env.HERMES_GATEWAY_URL || 'http://localhost:8642/v1/chat/completions';
const API_KEY = process.env.HERMES_API_KEY || 'hermes_secret_key_8642';
const MODEL = process.env.HERMES_MODEL || 'gemini-3.7-medium';

const TIER_1 = `You are an AI research specialist. Be direct: match response length to weight of ask. No filler. Output structured findings with verified claims.`;
const TIER_2 = `Format findings as declarative facts. State prerequisites and limitations.`;

function runViaHermesCli(systemPrompt: string, topic: string): string {
  const prompt = `${systemPrompt}\n\nPerform comprehensive research and analysis on the following topic:\n\n${topic}`;
  const escaped = prompt.replace(/'/g, "'\\''");
  try {
    const out = execSync(`hermes -z '${escaped}'`, { encoding: 'utf-8', timeout: 120000 });
    if (out.trim()) return out.trim();
  } catch (e) {
    // fallback to hermes chat -q
    const out2 = execSync(`hermes chat -q '${escaped}' -Q`, { encoding: 'utf-8', timeout: 120000 });
    const lines = out2.split('\n').filter(l => !l.startsWith('session_id:'));
    return lines.join('\n').trim();
  }
  return '';
}

export async function executeResearch(topic: string, outputPath?: string): Promise<string> {
  const cwd = process.cwd();
  const tier3 = `Environment & CWD: ${cwd}\nTask: ${topic}\nTime: ${new Date().toISOString()}`;
  const systemPrompt = `${TIER_1}\n\n${TIER_2}\n\n${tier3}`;

  let resultText = '';

  try {
    const messages: Message[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Analyze and document technical findings for:\n${topic}` }
    ];

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const res = await fetch(GATEWAY_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({ model: MODEL, messages, temperature: 0.2 }),
      signal: controller.signal
    });
    clearTimeout(timeout);

    if (res.ok) {
      const data = await res.json();
      resultText = data.choices?.[0]?.message?.content || '';
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    console.warn(`[Notice] Gateway HTTP failed (${err}). Falling back to Hermes CLI directly...`);
    resultText = runViaHermesCli(systemPrompt, topic);
  }

  if (outputPath && resultText) {
    const fullOut = resolve(cwd, outputPath);
    mkdirSync(dirname(fullOut), { recursive: true });
    writeFileSync(fullOut, `# Research: ${topic}\n\n${resultText}`, 'utf-8');
    console.log(`Saved to: ${fullOut}`);
  }

  return resultText;
}

const topic = process.argv[2];
if (topic) {
  const out = process.argv[3] || `tools/research/${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}.md`;
  executeResearch(topic, out).catch(console.error);
}
