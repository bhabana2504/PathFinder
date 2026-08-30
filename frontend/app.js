// --- CENTRAL API CLIENT & AUTH STATE ---
const BASE_URL = window.location.origin === "null" || window.location.protocol === "file:" || !window.location.host.includes("8000")
  ? "http://127.0.0.1:8000"
  : ""; 
let currentUser = null;
let token = localStorage.getItem("token");

// Central state for Auth Modal
let authState = "login"; // "login" or "register"

// Telemetry terminal logger
function logToTerminal(tag, type, message) {
  const terminalBody = document.querySelector(".terminal-logs-body");
  if (!terminalBody) return;
  const now = new Date();
  const timeStr = `[${now.toTimeString().split(' ')[0]}]`;
  const line = document.createElement("div");
  line.className = "log-line";
  line.innerHTML = `<span class="log-timestamp">${timeStr}</span> <span class="log-tag tag-${type}">${tag.toUpperCase()}</span> ${message}`;
  terminalBody.appendChild(line);
  terminalBody.scrollTop = terminalBody.scrollHeight;
}

// Global API Fetch wrapper
async function apiRequest(endpoint, method = "GET", body = null) {
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  const options = { method, headers };
  if (body) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (response.status === 401) {
      localStorage.removeItem("token");
      token = null;
      currentUser = null;
      updateNavbarState();
      showToast("Session expired. Please sign in.", "error");
      openAuthModal("login");
      window.location.hash = "#discover";
      throw new Error("Unauthorized");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(errorData.detail || "API request failed");
    }

    if (response.status === 204) return {};
    return await response.json();
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
}

// Toast notification alerts
function showToast(message, type = "success") {
  const toast = document.getElementById("notification-toast");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4000);
}

// Global visual spinner
function showLoader(visible, text = "Loading...") {
  const loader = document.getElementById("global-loader");
  const loaderText = document.getElementById("loader-text");
  if (loaderText) loaderText.textContent = text;
  if (loader) {
    if (visible) loader.classList.remove("hidden");
    else loader.classList.add("hidden");
  }
}

function updateNavbarState() {
  const loginActionBtn = document.getElementById("btn-auth-action");
  const ctaActionBtn = document.getElementById("btn-cta-action");

  if (token) {
    if (loginActionBtn) loginActionBtn.textContent = "Log out";
    if (ctaActionBtn) {
      ctaActionBtn.innerHTML = 'Build my path <i data-lucide="arrow-right" style="width: 15px; height: 15px;"></i>';
      ctaActionBtn.href = "#dashboard";
    }
  } else {
    if (loginActionBtn) loginActionBtn.textContent = "Log in";
    if (ctaActionBtn) {
      ctaActionBtn.innerHTML = 'Build my path <i data-lucide="arrow-right" style="width: 15px; height: 15px;"></i>';
      ctaActionBtn.href = "#onboarding";
    }
  }
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// --- ROUTER SYSTEM ---
const AUTHENTICATED_VIEWS = ["dashboard", "skills", "roadmap", "progress", "profile", "onboarding"];

async function handleRouting() {
  const hash = window.location.hash || "#discover";
  const viewName = hash.replace("#", "");

  // Update active links in top Navbar
  document.querySelectorAll(".site-nav .nav-links a").forEach(item => {
    item.classList.remove("active");
    if (item.getAttribute("data-view") === viewName) {
      item.classList.add("active");
    }
  });

  // Authentication guards
  if (AUTHENTICATED_VIEWS.includes(viewName)) {
    if (!token) {
      showToast("Access restricted. Please log in first.", "error");
      window.location.hash = "#discover";
      openAuthModal("login");
      return;
    }
  }

  // Toggle View elements
  document.querySelectorAll("main > .view").forEach(section => {
    section.classList.add("hidden");
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.remove("hidden");
    // Lazy-load data
    loadViewData(viewName);
  } else {
    document.getElementById("view-discover").classList.remove("hidden");
    loadViewData("discover");
  }

  // Refresh lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Update header solid background immediately on route transition
  updateHeaderScroll();
}

function updateHeaderScroll() {
  const header = document.querySelector(".site-nav");
  if (!header) return;
  const hash = window.location.hash || "#discover";
  const viewName = hash.replace("#", "");
  
  if (viewName === "discover" && window.scrollY < 50) {
    header.classList.remove("nav-solid");
  } else {
    header.classList.add("nav-solid");
  }
}

window.addEventListener("scroll", updateHeaderScroll);
window.addEventListener("hashchange", handleRouting);

// Load data corresponding to view name
async function loadViewData(viewName) {
  showLoader(true, `Loading ${viewName} atlas...`);
  try {
    if (viewName === "discover") {
      await loadDiscoverView();
    } else if (viewName === "careers") {
      await loadCareersView();
    } else if (viewName === "skills") {
      await loadSkillsView();
    } else if (viewName === "resources") {
      await loadResourcesView();
    } else if (viewName === "roadmap") {
      await loadRoadmapView();
    } else if (viewName === "progress") {
      await loadProgressView();
    } else if (viewName === "dashboard") {
      await loadDashboardView();
    } else if (viewName === "profile") {
      await loadProfileView();
    } else if (viewName === "onboarding") {
      await initOnboardingWizard();
    }
  } catch (err) {
    console.error(`Error loading view ${viewName}:`, err);
    showToast(err.message || "Failed to sync visual templates", "error");
  } finally {
    showLoader(false);
  }
}

// --- 1. DISCOVER VIEW LOADER ---
async function loadDiscoverView() {
  const [cList, rList] = await Promise.all([
    apiRequest("/api/careers"),
    apiRequest("/api/resources")
  ]);

  // Render 4 preview careers
  const grid = document.getElementById("discover-careers-grid");
  grid.innerHTML = "";
  const colorSchemes = ["coral", "teal", "ink", "gold"];
  
  cList.slice(0, 4).forEach((c, i) => {
    const color = colorSchemes[i % 4];
    const item = document.createElement("a");
    item.href = "#careers";
    item.className = `career-card card-${color}`;
    item.innerHTML = `
      <span class="card-number">0${i + 1}</span>
      <span class="card-arrow"><i data-lucide="move-up-right" style="width: 18px; height: 18px;"></i></span>
      <div class="career-glyph"><i data-lucide="target" style="width: 30px; height: 30px;"></i></div>
      <h3>${c.name}</h3>
      <p>${c.description || 'Develop skills to match this career objective.'}</p>
      <div class="card-meta">
        <span>${c.required_skills.slice(0, 3).join(" • ")}</span>
        <span>18–24 mos</span>
      </div>
    `;
    grid.appendChild(item);
  });

  // Render top 3 resources preview
  const resGrid = document.getElementById("discover-resources-grid");
  resGrid.innerHTML = "";
  rList.slice(0, 3).forEach((r, i) => {
    const item = document.createElement("article");
    item.className = "resource-card";
    const colors = ["#e8785c", "#258c83", "#e1b24c"];
    item.style.setProperty("--card-color", colors[i % 3]);
    item.innerHTML = `
      <div class="resource-cover">
        <span class="resource-type">${r.resource_type}</span>
        <i data-lucide="book-open" style="width: 28px; height: 28px;"></i>
        <strong>${r.title}</strong>
        <span class="resource-spine">PathFinder / 0${i + 1}</span>
      </div>
      <div class="resource-info">
        <div>
          <span class="micro-label">AI PICK • 94% match</span>
          <h3>${r.title}</h3>
        </div>
        <button class="icon-button"><i data-lucide="arrow-right" style="width: 17px; height: 17px;"></i></button>
        <div class="resource-meta">
          <span>${r.skill}</span>
          <span>${r.estimated_hours}h</span>
          <span>${r.difficulty}</span>
        </div>
      </div>
    `;
    resGrid.appendChild(item);
  });

  // Render mini roadmap preview
  const miniRoadmap = document.getElementById("discover-roadmap-preview");
  miniRoadmap.innerHTML = "";
  const nodes = ["Start point", "Python Fundamentals", "Machine Learning", "RAG Systems", "AI Engineer Goal"];
  nodes.forEach((n, i) => {
    const item = document.createElement("div");
    item.className = `mini-node ${i < 2 ? 'done' : i === 2 ? 'current' : ''}`;
    item.innerHTML = `
      <span>
        ${i < 2 ? '<i data-lucide="check" style="width: 13px; height: 13px;"></i>' : 
          i === 2 ? '<i data-lucide="sparkles" style="width: 13px; height: 13px;"></i>' : 
          '<i data-lucide="lock" style="width: 12px; height: 12px;"></i>'}
      </span>
      <strong>${n}</strong>
      ${i < nodes.length - 1 ? '<i></i>' : ''}
    `;
    miniRoadmap.appendChild(item);
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// --- 2. CAREERS EXPLORER VIEW LOADER ---
async function loadCareersView() {
  const cList = await apiRequest("/api/careers");

  document.getElementById("career-count").innerHTML = `${cList.length} paths in the atlas`;

  const grid = document.getElementById("careers-explorer-grid");
  grid.innerHTML = "";
  const colorSchemes = ["coral", "teal", "ink", "gold"];
  
  cList.forEach((c, i) => {
    const color = colorSchemes[i % 4];
    const card = document.createElement("div");
    card.className = `career-card card-${color}`;
    card.innerHTML = `
      <span class="card-number">0${i + 1}</span>
      <span class="card-arrow"><i data-lucide="move-up-right" style="width: 18px; height: 18px;"></i></span>
      <div class="career-glyph"><i data-lucide="target" style="width: 30px; height: 30px;"></i></div>
      <h3>${c.name}</h3>
      <p>${c.description || 'Acquire required skills to land this job role.'}</p>
      <div class="card-meta">
        <span>${c.required_skills.join(" • ")}</span>
        <span>18–24 mos</span>
      </div>
    `;
    // Click triggers onboarding wizard with pre-selected career
    card.addEventListener("click", () => {
      onboardingSelectedCareer = c.name;
      window.location.hash = "#onboarding";
    });
    grid.appendChild(card);
  });

  // Render Compare paths bars
  const compareBox = document.getElementById("compare-bars-container");
  compareBox.innerHTML = "";
  const mockSkills = [
    { name: "Python Programming", current: 75, offset: 0 },
    { name: "Machine Learning", current: 40, offset: 10 },
    { name: "RAG & LLMs", current: 20, offset: 15 }
  ];
  mockSkills.forEach(s => {
    const row = document.createElement("div");
    row.className = "compare-row";
    row.innerHTML = `
      <span>${s.name}</span>
      <div>
        <i style="width: ${s.current}%"></i>
        <b>${s.current + s.offset}%</b>
      </div>
    `;
    compareBox.appendChild(row);
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// --- 3. SKILL GAP VIEW LOADER ---
async function loadSkillsView() {
  const gaps = await apiRequest("/api/skill-gap");
  const report = await apiRequest("/api/progress/report");

  // Update readiness value
  const readinessText = document.getElementById("readiness-value-text");
  const percent = Math.round(report.current_readiness * 100);
  if (readinessText) {
    readinessText.innerHTML = `${percent}<small>%</small>`;
  }

  // Draw comparison rows
  const listContainer = document.getElementById("skills-rows-container");
  listContainer.innerHTML = "";

  const gapKeys = Object.keys(gaps.gap_analysis).sort((a, b) => {
    const scoreA = gaps.skill_scores[a] || 0;
    const scoreB = gaps.skill_scores[b] || 0;
    return scoreB - scoreA;
  });

  gapKeys.forEach((skillName, i) => {
    const analysis = gaps.gap_analysis[skillName];
    const currentPercent = Math.round((analysis.current || 0) * 100);
    const targetPercent = Math.round((analysis.required || 0.8) * 100);
    const gapPercent = Math.round((analysis.gap || 0) * 100);
    const priorityScore = Math.round((gaps.skill_scores[skillName] || 0.5) * 100);

    const row = document.createElement("div");
    row.className = "skill-row";
    row.setAttribute("data-testid", `skill-row-${i}`);
    row.innerHTML = `
      <div class="skill-name">
        <strong>${skillName}</strong>
        <small>Priority ${priorityScore}</small>
      </div>
      <div class="skill-bars">
        <span style="width: ${targetPercent}%"></span>
        <i style="width: ${currentPercent}%"></i>
      </div>
      <strong class="gap-value">${gapPercent}% gap</strong>
    `;
    listContainer.appendChild(row);
  });

  if (gapKeys.length === 0) {
    listContainer.innerHTML = `<p class="empty-text" style="padding: 20px 0;">No gaps found! Complete onboarding to select skills.</p>`;
  }

  // Populates priority learning checklist
  const priorityContainer = document.getElementById("skills-priority-items-container");
  priorityContainer.innerHTML = "";
  
  gapKeys.forEach((skillName, i) => {
    const priorityScore = Math.round((gaps.skill_scores[skillName] || 0.5) * 100);
    const item = document.createElement("div");
    item.className = "priority-item";
    item.innerHTML = `
      <span>0${i + 1}</span>
      <strong>${skillName}</strong>
      <em>${priorityScore}</em>
      <i data-lucide="arrow-right" style="width: 16px; height: 16px; color: var(--coral);"></i>
    `;
    priorityContainer.appendChild(item);
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// --- 4. RESOURCE LIBRARY VIEW LOADER ---
let fullResourcesList = [];

async function loadResourcesView() {
  const [res, recs] = await Promise.all([
    apiRequest("/api/resources"),
    apiRequest("/api/recommendations").catch(() => ({ recommendations: [] }))
  ]);

  // Combine resources with score data
  fullResourcesList = res.map(r => {
    const match = recs.recommendations.find(rec => rec.title === r.title);
    return {
      ...r,
      score: match ? Math.round(match.match_score * 100) : 75,
      suitability_score: match ? match.match_score : 0.75,
      reason: match ? match.reason : "Provides core skills for selected track.",
      breakdown: match ? match.score_breakdown : null
    };
  });

  // Populate Skill filter options
  const filterSkillSelect = document.getElementById("filter-skill-select");
  const uniqueSkills = Array.from(new Set(fullResourcesList.map(r => r.skill)));
  filterSkillSelect.innerHTML = `<option value="">All Skills</option>`;
  uniqueSkills.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    filterSkillSelect.appendChild(opt);
  });

  renderFilteredResources();
}

// Filter and render resources
function renderFilteredResources() {
  const searchVal = document.getElementById("resource-search-input").value.toLowerCase();
  const skillVal = document.getElementById("filter-skill-select").value;
  const diffVal = document.getElementById("filter-difficulty-select").value;
  const sortVal = document.getElementById("sort-relevance-select").value;

  let filtered = fullResourcesList.filter(r => {
    const matchesSearch = r.title.toLowerCase().includes(searchVal) || r.skill.toLowerCase().includes(searchVal);
    const matchesSkill = !skillVal || r.skill === skillVal;
    const matchesDiff = !diffVal || r.difficulty.toLowerCase() === diffVal.toLowerCase();
    return matchesSearch && matchesSkill && matchesDiff;
  });

  // Sort resources
  if (sortVal === "match") {
    filtered.sort((a, b) => b.suitability_score - a.suitability_score);
  } else if (sortVal === "duration") {
    filtered.sort((a, b) => a.estimated_hours - b.estimated_hours);
  }

  const grid = document.getElementById("resources-library-grid");
  const emptyState = document.getElementById("library-empty-state");
  grid.innerHTML = "";

  if (filtered.length === 0) {
    emptyState.classList.remove("hidden");
  } else {
    emptyState.classList.add("hidden");
    
    filtered.forEach((r, i) => {
      const card = document.createElement("div");
      card.className = "resource-card";
      card.setAttribute("data-testid", `resource-card-${i}`);
      const colors = ["#e8785c", "#258c83", "#e1b24c", "#17352f"];
      card.style.setProperty("--card-color", colors[i % 4]);
      
      card.innerHTML = `
        <div class="resource-cover">
          <span class="resource-type">${r.resource_type}</span>
          <i data-lucide="book-open" style="width: 28px; height: 28px;"></i>
          <strong>${r.title}</strong>
          <span class="resource-spine">PathFinder / 0${i + 1}</span>
        </div>
        <div class="resource-info">
          <div>
            <span class="micro-label">AI PICK • ${r.score}% match</span>
            <h3>${r.title}</h3>
            <p style="font-size: 12px; margin-top: 5px; color: var(--muted);">${r.reason}</p>
          </div>
          <button class="icon-button btn-explain-toggle" data-index="${i}">
            <i data-lucide="chevron-down" style="width: 15px; height: 15px;"></i>
          </button>
          
          <!-- Explain panel, collapsed by default -->
          <div id="explain-panel-${i}" class="explain-panel hidden">
            <h4>Match Score Breakdown</h4>
            <div class="explain-metrics">
              <div class="explain-metric">
                <strong>${r.breakdown ? Math.round(r.breakdown.career_relevance * 100) : 80}%</strong>
                <span>Career Relevance</span>
              </div>
              <div class="explain-metric">
                <strong>${r.breakdown ? Math.round(r.breakdown.difficulty_match * 100) : 75}%</strong>
                <span>Difficulty Match</span>
              </div>
              <div class="explain-metric">
                <strong>${r.breakdown ? Math.round(r.breakdown.schedule_alignment * 100) : 85}%</strong>
                <span>Schedule Alignment</span>
              </div>
            </div>
          </div>

          <div class="resource-meta">
            <span>${r.skill}</span>
            <span>${r.estimated_hours}h</span>
            <span>${r.difficulty}</span>
          </div>
        </div>
      `;

      // Toggle match score explanation panel
      card.querySelector(".btn-explain-toggle").addEventListener("click", (e) => {
        e.stopPropagation();
        const btn = e.currentTarget;
        const panel = card.querySelector(".explain-panel");
        panel.classList.toggle("hidden");
        const icon = btn.querySelector("i");
        if (panel.classList.contains("hidden")) {
          btn.innerHTML = `<i data-lucide="chevron-down" style="width: 15px; height: 15px;"></i>`;
        } else {
          btn.innerHTML = `<i data-lucide="chevron-up" style="width: 15px; height: 15px;"></i>`;
        }
        if (window.lucide) window.lucide.createIcons();
      });

      grid.appendChild(card);
    });
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Add event listeners for library filters
document.getElementById("resource-search-input").addEventListener("input", renderFilteredResources);
document.getElementById("filter-skill-select").addEventListener("change", renderFilteredResources);
document.getElementById("filter-difficulty-select").addEventListener("change", renderFilteredResources);
document.getElementById("sort-relevance-select").addEventListener("change", renderFilteredResources);


// --- 5. LEARNING PATH ROADMAP VIEW LOADER ---
async function loadRoadmapView() {
  const path = await apiRequest("/api/learning-path");

  const timeline = document.getElementById("roadmap-timeline-container");
  timeline.innerHTML = "";

  if (path.nodes.length === 0) {
    timeline.innerHTML = `<p class="empty-text">No path milestones computed. Complete onboarding settings first.</p>`;
    return;
  }

  path.nodes.forEach((node, i) => {
    const isDone = node.state === "completed";
    const isCurrent = node.state === "available";
    const isLocked = node.state === "locked";

    const item = document.createElement("div");
    item.className = `road-node ${node.state}`;
    item.innerHTML = `
      <div class="node-bubble">
        ${isDone ? '<i data-lucide="check" style="width: 16px; height: 16px;"></i>' : 
          isCurrent ? '<i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>' : 
          '<i data-lucide="lock" style="width: 15px; height: 15px;"></i>'}
      </div>
      <div>
        <span>STEP 0${i + 1} • ${node.skill}</span>
        <h3>${node.title}</h3>
        <p>${node.state === 'completed' ? 'Completed milestone!' : 
          node.state === 'available' ? 'Current focused learning target.' : 
          'Milestone locked. Complete prerequisites to unlock.'}</p>
      </div>
      ${i < path.nodes.length - 1 ? '<i class="road-connector"></i>' : ''}
    `;
    timeline.appendChild(item);
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}


// --- 6. PROGRESS VIEW LOADER ---
async function loadProgressView() {
  const report = await apiRequest("/api/progress/report");
  const profile = await apiRequest("/api/learners/profile");

  // Populate numbers
  document.getElementById("progress-hours-completed").textContent = `${report.learning_hours_logged}h`;
  document.getElementById("progress-completed-count").textContent = report.completed_count;
  document.getElementById("progress-streak-count").textContent = report.streak_count || 12;

  // Render consistency Heatmap grid (84 blocks representing days)
  const heatmap = document.getElementById("progress-heatmap-container");
  heatmap.innerHTML = "";
  
  // Construct 84 days. We will shade some based on learning sessions completed
  for (let i = 0; i < 84; i++) {
    const day = document.createElement("i");
    // Generate mock consistent pattern
    let heat = 0;
    if (i % 7 === 0) heat = 3;
    else if (i % 3 === 0) heat = 1;
    else if (i % 5 === 0) heat = 2;
    else if (i % 11 === 0) heat = 4;
    
    day.className = `heat-${heat}`;
    day.setAttribute("data-testid", `heatmap-day-${i}`);
    day.title = `Day ${i}: ${heat} learning sessions logged`;
    heatmap.appendChild(day);
  }

  // Populate Achievements milestones list
  const container = document.getElementById("progress-achievements-container");
  container.innerHTML = "";
  
  const achievements = [
    { title: "PATH BUILDER", desc: "Completed your first roadmap step", unlocked: report.completed_count > 0 },
    { title: "CONSISTENCY ACE", desc: "Logged sessions 5 days in a row", unlocked: report.streak_count >= 5 },
    { title: "PYTHON MASTER", desc: "Reach 80% Python proficiency", unlocked: profile.current_skills.includes("Python") },
    { title: "RAG EXPLORER", desc: "Complete your first RAG project", unlocked: profile.completed_resources.length > 5 }
  ];

  achievements.forEach((ach, i) => {
    const item = document.createElement("div");
    item.className = `achievement ${ach.unlocked ? 'unlocked' : 'locked'}`;
    item.setAttribute("data-testid", `achievement-${i}`);
    item.innerHTML = `
      <span>
        ${ach.unlocked ? '<i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>' : 
          '<i data-lucide="lock" style="width: 15px; height: 15px;"></i>'}
      </span>
      <div>
        <strong>${ach.title}</strong>
        <small>${ach.desc}</small>
      </div>
    `;
    container.appendChild(item);
  });

  // Populate Assessment Simulator skills dropdown selection
  const assessDropdown = document.getElementById("assess-skill");
  assessDropdown.innerHTML = "";
  
  if (profile.current_skills && profile.current_skills.length > 0) {
    profile.current_skills.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      assessDropdown.appendChild(opt);
    });
  } else {
    // Fallback if onboarding not complete
    const fallback = ["Python", "Statistics", "Machine Learning", "RAG + LLMs"];
    fallback.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      assessDropdown.appendChild(opt);
    });
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Submit assessment simulator grade
document.getElementById("form-assessment").addEventListener("submit", async (e) => {
  e.preventDefault();
  const skill = document.getElementById("assess-skill").value;
  const score = parseFloat(document.getElementById("assess-score").value);

  showLoader(true, "Submitting assessment grade...");
  try {
    const res = await apiRequest("/api/progress/assessment", "POST", { skill_name: skill, score: score });
    showToast(`Assessment submitted! New proficiency: ${res.new_proficiency.toFixed(2)}`);
    logToTerminal("progress", "ok", `Submitted ${skill} quiz grade: ${score}. Adjusted level: ${res.new_proficiency.toFixed(2)}`);
    await loadProgressView();
  } catch (err) {
    showToast(err.message || "Failed to submit assessment grading", "error");
  } finally {
    showLoader(false);
  }
});


// --- 7. DASHBOARD VIEW LOADER ---
let currentFocusResourceId = null;

async function loadDashboardView() {
  const [profile, gaps, path, recs] = await Promise.all([
    apiRequest("/api/learners/profile"),
    apiRequest("/api/skill-gap"),
    apiRequest("/api/learning-path"),
    apiRequest("/api/recommendations")
  ]);

  currentUser = profile;
  logToTerminal("system", "ok", `Telemetry synced for career goal: ${profile.career_goal}.`);

  // Welcome user
  document.getElementById("dashboard-user-kicker").textContent = `Good evening, ${profile.name || "Student"}`;
  document.getElementById("dashboard-user-title").innerHTML = `Your path to <em>${profile.career_goal}</em>.`;

  // Stats row
  const readinessVal = Math.round(path.completion_percentage);
  document.getElementById("dash-readiness-text").textContent = `${readinessVal}%`;
  document.getElementById("dash-skills-count").textContent = profile.current_skills.length;
  
  // Weekly hours logged
  const totalLoggedHours = 8.5; // Mock weekly progress tracking
  document.getElementById("dash-week-hours").textContent = `${totalLoggedHours}h`;
  document.getElementById("dash-total-hours-label").textContent = `${totalLoggedHours} hours`;

  // Focus next course item
  const focusTitle = document.getElementById("dash-focus-title");
  const focusSub = document.getElementById("dash-focus-subtitle");
  const focusActions = document.getElementById("focus-resource-actions");
  
  focusActions.innerHTML = "";

  if (path.current_node) {
    currentFocusResourceId = path.current_node.resource_id;
    focusTitle.textContent = path.current_node.title;
    focusSub.textContent = `Skill: ${path.current_node.skill} • Duration: ${path.current_node.estimated_hours} hrs`;
    
    // Inject Mark Complete button
    focusActions.innerHTML = `
      <button id="btn-dash-complete" class="button button-coral" style="padding: 8px 16px; font-size: 11px;">
        Mark as complete <i data-lucide="check" style="width: 14px; height: 14px;"></i>
      </button>
    `;

    // Button event listener
    document.getElementById("btn-dash-complete").addEventListener("click", async () => {
      showLoader(true, "Marking course focus completed...");
      try {
        await apiRequest("/api/progress/complete", "POST", { resource_id: currentFocusResourceId, rating: 5.0 });
        showToast("Completed milestone! Roadmap updated.");
        logToTerminal("progress", "ok", `Logged completion: ${path.current_node.title}.`);
        await loadDashboardView();
      } catch (err) {
        showToast(err.message || "Failed to mark complete", "error");
      } finally {
        showLoader(false);
      }
    });

  } else {
    currentFocusResourceId = null;
    focusTitle.textContent = "Roadmap fully completed!";
    focusSub.textContent = "Great job! You achieved your required career target competencies.";
  }

  // Populate weekly rhythm charts Mon-Sun (mock data aligned with weekly commitment)
  const barsBox = document.getElementById("dashboard-week-bars");
  barsBox.innerHTML = "";
  const values = [1.5, 2.0, 1.0, 2.5, 0.5, 1.0, 0.0];
  values.forEach((v, i) => {
    const block = document.createElement("div");
    block.innerHTML = `
      <i style="height: ${v * 25}px"></i>
      <small>${["M", "T", "W", "T", "F", "S", "S"][i]}</small>
    `;
    barsBox.appendChild(block);
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}


// --- 8. PROFILE SETTINGS VIEW LOADER ---
async function loadProfileView() {
  const [profile, cList] = await Promise.all([
    apiRequest("/api/learners/profile"),
    apiRequest("/api/careers")
  ]);

  document.getElementById("profile-name").value = profile.name || "";
  document.getElementById("profile-experience").value = profile.experience_level;
  document.getElementById("profile-hours").value = profile.learning_hours_per_week;
  document.getElementById("profile-hours-indicator").textContent = `${profile.learning_hours_per_week} Hours`;
  document.getElementById("profile-interests").value = profile.interests.join(", ");

  // Populate careers drop down
  const careerSelect = document.getElementById("profile-career");
  careerSelect.innerHTML = "";
  cList.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.name;
    opt.textContent = c.name;
    if (c.name === profile.career_goal) {
      opt.selected = true;
    }
    careerSelect.appendChild(opt);
  });
}

// Profile schedule hours slider indicator
document.getElementById("profile-hours").addEventListener("input", (e) => {
  document.getElementById("profile-hours-indicator").textContent = `${e.target.value} Hours`;
});

// Profile Settings Form submission handler
document.getElementById("form-profile").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("profile-name").value;
  const career = document.getElementById("profile-career").value;
  const experience = document.getElementById("profile-experience").value;
  const hours = parseFloat(document.getElementById("profile-hours").value);
  const rawInterests = document.getElementById("profile-interests").value;
  const interests = rawInterests.split(",").map(i => i.trim()).filter(i => i.length > 0);

  const successBanner = document.getElementById("profile-success-banner");
  const errorBanner = document.getElementById("profile-error-banner");
  successBanner.classList.add("hidden");
  errorBanner.classList.add("hidden");

  showLoader(true, "Saving profile changes...");
  try {
    await apiRequest("/api/learners/profile", "POST", {
      name,
      career_goal: career,
      experience_level: experience,
      learning_hours_per_week: hours,
      interests: interests.length > 0 ? interests : [career],
      current_skills: currentUser ? currentUser.current_skills : []
    });
    successBanner.classList.remove("hidden");
    logToTerminal("system", "ok", "Profile settings saved. Telemetry recalculated.");
    showToast("Profile settings updated!");
  } catch (err) {
    errorBanner.textContent = err.message || "Failed to update profile settings.";
    errorBanner.classList.remove("hidden");
  } finally {
    showLoader(false);
  }
});


// --- 9. ONBOARDING WIZARD WORKFLOWS ---
let onboardingStep = 1;
let onboardingSelectedCareer = "";
let onboardingSelectedSkills = [];
let onboardingCareers = [];
let onboardingSkills = [];

async function initOnboardingWizard() {
  onboardingStep = 1;
  onboardingSelectedSkills = [];
  
  showLoader(true, "Loading career atlas...");
  try {
    const [cList, sList] = await Promise.all([
      apiRequest("/api/careers"),
      apiRequest("/api/skills")
    ]);
    onboardingCareers = cList;
    onboardingSkills = sList;

    renderOnboardingCareers();
    renderOnboardingSkills();
    renderWizardStep();
  } catch (err) {
    showToast("Failed to load onboarding tracks", "error");
  } finally {
    showLoader(false);
  }
}

function renderWizardStep() {
  // Toggle step panels
  document.querySelectorAll(".wizard-panel").forEach(p => p.classList.add("hidden"));
  document.getElementById(`wiz-step-${onboardingStep}`).classList.remove("hidden");

  // Toggle wizard active steps indicators
  document.querySelectorAll(".wizard-progress .wiz-step").forEach((el, index) => {
    if (index + 1 <= onboardingStep) el.classList.add("active");
    else el.classList.remove("active");
  });

  const prevBtn = document.getElementById("btn-wiz-prev");
  const nextBtn = document.getElementById("btn-wiz-next");

  if (onboardingStep > 1) prevBtn.classList.remove("hidden");
  else prevBtn.classList.add("hidden");

  if (onboardingStep === 4) {
    nextBtn.innerHTML = `Complete Onboarding <i data-lucide="check" style="width: 14px; height: 14px;"></i>`;
    renderOnboardingSummary();
  } else {
    nextBtn.innerHTML = `Continue <i data-lucide="arrow-right" style="width: 14px; height: 14px;"></i>`;
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function renderOnboardingCareers() {
  const container = document.getElementById("onboarding-careers-grid");
  container.innerHTML = "";

  onboardingCareers.forEach(c => {
    const card = document.createElement("div");
    card.className = `career-select-card ${onboardingSelectedCareer === c.name ? 'selected' : ''}`;
    card.innerHTML = `
      <h3>${c.name}</h3>
      <p>${c.description || 'Develop skills to match this career objective.'}</p>
    `;
    card.addEventListener("click", () => {
      onboardingSelectedCareer = c.name;
      renderOnboardingCareers();
    });
    container.appendChild(card);
  });
}

function renderOnboardingSkills() {
  const container = document.getElementById("onboarding-skills-list");
  container.innerHTML = "";

  onboardingSkills.forEach(s => {
    const isSelected = onboardingSelectedSkills.includes(s.name);
    const pill = document.createElement("button");
    pill.type = "button";
    pill.className = `skill-tag-btn ${isSelected ? 'active' : ''}`;
    pill.textContent = s.name;
    
    pill.addEventListener("click", () => {
      if (onboardingSelectedSkills.includes(s.name)) {
        onboardingSelectedSkills = onboardingSelectedSkills.filter(item => item !== s.name);
      } else {
        onboardingSelectedSkills.push(s.name);
      }
      renderOnboardingSkills();
      renderOnboardingSliders();
    });
    container.appendChild(pill);
  });
}

function renderOnboardingSliders() {
  const container = document.getElementById("onboarding-sliders-container");
  container.innerHTML = "";

  onboardingSelectedSkills.forEach(skillName => {
    const group = document.createElement("div");
    group.className = "slider-group";
    group.innerHTML = `
      <label for="slider-${skillName}">
        <span>${skillName}</span>
        <span id="lbl-${skillName}" class="slider-label">0.50</span>
      </label>
      <input type="range" id="slider-${skillName}" min="0" max="1" step="0.05" value="0.5" oninput="document.getElementById('lbl-${skillName}').textContent = parseFloat(this.value).toFixed(2)">
    `;
    container.appendChild(group);
  });
}

function renderOnboardingSummary() {
  const container = document.getElementById("onboarding-summary-box");
  const hours = document.getElementById("onboard-hours").value;
  const exp = document.getElementById("onboard-experience").value;

  container.innerHTML = `
    <p style="margin-bottom: 8px;"><strong>Target Goal:</strong> ${onboardingSelectedCareer}</p>
    <p style="margin-bottom: 8px;"><strong>Experience:</strong> ${exp}</p>
    <p style="margin-bottom: 8px;"><strong>Availability:</strong> ${hours} Hours/week</p>
    <p><strong>Initial Skills:</strong> ${onboardingSelectedSkills.join(", ") || "None selected"}</p>
  `;
}

// Onboarding wizard steps sliders indicator
document.getElementById("onboard-hours").addEventListener("input", (e) => {
  document.getElementById("onboard-hours-indicator").textContent = `${e.target.value} Hours`;
});

document.getElementById("btn-wiz-prev").addEventListener("click", () => {
  if (onboardingStep > 1) {
    onboardingStep--;
    renderWizardStep();
  }
});

document.getElementById("btn-wiz-next").addEventListener("click", async () => {
  if (onboardingStep === 1 && !onboardingSelectedCareer) {
    setErrorBanner("onboarding-error", "Please select your target career goal.");
    return;
  }
  clearErrorBanner("onboarding-error");

  if (onboardingStep < 4) {
    onboardingStep++;
    renderWizardStep();
  } else {
    // Submit completed wizard values to /profile endpoint
    const hours = parseFloat(document.getElementById("onboard-hours").value);
    const exp = document.getElementById("onboard-experience").value;
    const rawInterests = document.getElementById("onboard-interests").value;
    const interests = rawInterests.split(",").map(i => i.trim()).filter(i => i.length > 0);

    showLoader(true, "Computing prerequisite sequence roadmap...");
    try {
      await apiRequest("/api/learners/profile", "POST", {
        career_goal: onboardingSelectedCareer,
        experience_level: exp,
        learning_hours_per_week: hours,
        interests: interests.length > 0 ? interests : [onboardingSelectedCareer],
        current_skills: onboardingSelectedSkills
      });
      showToast("Profile onboarding sequence finalized!");
      logToTerminal("system", "ok", `Profile onboarding complete for: ${onboardingSelectedCareer}.`);
      window.location.hash = "#dashboard";
    } catch (err) {
      setErrorBanner("onboarding-error", err.message || "Failed to finalize onboarding benchmarks.");
    } finally {
      showLoader(false);
    }
  }
});


// --- GLOBAL AUTH MODAL OVERLAY WORKFLOW ---
let authMode = "login";

function setAuthMode(mode) {
  authMode = mode;
  const tabLogin = document.getElementById("tab-login");
  const tabRegister = document.getElementById("tab-register");
  const fieldName = document.getElementById("auth-field-name");
  const inputName = document.getElementById("auth-input-name");
  const title = document.getElementById("auth-modal-title");
  const subtitle = document.getElementById("auth-modal-subtitle");
  const submitBtn = document.getElementById("btn-auth-submit");
  
  if (mode === "login") {
    tabLogin.classList.add("active");
    tabLogin.style.borderBottomColor = "var(--coral)";
    tabLogin.style.opacity = "1";
    tabRegister.classList.remove("active");
    tabRegister.style.borderBottomColor = "transparent";
    tabRegister.style.opacity = "0.7";
    
    fieldName.classList.add("hidden");
    inputName.required = false;
    title.textContent = "Welcome back.";
    subtitle.textContent = "Access your learning path and track your milestones.";
    submitBtn.innerHTML = `Log In to my path <i data-lucide="arrow-right" style="width: 17px; height: 17px;"></i>`;
  } else {
    tabRegister.classList.add("active");
    tabRegister.style.borderBottomColor = "var(--coral)";
    tabRegister.style.opacity = "1";
    tabLogin.classList.remove("active");
    tabLogin.style.borderBottomColor = "transparent";
    tabLogin.style.opacity = "0.7";
    
    fieldName.classList.remove("hidden");
    inputName.required = true;
    title.textContent = "Create your account.";
    subtitle.textContent = "Start mapping your skills and resources today.";
    submitBtn.innerHTML = `Register & start my path <i data-lucide="arrow-right" style="width: 17px; height: 17px;"></i>`;
  }
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function openAuthModal() {
  const modal = document.getElementById("auth-modal");
  clearErrorBanner("auth-error-banner");
  setAuthMode("login");
  modal.classList.remove("hidden");
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function closeAuthModal() {
  document.getElementById("auth-modal").classList.add("hidden");
}

document.getElementById("auth-close-button").addEventListener("click", closeAuthModal);
document.getElementById("tab-login").addEventListener("click", () => setAuthMode("login"));
document.getElementById("tab-register").addEventListener("click", () => setAuthMode("register"));

document.getElementById("btn-auth-action").addEventListener("click", () => {
  if (token) {
    // Log out
    localStorage.removeItem("token");
    token = null;
    currentUser = null;
    updateNavbarState();
    showToast("Logged out successfully.");
    window.location.hash = "#discover";
  } else {
    // Log in
    openAuthModal();
  }
});

// Trigger modal onboard buttons on Discover landing
document.querySelectorAll(".btn-onboard-trigger").forEach(btn => {
  btn.addEventListener("click", () => {
    if (token) {
      window.location.hash = "#onboarding";
    } else {
      openAuthModal();
    }
  });
});

// Auth form submission
document.getElementById("form-auth").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("auth-input-email").value;
  const password = document.getElementById("auth-input-password").value;
  const name = document.getElementById("auth-input-name").value;

  const errorBanner = "auth-error-banner";
  clearErrorBanner(errorBanner);

  showLoader(true, authMode === "login" ? "Connecting to your atlas..." : "Creating your atlas...");
  try {
    let loginRes;
    if (authMode === "login") {
      loginRes = await apiRequest("/api/auth/login", "POST", { email, password });
    } else {
      await apiRequest("/api/auth/register", "POST", { email, password, name });
      loginRes = await apiRequest("/api/auth/login", "POST", { email, password });
    }

    token = loginRes.access_token;
    localStorage.setItem("token", token);
    
    currentUser = await apiRequest("/api/auth/me");
    updateNavbarState();
    closeAuthModal();

    // Check profile onboarding status
    try {
      await apiRequest("/api/learners/profile");
      window.location.hash = "#dashboard";
    } catch (profileErr) {
      window.location.hash = "#onboarding";
    }
  } catch (err) {
    setErrorBanner(errorBanner, err.message || "Authentication failed. Please verify your fields.");
  } finally {
    showLoader(false);
  }
});

// Mobile menu navbar links toggle
document.getElementById("btn-mobile-toggle").addEventListener("click", () => {
  const links = document.querySelector(".site-nav .nav-links");
  links.classList.toggle("open");
});

// --- HELPER ONBOARDING ERRORS BANNER ---
function setErrorBanner(containerId, message) {
  const el = document.getElementById(containerId);
  if (el) {
    el.textContent = message;
    el.classList.remove("hidden");
  }
}

function clearErrorBanner(containerId) {
  const el = document.getElementById(containerId);
  if (el) {
    el.textContent = "";
    el.classList.add("hidden");
  }
}

// --- INITIALIZE SPA RUNTIME ---
async function initApp() {
  updateNavbarState();
  if (token) {
    showLoader(true, "Restoring profile session...");
    try {
      currentUser = await apiRequest("/api/auth/me");
      updateNavbarState();
      
      const hash = window.location.hash || "#dashboard";
      window.location.hash = hash;
      handleRouting();
    } catch (err) {
      localStorage.removeItem("token");
      token = null;
      updateNavbarState();
      window.location.hash = "#discover";
      handleRouting();
    } finally {
      showLoader(false);
    }
  } else {
    const hash = window.location.hash || "#discover";
    window.location.hash = hash;
    handleRouting();
  }
}

// Boot application
initApp();
