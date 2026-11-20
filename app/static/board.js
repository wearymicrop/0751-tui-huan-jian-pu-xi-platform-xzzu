const section = document.body.dataset.section;
const selector = document.querySelector('#sample');
const batch = document.querySelector('#batch');
const startInput = document.querySelector('#start');
const endInput = document.querySelector('#end');
const filters = document.querySelector('#filters');
const initial = new URLSearchParams(location.search);
let archiveId = initial.get('run');
let activeQuery;
let loadVersion = 0;
let serialVersion = 0;

function queryParams() {
  const params = new URLSearchParams({sample:selector.value === 'archive' ? 'dirty' : selector.value, batch:batch.value});
  if (startInput.value) params.set('start', `${startInput.value}T00:00:00Z`);
  if (endInput.value) params.set('end', `${endInput.value}T00:00:00Z`);
  if (archiveId) params.set('run', archiveId);
  return params;
}

function renderMetrics(balance, recall) {
  const metrics = [['台账件数', balance.population], ...(recall ? [['暴露件',recall.count],['证据路径',recall.paths.length],['争议件',balance.totals.disputed],['数量差额',balance.difference]] : Object.entries(balance.totals).map(([key,value]) => [stateLabels[key],value]))];
  document.querySelector('#metrics').replaceChildren(...metrics.map(([label,value]) => {
    const cell = elem('div', undefined, 'kpi');
    cell.append(elem('span', label), elem('strong', value));
    return cell;
  }));
}

function updateLinks(params) {
  for (const link of document.querySelectorAll('nav a')) {
    const url = new URL(link.href);
    url.search = params.toString();
    link.href = url.href;
  }
}

async function refresh() {
  const version = ++loadVersion;
  const params = queryParams();
  feedback('正在计算…');
  try {
    let balance, report, catalog, recall;
    if (archiveId) {
      const saved = await api(`/api/runs/${encodeURIComponent(archiveId)}`);
      if (version !== loadVersion) return;
      batch.value = saved.query.batch;
      startInput.value = saved.query.start.slice(0, 10);
      endInput.value = saved.query.end.slice(0, 10);
      ({balance,catalog,recall} = saved.result);
      report = saved.result[section];
    } else {
      const reportCall = ['recall','balance','catalog','evidence'].includes(section) ? null : api(`/api/${section}?${params}`);
      [balance,catalog,recall,report] = await Promise.all([
        api(`/api/balance?${params}`), api(`/api/catalog?${params}`), api(`/api/recall?${params}`), reportCall,
      ]);
      if (version !== loadVersion) return;
      report = report || ({balance,catalog})[section];
    }
    if (section === 'recall') renderBranch(recall);
    else if (section === 'evidence') await renderArchive();
    else renderReport(report);
    if (version !== loadVersion) return;
    activeQuery = params;
    serialVersion++;
    document.querySelector('#serial-result').replaceChildren(elem('p', '选择节点或输入序列号。', 'empty'));
    renderMetrics(balance, section === 'recall' ? recall : null);
    document.querySelector('#snapshot').textContent = `盘点至 ${compactTime(balance.as_of)} UTC`;
    document.querySelector('#lots').replaceChildren(...[...new Set(Object.values(catalog.parts).map(p => p.batch))].sort().map(value => {
      const option = elem('option'); option.value = value; return option;
    }));
    updateLinks(params);
    feedback('计算完成');
  } catch (error) { if (version === loadVersion) feedback(error.message, true); }
}

async function lookup(serial) {
  const version = ++serialVersion;
  const target = document.querySelector('#serial-result');
  document.querySelector('#serial-input').value = serial;
  target.replaceChildren(elem('p', '正在读取证据…', 'empty'));
  try {
    const data = await api(`/api/evidence/${encodeURIComponent(serial)}?${activeQuery || queryParams()}`);
    if (version === serialVersion) renderSerial(data);
  } catch (error) {
    if (version === serialVersion) target.replaceChildren(elem('p', error.message, 'empty error'));
  }
}

function setArchiveMode() {
  if (archiveId) selector.value = 'archive';
  for (const field of [batch, startInput, endInput, document.querySelector('#save-run'), filters.querySelector('[type=submit]')]) field.disabled = Boolean(archiveId);
}

const start = initial.get('start');
const end = initial.get('end');
if (initial.has('batch')) batch.value = initial.get('batch');
if (start) startInput.value = start.slice(0, 10);
if (end) endInput.value = end.slice(0, 10);
setArchiveMode();
filters.addEventListener('submit', event => { event.preventDefault(); refresh(); });
selector.addEventListener('change', () => { archiveId = null; setArchiveMode(); refresh(); });
document.querySelector('#serial-form').addEventListener('submit', event => { event.preventDefault(); lookup(document.querySelector('#serial-input').value.trim()); });
document.addEventListener('click', event => { const serial = event.target.closest('[data-serial]'); if (serial) lookup(serial.dataset.serial); });

async function saveRun(payload) {
  if (startInput.value) payload.start = `${startInput.value}T00:00:00Z`;
  if (endInput.value) payload.end = `${endInput.value}T00:00:00Z`;
  const result = await api('/api/runs', payload);
  if (section === 'evidence') await renderArchive();
  feedback(result.reused ? '已存在相同归档' : '已保存追溯凭证');
}

document.querySelector('#save-run').addEventListener('click', async event => {
  const button = event.currentTarget;
  button.disabled = true;
  try { await saveRun({sample:selector.value, batch:batch.value}); }
  catch (error) { feedback(error.message, true); }
  finally { button.disabled = Boolean(archiveId); }
});

document.querySelector('#upload-form')?.addEventListener('submit', async event => {
  event.preventDefault();
  const file = document.querySelector('#upload-file').files[0];
  const button = event.currentTarget.querySelector('button');
  button.disabled = true;
  try {
    if (file.size > 5000000) throw new Error('源文件大小须在 5 MB 以内');
    let source;
    try { source = JSON.parse(await file.text()); }
    catch { throw new Error('源文件不是有效 JSON'); }
    await saveRun({source, batch:source?.default_batch || batch.value});
  } catch (error) { feedback(error.message, true); }
  finally { button.disabled = false; }
});
refresh();
