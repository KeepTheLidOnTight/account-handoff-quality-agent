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
const GREEN = '#BCEF59', WHITE = '#FFFFFF';
const bodyStyle = { typeface: 'Inter', fontSize: '18pt', color: WHITE };
const headerStyle = { typeface: 'Inter Medium', fontSize: '24pt', color: GREEN };
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
function owner(person) { return `${person.owner_name}\n${person.team}`; }
function itemText(items, ctx, sources) { return items?.length ? items.map(x => `${x.text}${ctx.refs(x.source_ids, sources)}`).join('\n') : 'None recorded.'; }
function actionText(a, ctx, sources) { return `${a.text}\n${a.owner}\nDue: ${a.due || 'Not confirmed'}. ${a.status.charAt(0).toUpperCase() + a.status.slice(1)}.${ctx.refs(a.source_ids, sources)}`; }
function actionTitle(a, i, accountName) {
  const prefix = accountName.split(/\s/)[0].toLowerCase() + '-';
  const words = (a.id.toLowerCase().startsWith(prefix) ? a.id.slice(prefix.length) : a.id).replace(/[-_]+/g, ' ');
  return words.length <= 30 && /[a-z]{3}/i.test(words) ? (words[0].toUpperCase() + words.slice(1)).replace(/\b(qbr|sso|api)\b/gi, token => token.toUpperCase()) : `Action ${i + 1}`;
}
function summarySources(event) {
  return [...new Set([...event.source_ids, ...['commitments','gaps','risks'].flatMap(k => (event.assessment[k] || []).flatMap(x => x.source_ids))])];
}
// Whole sections stay together. Exceptionally long text gets explicit
// continuation regions, split at sentence boundaries whenever possible.
function wrap(text, width = 49) {
  const lines = [];
  for (const paragraph of String(text).split('\n')) {
    if (!paragraph) { lines.push(''); continue; }
    let line = '';
    for (const token of paragraph.split(/\s+/)) {
      let word = token;
      if (word.length > width) {
        if (line) { lines.push(line); line = ''; }
        while (word.length > width) { lines.push(word.slice(0, width)); word = word.slice(width); }
      }
      if (line && line.length + word.length + 1 > width) { lines.push(line); line = word; }
      else line = line ? `${line} ${word}` : word;
    }
    if (line) lines.push(line);
  }
  return lines;
}
function fragments(section) {
  const limit = section.title.length > 29 ? 4 : 5;
  if (wrap(section.body).length <= limit) return [section];
  const units = section.body.split(/(?<=[.!?])\s+(?!\[)|\n/).filter(Boolean);
  const chunks = []; let chunk = '';
  for (const unit of units) {
    const combined = chunk ? `${chunk}\n${unit}` : unit;
    if (chunk && wrap(combined).length > limit) { chunks.push(chunk); chunk = unit; }
    else chunk = combined;
    // Very long single statements cannot fit one region. Keep all words and
    // label the continuation rather than silently truncating the statement.
    if (wrap(chunk).length > limit) {
      const lines = wrap(chunk);
      while (lines.length > limit) chunks.push(lines.splice(0, limit).join('\n'));
      chunk = lines.join('\n');
    }
  }
  if (chunk) chunks.push(chunk);
  return chunks.map((body, i) => ({ title: `${section.title}${i ? ' (cont.)' : ''}`, body }));
}
const paragraph = (runs, extra = {}) => ({ runs, bulletCharacter: '', marginLeft: 0, indent: 0, spaceBefore: 0, spaceAfter: 0, ...extra });
function setText(shape, content, options = {}) {
  shape.text.style = { typeface: 'Inter', fontSize: 24, color: WHITE, lineSpacing: 1, alignment: 'left', verticalAlignment: 'top', autoFit: 'none', insets: { top: 0, left: 0, right: 0, bottom: 0 }, ...options };
  shape.text = typeof content === 'string' ? content.split('\n').map(line => paragraph([{run: line}])) : content;
}
function setCell(shape, section) {
  setText(shape, [
    paragraph([{ run: section.title, textStyle: headerStyle }], { spaceAfter: 350 }),
    ...section.body.split('\n').map(line => paragraph([{ run: line, textStyle: bodyStyle }]))
  ]);
}
function byId(slide, id) {
  const shape = slide.shapes.items.find(s => s.id === id);
  if (!shape) throw new Error(`Template shape ${id} is missing; restore assets/project-kickoff.pptx.`);
  return shape;
}
async function main() {
  const options = args(process.argv.slice(2));
  const view = historyView(options['--history']);
  if (view.schema_version !== 1 || !Array.isArray(view.events) || !view.events.length || !view.current) throw new Error('The validated history must contain at least one handoff event.');
  const { PresentationFile, FileBlob } = await artifactTool();
  const presentation = await PresentationFile.importPptx(await FileBlob.load(path.join(projectDir, 'assets/project-kickoff.pptx')));
  const originals = [...presentation.slides.items];
  if (originals.length !== 12) throw new Error('Unexpected Project Kickoff template; restore assets/project-kickoff.pptx.');
  const gridTemplate = originals[4], overviewTemplate = originals[5];
  const produced = [];
  function finish(slide, title, note, templateKind = 'grid', footer = 'Current account view') {
    const titleId = templateKind === 'overview' ? '533' : '3';
    const numberId = templateKind === 'overview' ? '532' : '2';
    const footerId = templateKind === 'overview' ? '4' : '6';
    setText(byId(slide, titleId), title, { typeface: 'Inter Medium', fontSize: 38.67 });
    setText(byId(slide, numberId), String(produced.length + 1), { fontSize: 13.33, alignment: 'right', verticalAlignment: 'bottom' });
    setText(byId(slide, footerId), '');
    // A regular text object keeps the policy visible even in viewers that hide
    // inherited footer placeholders. Its position follows the source footer.
    const foot = slide.shapes.add({ geometry: 'textbox', name: 'Baton policy footer', position: { left: 41.33, top: 659.31, width: 1090, height: 25.33 }, fill: 'none', line: { fill: 'none', width: 0 } });
    setText(foot, `Baton / ${footer}${options['--demo'] ? ' / Simulated example' : ''}`, { fontSize: 13.33, verticalAlignment: 'bottom' });
    slide.speakerNotes.textFrame.setText(note);
    produced.push(slide);
    return slide;
  }
  function gridPages(title, sections, notes, footer) {
    const regions = sections.flatMap(s => fragments(s));
    for (let i = 0; i < regions.length; i += 4) {
      const slide = gridTemplate.duplicate();
      const cells = ['10', '11', '4', '5'].map(id => byId(slide, id));
      for (let j = 0; j < 4; j++) {
        const section = regions[i + j];
        if (section) setCell(cells[j], section); else setText(cells[j], '');
      }
      finish(slide, `${title}${i ? ` (continued ${Math.floor(i / 4) + 1})` : ''}`, notes, 'grid', footer);
    }
  }
  const last = view.events.at(-1);
  const currentCtx = context(last.sources);
  const currentNotes = `Current overview derived from validated stored history. As of ${view.current.as_of}. This is not live CRM data.\nAccount: ${view.account.name} (${view.account.id})\nLatest handoff: ${view.current.latest_handoff_id}\n\n${currentCtx.notes}`;
  const overview = overviewTemplate.duplicate();
  setText(byId(overview, '534'), `${view.current.readiness}\nAs of ${view.current.as_of.slice(0, 10)}`, { fontSize: 32 });
  const summaryLines = wrap(last.assessment.summary + currentCtx.refs(summarySources(last)), 42);
  setText(byId(overview, '12'), summaryLines.slice(0, 7).join('\n'), { fontSize: 22.67 });
  setCell(byId(overview, '6'), { title: 'Current owner', body: owner(view.current.owner) });
  setCell(byId(overview, '8'), { title: 'Latest handoff', body: `${last.from.team} to ${last.to.team}\n${last.effective_at.slice(0,10)}${currentCtx.refs(last.source_ids)}` });
  finish(overview, `${view.account.name}\nCurrent account overview`, currentNotes, 'overview');
  if (summaryLines.length > 7) gridPages('Current assessment (continued)', [{title:'Assessment summary',body:summaryLines.slice(7).join('\n')}], currentNotes);
  gridPages('Current customer context', [
    { title: 'Customer goals', body: itemText(last.assessment.goals, currentCtx, last.sources) },
    { title: 'Stakeholders', body: itemText(last.assessment.stakeholders, currentCtx, last.sources) }
  ], currentNotes);
  const openActions = view.current.open_actions || [];
  const actionCtx = context(openActions.flatMap(a => a.sources));
  const actionNotes = `Outstanding actions as of ${view.current.as_of}. These are the most recent recorded action states across every stored handoff. An action stays open until a later event explicitly changes its status.\n\n${openActions.map(a => `Action ${a.id}\nOriginating handoff: ${a.event_id}\nLast update: ${a.updated_event_id}\n${a.text}`).join('\n\n')}\n\n${actionCtx.notes}`;
  gridPages(`Outstanding actions as of ${view.current.as_of.slice(0,10)}`, openActions.length ? openActions.map((a, i) => ({ title: actionTitle(a, i, view.account.name), body: actionText(a, actionCtx, a.sources) })) : [{title:'No open actions',body:'The stored history contains no outstanding actions.'}], actionNotes);
  for (const event of view.events) {
    const date = event.effective_at.slice(0, 10);
    const ctx = context(event.sources);
    const policy = event.handoff_type === 'sales_to_implementation' ? 'Sales handoff policy' : 'Internal transfer policy';
    const historyFooter = `${policy} / Historical snapshot`;
    const note = `Historical snapshot: ${event.handoff_id}\nEffective: ${event.effective_at}\nRecorded: ${event.recorded_at}\nType: ${event.handoff_type}\nPolicy: ${policy}. Sales baseline checks structured prerequisites; internal transfers use a separate receiving-team assessment.\nThese statements and action statuses describe the handoff at this point in time. Later events do not change this snapshot.\n\n${ctx.notes}`;
    gridPages(`${date} handoff: ${event.from.team} to ${event.to.team}`, [
      { title: 'Ownership transfer', body: `${event.from.owner_name} (${event.from.team}) to ${event.to.owner_name} (${event.to.team}).\n${event.reason}${ctx.refs(event.source_ids)}` },
      { title: `Readiness: ${event.assessment.readiness}`, body: `${event.assessment.baseline && event.assessment.baseline !== event.assessment.readiness ? `Structured baseline: ${event.assessment.baseline}.\n` : ''}${event.assessment.summary}${ctx.refs(summarySources(event))}` },
      { title: 'Customer goals', body: itemText(event.assessment.goals, ctx, event.sources) },
      { title: 'Stakeholders', body: itemText(event.assessment.stakeholders, ctx, event.sources) }
    ], note, historyFooter);
    gridPages(`${date} commitments and follow-up`, [
      { title: 'Commitments', body: itemText(event.assessment.commitments, ctx, event.sources) },
      { title: 'Gaps', body: itemText(event.assessment.gaps, ctx, event.sources) },
      { title: 'Risks', body: itemText(event.assessment.risks, ctx, event.sources) },
      ...(event.actions?.length ? event.actions.map((a, i) => ({ title: actionTitle(a, i, view.account.name), body: actionText(a, ctx, event.sources) })) : [{title:'Actions at handoff',body:'None recorded.'}])
    ], note, historyFooter);
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
