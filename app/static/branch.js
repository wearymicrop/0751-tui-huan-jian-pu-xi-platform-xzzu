function renderBranch(result) {
  const board = document.querySelector('#branches');
  const groups = new Map();
  for (const row of result.paths) {
    if (!groups.has(row.origin)) groups.set(row.origin, []);
    groups.get(row.origin).push(row);
  }
  board.replaceChildren();
  for (const [origin, paths] of groups) {
    const branch = elem('div', undefined, 'branch');
    const list = elem('ul', undefined, 'paths');
    for (const record of paths) {
      const path = elem('li', undefined, 'path');
      record.path.slice(1).forEach((serial, index) => {
        if (index) path.append(elem('span', undefined, 'connector'));
        path.append(serialButton(serial, 'node'));
      });
      path.append(elem('span', `${compactTime(record.start)} → ${compactTime(record.end)}`, 'window'));
      list.append(path);
    }
    branch.append(serialButton(origin, 'origin'), list);
    board.append(branch);
  }
  if (!groups.size) board.append(elem('p', '所选时间无装配暴露。', 'empty'));
  document.querySelector('#branch-summary').textContent = `${result.count} 件受影响 · ${result.paths.length} 条证据`;
  document.querySelector('#recall-window').textContent = `${result.batch} · [${compactTime(result.start)}, ${compactTime(result.end)}) UTC`;
}
