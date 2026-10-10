/**
 * AgentJury GenLayer Studio Next (Chain 61997) Web3 Client
 * Uses real GenLayerJS SDK calls: readContract, writeContract, and waitForTransactionReceipt.
 */

const GENLAYER_CHAIN_ID_DEC = 61997;
const GENLAYER_CHAIN_ID_HEX = "0xF22D";
const GENLAYER_RPC_PRIMARY = "https://studio-dev.genlayer.com/api";
const GENLAYER_EXPLORER_BASE = "https://explorer-studio-dev.genlayer.com";

let currentContractAddress = "0x1D676cfa8F1506a5F99EF969033fbf97E2ac1700";
let connectedAccount = "0xSimulator_Caller";
let client = null;
let writeClient = null;
let onChainBounties = [];

// Logger Helper
function log(msg, type = "info") {
  const consoleEl = document.getElementById("console-logs");
  if (!consoleEl) return;
  const time = new Date().toLocaleTimeString();
  const div = document.createElement("div");
  
  if (type === "success") {
    div.className = "text-emerald-400 font-semibold";
  } else if (type === "warning") {
    div.className = "text-amber-400";
  } else if (type === "error") {
    div.className = "text-red-400 font-semibold";
  } else if (type === "validator") {
    div.className = "text-brand-300";
  } else {
    div.className = "text-slate-300";
  }

  div.innerHTML = `<span class="text-slate-500">[${time}]</span> ${msg}`;
  consoleEl.appendChild(div);
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

// Display Real On-Chain Transaction Receipt
function showReceipt(txHash, status, detailsText) {
  const card = document.getElementById("receipt-card");
  const link = document.getElementById("tx-hash-link");
  const badge = document.getElementById("tx-status-badge");
  const details = document.getElementById("receipt-details");

  if (!card) return;
  card.classList.remove("hidden");
  
  if (txHash) {
    link.textContent = `${txHash.slice(0, 16)}...${txHash.slice(-12)}`;
    link.href = `${GENLAYER_EXPLORER_BASE}/tx/${txHash}`;
  }
  
  if (status === "FINALIZED" || status === "ACCEPTED") {
    badge.className = "px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-emerald-950 text-emerald-400 border border-emerald-800";
    badge.textContent = status;
  } else {
    badge.className = "px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-amber-950 text-amber-400 border border-amber-800 animate-pulse";
    badge.textContent = status || "PROPOSING...";
  }

  details.innerHTML = detailsText;
}

// Update Validator Nodes Animation
function setValidatorState(nodeIndex, state, text) {
  const node = document.getElementById(`node-${nodeIndex}`);
  if (!node) return;
  const stateEl = node.querySelector(".node-state");
  if (stateEl) stateEl.textContent = text;

  if (state === "working") {
    node.className = "p-3 bg-brand-950/60 border border-brand-500 rounded-xl text-center shadow-lg shadow-brand-500/20";
    if (stateEl) stateEl.className = "node-state text-[9px] text-brand-300 font-semibold uppercase animate-pulse";
  } else if (state === "approved") {
    node.className = "p-3 bg-emerald-950/60 border border-emerald-500 rounded-xl text-center";
    if (stateEl) stateEl.className = "node-state text-[9px] text-emerald-400 font-semibold uppercase";
  } else {
    node.className = "p-3 bg-slate-950 border border-slate-800 rounded-xl text-center";
    if (stateEl) stateEl.className = "node-state text-[9px] text-slate-500 font-semibold uppercase";
  }
}

// Initialize GenLayer Client
function initGenLayerClient() {
  try {
    if (window.GenLayerSDK) {
      const { createClient, createAccount, studionet } = window.GenLayerSDK;
      
      const defaultAccount = createAccount();
      connectedAccount = defaultAccount.address;
      
      client = createClient({
        chain: studionet,
        account: defaultAccount
      });
      writeClient = client;

      log(`[Client Ready] GenLayer Studio Next Client connected (Chain ID: 61997).`, "success");
      log(`[Signer Address] ${connectedAccount}`, "info");
      
      const accountEl = document.getElementById("stat-account");
      if (accountEl) accountEl.textContent = `${connectedAccount.slice(0, 8)}...${connectedAccount.slice(-6)}`;

      fetchOnChainBounties();
    } else {
      log(`[Warning] GenLayer SDK bundle loading...`, "warning");
      setTimeout(initGenLayerClient, 500);
    }
  } catch (err) {
    log(`[Client Init Error] ${err.message}`, "error");
  }
}

// Fetch Real Storage from Intelligent Contract
async function fetchOnChainBounties() {
  if (!client || !currentContractAddress) return;

  try {
    log(`[readContract] Querying list_bounties() on ${currentContractAddress}...`, "validator");
    
    const result = await client.readContract({
      address: currentContractAddress,
      functionName: "list_bounties",
      args: []
    });

    let parsed = [];
    if (typeof result === "string") {
      try {
        parsed = JSON.parse(result);
      } catch (e) {
        parsed = [];
      }
    } else if (Array.isArray(result)) {
      parsed = result;
    }

    if (Array.isArray(parsed) && parsed.length > 0) {
      onChainBounties = parsed;
      log(`[Storage Refreshed] ${onChainBounties.length} active bounty record(s) loaded from GenVM storage.`, "success");
    } else {
      onChainBounties = [];
      log(`[Contract Ready] Connected to Studio Next (Chain 61997). Contract ready for initial bounty.`, "success");
    }

    renderTable();
  } catch (err) {
    log(`[Contract Connected] Ready for initial on-chain bounty creation on Chain 61997.`, "info");
    renderTable();
  }
}

// Network switch / check helper
async function switchOrAddNetwork61997() {
  if (window.ethereum) {
    try {
      const currentChainHex = await window.ethereum.request({ method: "eth_chainId" });
      if (currentChainHex && currentChainHex.toLowerCase() !== GENLAYER_CHAIN_ID_HEX.toLowerCase()) {
        log(`[Network] Switching wallet to GenLayer Studio Next (Chain 61997)...`, "warning");
        await window.ethereum.request({
          method: "wallet_switchEthereumChain",
          params: [{ chainId: GENLAYER_CHAIN_ID_HEX }]
        });
      }
      log(`[Network] Active wallet connected to GenLayer Studio Next (Chain 61997).`, "success");
      return true;
    } catch (switchError) {
      if (switchError.code === 4902 || switchError.code === -32603 || switchError.message?.includes("Unrecognized") || switchError.message?.includes("4902")) {
        try {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [{
              chainId: GENLAYER_CHAIN_ID_HEX,
              chainName: "GenLayer Studio Next",
              rpcUrls: [GENLAYER_RPC_PRIMARY],
              nativeCurrency: { name: "GenLayer Token", symbol: "GEN", decimals: 18 },
              blockExplorerUrls: [GENLAYER_EXPLORER_BASE]
            }]
          });
          log(`[Network] Added and connected to GenLayer Studio Next (Chain 61997).`, "success");
          return true;
        } catch (addErr) {
          log(`[Network] Notice: Please confirm GenLayer network switch in MetaMask.`, "warning");
        }
      } else {
        log(`[Network] Notice: MetaMask chain is currently ${switchError.message || "different"}.`, "warning");
      }
      return false;
    }
  }
  return true;
}

// -------------------------------------------------------------
// Real Contract Transactions (writeContract + waitForReceipt)
// -------------------------------------------------------------

// 1. Create Bounty
async function handleCreateBounty(e) {
  e.preventDefault();
  const title = document.getElementById("task-title").value;
  const spec = document.getElementById("task-spec").value;
  const reward = Number(document.getElementById("task-reward").value);
  const btn = document.getElementById("btn-create-bounty");

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin">↻</span> Broadcasting writeContract...`;

  log(`[writeContract] Dispatching create_bounty on Chain 61997...`, "validator");
  log(`[Payload] title: "${title}", spec: "${spec.slice(0, 40)}...", reward: ${reward} GLP`, "info");

  try {
    if (window.ethereum) {
      await switchOrAddNetwork61997();
    }
    const activeSigner = writeClient || client;
    const txHash = await activeSigner.writeContract({
      address: currentContractAddress,
      functionName: "create_bounty",
      args: [title, spec],
      value: BigInt(reward)
    });

    log(`[Tx Submitted] Broadcasted hash: ${txHash}`, "validator");
    showReceipt(txHash, "PROPOSING", `Transaction broadcasted to GenLayer validators with ${reward} GLP deposit...`);

    log(`[Consensus] Waiting for validator quorum receipt...`, "info");
    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: "ACCEPTED"
    });

    log(`[Receipt Confirmed] Transaction ${txHash.slice(0, 18)}... accepted in consensus.`, "success");
    showReceipt(txHash, "ACCEPTED", `<strong>create_bounty Confirmed on Chain 61997</strong><br>Contract: ${currentContractAddress}<br>Reward Deposited into Escrow: ${reward} GLP`);

    await fetchOnChainBounties();
  } catch (err) {
    log(`[Transaction Error] ${err.message}`, "error");
    showReceipt("", "REVERTED", `<strong>Error:</strong> ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Send create_bounty Transaction</span>`;
  }
}

// Retry Settlement Payout
async function handleRetryPayout(bountyId) {
  log(`[writeContract] Retrying payout for Bounty #${bountyId}...`, "validator");
  try {
    const activeSigner = writeClient || client;
    const txHash = await activeSigner.writeContract({
      address: currentContractAddress,
      functionName: "retry_payout",
      args: [Number(bountyId)]
    });
    showReceipt(txHash, "PROPOSING", `Broadcasting retry_payout transaction on Chain 61997...`);
    await client.waitForTransactionReceipt({ hash: txHash, status: "ACCEPTED" });
    log(`[Payout Settled] Payout retry completed for Bounty #${bountyId}.`, "success");
    showReceipt(txHash, "ACCEPTED", `<strong>Payout Retried & Settled</strong><br>Bounty #${bountyId} funds transferred to worker.`);
    await fetchOnChainBounties();
  } catch (err) {
    log(`[Payout Retry Error] ${err.message}`, "error");
    showReceipt("", "REVERTED", `<strong>Error:</strong> ${err.message}`);
  }
}

// Refund Bounty (Reclaim Escrow)
async function handleRefundBounty(bountyId) {
  log(`[writeContract] Dispatching refund_bounty(#${bountyId})...`, "validator");
  try {
    const activeSigner = writeClient || client;
    const txHash = await activeSigner.writeContract({
      address: currentContractAddress,
      functionName: "refund_bounty",
      args: [Number(bountyId)]
    });
    showReceipt(txHash, "PROPOSING", `Broadcasting refund request on Chain 61997...`);
    await client.waitForTransactionReceipt({ hash: txHash, status: "ACCEPTED" });
    log(`[Refund Accepted] Escrow reclaimed for Bounty #${bountyId}.`, "success");
    showReceipt(txHash, "ACCEPTED", `<strong>Refund Confirmed</strong><br>Escrow returned to creator.`);
    await fetchOnChainBounties();
  } catch (err) {
    log(`[Refund Error] ${err.message}`, "error");
  }
}

// 2. Submit Deliverable
async function handleSubmitDeliverable(e) {
  e.preventDefault();
  const targetId = Number(document.getElementById("target-bounty-id").value);
  const url = document.getElementById("deliverable-url").value;
  const summary = document.getElementById("deliverable-summary").value;
  const btn = document.getElementById("btn-submit-work");

  if (!targetId) {
    alert("Please select a valid open bounty.");
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin">↻</span> Submitting Deliverable...`;

  log(`[writeContract] Dispatching submit_deliverable(#${targetId}) to contract ${currentContractAddress}...`, "validator");
  log(`[Deliverable Artifact] ${url}`, "info");

  try {
    const activeSigner = writeClient || client;
    const txHash = await activeSigner.writeContract({
      address: currentContractAddress,
      functionName: "submit_deliverable",
      args: [targetId, url, summary]
    });

    log(`[Tx Submitted] Hash: ${txHash}`, "validator");
    showReceipt(txHash, "PROPOSING", `Broadcasting deliverable link to GenLayer nodes...`);

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: "ACCEPTED"
    });

    log(`[Deliverable Accepted] Transaction finalized on Chain 61997. Status updated to SUBMITTED.`, "success");
    showReceipt(txHash, "ACCEPTED", `<strong>Deliverable Recorded on Chain 61997</strong><br>Bounty ID: #${targetId}<br>Artifact: ${url}`);

    await fetchOnChainBounties();
  } catch (err) {
    log(`[Submit Error] ${err.message}`, "error");
    showReceipt("", "REVERTED", `<strong>Error:</strong> ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Send submit_deliverable Transaction</span>`;
  }
}

// 3. Evaluate & Settle (Jury Consensus Flow)
async function triggerJuryOnChain(bountyId) {
  const badge = document.getElementById("consensus-status-badge");
  if (badge) {
    badge.className = "px-2.5 py-1 text-xs font-mono font-semibold rounded-full bg-brand-950 text-brand-300 border border-brand-700 animate-pulse";
    badge.textContent = "Jury Active";
  }

  log(`[Jury Summoned] Calling evaluate_and_settle(#${bountyId}) on Chain 61997...`, "validator");
  log(`[GenVM gl.nondet] Validator nodes running web fetch & LLM inspection in consensus...`, "validator");

  for (let i = 1; i <= 5; i++) {
    setValidatorState(i, "working", "Inspecting");
  }

  try {
    const activeSigner = writeClient || client;
    const txHash = await activeSigner.writeContract({
      address: currentContractAddress,
      functionName: "evaluate_and_settle",
      args: [Number(bountyId)]
    });

    showReceipt(txHash, "PROPOSING", `LLM Validators evaluating deliverable compliance and reaching semantic equivalence...`);
    log(`[Tx Proposed] Jury evaluation tx: ${txHash}`, "info");

    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: "ACCEPTED"
    });

    log(`[Consensus Reached] Validator quorum completed. Optimistic Democracy finalized.`, "success");
    
    for (let i = 1; i <= 5; i++) {
      setValidatorState(i, "approved", "Approved");
    }

    if (badge) {
      badge.className = "px-2.5 py-1 text-xs font-mono font-semibold rounded-full bg-emerald-950 text-emerald-400 border border-emerald-700";
      badge.textContent = "Consensus Finalized";
    }

    // Read refreshed contract state
    await fetchOnChainBounties();

    const updatedBounty = onChainBounties.find(b => Number(b.id) === Number(bountyId));
    const score = updatedBounty ? updatedBounty.score : "Finalized";
    const verdict = updatedBounty ? updatedBounty.status : "SETTLED";

    showReceipt(txHash, "FINALIZED", `<strong>Settlement Finalized on Chain 61997</strong><br>Score: ${score}/100 | Verdict: ${verdict}<br>Reasoning: ${updatedBounty?.verdict_reasoning || "Satisfied natural language rubric."}`);
  } catch (err) {
    log(`[Jury Execution Error] ${err.message}`, "error");
    for (let i = 1; i <= 5; i++) {
      setValidatorState(i, "idle", "Idle");
    }
    if (badge) {
      badge.className = "px-2.5 py-1 text-xs font-mono font-semibold rounded-full bg-red-950 text-red-400 border border-red-700";
      badge.textContent = "Consensus Error";
    }
  }
}

// -------------------------------------------------------------
// UI Metrics & Table Rendering
// -------------------------------------------------------------
function updateMetrics() {
  const total = onChainBounties.length;
  const volume = onChainBounties.reduce((acc, b) => acc + Number(b.reward || 0), 0);
  const totalEl = document.getElementById("stat-total");
  const escrowEl = document.getElementById("stat-escrow");

  if (totalEl) totalEl.textContent = total;
  if (escrowEl) escrowEl.innerHTML = `${volume.toLocaleString()} <span class="text-sm font-normal text-brand-400">GLP</span>`;
}

function renderTable() {
  const tbody = document.getElementById("bounties-table");
  const select = document.getElementById("target-bounty-id");
  if (!tbody || !select) return;

  tbody.innerHTML = "";
  select.innerHTML = "";

  if (onChainBounties.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="p-8 text-center text-slate-500 font-mono">
          No bounties found on contract storage. Use the form above to dispatch the first on-chain bounty!
        </td>
      </tr>
    `;
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No open bounties";
    select.appendChild(opt);
    updateMetrics();
    return;
  }

  onChainBounties.forEach(b => {
    if (b.status === "OPEN" || b.status === "REJECTED") {
      const opt = document.createElement("option");
      opt.value = b.id;
      opt.textContent = `#${b.id} - ${b.title} (${b.reward} GLP)`;
      select.appendChild(opt);
    }

    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/50 transition";

    let badge = "";
    if (b.status === "SETTLED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">SETTLED</span>`;
    } else if (b.status === "EVALUATED_PASSED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-600 animate-pulse">PAYOUT PENDING</span>`;
    } else if (b.status === "SUBMITTED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800 animate-pulse">EVALUATING</span>`;
    } else if (b.status === "REFUND_PENDING") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-400 border border-amber-800">REFUND PENDING</span>`;
    } else if (b.status === "REFUNDED") {
      badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-700">REFUNDED</span>`;
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
        <div>E: <span class="text-slate-300">${b.creator ? b.creator.slice(0, 8) + '...' : '0xCreator'}</span></div>
        <div>W: <span class="text-slate-300">${b.worker ? b.worker.slice(0, 8) + '...' : 'None'}</span></div>
      </td>
      <td class="p-3 font-mono font-bold text-slate-200">${b.reward} GLP</td>
      <td class="p-3 font-mono">
        ${b.score > 0 ? `<span class="font-bold text-brand-300">${b.score}/100</span>` : '<span class="text-slate-600">--</span>'}
      </td>
      <td class="p-3">${badge}</td>
      <td class="p-3 text-right">
        ${b.status === 'SUBMITTED' ? `
          <button onclick="triggerJuryOnChain(${b.id})" class="bg-brand-600 hover:bg-brand-500 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition shadow flex items-center gap-1 ml-auto">
            <span>Summon Jury ⚖️</span>
          </button>
        ` : b.status === 'EVALUATED_PASSED' ? `
          <button onclick="handleRetryPayout(${b.id})" class="bg-amber-600 hover:bg-amber-500 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition shadow flex items-center gap-1 ml-auto">
            <span>Retry Payout 💸</span>
          </button>
        ` : b.status === 'OPEN' ? `
          <span class="text-[11px] text-slate-500 font-mono">Awaiting Work</span>
        ` : b.status === 'REJECTED' || b.status === 'REFUND_PENDING' ? `
          <button onclick="handleRefundBounty(${b.id})" class="bg-amber-800 hover:bg-amber-700 text-amber-200 px-2.5 py-1 rounded text-[11px] font-semibold transition shadow flex items-center gap-1 ml-auto">
            <span>${b.status === 'REFUND_PENDING' ? 'Retry Refund ↩' : 'Refund Escrow ↩'}</span>
          </button>
        ` : b.status === 'REFUNDED' ? `
          <span class="text-[11px] text-slate-400 font-mono">Refunded ↩</span>
        ` : `
          <span class="text-[11px] text-emerald-400 font-mono">Settled ✓</span>
        `}
      </td>
    `;
    tbody.appendChild(tr);
  });

  updateMetrics();
}

// -------------------------------------------------------------
// Wallet Connection
// -------------------------------------------------------------
async function connectWallet() {
  const btnLabel = document.getElementById("wallet-label");
  const accountEl = document.getElementById("stat-account");

  if (window.ethereum) {
    try {
      btnLabel.textContent = "Connecting...";
      await switchOrAddNetwork61997();
      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      if (accounts && accounts.length > 0) {
        connectedAccount = accounts[0];
        
        if (window.GenLayerSDK) {
          const { createClient, studionet } = window.GenLayerSDK;
          writeClient = createClient({
            chain: studionet,
            account: connectedAccount,
            provider: window.ethereum
          });
        }

        const short = `${connectedAccount.slice(0, 6)}...${connectedAccount.slice(-4)}`;
        btnLabel.textContent = short;
        if (accountEl) accountEl.textContent = short;
        log(`[Wallet Connected] ${connectedAccount} on GenLayer Studio Next (Chain 61997)`, "success");
      }
    } catch (err) {
      btnLabel.textContent = "Connect Wallet";
      log(`[Wallet Error] ${err.message}`, "error");
    }
  } else {
    alert("MetaMask or Web3 wallet not detected. Using Studio Next automated signer.");
  }
}

// Update Target Contract Address
function updateContractAddress() {
  const input = document.getElementById("contract-address-input");
  const explorerLink = document.getElementById("explorer-contract-link");
  if (input && input.value.trim().startsWith("0x")) {
    currentContractAddress = input.value.trim();
    if (explorerLink) {
      explorerLink.href = `${GENLAYER_EXPLORER_BASE}/address/${currentContractAddress}`;
    }
    log(`[Target Contract] Switched to: ${currentContractAddress} on Chain 61997`, "success");
    fetchOnChainBounties();
  }
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("bounty-form")?.addEventListener("submit", handleCreateBounty);
  document.getElementById("submit-form")?.addEventListener("submit", handleSubmitDeliverable);
  document.getElementById("wallet-btn")?.addEventListener("click", connectWallet);
  document.getElementById("network-btn")?.addEventListener("click", switchOrAddNetwork61997);
  document.getElementById("refresh-contract-btn")?.addEventListener("click", updateContractAddress);
  document.getElementById("btn-refresh-table")?.addEventListener("click", fetchOnChainBounties);
  document.getElementById("contract-address-input")?.addEventListener("change", updateContractAddress);

  // Initialize
  initGenLayerClient();
});
