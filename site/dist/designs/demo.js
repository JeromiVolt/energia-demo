'use strict';
// Browser-only model. No device, wallet, network request or financial operation.
let receiving = false;
let received = 0;
let eth = 0;
let tick = null;
const receive = document.querySelector('#receive');
const reset = document.querySelector('#reset');
const status = document.querySelector('#receive-status');
const balance = document.querySelector('#balance');
const meter = document.querySelector('#meter');
const amount = document.querySelector('#amount');
const quote = document.querySelector('#quote');
const exchangeStatus = document.querySelector('#exchange-status');
const exchanged = document.querySelector('#exchanged');
function render() {
 balance.textContent = received.toFixed(0);
 meter.style.width = `${received}%`;
 exchanged.textContent = `${eth.toFixed(3)} DEMO-ETH`;
}
receive.addEventListener('click', () => {
 if (receiving) return;
 receiving = true;
 receive.disabled = true;
 let steps = 0;
 status.textContent = 'Симуляция: Type 1 → Type 2 → Type 3 → JeromiPAD.';
 tick = setInterval(() => {
  steps += 1;
  received = Math.min(100, received + 5);
  render();
  if (steps >= 6 || received >= 100) {
   clearInterval(tick); receiving = false; receive.disabled = false;
   status.textContent = 'Тестовый приём завершён. Это программные единицы без денежной стоимости.';
  }
 }, 500);
});
reset.addEventListener('click', () => {
 clearInterval(tick); receiving = false; received = 0; eth = 0;
 receive.disabled = false; render();
 status.textContent = 'Симуляция сброшена.';
 exchangeStatus.textContent = 'Реальные кошельки не подключены.';
});
function updateQuote() {
 const v = amount.valueAsNumber;
 const valid = Number.isFinite(v) && v > 0 && v <= 100;
 amount.setAttribute('aria-invalid', String(!valid));
 quote.value = valid ? `${(v * .001).toFixed(3)} DEMO-ETH` : 'Введите от 1 до 100';
}
amount.addEventListener('input', updateQuote);
document.querySelector('#exchange').addEventListener('click', () => {
 const v = amount.valueAsNumber;
 if (!Number.isFinite(v) || v <= 0 || v > 100) {
  exchangeStatus.textContent = 'Укажите от 1 до 100 тестовых Jeromi.'; return;
 }
 if (v > received) {
  exchangeStatus.textContent = 'Недостаточно тестовых единиц. Сначала запустите демонстрационный приём.'; return;
 }
 received -= v; eth += v * .001; render();
 exchangeStatus.textContent = 'Запись изменена только в памяти страницы. ETH не отправлен; реальный обмен отсутствует.';
});
render(); updateQuote();
