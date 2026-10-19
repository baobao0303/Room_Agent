#!/usr/bin/env node
const { existsSync, mkdirSync, readFileSync, writeFileSync } = require('node:fs');
const { dirname, join, resolve } = require('node:path');
const { cacheDir, sync } = require('./sync-tds-tokens');

const skillDir = resolve(__dirname, '..');

function usage() {
  return `Usage:
  node set-tds-theme-preset.js <themePreset> [project]
  node set-tds-theme-preset.js --list

Examples:
  node set-tds-theme-preset.js green
  node set-tds-theme-preset.js blue crm
`;
}

function readJson(file) {
  if (!existsSync(file)) return {};
  try {
    return JSON.parse(readFileSync(file, 'utf8'));
  } catch (error) {
    throw new Error(`${file} is not valid JSON: ${error.message}`);
  }
}

function ensureObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

async function loadThemePresets() {
  const themeFile = join(cacheDir(), 'theme.json');
  if (!existsSync(themeFile) && process.env.TDS_TOKEN_LOOKUP_OFFLINE !== '1') {
    await sync();
  }

  const themes = readJson(themeFile);
  if (!Array.isArray(themes)) {
    throw new Error(`Theme token file is not an array: ${themeFile}`);
  }
  return themes.map(theme => theme.name).filter(Boolean);
}

function legacyProject(project) {
  const candidates = [
    join(process.cwd(), '.claude', 'tds-project-token-map.json'),
    join(process.cwd(), '.codex', 'tds-project-token-map.json'),
  ];
  for (const candidate of candidates) {
    const data = readJson(candidate);
    const legacy = data?.projects?.[project];
    if (legacy && typeof legacy === 'object' && !Array.isArray(legacy)) {
      return structuredClone(legacy);
    }
  }
  return null;
}

function writeProjectTheme(file, project, themePreset, legacy) {
  const config = ensureObject(readJson(file));
  config.version = config.version || 1;
  config.projects = ensureObject(config.projects);
  if (!config.projects[project] && legacy) {
    config.projects[project] = legacy;
  }
  config.projects[project] = ensureObject(config.projects[project]);
  config.projects[project].themePreset = themePreset;
  config.projects[project].themes = ensureObject(config.projects[project].themes);
  config.projects[project].themes.default = ensureObject(config.projects[project].themes.default);
  config.projects[project].themes.default.modes = ensureObject(config.projects[project].themes.default.modes);
  config.projects[project].themes.default.modes.light = ensureObject(config.projects[project].themes.default.modes.light);
  config.projects[project].themes.default.modes.dark = ensureObject(config.projects[project].themes.default.modes.dark);

  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`);
}

async function main(argv) {
  const [themePreset, project = 'default'] = argv;
  if (!themePreset || themePreset === '-h' || themePreset === '--help') {
    process.stdout.write(usage());
    process.exit(themePreset ? 0 : 2);
  }

  const presets = await loadThemePresets();
  if (themePreset === '--list' || themePreset === 'list') {
    process.stdout.write(JSON.stringify({ status: 'ok', themePresets: presets }, null, 2) + '\n');
    return;
  }
  if (themePreset !== 'other' && themePreset !== 'none' && !presets.includes(themePreset)) {
    throw new Error(`Unsupported themePreset "${themePreset}". Supported presets from theme.json: ${presets.join(', ') || '(none)'} or "other"`);
  }

  const targets = [
    join(skillDir, 'references', 'config', 'tds-project-token-map.json'),
  ];
  const legacy = legacyProject(project);

  for (const target of targets) {
    writeProjectTheme(target, project, themePreset, legacy);
  }

  process.stdout.write(JSON.stringify({
    status: 'ok',
    project,
    themePreset,
    files: targets,
  }, null, 2) + '\n');
}

if (require.main === module) {
  main(process.argv.slice(2)).catch(error => {
    process.stderr.write(`${error.message}\n`);
    process.exit(1);
  });
}
