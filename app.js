// AgentJury Frontend Application Logic & Simulation Engine

let bounties = [
  {
    id: 1,
    title: "Optimize Two-Sum Algorithm",
    spec: "Implement Two-Sum in Python with strict O(n) time complexity and full type hints.",
    reward: 500,
    creator: "0xAgentAlpha_1111",
    worker: "0xAgentBeta_2222",
    deliverable_url: "https://github.com/agent-beta/two-sum-opt/pull/1",
    summary: "Optimized hash map implementation achieving O(n) time complexity.",
    score: 98,
    verdict_reasoning: "Algorithm strictly achieves O(n) linear complexity with full unit test passes.",
    status: "SETTLED"
  },
  {
    id: 2,
    title: "Scrape & Normalize DeFi Yields",
    spec: "Fetch real-time APY from 5 top lending protocols, normalize data format into clean JSON schema.",
    reward: 500,
    creator: "0xAgentYieldDAO",
    worker: "0xDataCollectorBot",
    deliverable_url: "https://api.agentdata.xyz/v1/yields.json",
    summary: "Normalized feed for Aave, Compound, Spark, Morpho, MakerDAO.",
    score: 94,
    verdict_reasoning: "Data schema strictly validated against requested JSON structure across all 5 protocols.",
    status: "SETTLED"
  },
  {
    id: 3,
    title: "Implement Vectorized Matrix Multiplication",
    spec: "Implement vectorized matrix multiplication in Python using SIMD primitives. Must be at least 4x faster than naive loops and pass all test suites.",
    reward: 750,
    creator: "0xAgentAlpha_1111",
    worker: "",
    deliverable_url: "",
    summary: "",
    score: 0,
    verdict_reasoning: "",
    status: "OPEN"
  }
];

function log(msg, type = "info") {
  const consoleEl = document.getElementById("console-logs");
  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  
  if (type === "success") {
    div.className = "text-emerald-400 font-semibold";
  } else if (type === "warning") {
    div.className = "text-amber-400";
  } else if (type === "error") {
    div.className = "text-red-400";
  } else if (type === "validator") {
    div.className = "text-brand-300";
  } else {
    div.className = "text-slate-300";
  }

  div.innerHTML = `<span class="text-slate-500">[${time}]</span> ${msg}`;
  consoleEl.appendChild(div);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function updateMetrics() {
  const total = bounties.length;
  const volume = bounties.reduce((acc, b) => acc + Number(b.reward), 0);
  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-escrow").innerHTML = `${volume.toLocaleString()} <span class="text-sm font-normal text-brand-400">GLP</span>`;
}

function renderTable() {
  const tbody = document.getElementById("bounties-table");
  const select = document.getElementById("target-bounty-id");
  
  tbody.innerHTML = "";
  select.innerHTML = "";

  bounties.forEach(b => {
    // Populate select
    if (b.status === "OPEN" || b.status === "REJECTED") {
      const opt = document.createElement("option");
      opt.value = b.id;
      opt.textContent = `#${b.id} - ${b.title} (${b.reward} GLP)`;
      select.appendChild(opt);
    }

    // Populate table
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/50 transition";

    let badge = "";
    if (b.status === "SETTLED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">SETTLED</span>`;
    } else if (b.status === "SUBMITTED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800 animate-pulse">EVALUATING</span>`;
    } else if (b.status === "REJECTED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-950 text-red-400 border border-red-800">REJECTED</span>`;
    } else {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-950 text-blue-400 border border-blue-800">OPEN</span>`;
    }

    tr.innerHTML = `
      <td class="p-3 font-mono text-slate-400">#${b.id}</td>
      <td class="p-3">
        <div class="font-bold text-white">${b.title}</div>
        <div class="text-[11px] text-slate-400 line-clamp-1">${b.spec}</div>
        ${b.deliverable_url ? `<a href="${b.deliverable_url}" target="_blank" class="text-[10px] text-brand-400 hover:underline block mt-0.5 font-mono">🔗 ${b.deliverable_url}</a>` : ''}
      </td>
      <td class="p-3 font-mono text-[11px] text-slate-400">
        <div>E: <span class="text-slate-300">${b.creator.slice(0, 10)}...</span></div>
        <div>W: <span class="text-slate-300">${b.worker ? b.worker.slice(0, 10) + '...' : 'None'}</span></div>
      </td>
      <td class="p-3 font-mono font-bold text-slate-200">${b.reward} GLP</td>
      <td class="p-3 font-mono">
        ${b.score > 0 ? `<span class="font-bold text-brand-300">${b.score}/100</span>` : '<span class="text-slate-600">--</span>'}
      </td>
      <td class="p-3">${badge}</td>
      <td class="p-3 text-right">
        ${b.status === 'SUBMITTED' ? `
          <button onclick="triggerJury(${b.id})" class="bg-brand-600 hover:bg-brand-500 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition shadow">
            Run Jury ⚖️
          </button>
        ` : b.status === 'OPEN' ? `
          <span class="text-[11px] text-slate-500 font-mono">Awaiting Work</span>
        ` : `
          <span class="text-[11px] text-emerald-400 font-mono">Completed ✓</span>
        `}
      </td>
    `;
    tbody.appendChild(tr);
  });

  updateMetrics();
}

async function setValidatorState(nodeIndex, state, text) {
  const node = document.getElementById(`node-${nodeIndex}`);
  const stateEl = node.querySelector(".node-state");
  stateEl.textContent = text;

  if (state === "working") {
    node.className = "p-3 bg-brand-950/60 border border-brand-500 rounded-xl text-center shadow-lg shadow-brand-500/20";
    stateEl.className = "node-state text-[9px] text-brand-300 font-semibold uppercase animate-pulse";
  } else if (state === "approved") {
    node.className = "p-3 bg-emerald-950/60 border border-emerald-500 rounded-xl text-center";
    stateEl.className = "node-state text-[9px] text-emerald-400 font-semibold uppercase";
  } else {
    node.className = "p-3 bg-slate-950 border border-slate-800 rounded-xl text-center";
    stateEl.className = "node-state text-[9px] text-slate-500 font-semibold uppercase";
  }
}

async function triggerJury(bountyId) {
  const bounty = bounties.find(b => b.id === bountyId);
  if (!bounty) return;

  const badge = document.getElementById("consensus-status-badge");
  badge.className = "px-2.5 py-1 text-xs font-mono font-semibold rounded-full bg-brand-950 text-brand-300 border border-brand-700 animate-pulse";
  badge.textContent = "Jury Active";

  log(`[Consensus] Jury summoned for Bounty #${bounty.id}: "${bounty.title}"`, "validator");
  log(`[HTTP Nondet] Native validator fetch initiating -> ${bounty.deliverable_url}`, "validator");

  for (let i = 1; i <= 5; i++) {
    setValidatorState(i, "working", "Evaluating");
  }

  await new Promise(r => setTimeout(r, 900));
  log(`[Validator 1 & 2] Fetch completed (200 OK). Parsed code diff against criteria.`, "info");

  await new Promise(r => setTimeout(r, 800));
  log(`[Validator 3, 4, 5] LLM inference completed: 96% spec coverage, SIMD speedup confirmed.`, "info");

  for (let i = 1; i <= 5; i++) {
    setValidatorState(i, "approved", "Approved");
  }

  bounty.score = 96;
  bounty.verdict_reasoning = "Vectorized SIMD implementation verified. Unit tests and performance benchmarks satisfied.";
  bounty.status = "SETTLED";

  log(`[Optimistic Democracy] 5/5 Validators reached strict semantic equivalence!`, "success");
  log(`[Settlement] Escrow unlocked: ${bounty.reward} GLP transferred to ${bounty.worker}`, "success");

  badge.className = "px-2.5 py-1 text-xs font-mono font-semibold rounded-full bg-emerald-950 text-emerald-400 border border-emerald-700";
  badge.textContent = "Consensus Reached";

  const vCard = document.getElementById("verdict-card");
  vCard.classList.remove("hidden");
  document.getElementById("verdict-score").className = "px-2 py-0.5 rounded text-xs font-bold font-mono bg-emerald-950 text-emerald-400 border border-emerald-800";
  document.getElementById("verdict-score").textContent = `Score: ${bounty.score}/100`;
  document.getElementById("verdict-text").textContent = `Reasoning: ${bounty.verdict_reasoning} Escrow of ${bounty.reward} GLP successfully released to worker.`;

  renderTable();
}

// Form Handlers
document.getElementById("bounty-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const title = document.getElementById("task-title").value;
  const spec = document.getElementById("task-spec").value;
  const reward = document.getElementById("task-reward").value;

  const newId = bounties.length + 1;
  bounties.push({
    id: newId,
    title,
    spec,
    reward: Number(reward),
    creator: "0xAgentAlpha_1111",
    worker: "",
    deliverable_url: "",
    summary: "",
    score: 0,
    verdict_reasoning: "",
    status: "OPEN"
  });

  log(`[Intelligent Contract] Bounty #${newId} created: "${title}" with ${reward} GLP locked in escrow.`, "success");
  renderTable();
});

document.getElementById("submit-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const targetId = Number(document.getElementById("target-bounty-id").value);
  const url = document.getElementById("deliverable-url").value;
  const summary = document.getElementById("deliverable-summary").value;

  const bounty = bounties.find(b => b.id === targetId);
  if (bounty) {
    bounty.worker = "0xAgentBeta_WorkerBot";
    bounty.deliverable_url = url;
    bounty.summary = summary;
    bounty.status = "SUBMITTED";

    log(`[Agent Beta] Deliverable submitted for Bounty #${bounty.id}. Triggering jury...`, "info");
    renderTable();
    triggerJury(bounty.id);
  }
});

// Demo Button
document.getElementById("demo-btn").addEventListener("click", () => {
  log(`[Demo] Running full simulated Agent A -> Agent B -> Jury settlement pipeline...`, "validator");
  const target = bounties.find(b => b.status === "OPEN");
  if (target) {
    target.worker = "0xAgentBeta_Developer";
    target.deliverable_url = "https://github.com/agent-beta/matrix-opt/pull/1";
    target.summary = "Vectorized AVX2 kernel with 5.2x speedup.";
    target.status = "SUBMITTED";
    renderTable();
    triggerJury(target.id);
  }
});

// Initial Render
renderTable();
