// Chat with the AI teacher (spec 028). Without JavaScript the ask forms on the
// page still post to the ask page, so this script only builds on them.
(() => {
  const chat = document.getElementById("chat");
  if (!chat) return;

  const KEY = "teacher-chat";
  const MAX_MESSAGES = 12; // the last 6 exchanges
  const list = chat.querySelector(".messages");
  const input = chat.querySelector("#chat-input");
  const toggle = document.querySelector(".chat-toggle");
  let busy = false;

  // sessionStorage keeps the chat while moving between items in this tab. It
  // can be blocked (private windows), so the chat must work without it.
  function read(key, fallback) {
    try {
      return JSON.parse(sessionStorage.getItem(key)) ?? fallback;
    } catch {
      return fallback;
    }
  }
  function write(key, value) {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Not stored: the chat still works on this page.
    }
  }

  let history = read(KEY, []);

  function bubble(role, text) {
    const li = document.createElement("li");
    li.className = role;
    li.textContent = text;
    list.append(li);
    list.scrollTop = list.scrollHeight;
    return li;
  }

  function show(open, focus = true) {
    chat.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    write(`${KEY}-open`, open);
    if (focus) (open ? input : toggle).focus();
  }

  async function send(text) {
    text = text.trim();
    if (!text || busy) return;
    busy = true;
    show(true);
    bubble("user", text);
    const reply = bubble("assistant pending", "…");
    list.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(chat.dataset.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item: chat.dataset.item, message: text, history }),
      });
      if (response.redirected) {
        location.href = response.url; // the profile was closed in another tab
        return;
      }
      if (response.status === 422) {
        history = [];
        write(KEY, history);
        reply.textContent = "The saved chat was damaged and has been cleared. Please ask again.";
        reply.className = "assistant error";
        return;
      }
      // The server sends the answer one checked sentence at a time.
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let answer = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        answer += decoder.decode(value, { stream: true });
        reply.textContent = answer;
        list.scrollTop = list.scrollHeight;
      }
      reply.className = response.ok ? "assistant" : "assistant error";
      if (response.ok) {
        history = [...history, { role: "user", content: text }, { role: "assistant", content: answer }];
        history = history.slice(-MAX_MESSAGES);
        write(KEY, history);
      }
    } catch {
      reply.textContent = "Could not reach the app. Is it still running?";
      reply.className = "assistant error";
    } finally {
      list.setAttribute("aria-busy", "false");
      busy = false;
    }
  }

  for (const message of history) bubble(message.role, message.content);
  toggle.hidden = false;
  toggle.addEventListener("click", () => show(chat.hidden));
  chat.querySelector(".chat-close").addEventListener("click", () => show(false));
  chat.addEventListener("keydown", (event) => {
    if (event.key === "Escape") show(false);
  });
  chat.querySelector(".chat-form").addEventListener("submit", (event) => {
    event.preventDefault();
    send(input.value);
    input.value = "";
  });
  // The teaching card's ask form and "Explain my mistake" open the chat.
  for (const form of document.querySelectorAll("form.ask, form.explain")) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const question = form.elements.question;
      send(question.value);
      if (question.type !== "hidden") question.value = "";
    });
  }
  if (read(`${KEY}-open`, false)) show(true, false);
})();
