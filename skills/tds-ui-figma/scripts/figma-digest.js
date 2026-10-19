#!/usr/bin/env node
// figma-digest.js — PostToolUse hook for mcp__framelink__get_figma_data
// Trims framelink output + resolves hex -> TDS class, replaces tool output via
// hookSpecificOutput.updatedToolOutput. On error: exit 0 silent -> original passes through.
const { readFileSync } = require('node:fs');
const { lookup } = require('./tds-token-lookup');

const PROJECT = process.env.TDS_PROJECT || '';
const THEME_PRESET = process.env.TDS_THEME_PRESET || 'default';
const MODE = process.env.TDS_MODE || 'light';
const NOISE_KEYS = new Set([
  'designedWidth', 'designedHeight', 'textAlignVertical', 'imageRef',
  'imageDownloadArguments', 'scaleMode', 'backgroundSize', 'backgroundRepeat',
  'isBackground', 'strokeWeight', 'fontFamily'
]);

function safe(f) { try { return f(); } catch { return null; } }
const input = safe(() => JSON.parse(readFileSync(0, 'utf8')));
if (!input || input.hook_event_name !== 'PostToolUse') process.exit(0);
const resp = input.tool_response;

function extractText(r) {
  if (r == null) return '';
  if (typeof r === 'string') return r;
  if (Array.isArray(r)) return r.map(b => typeof b === 'string' ? b : (b && b.text) || '').join('\n');
  if (typeof r === 'object') {
    if (typeof r.text === 'string') return r.text;
    if (Array.isArray(r.content)) return r.content.map(b => (b && b.text) || '').join('\n');
    return JSON.stringify(r);
  }
  return String(r);
}
function shapeText(r, text) {
  if (typeof r === 'string') return text;
  if (Array.isArray(r)) return [{ type: 'text', text }];
  if (r && typeof r === 'object') {
    if (typeof r.text === 'string') return { ...r, text };
    if (Array.isArray(r.content)) return { ...r, content: [{ type: 'text', text }] };
  }
  return text;
}

const raw = safe(() => extractText(resp)) || '';
if (!raw || (!raw.includes('GLOBAL_VARS') && !raw.includes('NODES'))) process.exit(0);

// ---------- TRIM ----------
const sections = {};
let cur = null;
for (const line of raw.split(/\r?\n/)) {
  const h = line.match(/^([A-Z][A-Z_]*):$/);
  if (h) { cur = h[1]; sections[cur] = []; continue; }
  if (cur) sections[cur].push(line);
}
const block = s => (sections[s] || []).join('\n');

function parseVars(text) {
  const out = new Map(); let name = null, parts = [];
  const flush = () => { if (name) { let v = parts.join(' ').replace(/\s+/g, ' ').trim(); if (v === '[]') v = ''; out.set(name, v); } };
  for (const line of text.split('\n')) {
    if (/^\S/.test(line)) {
      flush();
      const ci = line.lastIndexOf(':');
      name = ci >= 0 ? line.slice(0, ci) : line;
      const rest = ci >= 0 ? line.slice(ci + 1).trim() : '';
      parts = rest ? [rest] : [];
    } else if (name) {
      const t = line.trim().replace(/^-\s+/, '');
      if (t && t !== '[]') parts.push(t);
    }
  }
  flush();
  return out;
}
const globals = parseVars(block('GLOBAL_VARS'));
const elements = parseVars(block('ELEMENTS'));
const nodesText = block('NODES');
const elementsText = block('ELEMENTS');
const scan = s => {
  const refs = new Set();
  for (const m of s.matchAll(/\b(fill_[a-f0-9]+)\b/g)) refs.add(m[1]);
  for (const m of s.matchAll(/\b(layout_[a-f0-9]+)\b/g)) refs.add(m[1]);
  for (const m of s.matchAll(/template=(EL-[\w]+)/g)) refs.add(m[1]);
  for (const m of s.matchAll(/\{(ts\d)\}/g)) refs.add(m[1]);
  for (const m of s.matchAll(/textStyle="([^"]+)"/g)) refs.add(m[1]);
  for (const m of s.matchAll(/textStyle=(\S+)/g)) refs.add(m[1]);
  return refs;
};
const refs = new Set([...scan(nodesText), ...scan(elementsText)]);
let nodes = nodesText;
for (const [k, v] of globals) if (k.startsWith('fill_')) nodes = nodes.split(`fills=${k}`).join(`fills=${v || '-'}`);

// strip noise from inline JSON blobs in NODES (layout={...}, textStyle={...}, fills=[IMAGE])
function stripObj(o) {
  if (Array.isArray(o)) { o.forEach(stripObj); return o; }
  if (o && typeof o === 'object') { for (const k of Object.keys(o)) { if (NOISE_KEYS.has(k)) delete o[k]; else stripObj(o[k]); } }
  return o;
}
function compactJsonBlobs(text) {
  text = text.replace(/fills=\[\{[\s\S]*?\}\]/g, (m) => {
    if (/"type"\s*:\s*"IMAGE"/.test(m)) return 'fills=[IMAGE]';
    if (/"type"\s*:\s*"GRADIENT/.test(m)) {
      const g = /"(?:gradient|cssGradient)"\s*:\s*"([^"]+)"/.exec(m);
      if (g) return `fills=[GRADIENT ${g[1]}]`;
      const stops = [...m.matchAll(/#[0-9A-Fa-f]{3,8}\b/g)].map(s => s[0]);
      if (stops.length) return `fills=[GRADIENT ${stops.join('→')}]`;
      return 'fills=[GRADIENT]';
    }
    return m;
  });
  let out = '', i = 0;
  while (i < text.length) {
    const m = /(\b[a-zA-Z_]\w*)=\{/.exec(text.slice(i));
    if (!m) { out += text.slice(i); break; }
    const start = i + m.index;
    out += text.slice(i, start);
    const bracePos = start + m[1].length + 1;
    let depth = 0, j = bracePos;
    for (; j < text.length; j++) {
      if (text[j] === '{') depth++;
      else if (text[j] === '}') { depth--; if (depth === 0) break; }
    }
    if (depth !== 0) { out += text.slice(start); break; }
    const jsonStr = text.slice(bracePos, j + 1);
    let rep;
    try { rep = `${m[1]}=${JSON.stringify(stripObj(JSON.parse(jsonStr)))}`; }
    catch { rep = text.slice(start, j + 1); }
    out += rep;
    i = j + 1;
  }
  return out;
}
nodes = compactJsonBlobs(nodes);

// strip noise tokens from flattened var lines
const stripVarNoise = v => v.replace(/\s*(fontFamily:\s+[^:]+?(?=\s+\w+:)|textAlignVertical:\s+\S+)/g, '');
const gvOut = [...globals.entries()].filter(([k, v]) => refs.has(k) && v && !k.startsWith('fill_')).map(([k, v]) => `  ${k}: ${stripVarNoise(v)}`);
const elOut = [...elements.entries()].filter(([k, v]) => refs.has(k) && v).map(([k, v]) => `  ${k}: ${stripVarNoise(v)}`);

const hexes = [...new Set([...nodes.matchAll(/#[0-9A-Fa-f]{6}\b/g)].map(m => m[0]))];

// ---------- assemble ----------
async function emitDigest() {
  const colorLines = [];
  for (const h of hexes) {
    const roles = ['text', 'background', 'border', 'icon', 'surface', 'ring'];
    const roleResults = [];
    for (const role of roles) {
      const result = await lookup([h, role, PROJECT, THEME_PRESET, MODE]);
      if (result.reason === 'themePresetRequired') {
        const message = [
          'THEME_PRESET_REQUIRED:',
          `  ${h} requires project themePreset before Figma analysis can continue.`,
          '  Run node <skill-dir>/scripts/set-tds-theme-preset.js --list from the project root, ask the user to choose one supported preset from remote theme.json, then save it with set-tds-theme-preset.js <themePreset> [project].',
          ''
        ].join('\n');
        const out = { hookSpecificOutput: { hookEventName: 'PostToolUse', updatedToolOutput: shapeText(resp, message) } };
        process.stdout.write(JSON.stringify(out));
        return;
      }
      if (result.reason === 'unsupportedThemePreset') {
        const message = [
          'UNSUPPORTED_THEME_PRESET:',
          `  ${result.themePreset} is not present in the current remote theme.json.`,
          `  Supported presets: ${(result.supportedThemePresets || []).join(', ') || '(none)'}.`,
          '  Ask the user to choose one supported preset before mapping colors.',
          ''
        ].join('\n');
        const out = { hookSpecificOutput: { hookEventName: 'PostToolUse', updatedToolOutput: shapeText(resp, message) } };
        process.stdout.write(JSON.stringify(out));
        return;
      }
      if (result.status === 'exact') roleResults.push(`${role}: ${result.matches[0]} (${result.source})`);
      else if (result.status === 'ambiguous') roleResults.push(`${role}: AMBIGUOUS ${result.matches.join(' | ')}`);
    }
    colorLines.push(roleResults.length ? `  ${h} -> ${roleResults.join('; ')}` : `  ${h} -> MISSING (ask user)`);
  }

  const parts = ['GLOBAL_VARS:', ...gvOut];
  if (elOut.length) parts.push('ELEMENTS:', ...elOut);
  parts.push('NODES:', nodes.trim());
  if (colorLines.length) parts.push(`COLOR_MAP (project=${PROJECT || 'none'}, themePreset=${THEME_PRESET || 'none'}, mode=${MODE}):`, ...colorLines);
  const digest = parts.join('\n') + '\n';

  const out = { hookSpecificOutput: { hookEventName: 'PostToolUse', updatedToolOutput: shapeText(resp, digest) } };
  process.stdout.write(JSON.stringify(out));
}

emitDigest().catch(() => process.exit(0));
