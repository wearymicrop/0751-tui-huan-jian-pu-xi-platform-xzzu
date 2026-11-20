async function renderArchive() {
  const data = await api('/api/runs');
  const list = document.querySelector('#archive-list');
  list.replaceChildren();
  document.querySelector('#archive-count').textContent = `${data.runs.length} 份`;
  if (!data.runs.length) list.append(elem('p', '暂无归档。', 'empty'));
  for (const run of data.runs) {
    const row = elem('div', undefined, 'archive-row');
    const detail = elem('a', `${run.batch} · ${run.id.slice(0, 12)}`);
    detail.href = `/board/recall?run=${encodeURIComponent(run.id)}`;
    const download = elem('a', '下载证据');
    download.href = `/api/runs/${encodeURIComponent(run.id)}/export`;
    const rerun = elem('button', '重跑归档');
    rerun.type = 'button';
    rerun.addEventListener('click', async () => {
      rerun.disabled = true;
      try {
        await api(`/api/runs/${encodeURIComponent(run.id)}/rerun`, {});
        feedback('重跑一致');
      } catch (error) { feedback(error.message, true); }
      finally { rerun.disabled = false; }
    });
    row.append(detail, elem('small', run.created), rerun, download);
    list.append(row);
  }
}
