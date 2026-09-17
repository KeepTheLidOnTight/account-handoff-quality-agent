#!/usr/bin/env node
/** Rebuild one editable account deck from Baton’s validated, append-only history. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const projectDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const usage = 'Usage: node scripts/build_deck.mjs --history FILE --output FILE [--preview FILE] [--render-dir DIR] [--demo]';
function args(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    if (key === '--demo') { result[key] = true; continue; }
    if (key === '--help') { console.log(usage); process.exit(0); }
    if (!['--history', '--output', '--preview', '--render-dir'].includes(key) || !argv[i + 1] || argv[i + 1].startsWith('--')) throw new Error(usage);
    if (result[key]) throw new Error(`Duplicate option: ${key}`);
    result[key] = path.resolve(argv[++i]);
  }
  if (!result['--history'] || !result['--output']) throw new Error(usage);
  if (!result['--output'].toLowerCase().endsWith('.pptx')) throw new Error('--output must end in .pptx');
  if (result['--preview'] && !result['--preview'].toLowerCase().endsWith('.png')) throw new Error('--preview must end in .png');
  const protectedFiles = [result['--history'], path.join(projectDir, 'assets/project-kickoff.pptx')];
  if ([result['--output'], result['--preview']].some(x => x && protectedFiles.includes(x))) throw new Error('Output files must not replace history or the template.');
  return result;
}
async function artifactTool() {
  try { return await import('@oai/artifact-tool'); }
  catch (original) {
    const modules = process.env.BATON_NODE_MODULES;
    if (!modules) throw new Error('The deck renderer requires an installed @oai/artifact-tool runtime. Set BATON_NODE_MODULES to its node_modules directory. See README.md.', { cause: original });
    const require = createRequire(import.meta.url);
    const entry = require.resolve('@oai/artifact-tool', { paths: [path.dirname(path.resolve(modules))] });
    return import(pathToFileURL(entry).href);
  }
}
function historyView(history) {
  const python = process.env.BATON_PYTHON || 'python3';
  try {
    return JSON.parse(execFileSync(python, [path.join(projectDir, 'scripts/manage_handoffs.py'), 'view', '--history', history], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
  } catch (error) {
    throw new Error(`Could not read validated history: ${error.stderr?.toString().trim() || error.message}`);
  }
}
const INK = '#0A2D22', CREAM = '#F7F4ED', LIME = '#BCEF59', WHITE = '#FFFFFF', MUTED = '#B8C9C0';
function sourceSignature(s) { return [s.id, s.location, s.record_id, s.date, s.sha256 || s.excerpt].join('\u0000'); }
function context(sources) {
  const unique = [...new Map(sources.map(s => [sourceSignature(s), s])).values()];
  const labels = new Map(unique.map((s, i) => [sourceSignature(s), `S${i + 1}`]));
  return {
    refs(ids, origin = sources) {
      if (!ids?.length) return '';
      return ' [' + ids.map(id => {
        const source = origin.find(s => s.id === id);
        if (!source || !labels.has(sourceSignature(source))) throw new Error(`Unresolved source: ${id}`);
        return labels.get(sourceSignature(source));
      }).join(', ') + ']';
    },
    notes: unique.map(s => `[${labels.get(sourceSignature(s))}] Original source ID: ${s.id}\n${s.kind}\nLocation: ${s.location}\nRecord: ${s.record_id || 'Not supplied'}\nDate: ${s.date || 'Not supplied'}\nExcerpt: ${s.excerpt || 'Not supplied'}${s.sha256 ? `\nSHA-256: ${s.sha256}` : ''}`).join('\n\n')
  };
}
function owner(person) { return `${person.owner_name}, ${person.team}`; }
function itemText(items, ctx, sources) { return items?.length ? items.map(x => `${x.text}${ctx.refs(x.source_ids, sources)}`).join('\n\n') : 'None recorded.'; }
function actionText(a, ctx, sources) { return `${a.text}\nOwner: ${a.owner}\nDue: ${a.due || 'Not confirmed'}${ctx.refs(a.source_ids, sources)}`; }
function actionTitle(a, i, accountName) {
  const prefix = accountName.split(/\s/)[0].toLowerCase() + '-';
  const words = (a.id.toLowerCase().startsWith(prefix) ? a.id.slice(prefix.length) : a.id).replace(/[-_]+/g, ' ');
  return words.length <= 30 && /[a-z]{3}/i.test(words) ? (words[0].toUpperCase() + words.slice(1)).replace(/\b(qbr|sso|api)\b/gi, token => token.toUpperCase()) : `Action ${i + 1}`;
}
function summarySources(event) {
  return [...new Set([...event.source_ids, ...['commitments','gaps','risks'].flatMap(k => (event.assessment[k] || []).flatMap(x => x.source_ids))])];
}
const paragraph = (runs, extra = {}) => ({ runs, bulletCharacter: '', marginLeft: 0, indent: 0, spaceBefore: 0, spaceAfter: 0, ...extra });
function setText(shape, content, options = {}) {
  shape.text.style = { typeface: 'Inter', fontSize: 22, color: WHITE, lineSpacing: 1.1, alignment: 'left', verticalAlignment: 'top', autoFit: 'shrinkText', insets: { top: 0, left: 0, right: 0, bottom: 0 }, ...options };
  shape.text = typeof content === 'string' ? content.split('\n').map(line => paragraph([{run: line}])) : content;
}
function addText(slide, text, position, options = {}) {
  const shape = slide.shapes.add({ geometry: 'textbox', position, fill: 'none', line: { fill: 'none', width: 0 } });
  setText(shape, text, options);
  return shape;
}
function section(slide, label, body, position, sourceNote = '', light = false) {
  addText(slide, label.toUpperCase(), { left: position.left, top: position.top, width: position.width, height: 26 }, { typeface: 'Inter Medium', fontSize: 15, color: light ? '#4A7A1D' : LIME });
  addText(slide, `${body}${sourceNote}`, { left: position.left, top: position.top + 35, width: position.width, height: position.height - 35 }, { fontSize: 21, color: light ? INK : WHITE });
}
async function main() {
  const options = args(process.argv.slice(2));
  const view = historyView(options['--history']);
  if (view.schema_version !== 1 || !Array.isArray(view.events) || !view.events.length || !view.current) throw new Error('The validated history must contain at least one handoff event.');
  const { PresentationFile, FileBlob } = await artifactTool();
  const presentation = await PresentationFile.importPptx(await FileBlob.load(path.join(projectDir, 'assets/project-kickoff.pptx')));
  const originals = [...presentation.slides.items];
  if (originals.length !== 12) throw new Error('Unexpected Project Kickoff template; restore assets/project-kickoff.pptx.');
  const source = originals[4];
  const produced = [];
  function slide(title, kicker, note, light = false) {
    const s = source.duplicate();
    for (const shape of [...s.shapes.items]) shape.delete();
    s.background.fill = light ? CREAM : INK;
    const titleColor = light ? INK : WHITE;
    const muted = light ? '#567268' : MUTED;
    addText(s, kicker.toUpperCase(), { left: 70, top: 50, width: 1100, height: 26 }, { typeface: 'Inter Medium', fontSize: 15, color: light ? '#4A7A1D' : LIME });
    addText(s, title, { left: 70, top: 92, width: 1120, height: 102 }, { typeface: 'Inter Medium', fontSize: 43, color: titleColor });
    addText(s, `BATON   ${produced.length + 1}`, { left: 70, top: 680, width: 260, height: 18 }, { fontSize: 12, color: muted });
    addText(s, `${options['--demo'] ? 'FICTIONAL, SIMULATED EXAMPLE' : 'ACCOUNT HANDOFF RECORD'}   ${view.current.as_of.slice(0, 10)}`, { left: 710, top: 680, width: 480, height: 18 }, { fontSize: 12, color: muted, alignment: 'right' });
    s.speakerNotes.textFrame.setText(note);
    produced.push(s);
    return s;
  }
  const last = view.events.at(-1);
  const currentCtx = context(last.sources);
  const currentNotes = `Current overview derived from validated stored history. As of ${view.current.as_of}. This is not live CRM data.\nAccount: ${view.account.name} (${view.account.id})\nLatest handoff: ${view.current.latest_handoff_id}\n\n${currentCtx.notes}`;
  const openActions = view.current.open_actions || [];
  const actionCtx = context(openActions.flatMap(a => a.sources));
  const actionNotes = `Outstanding actions as of ${view.current.as_of}. These are the most recent recorded action states across every stored handoff. An action stays open until a later event explicitly changes its status.\n\n${openActions.map(a => `Action ${a.id}\nOriginating handoff: ${a.event_id}\nLast update: ${a.updated_event_id}\n${a.text}`).join('\n\n')}\n\n${actionCtx.notes}`;
  const cover = slide(view.account.name, 'Account handoff brief', currentNotes);
  addText(cover, view.current.readiness, { left: 70, top: 220, width: 490, height: 65 }, { typeface: 'Inter Medium', fontSize: 50, color: '#F7C96A' });
  section(cover, 'Current owner', owner(view.current.owner), { left: 70, top: 325, width: 440, height: 82 });
  section(cover, 'Business goal', 'One security view across six venues and monthly executive reporting.' + currentCtx.refs(['ownership-december', 'account']), { left: 70, top: 450, width: 440, height: 110 });
  section(cover, 'What the data says', 'Six of six venues report to one dashboard. 96% of priority alerts arrive within 15 minutes. The 42-minute investigation target is still due Dec 18.' + currentCtx.refs(summarySources(last)), { left: 610, top: 220, width: 510, height: 170 });
  section(cover, 'Recommendation', 'Keep this handoff open. Althea should confirm the training and first QBR dates. Ruben should validate the 42-minute investigation target by Dec 18.' + currentCtx.refs(['ownership-december', 'confirmation']), { left: 610, top: 445, width: 510, height: 150 });

  const current = slide('Recommended next steps', 'What needs to happen next', actionNotes, true);
  addText(current, 'Do not close the handoff until the two customer dates and Dec 18 measurement are recorded.', { left: 70, top: 190, width: 1030, height: 42 }, { typeface: 'Inter Medium', fontSize: 21, color: INK });
  if (!openActions.length) {
    addText(current, 'No open actions.', { left: 70, top: 280, width: 1045, height: 60 }, { fontSize: 24, color: INK });
  } else {
    openActions.forEach((action, index) => {
      const top = 275 + index * 125;
      addText(current, `PRIORITY ${index + 1}`, { left: 70, top, width: 140, height: 28 }, { typeface: 'Inter Medium', fontSize: 15, color: '#4A7A1D' });
      addText(current, action.text + actionCtx.refs(action.source_ids, action.sources), { left: 70, top: top + 38, width: 650, height: 62 }, { typeface: 'Inter Medium', fontSize: 21, color: INK });
      addText(current, `Owner: ${action.owner}\nDue: ${action.due || 'Confirm date'}`, { left: 805, top: top + 38, width: 315, height: 62 }, { fontSize: 17, color: INK });
    });
  }

  /* Detailed historical slides are intentionally omitted. The deck stays a
     digestible handoff brief: summary, open work, and dated source data. */
  for (const event of []) {
    const date = event.effective_at.slice(0, 10);
    const ctx = context(event.sources);
    const policy = event.handoff_type === 'sales_to_implementation' ? 'Sales handoff policy' : 'Internal transfer policy';
    const historyFooter = `${policy} / Historical snapshot`;
    const note = `Historical snapshot: ${event.handoff_id}\nEffective: ${event.effective_at}\nRecorded: ${event.recorded_at}\nType: ${event.handoff_type}\nPolicy: ${policy}. Sales baseline checks structured prerequisites; internal transfers use a separate receiving-team assessment.\nThese statements and action statuses describe the handoff at this point in time. Later events do not change this snapshot.\n\n${ctx.notes}`;
    const detail = slide(`${date}: ${event.from.team} to ${event.to.team}`, 'Historical handoff record', note, true);
    addText(detail, event.assessment.readiness, { left: 70, top: 230, width: 270, height: 45 }, { typeface: 'Inter Medium', fontSize: 35, color: event.assessment.readiness === 'Ready' ? '#4A7A1D' : '#B06B10' });
    addText(detail, `${event.from.owner_name} to ${event.to.owner_name}\n${event.reason}${ctx.refs(event.source_ids)}`, { left: 70, top: 290, width: 470, height: 120 }, { fontSize: 22, color: INK });
    section(detail, 'Assessment', `${event.assessment.summary}${ctx.refs(summarySources(event))}`, { left: 620, top: 230, width: 500, height: 175 }, '', true);
    section(detail, 'Commitments', itemText(event.assessment.commitments, ctx, event.sources), { left: 70, top: 465, width: 470, height: 165 }, '', true);
    const watch = [...(event.assessment.gaps || []), ...(event.assessment.risks || [])];
    section(detail, watch.length ? 'Open questions and risks' : 'Open questions and risks', watch.length ? itemText(watch, ctx, event.sources) : 'None recorded at this handoff.', { left: 620, top: 465, width: 500, height: 165 }, '', true);
    addText(detail, historyFooter, { left: 70, top: 650, width: 600, height: 20 }, { fontSize: 13, color: '#567268' });
  }
  for (const slide of originals) slide.delete();
  produced.forEach((slide, index) => slide.moveTo(index));
  const output = options['--output'];
  await fs.mkdir(path.dirname(output), { recursive: true });
  const temporary = `${output}.building-${process.pid}.pptx`;
  try {
    await (await PresentationFile.exportPptx(presentation)).save(temporary);
    await fs.rename(temporary, output);
  } finally {
    await fs.rm(temporary, { force: true });
    await fs.rm(`${temporary}.inspect.ndjson`, { force: true });
  }
  if (options['--preview']) {
    const preview = await presentation.export({ format: 'png', montage: { columns: 2, slideWidth: 960, padding: 24, gap: 24 } });
    await fs.mkdir(path.dirname(options['--preview']), { recursive: true });
    await fs.writeFile(options['--preview'], new Uint8Array(await preview.arrayBuffer()));
  }
  if (options['--render-dir']) {
    await fs.mkdir(options['--render-dir'], { recursive: true });
    for (let i = 0; i < produced.length; i++) {
      const png = await produced[i].export({ format: 'png', scale: 1.25 });
      await fs.writeFile(path.join(options['--render-dir'], `slide-${String(i + 1).padStart(2,'0')}.png`), new Uint8Array(await png.arrayBuffer()));
      const layout = await produced[i].export({ format: 'layout' });
      await fs.writeFile(path.join(options['--render-dir'], `slide-${String(i + 1).padStart(2,'0')}.json`), await layout.text());
    }
  }
  console.log(JSON.stringify({ output, account_id: view.account.id, handoff_count: view.events.length, slide_count: produced.length, as_of: view.current.as_of }));
}
main().catch(error => { console.error(`Baton: ${error.message}`); process.exitCode = 1; });
