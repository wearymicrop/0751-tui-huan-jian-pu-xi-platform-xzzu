const stateLabels = {mounted:'在装', stock:'库存', returned:'退回', disputed:'争议'};
const actionLabels = {mount:'装入', detach:'拆出', return:'退回', restock:'复入库'};

function elem(tag, text, className) {
  const result = document.createElement(tag);
  if (text !== undefined) result.textContent = text;
  if (className) result.className = className;
  return result;
}

function serialButton(serial, className) {
  const button = elem('button', serial, className);
  button.type = 'button';
  button.dataset.serial = serial;
  return button;
}

function compactTime(value) {
  return value ? value.replace('.000000Z', 'Z').replace('T00:00:00Z', '').replace('T', ' ').replace(/Z$/, '') : '未拆出';
}

async function api(path, payload) {
  const options = payload === undefined ? {} : {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)};
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || '请求未成功');
  return data;
}

function feedback(message, error = false) {
  const status = document.querySelector('#feedback');
  status.textContent = message;
  status.dataset.error = String(error);
}
