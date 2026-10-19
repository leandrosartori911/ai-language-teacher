// Chat with the AI teacher: the side panel about one item (spec 028) and the
// Teacher page (spec 034), which has no close button and is always shown.
// Without JavaScript the ask forms still post to the ask page.
(() => {
  const chat = document.getElementById("chat");
  if (!chat) return;

  const KEY = chat.dataset.key || "teacher-chat";
  const MAX_MESSAGES = 12; // the last 6 exchanges
  const list = chat.querySelector(".messages");
  const input = chat.querySelector("#chat-input");
  const close = chat.querySelector(".chat-close");
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

  // On wide screens the panel opens below the sticky header (spec 031).
  const header = document.querySelector("header");
  function fitBelowHeader() {
    document.documentElement.style.setProperty("--header-height", `${header.offsetHeight}px`);
  }
  addEventListener("resize", fitBelowHeader);

  function show(open, focus = true) {
    if (!close) return; // the Teacher page is always open
    fitBelowHeader();
    chat.hidden = !open;
    write(`${KEY}-open`, open);
    // Closing goes back to the ask form, which reopens the panel.
    if (focus) (open ? input : document.querySelector("form.ask input[name=question]"))?.focus();
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
  fitBelowHeader();
  if (close) {
    close.addEventListener("click", () => show(false));
    chat.addEventListener("keydown", (event) => {
      if (event.key === "Escape") show(false);
    });
  } else {
    chat.hidden = false;
  }
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
