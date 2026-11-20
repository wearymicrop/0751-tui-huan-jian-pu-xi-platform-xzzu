function renderReport(result) {
  const table = document.querySelector('#report-table');
  const columns = [...table.querySelectorAll('th')].map(cell => cell.dataset.field);
  const records = Object.values(result[table.dataset.key]);
  const body = table.tBodies[0];
  body.replaceChildren();
  for (const record of records) {
    const row = body.insertRow();
    for (const field of columns) {
      const cell = row.insertCell();
      const value = record[field];
      if (['serial','child','parent','active_parent'].includes(field) && value) {
        cell.append(serialButton(value));
      } else if (['at','start','end','registered'].includes(field)) {
        cell.textContent = compactTime(value);
      } else {
        cell.textContent = stateLabels[value] || actionLabels[value] || (Array.isArray(value) ? value.join('、') : value ?? '—');
        if (typeof value === 'number') cell.className = 'num';
      }
    }
  }
  document.querySelector('#report-count').textContent = `${records.length} 条`;
  const notes = document.querySelector('#report-notes');
  notes.replaceChildren();
  if (result.aliases) {
    notes.append(elem('h3', '别名映射'));
    for (const [alias, serial] of Object.entries(result.aliases)) notes.append(elem('div', `${alias} → ${serial}`));
  }
  if (result.issues) {
    notes.append(elem('h3', `隔离记录 · ${result.issues.length}`));
    const list = elem('ul');
    for (const issue of result.issues) list.append(elem('li', `第 ${issue.row} 行 · ${issue.serial || issue.alias || issue.child || '—'} · ${issue.message}`));
    notes.append(list);
  }
  if (result.status) notes.append(elem('h3', `数量${result.difference === 0 ? '已对平' : '有差异'} · ${result.difference} 件差额`));
}
