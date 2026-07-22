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
    ev.approved_uses, ev.off_label, ev.drug_class, ev.mechanism,
  ].some((field) => (field || "").toLowerCase().includes(query));
}

/* Returns distinct medications whose generic or brand name matches the
   query — the signal that the user is asking about a drug, not a person. */
function matchingMedications(events, query) {
  if (!query || query.length < 3) return [];
  const seen = new Map();
  for (const ev of events) {
    const generic = (ev.medication || "").toLowerCase();
    const brand = (ev.brand || "").toLowerCase();
    const drugClass = (ev.drug_class || "").toLowerCase();
    if ((generic.includes(query) || brand.includes(query) || drugClass.includes(query))
        && !seen.has(ev.medication)) {
      seen.set(ev.medication, ev);
    }
  }
  return [...seen.values()].slice(0, 3);
}

/* Renders the medication information card shown when a search names a drug. */
function medInfoCard(ev, query) {
  const field = (label, value) => `
    <div><div class="detail-label">${label}</div>
    <div class="detail-value">${highlight(value, query)}</div></div>`;
  return `
    <div class="card medinfo">
      <div class="medinfo-head">
        <span class="medinfo-name">${highlight(ev.medication, query)}</span>
        <span class="med-brand">${highlight(ev.brand, query)} &middot; ${esc(ev.strength)} ${esc(ev.form)}</span>
        <span class="row-spacer"></span>
        <span class="chip chip-plain">${highlight(ev.drug_class, query)}</span>
        <span class="chip chip-plain">${esc(ev.dea_schedule)}</span>
      </div>
      <p class="medinfo-mechanism"><strong>How it works.</strong> ${highlight(ev.mechanism, query)}</p>
      <div class="detail-grid">
        ${field("Approved to treat", ev.approved_uses)}
        ${field("Common off-label uses", ev.off_label)}
        ${field("Common side effects", ev.side_effects)}
        ${field("Avoid mixing with", ev.interactions)}
        ${field("Not for people with", ev.contraindications)}
        ${field("How to store it", ev.storage)}
      </div>
      <div class="medinfo-source">Label source: ${esc(ev.source)}</div>
    </div>`;
}

/* Renders the "About this medication" section, or nothing. */
function medInfoSection(events, query) {
  const meds = matchingMedications(events, query);
  if (!meds.length) return "";
  return `
    <h2 class="section-title">About ${meds.length === 1 ? "this medication" : "these medications"}</h2>
    ${meds.map((m) => medInfoCard(m, query)).join("")}`;
}

/* Live lookup for drugs not in the family's data, via /api/drug
   (RxNorm + openFDA). Cached per query; debounced; re-renders on arrival. */
const externalCache = new Map();
let externalTimer = null;

function scheduleExternalLookup(query, rerender) {
  clearTimeout(externalTimer);
  externalTimer = setTimeout(async () => {
    try {
      const response = await fetch(`/api/drug?name=${encodeURIComponent(query)}`);
      const info = await response.json();
      externalCache.set(query, info.found ? info : null);
    } catch (err) {
      externalCache.set(query, null);
    }
    rerender();
  }, 450);
}

/* Renders the card for an FDA-label lookup result. */
function externalMedCard(info, query) {
  const field = (label, value) => value ? `
    <div><div class="detail-label">${label}</div>
    <div class="detail-value">${highlight(value, query)}</div></div>` : "";
  return `
    <div class="card medinfo medinfo-external">
      <div class="medinfo-head">
        <span class="medinfo-name">${highlight(info.generic_name, query)}</span>
        ${info.brand_name ? `<span class="med-brand">${highlight(info.brand_name, query)}</span>` : ""}
        <span class="row-spacer"></span>
        ${info.drug_class ? `<span class="chip chip-plain">${highlight(info.drug_class, query)}</span>` : ""}
        <span class="chip chip-ok">FDA label</span>
      </div>
      ${info.mechanism ? `<p class="medinfo-mechanism"><strong>How it works.</strong> ${highlight(info.mechanism, query)}</p>` : ""}
      <div class="detail-grid">
        ${field("Approved to treat", info.approved_uses)}
        ${field("Drug interactions", info.interactions)}
        ${field("Contraindications", info.contraindications)}
        ${field("Pediatric use", info.pediatric_use)}
      </div>
      <div class="medinfo-source">${esc(info.source)} &middot;
        <a href="${esc(info.dailymed_url)}" target="_blank" rel="noopener noreferrer">Full label on DailyMed</a>
      </div>
    </div>`;
}

/* Returns the external-lookup section when the search names a drug the
   family data cannot answer: a card once fetched, a hint while fetching. */
function externalMedSection(events, query, rerender) {
  if (!query || query.length < 4) return "";
  if (matchingMedications(events, query).length) return "";
  if (externalCache.has(query)) {
    const info = externalCache.get(query);
    if (!info) return "";
    return `<h2 class="section-title">From the FDA label database</h2>${externalMedCard(info, query)}`;
  }
  scheduleExternalLookup(query, rerender);
  return `<p class="external-hint">Checking the FDA label database&hellip;</p>`;
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
