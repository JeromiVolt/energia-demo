'use strict';
// Local illustrative controls. No network calls, wallet APIs or persisted data.
const startButton = document.getElementById('meditate');
const resetButton = document.getElementById('reset');
const timer = document.getElementById('timer');
const status = document.getElementById('timer-status');
let deadline = 0;
let interval = null;
function stopTimer() {
  clearInterval(interval);
  interval = null;
  startButton.disabled = false;
}
function updateTimer() {
  const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  timer.textContent = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;
  if (remaining === 0) {
    stopTimer();
    status.textContent = 'Практика завершена. Никакие средства или награды не начислены.';
  }
}
startButton.addEventListener('click', () => {
  deadline = Date.now() + 60000;
  startButton.disabled = true;
  status.textContent = 'Идёт демонстрационный отсчёт времени.';
  interval = setInterval(updateTimer, 250);
  updateTimer();
});
resetButton.addEventListener('click', () => {
  stopTimer();
  timer.textContent = '01:00';
  status.textContent = 'Таймер сброшен.';
});
const amount = document.getElementById('amount');
const output = document.getElementById('exchange-output');
amount.addEventListener('input', () => {
  const value = amount.valueAsNumber;
  const valid = Number.isFinite(value) && value >= 0 && value <= 1000000;
  amount.setAttribute('aria-invalid', String(!valid));
  output.value = valid ? `${(value * 0.001).toFixed(6)} DEMO-ETH` : 'Введите число от 0 до 1 000 000';
});
