#!/usr/bin/env node
const { existsSync, mkdirSync, readFileSync, writeFileSync } = require('node:fs');
const { dirname, join, resolve } = require('node:path');
const { homedir } = require('node:os');

const skillDir = resolve(__dirname, '..');
const sourcesFile = join(skillDir, 'references', 'config', 'tds-token-sources.json');

function cacheDir() {
  if (process.env.TDS_TOKEN_CACHE_DIR) return resolve(process.env.TDS_TOKEN_CACHE_DIR);
  if (process.env.XDG_CACHE_HOME) return join(process.env.XDG_CACHE_HOME, 'tds-ui-figma', 'tokens');
  if (process.env.LOCALAPPDATA) return join(process.env.LOCALAPPDATA, 'tds-ui-figma', 'tokens');
  return join(homedir(), '.cache', 'tds-ui-figma', 'tokens');
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

async function fetchJson(url) {
  const response = await fetch(url, { headers: { accept: 'application/json' } });
  if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText} for ${url}`);
  return response.json();
}

async function sync() {
  const sources = readJson(sourcesFile).sources;
  const outDir = cacheDir();
  mkdirSync(outDir, { recursive: true });

  const files = {
    themeTokens: 'theme.json',
    globalTokens: 'global.json',
    aliasTokens: 'alias.json'
  };

  const result = {};
  for (const [key, fileName] of Object.entries(files)) {
    const url = sources[key];
    if (!url) throw new Error(`Missing token source: ${key}`);
    const data = await fetchJson(url);
    const target = join(outDir, fileName);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, JSON.stringify(data, null, 2) + '\n');
    result[key] = { url, file: target };
  }

  writeFileSync(join(outDir, 'manifest.json'), JSON.stringify({
    version: 1,
    syncedAt: new Date().toISOString(),
    sources
  }, null, 2) + '\n');

  return result;
}

if (require.main === module) {
  sync()
    .then(result => {
      process.stdout.write(JSON.stringify({ status: 'ok', cacheDir: cacheDir(), files: result }, null, 2) + '\n');
    })
    .catch(error => {
      process.stderr.write(`${error.message}\n`);
      process.exit(1);
    });
}

module.exports = { cacheDir, sync };
