function renderSerial(data) {
  const target = document.querySelector('#serial-result');
  target.replaceChildren(elem('h3', data.part.serial), elem('p', `${data.part.kind} · ${data.part.batch}`));
  if (data.position) target.append(elem('p', `${stateLabels[data.position.state]}${data.position.active_parent ? ` · ${data.position.active_parent}` : ''}`));
  const evidence = [
    ['拆装记录', data.edges.map(e => `${e.child} → ${e.parent} · ${compactTime(e.start)} 至 ${compactTime(e.end)} · 行 ${e.mount_row}`)],
    ['召回路径', data.exposures.map(e => `${e.path.join(' → ')} · 行 ${e.mount_rows.join(' / ')}`)],
    ['关联异常', data.issues.map(e => `${e.message} · 行 ${e.row}`)],
  ];
  for (const [label, records] of evidence) {
    target.append(elem('h4', `${label} · ${records.length}`));
    const list = elem('ul');
    for (const line of records) list.append(elem('li', line));
    if (records.length) target.append(list);
  }
}
