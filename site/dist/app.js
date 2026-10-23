(() => {
'use strict';
// Local illustrative controls. No network calls, wallet APIs or persisted data.
const startButton = document.getElementById('meditate');
const resetButton = document.getElementById('timer-reset');
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

})();
