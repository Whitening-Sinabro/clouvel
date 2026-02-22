/**
 * Clouvel API Worker
 * v4.0: Server-side state (KV) + Version check + FREE tier changes
 *
 * Existing Endpoints:
 * - POST /api/manager - C-Level manager feedback
 * - POST /api/ship - Ship permission check
 * - GET  /api/trial/status - Trial status (legacy)
 *
 * v4.0 Endpoints (server-side state):
 * - POST /api/v2/sync - Unified state sync
 * - POST /api/v2/trial/start - Start trial (server clock)
 * - POST /api/v2/project/register - Register first project (immutable)
 * - POST /api/v2/meeting/consume - Consume meeting quota
 * - POST /api/v2/experiment/assign - A/B experiment assignment (sticky)
 * - POST /api/v2/heartbeat - License heartbeat (24h)
 * - GET  /api/v2/check - Revocation check
 */

const MIN_VERSION = "3.0.0";
const FREE_MANAGERS = ["PM"];
const ALL_MANAGERS = ["PM", "CTO", "QA", "CDO", "CMO", "CFO", "CSO", "ERROR"];

const TRIAL_DAYS = 7;
const TRIAL_TTL_SECONDS = 30 * 24 * 3600;          // 30 days
const FIRST_PROJECT_TTL_SECONDS = null;              // no expiry
const MEETING_QUOTA_TTL_SECONDS = 45 * 24 * 3600;   // 45 days
const EXPERIMENT_TTL_SECONDS = 90 * 24 * 3600;       // 90 days
const LICENSE_CACHE_TTL_SECONDS = 24 * 3600;          // 24 hours
const FREE_MONTHLY_MEETINGS = 3;

// Polar.sh API for license validation
const POLAR_VALIDATE_URL = "https://api.polar.sh/v1/customer-portal/license-keys/validate";

// ============================================================
// Utility helpers
// ============================================================

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

function compareVersions(v1, v2) {
  const parts1 = v1.split(".").map(Number);
  const parts2 = v2.split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    const p1 = parts1[i] || 0;
    const p2 = parts2[i] || 0;
    if (p1 !== p2) return p1 - p2;
  }
  return 0;
}

function isVersionAcceptable(clientVersion) {
  if (!clientVersion) return false;
  try {
    return compareVersions(clientVersion, MIN_VERSION) >= 0;
  } catch {
    return false;
  }
}

function upgradeRequiredResponse() {
  return jsonResponse(
    {
      error: "upgrade_required",
      message: `Clouvel v${MIN_VERSION}+ required. Run: pip install --upgrade clouvel`,
      min_version: MIN_VERSION,
      changes: {
        free_managers: "PM only (was PM, CTO, QA)",
        can_code: "WARN mode (was BLOCK)",
        projects: "1 limit for FREE tier",
      },
    },
    426
  );
}

function handleCors() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers":
        "Content-Type, X-Clouvel-Client, X-Clouvel-Version",
    },
  });
}

/**
 * Parse and validate machine_id from request body.
 */
function requireMachineId(body) {
  const mid = body.machine_id;
  if (!mid || typeof mid !== "string" || mid.length < 8) {
    return null;
  }
  return mid;
}

/**
 * Validate license via Polar.sh API, with KV cache.
 */
async function validateLicense(env, licenseKey) {
  if (!licenseKey || licenseKey.length < 10) return null;

  // Check KV cache first
  const cacheKey = `license:${licenseKey}`;
  const cached = await env.STATE.get(cacheKey, "json");
  if (cached) return cached;

  try {
    const resp = await fetch(POLAR_VALIDATE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        key: licenseKey,
        organization_id: env.POLAR_ORG_ID || "",
      }),
    });
    if (resp.ok) {
      const data = await resp.json();
      const result = {
        valid: data.valid === true,
        tier: data.valid ? (data.benefit?.type || "personal") : null,
        customer_id: data.customer_id || null,
      };
      // Cache for 24h
      await env.STATE.put(cacheKey, JSON.stringify(result), {
        expirationTtl: LICENSE_CACHE_TTL_SECONDS,
      });
      return result;
    }
  } catch {
    // Network error — fall through
  }
  return null;
}

/**
 * Simple license check (body.licenseKey length > 10) for legacy endpoints.
 */
function hasValidLicense(body) {
  return body.licenseKey && body.licenseKey.length > 10;
}

// ============================================================
// v4.0: Server-side state handlers
// ============================================================

/**
 * POST /api/v2/sync — Unified state synchronization
 *
 * First call: seed KV from local_state (migration).
 * Subsequent: KV is source of truth.
 */
async function handleSync(request, env) {
  const body = await request.json();
  const mid = requireMachineId(body);
  if (!mid) return jsonResponse({ error: "machine_id required" }, 400);

  const localState = body.local_state || {};
  const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM

  // --- Trial ---
  let trialKV = await env.STATE.get(`trial:${mid}`, "json");
  if (!trialKV && localState.trial && localState.trial.started_at) {
    // Migration: seed from local (one-time)
    trialKV = {
      started_at: localState.trial.started_at,
      machine_id: mid,
      seeded_from: "local",
      seeded_at: new Date().toISOString(),
    };
    await env.STATE.put(`trial:${mid}`, JSON.stringify(trialKV), {
      expirationTtl: TRIAL_TTL_SECONDS,
    });
  }
  const trialResult = buildTrialResult(trialKV);

  // --- First Project ---
  let fpKV = await env.STATE.get(`fp:${mid}`, "json");
  if (!fpKV && localState.first_project && localState.first_project.path_hash) {
    // Migration: seed from local
    fpKV = {
      path_hash: localState.first_project.path_hash,
      machine_id: mid,
      registered_at: new Date().toISOString(),
      seeded_from: "local",
    };
    await env.STATE.put(`fp:${mid}`, JSON.stringify(fpKV));
    // No TTL — immutable
  }

  // --- Meeting Quota ---
  const mqKey = `mq:${mid}:${currentMonth}`;
  let mqKV = await env.STATE.get(mqKey, "json");
  if (!mqKV && localState.meeting_quota) {
    const localUsed = localState.meeting_quota.used || 0;
    mqKV = { month: currentMonth, used: localUsed };
    await env.STATE.put(mqKey, JSON.stringify(mqKV), {
      expirationTtl: MEETING_QUOTA_TTL_SECONDS,
    });
  }
  if (!mqKV) {
    mqKV = { month: currentMonth, used: 0 };
  }
  // Anti-abuse: take max of local and server
  if (localState.meeting_quota && localState.meeting_quota.month === currentMonth) {
    const localUsed = localState.meeting_quota.used || 0;
    if (localUsed > mqKV.used) {
      mqKV.used = localUsed;
      await env.STATE.put(mqKey, JSON.stringify(mqKV), {
        expirationTtl: MEETING_QUOTA_TTL_SECONDS,
      });
    }
  }

  // --- Experiments ---
  let expKV = await env.STATE.get(`exp:${mid}`, "json");
  if (!expKV && localState.experiments) {
    // Seed: take local assignments
    expKV = {};
    for (const [name, info] of Object.entries(localState.experiments)) {
      const variant = typeof info === "string" ? info : info.variant;
      if (variant) expKV[name] = variant;
    }
    if (Object.keys(expKV).length > 0) {
      await env.STATE.put(`exp:${mid}`, JSON.stringify(expKV), {
        expirationTtl: EXPERIMENT_TTL_SECONDS,
      });
    }
  }
  if (!expKV) expKV = {};

  // --- License ---
  const licenseResult = await validateLicense(env, body.license_key);

  const mqRemaining = Math.max(0, FREE_MONTHLY_MEETINGS - mqKV.used);

  return jsonResponse({
    server_state: {
      trial: trialResult,
      first_project: fpKV
        ? { path_hash: fpKV.path_hash, locked: true }
        : { path_hash: null, locked: false },
      meeting_quota: {
        month: currentMonth,
        used: mqKV.used,
        limit: FREE_MONTHLY_MEETINGS,
        remaining: mqRemaining,
      },
      experiments: expKV,
      license: licenseResult
        ? { valid: licenseResult.valid, tier: licenseResult.tier }
        : { valid: false, tier: null },
    },
    next_sync_seconds: 3600,
  });
}

function buildTrialResult(trialKV) {
  if (!trialKV || !trialKV.started_at) {
    return { active: false, remaining_days: 0, source: "server" };
  }
  const start = new Date(trialKV.started_at);
  const now = new Date();
  const elapsedMs = now.getTime() - start.getTime();
  const elapsedDays = Math.floor(elapsedMs / (24 * 3600 * 1000));
  const remaining = Math.max(0, TRIAL_DAYS - elapsedDays);
  return {
    active: remaining > 0,
    remaining_days: remaining,
    started_at: trialKV.started_at,
    source: "server",
  };
}

/**
 * POST /api/v2/trial/start — Start trial (server clock, one-time).
 */
async function handleTrialStart(request, env) {
  const body = await request.json();
  const mid = requireMachineId(body);
  if (!mid) return jsonResponse({ error: "machine_id required" }, 400);

  const existing = await env.STATE.get(`trial:${mid}`, "json");
  if (existing) {
    // Already started — 409
    return jsonResponse(
      {
        error: "trial_already_started",
        ...buildTrialResult(existing),
      },
      409
    );
  }

  const trialData = {
    started_at: new Date().toISOString(),
    machine_id: mid,
  };
  await env.STATE.put(`trial:${mid}`, JSON.stringify(trialData), {
    expirationTtl: TRIAL_TTL_SECONDS,
  });

  return jsonResponse({
    active: true,
    started_at: trialData.started_at,
    remaining_days: TRIAL_DAYS,
  });
}

/**
 * POST /api/v2/project/register — Register first project (immutable).
 */
async function handleProjectRegister(request, env) {
  const body = await request.json();
  const mid = requireMachineId(body);
  if (!mid) return jsonResponse({ error: "machine_id required" }, 400);

  const pathHash = body.path_hash;
  if (!pathHash || typeof pathHash !== "string") {
    return jsonResponse({ error: "path_hash required" }, 400);
  }

  const existing = await env.STATE.get(`fp:${mid}`, "json");
  if (existing) {
    // Already registered
    const isFirst = existing.path_hash === pathHash;
    return jsonResponse({
      registered: true,
      is_first: isFirst,
      tier: isFirst ? "first" : "additional",
      path_hash: existing.path_hash,
    });
  }

  // New registration
  const fpData = {
    path_hash: pathHash,
    machine_id: mid,
    registered_at: new Date().toISOString(),
  };
  await env.STATE.put(`fp:${mid}`, JSON.stringify(fpData));
  // No TTL — immutable

  return jsonResponse({
    registered: true,
    is_first: true,
    tier: "first",
    path_hash: pathHash,
  });
}

/**
 * POST /api/v2/meeting/consume — Consume one meeting from monthly quota.
 */
async function handleMeetingConsume(request, env) {
  const body = await request.json();
  const mid = requireMachineId(body);
  if (!mid) return jsonResponse({ error: "machine_id required" }, 400);

  // Check if Pro or first project (unlimited)
  const licenseResult = await validateLicense(env, body.license_key);
  if (licenseResult && licenseResult.valid) {
    return jsonResponse({ allowed: true, used: 0, remaining: 999, limit: 999 });
  }
  const fp = await env.STATE.get(`fp:${mid}`, "json");
  const projectHash = body.project_hash;
  if (fp && projectHash && fp.path_hash === projectHash) {
    // First project — unlimited
    return jsonResponse({ allowed: true, used: 0, remaining: 999, limit: 999 });
  }

  // Free additional project — monthly quota
  const currentMonth = new Date().toISOString().slice(0, 7);
  const mqKey = `mq:${mid}:${currentMonth}`;
  let mqKV = await env.STATE.get(mqKey, "json");
  if (!mqKV) {
    mqKV = { month: currentMonth, used: 0 };
  }

  if (mqKV.used >= FREE_MONTHLY_MEETINGS) {
    return jsonResponse({
      allowed: false,
      used: mqKV.used,
      remaining: 0,
      limit: FREE_MONTHLY_MEETINGS,
    });
  }

  mqKV.used += 1;
  await env.STATE.put(mqKey, JSON.stringify(mqKV), {
    expirationTtl: MEETING_QUOTA_TTL_SECONDS,
  });

  return jsonResponse({
    allowed: true,
    used: mqKV.used,
    remaining: Math.max(0, FREE_MONTHLY_MEETINGS - mqKV.used),
    limit: FREE_MONTHLY_MEETINGS,
  });
}

/**
 * POST /api/v2/experiment/assign — Sticky A/B experiment assignment.
 */
async function handleExperimentAssign(request, env) {
  const body = await request.json();
  const mid = requireMachineId(body);
  if (!mid) return jsonResponse({ error: "machine_id required" }, 400);

  const experiment = body.experiment;
  if (!experiment || typeof experiment !== "string") {
    return jsonResponse({ error: "experiment name required" }, 400);
  }

  let expKV = await env.STATE.get(`exp:${mid}`, "json");
  if (!expKV) expKV = {};

  // Already assigned — return sticky value
  if (expKV[experiment]) {
    return jsonResponse({
      variant: expKV[experiment],
      source: "server",
    });
  }

  // New assignment: deterministic hash-based
  const encoder = new TextEncoder();
  const data = encoder.encode(`${mid}:${experiment}`);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = new Uint8Array(hashBuffer);
  const hashValue = (hashArray[0] << 8 | hashArray[1]) % 100;

  // Default 2-way split: control vs variant_a
  const variant = hashValue < 50 ? "control" : "variant_a";
  expKV[experiment] = variant;

  await env.STATE.put(`exp:${mid}`, JSON.stringify(expKV), {
    expirationTtl: EXPERIMENT_TTL_SECONDS,
  });

  return jsonResponse({
    variant,
    source: "server",
  });
}

/**
 * POST /api/v2/heartbeat — License heartbeat (24h).
 * Replaces clouvel-license-webhook /heartbeat.
 */
async function handleHeartbeat(request, env) {
  const body = await request.json();
  const licenseKey = body.license_key || body.licenseKey;
  if (!licenseKey) return jsonResponse({ error: "license_key required" }, 400);

  const result = await validateLicense(env, licenseKey);
  if (!result) {
    return jsonResponse({ valid: false, error: "validation_failed" });
  }

  return jsonResponse({
    valid: result.valid,
    tier: result.tier,
    next_heartbeat_seconds: LICENSE_CACHE_TTL_SECONDS,
  });
}

/**
 * GET /api/v2/check — Revocation check.
 * Replaces clouvel-license-webhook /check.
 */
async function handleRevocationCheck(request, env) {
  const url = new URL(request.url);
  const licenseKey = url.searchParams.get("key");
  if (!licenseKey) return jsonResponse({ error: "key param required" }, 400);

  const cacheKey = `license:${licenseKey}`;
  const cached = await env.STATE.get(cacheKey, "json");

  if (cached) {
    return jsonResponse({
      valid: cached.valid,
      tier: cached.tier,
      source: "cache",
    });
  }

  // Not in cache — validate fresh
  const result = await validateLicense(env, licenseKey);
  if (!result) {
    return jsonResponse({ valid: false, source: "fresh", error: "validation_failed" });
  }

  return jsonResponse({
    valid: result.valid,
    tier: result.tier,
    source: "fresh",
  });
}

// ============================================================
// Existing v3 handlers (unchanged)
// ============================================================

async function handleManager(request) {
  const clientVersion = request.headers.get("X-Clouvel-Version");
  if (!isVersionAcceptable(clientVersion)) return upgradeRequiredResponse();

  const body = await request.json();
  const isPro = hasValidLicense(body);
  const activeManagers = isPro ? ALL_MANAGERS : FREE_MANAGERS;
  const topic = body.topic || "feature";

  const feedback = {};
  const managerData = {
    PM: { emoji: "\ud83d\udc54", title: "Product Manager", questions: ["Is this in the PRD?", "What is the MVP scope?", "What is the acceptance criteria?"] },
    CTO: { emoji: "\ud83d\udee0\ufe0f", title: "CTO", questions: ["Does this follow existing patterns?", "What is the maintenance burden?"] },
    QA: { emoji: "\ud83e\uddea", title: "QA Lead", questions: ["What are the edge cases?", "How will you test this?"] },
    CDO: { emoji: "\ud83c\udfa8", title: "Design Officer", questions: ["Is the UX intuitive?", "Does it match the design system?"] },
    CFO: { emoji: "\ud83d\udcb0", title: "CFO", questions: ["What is the cost impact?", "ROI calculation?"] },
    CSO: { emoji: "\ud83d\udd12", title: "Security Officer", questions: ["Any security concerns?", "Data protection compliance?"] },
    CMO: { emoji: "\ud83d\udce3", title: "Marketing Officer", questions: ["How will users discover this?", "Messaging strategy?"] },
    ERROR: { emoji: "\ud83d\udd25", title: "Error Prevention", questions: ["What could go wrong?", "Recovery plan?"] },
  };

  for (const mgr of activeManagers) feedback[mgr] = managerData[mgr];

  let formattedOutput = `## \ud83d\udca1 C-Level Perspectives\n\n`;
  formattedOutput += `**Topic**: ${topic}\n\n`;
  for (const mgr of activeManagers) {
    const d = managerData[mgr];
    formattedOutput += `**${d.emoji} ${d.title}**: ${d.questions.join(" ")}\n\n`;
  }

  const missedPerspectives = {};
  if (!isPro) {
    formattedOutput += `---\n\n`;
    formattedOutput += `**\ud83d\udc8e Pro: 7 more managers** (CTO, QA, CDO, CMO, CFO, CSO, ERROR)\n`;
    formattedOutput += `\u2192 https://polar.sh/clouvel (code: FIRST01)\n`;
    for (const mgr of ALL_MANAGERS) {
      if (!activeManagers.includes(mgr)) {
        missedPerspectives[mgr] = { emoji: managerData[mgr].emoji, hint: managerData[mgr].title };
      }
    }
  }

  return jsonResponse({
    topic,
    active_managers: activeManagers,
    feedback,
    formatted_output: formattedOutput,
    missed_perspectives: Object.keys(missedPerspectives).length > 0 ? missedPerspectives : undefined,
    tier: isPro ? "pro" : "free",
  });
}

async function handleShip(request) {
  const clientVersion = request.headers.get("X-Clouvel-Version");
  if (!isVersionAcceptable(clientVersion)) return upgradeRequiredResponse();

  const body = await request.json();
  const isPro = hasValidLicense(body);

  return jsonResponse({
    allowed: true,
    tier: isPro ? "pro" : "free",
    message: isPro ? "Pro license verified" : "FREE tier - ship allowed",
  });
}

async function handleTrialStatus(request) {
  const clientVersion = request.headers.get("X-Clouvel-Version");
  if (!isVersionAcceptable(clientVersion)) return upgradeRequiredResponse();

  return jsonResponse({
    tier: "free",
    features: {
      managers: FREE_MANAGERS,
      can_code_mode: "warn",
      project_limit: 1,
    },
    upgrade_url: "https://polar.sh/clouvel",
  });
}

// ============================================================
// Main fetch handler
// ============================================================

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") return handleCors();

    // --- v4.0 endpoints (server-side state) ---
    if (path === "/api/v2/sync" && request.method === "POST") {
      return handleSync(request, env);
    }
    if (path === "/api/v2/trial/start" && request.method === "POST") {
      return handleTrialStart(request, env);
    }
    if (path === "/api/v2/project/register" && request.method === "POST") {
      return handleProjectRegister(request, env);
    }
    if (path === "/api/v2/meeting/consume" && request.method === "POST") {
      return handleMeetingConsume(request, env);
    }
    if (path === "/api/v2/experiment/assign" && request.method === "POST") {
      return handleExperimentAssign(request, env);
    }
    if (path === "/api/v2/heartbeat" && request.method === "POST") {
      return handleHeartbeat(request, env);
    }
    if (path === "/api/v2/check" && request.method === "GET") {
      return handleRevocationCheck(request, env);
    }

    // --- Existing v3 endpoints ---
    if (path === "/api/manager" && request.method === "POST") {
      return handleManager(request);
    }
    if (path === "/api/ship" && request.method === "POST") {
      return handleShip(request);
    }
    if (path === "/api/trial/status" && request.method === "GET") {
      return handleTrialStatus(request);
    }

    // Health check
    if (path === "/" || path === "/health") {
      return jsonResponse({
        status: "ok",
        version: "4.0.0",
        min_client_version: MIN_VERSION,
        endpoints: {
          v2: ["/api/v2/sync", "/api/v2/trial/start", "/api/v2/project/register",
               "/api/v2/meeting/consume", "/api/v2/experiment/assign",
               "/api/v2/heartbeat", "/api/v2/check"],
          v3: ["/api/manager", "/api/ship", "/api/trial/status"],
        },
      });
    }

    return jsonResponse({ error: "not_found", path }, 404);
  },
};
