#!/usr/bin/env node
const { existsSync, readFileSync } = require('node:fs');
const { join, resolve } = require('node:path');
const { cacheDir, sync } = require('./sync-tds-tokens');

const skillDir = resolve(__dirname, '..');

function usage() {
  return `Usage:
  node tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]

Roles:
  text | icon | border | background | surface | ring

Environment:
  TDS_TOKEN_CACHE_DIR       Optional cache directory for theme.json/global.json/alias.json.
  TDS_TOKEN_LOOKUP_OFFLINE  Set to 1 to skip remote sync and use existing cache.
  TDS_PROJECT               Project key for project overrides.
  TDS_THEME_PRESET          Theme preset name from remote theme.json.
  TDS_MODE                  light or dark.
`;
}

function readJson(path, fallback = null) {
  try {
    return existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : fallback;
  } catch {
    return fallback;
  }
}

function normalizeHex(value) {
  if (!value || typeof value !== 'string') return '';
  const hex = value.trim().toUpperCase();
  if (!hex.startsWith('#')) return '';
  if (hex.length === 4) return `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`;
  return hex;
}

function cssPrefix(role) {
  if (role === 'text' || role === 'icon') return 'text-';
  if (role === 'border') return 'border-';
  if (role === 'ring') return 'ring-';
  if (role === 'background' || role === 'surface') return 'bg-';
  return '';
}

function semanticPrefix(role) {
  if (role === 'text') return 'tds-color-text-';
  if (role === 'icon') return 'tds-color-icon-';
  if (role === 'border') return 'tds-color-border-';
  if (role === 'ring') return 'tds-color-ring-';
  if (role === 'surface') return 'tds-color-surface-';
  if (role === 'background') return 'tds-color-background-';
  return 'tds-color-';
}

function classForGlobal(token, role) {
  const prefix = cssPrefix(role);
  const light = token.light || `${token.name}-light`;
  const dark = token.dark || `${token.name}-dark`;
  return `${prefix}${light} dark:${prefix}${dark}`;
}

function tokenHexes(token) {
  return [normalizeHex(token.lightValue), normalizeHex(token.darkValue)].filter(Boolean);
}

function loadProjectMap() {
  const candidates = [
    process.env.TDS_PROJECT_MAP,
    join(skillDir, 'references', 'config', 'tds-project-token-map.json'),
    join(process.cwd(), '.claude', 'tds-project-token-map.json'),
    join(process.cwd(), '.codex', 'tds-project-token-map.json')
  ].filter(Boolean);
  for (const candidate of candidates) {
    const data = readJson(candidate);
    if (data) return { data, file: candidate };
  }
  return { data: {}, file: 'none' };
}

function projectMatches(projectMap, hex, role, project, themeName, mode) {
  if (!project) return [];
  const modeNode = projectMap.projects?.[project]?.themes?.[themeName]?.modes?.[mode];
  const entry = modeNode?.[hex];
  return Array.isArray(entry?.[role]) ? entry[role] : [];
}

function projectThemePreset(projectMap, project, themePresetArg, presets) {
  if (presets.has(project) && (!themePresetArg || themePresetArg === 'default')) return project;
  const configuredPreset =
    (project ? projectMap.projects?.[project]?.themePreset : null)
    || projectMap.projects?.default?.themePreset
    || projectMap.themePreset
    || null;
  return themePresetArg && themePresetArg !== 'default'
    ? themePresetArg
    : process.env.TDS_THEME_PRESET
      || configuredPreset
      || null;
}

function findGlobalByClass(globalTokens, className) {
  const baseName = className.replace(/-(light|dark)$/, '');
  return globalTokens.find(token => token.name === className || token.name === baseName || token.light === className || token.dark === className);
}

function aliasMatches(aliasTokens, globalTokens, hex, role) {
  const prefix = semanticPrefix(role);
  const matches = [];
  for (const alias of aliasTokens) {
    if (!alias.name?.startsWith(prefix)) continue;
    const refs = [alias.lightValue, alias.darkValue]
      .filter(Boolean)
      .map(value => value.replace(/^(text|bg|border|ring)-/, ''))
      .map(value => value.replace(/\/\d+$/, ''));
    const linkedGlobal = refs
      .map(ref => findGlobalByClass(globalTokens, ref))
      .filter(Boolean);
    if (linkedGlobal.some(token => tokenHexes(token).includes(hex))) matches.push(alias.name);
  }
  return [...new Set(matches)];
}

function globalMatches(globalTokens, hex, role) {
  return globalTokens
    .filter(token => token.name?.startsWith('tds-color-') && tokenHexes(token).includes(hex))
    .map(token => classForGlobal(token, role));
}

function themeMatches(themeTokens, hex, role, themePreset) {
  if (!themePreset) return [];
  const preset = themeTokens.find(item => item.name === themePreset);
  if (!preset) return [];
  return (preset.globalColor || [])
    .filter(token => tokenHexes(token).includes(hex))
    .map(token => classForGlobal(token, role));
}

function requiresThemePreset(themeTokens, hex) {
  return themeTokens.some(preset => (preset.globalColor || []).some(token => {
    const isThemeToken = token.name?.startsWith('tds-color-primary-') || token.name?.startsWith('tds-color-secondary-');
    return isThemeToken && tokenHexes(token).includes(hex);
  }));
}

async function ensureTokens() {
  const dir = cacheDir();
  const needed = ['theme.json', 'global.json', 'alias.json'].map(file => join(dir, file));
  if (needed.every(existsSync)) return dir;
  if (process.env.TDS_TOKEN_LOOKUP_OFFLINE === '1') return dir;
  await sync();
  return dir;
}

async function lookup(argv) {
  const [rawHex, role, rawProject = process.env.TDS_PROJECT || '', rawThemePreset = 'default', rawMode = process.env.TDS_MODE || 'light'] = argv;
  if (!rawHex || !role || rawHex === '-h' || rawHex === '--help') {
    return { help: usage(), exitCode: rawHex ? 0 : 2 };
  }

  const hex = normalizeHex(rawHex);
  const mode = rawMode || 'light';
  const tokenDir = await ensureTokens();
  const themeTokens = readJson(join(tokenDir, 'theme.json'), []);
  const globalTokens = readJson(join(tokenDir, 'global.json'), []);
  const aliasTokens = readJson(join(tokenDir, 'alias.json'), []);
  const presets = new Set(Array.isArray(themeTokens) ? themeTokens.map(item => item.name).filter(Boolean) : []);
  const project = presets.has(rawProject) && (!rawThemePreset || rawThemePreset === 'default') ? '' : (rawProject || '');
  const themePresetArg = presets.has(rawProject) && (!rawThemePreset || rawThemePreset === 'default') ? rawProject : rawThemePreset;
  const projectMap = loadProjectMap();
  const themePreset = projectThemePreset(projectMap.data, project, themePresetArg, presets);
  if (themePreset && themePreset !== 'other' && themePreset !== 'none' && !presets.has(themePreset)) {
    return {
      tokenCacheDir: tokenDir,
      projectSource: projectMap.file,
      project,
      themePreset,
      mode,
      hex,
      role,
      source: 'themeTokens',
      matches: [],
      status: 'missing',
      reason: 'unsupportedThemePreset',
      supportedThemePresets: [...presets],
      message: 'This themePreset is not supported by the current remote theme.json. Sync tokens and choose one of supportedThemePresets.'
    };
  }

  const projectResult = projectMatches(projectMap.data, hex, role, project, 'default', mode);
  if (!projectResult.length && (!themePreset || themePreset === 'other' || themePreset === 'none') && requiresThemePreset(themeTokens, hex)) {
    return {
      tokenCacheDir: tokenDir,
      projectSource: projectMap.file,
      project,
      themePreset,
      mode,
      hex,
      role,
      source: 'themeTokens',
      matches: [],
      status: 'missing',
      reason: 'themePresetRequired',
      message: 'This hex appears in TDS primary/secondary theme tokens. Ask the user for the project themePreset before mapping it.'
    };
  }

  const themeResult = projectResult.length ? [] : themeMatches(themeTokens, hex, role, themePreset);
  const aliasResult = projectResult.length || themeResult.length ? [] : aliasMatches(aliasTokens, globalTokens, hex, role);
  const globalResult = projectResult.length || themeResult.length || aliasResult.length ? [] : globalMatches(globalTokens, hex, role);
  const matches = projectResult.length ? projectResult : themeResult.length ? themeResult : aliasResult.length ? aliasResult : globalResult;
  const source = projectResult.length ? 'projectMap' : themeResult.length ? 'themeTokens' : aliasResult.length ? 'aliasTokens' : globalResult.length ? 'globalTokens' : 'none';

  return {
    tokenCacheDir: tokenDir,
    projectSource: projectMap.file,
    project,
    themePreset,
    mode,
    hex,
    role,
    source,
    matches: [...new Set(matches)],
    status: matches.length === 1 ? 'exact' : matches.length > 1 ? 'ambiguous' : 'missing'
  };
}

if (require.main === module) {
  lookup(process.argv.slice(2))
    .then(result => {
      if (result.help) {
        const stream = result.exitCode === 0 ? process.stdout : process.stderr;
        stream.write(result.help);
        process.exit(result.exitCode);
      }
      process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    })
    .catch(error => {
      process.stderr.write(`${error.message}\n`);
      process.exit(1);
    });
}

module.exports = { lookup };
