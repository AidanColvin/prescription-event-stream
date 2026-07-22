/* Shared helpers: payload loading, safe rendering, search behavior. */

/* Escapes text for safe interpolation into innerHTML. */
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

/* Escapes text, then wraps case-insensitive matches of query in <mark>. */
function highlight(value, query) {
  const safe = esc(value);
  if (!query) return safe;
  const pattern = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return safe.replace(new RegExp(`(${pattern})`, "ig"), "<mark>$1</mark>");
}

/* Fields the search box matches against, on every page. */
function matchesQuery(ev, query) {
  if (!query) return true;
  return [
    ev.patient, ev.medication, ev.brand, ev.dea_schedule, ev.indication,
    ev.prescriber, ev.interactions, ev.event_id, ev.sig,
  ].some((field) => (field || "").toLowerCase().includes(query));
}

/* Fetches the evaluated queue once. Returns {events, summary, stats}. */
async function loadPayload() {
  const response = await fetch("/api/events?count=100");
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  const payload = await response.json();
  if (!Array.isArray(payload.events)) throw new Error("Malformed payload");
  return payload;
}

/* Wires a search input: live input events plus "/" to focus, Esc to clear. */
function bindSearch(input, onChange) {
  input.addEventListener("input", () => onChange(input.value.toLowerCase().trim()));
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    } else if (e.key === "Escape" && document.activeElement === input) {
      input.value = "";
      onChange("");
      input.blur();
    }
  });
}

let toastTimer = null;
/* Shows a transient confirmation message. */
function showToast(message) {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = message;
  requestAnimationFrame(() => el.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
}

/* Renders the API-unreachable state into a container. */
function renderLoadError(container) {
  container.innerHTML =
    '<div class="error-banner">The event stream is unreachable right now. ' +
    "Refresh to try again.</div>";
}
