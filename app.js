const form = document.querySelector('#quest-form');
const status = document.querySelector('#status');
const result = document.querySelector('#result');
const button = document.querySelector('#generate');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  button.disabled = true;
  status.textContent = 'The local model is composing your card…';
  result.hidden = true;
  try {
    const data = Object.fromEntries(new FormData(form));
    data.minutes = Number(data.minutes);
    const response = await fetch('/api/quest', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
    });
    const quest = await response.json();
    if (!response.ok) throw new Error(quest.error || 'Could not make the card');
    document.querySelector('#quest-title').textContent = quest.title;
    document.querySelector('#quest-intro').textContent = quest.intro;
    document.querySelector('#quest-reflection').textContent = quest.reflection;
    const list = document.querySelector('#quest-steps');
    list.replaceChildren();
    for (const step of quest.steps) {
      const item = document.createElement('li');
      const duration = document.createElement('span');
      duration.className = 'duration';
      duration.textContent = `${step.minutes} MIN`;
      const action = document.createElement('p');
      action.textContent = step.action;
      const notice = document.createElement('small');
      notice.textContent = step.notice;
      item.append(duration, action, notice);
      list.append(item);
    }
    status.textContent = 'Ready. Read once, then close your screen.';
    result.hidden = false;
    result.scrollIntoView({behavior: 'smooth', block: 'start'});
  } catch (error) {
    status.textContent = `${error.message}. Start Ollama and pull the model shown in README.`;
  } finally {
    button.disabled = false;
  }
});

document.querySelector('#print').addEventListener('click', () => window.print());
