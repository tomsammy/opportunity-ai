// Override native browser alert with dark glassmorphism modal
window.alert = function(message) {
  showNotification("System Notification", message);
};

let currentCategory = 'All';
let opportunitiesData = [];

document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
  fetchOpportunities();
  trackVisitorEvent('pageview');
});

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('stat-total').innerText = data.total || 0;
    document.getElementById('stat-scholarships').innerText = (data.scholarships || 0) + (data.grants || 0);
    document.getElementById('stat-jobs').innerText = data.jobs || 0;
    document.getElementById('stat-news').innerText = data.news || 0;
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchOpportunities() {
  const grid = document.getElementById('grid-container');
  grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);">Loading verified opportunities...</div>';

  try {
    const searchVal = document.getElementById('search-input').value;
    let url = `/api/opportunities?category=${encodeURIComponent(currentCategory)}`;
    if (searchVal) {
      url += `&search=${encodeURIComponent(searchVal)}`;
    }

    const res = await fetch(url);
    const result = await res.json();
    opportunitiesData = result.data || [];
    renderGrid(opportunitiesData);
  } catch (err) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color: #ef4444;">Failed to load data from server API.</div>';
  }
}

function renderGrid(items) {
  const grid = document.getElementById('grid-container');
  if (!items || items.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 60px; color: var(--text-muted); font-size:16px;">No matching opportunities found. Try adjusting your search query or filters.</div>';
    return;
  }

  grid.innerHTML = items.map(item => {
    const isNews = (item.category || '').toLowerCase() === 'news';
    const catClass = `tag-${(item.category || 'news').toLowerCase()}`;
    const buttonText = isNews ? 'Read Article ↗' : 'Apply Now ↗';

    const detailsHTML = isNews ? `
      <div class="card-details">
        <div class="detail-row">
          <span class="detail-label">Published:</span>
          <span class="detail-val">${item.published_at || 'Recent Update'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Type:</span>
          <span class="detail-val" style="color:var(--accent-blue);">Market Intelligence & News</span>
        </div>
      </div>
    ` : `
      <div class="card-details">
        <div class="detail-row">
          <span class="detail-label">Funding/Salary:</span>
          <span class="detail-val" style="color:var(--accent-emerald);">${item.funding_amount || 'Specified'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Deadline:</span>
          <span class="detail-val">${item.deadline || 'Rolling'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Eligibility:</span>
          <span class="detail-val">${item.eligibility || 'Open'}</span>
        </div>
      </div>
    `;

    return `
      <div class="card">
        <div>
          <div class="card-tag ${catClass}">${item.category || 'Opportunity'}</div>
          <h3 class="card-title">${item.title}</h3>
          <p class="card-summary">${item.summary || ''}</p>
        </div>

        <div>
          ${detailsHTML}

          <div class="card-footer" style="display:flex; flex-direction:column; gap:12px; align-items:stretch;">
            <div class="source-badge" style="font-size:12px; color:var(--text-subtle); font-weight:500;">
              📍 ${item.source_name || 'Verified Web'}
            </div>
            <div style="display:flex; gap:10px; width:100%;">
              <button class="btn btn-secondary" style="flex:1; justify-content:center; padding:10px; font-size:13px;" onclick="evaluateItemFit('${item.id}')">
                🎯 Evaluate Fit
              </button>
              <a href="${item.apply_url || '#'}" target="_blank" class="btn btn-primary" style="flex:1; justify-content:center; padding:10px; font-size:13px; text-decoration:none;">
                ${buttonText}
              </a>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function filterCategory(category, element) {
  currentCategory = category;
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  if (element) element.classList.add('active');
  fetchOpportunities();
}

function setSearch(term) {
  document.getElementById('search-input').value = term;
  fetchOpportunities();
  trackVisitorEvent('search', { query: term });
}

let searchTimeout;
function handleSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchOpportunities();
    const val = document.getElementById('search-input').value.trim();
    if (val.length > 1) {
      trackVisitorEvent('search', { query: val });
    }
  }, 400);
}

async function triggerCrawl() {
  const btn = document.getElementById('btn-crawl');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<span>⏳ Crawling Live Web...</span>';
  btn.disabled = true;

  try {
    const res = await fetch('/api/crawl', { method: 'POST' });
    const result = await res.json();
    showNotification("Sync Complete", result.message || "Crawl cycle completed successfully.");
    fetchStats();
    fetchOpportunities();
  } catch (err) {
    showNotification("Sync Error", "Failed to connect to the crawler service.", true);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

/* Modal Helper Functions */
function showNotification(title, message, isError = false) {
  const modal = document.getElementById('notification-modal');
  if (!modal) return;
  document.getElementById('modal-icon').innerText = isError ? '⚠️' : '🎉';
  document.getElementById('modal-title').innerText = title;
  document.getElementById('modal-message').innerText = message;
  modal.classList.add('open');
}

function closeNotificationModal() {
  const modal = document.getElementById('notification-modal');
  if (modal) {
    modal.classList.remove('open');
  }
}

/* Chat Drawer Functions */
function toggleChatDrawer() {
  const drawer = document.getElementById('chat-drawer');
  drawer.classList.toggle('open');
}

function handleChatKeyPress(e) {
  if (e.key === 'Enter') {
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  const chatBody = document.getElementById('chat-body');

  // Append User Message
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg msg-user';
  userDiv.innerText = query;
  chatBody.appendChild(userDiv);
  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  // Append Thinking Indicator
  const botDiv = document.createElement('div');
  botDiv.className = 'chat-msg msg-bot';
  botDiv.innerText = '🤔 Searching vector knowledge base...';
  chatBody.appendChild(botDiv);
  chatBody.scrollTop = chatBody.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });
    const result = await res.json();
    botDiv.innerHTML = formatMarkdown(result.answer || "No details found.");
  } catch (err) {
    botDiv.innerText = "Sorry, I ran into an issue connecting to the RAG server.";
  }
  chatBody.scrollTop = chatBody.scrollHeight;
}

function formatMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

/* PRD Target Audience Segment Filters */
let currentSegment = 'All';

function filterSegment(segment, element) {
  currentSegment = segment;
  document.querySelectorAll('.hero button.tab-btn').forEach(btn => {
    if (btn.onclick && btn.onclick.toString().includes('filterSegment')) {
      btn.classList.remove('active');
    }
  });
  if (element) element.classList.add('active');

  if (segment === 'Student') setSearch('Scholarship');
  else if (segment === 'JobSeeker') setSearch('Job');
  else if (segment === 'Entrepreneur') setSearch('Accelerator');
  else if (segment === 'Business') setSearch('Tender');
  else if (segment === 'NGO') setSearch('Grant');
  else filterCategory('All');
}

/* Candidate Profile Functions */
async function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  modal.classList.add('open');
  try {
    const res = await fetch('/api/profile');
    const result = await res.json();
    const p = result.profile || {};
    document.getElementById('prof-name').value = p.name || '';
    document.getElementById('prof-skills').value = (p.skills || []).join(', ');
    document.getElementById('prof-roles').value = (p.target_roles || []).join(', ');
    document.getElementById('prof-edu').value = p.education || '';
    document.getElementById('prof-exp').value = p.experience_summary || '';
  } catch (err) {
    console.error("Error loading profile:", err);
  }
}

function closeProfileModal() {
  document.getElementById('profile-modal').classList.remove('open');
}

async function saveProfile() {
  const payload = {
    name: document.getElementById('prof-name').value,
    skills: document.getElementById('prof-skills').value,
    target_roles: document.getElementById('prof-roles').value,
    education: document.getElementById('prof-edu').value,
    experience_summary: document.getElementById('prof-exp').value
  };

  try {
    await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    closeProfileModal();
    showNotification("Profile Saved", "Your candidate profile has been updated successfully.");
  } catch (err) {
    showNotification("Profile Error", "Failed to save candidate profile.", true);
  }
}

/* PRD Feature 3 Resume Upload Handler */
async function handleResumeUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  showNotification("Parsing Resume...", "AI is analyzing your resume to extract skills, education, and target roles.");

  const reader = new FileReader();
  reader.onload = async (e) => {
    const text = e.target.result;
    try {
      const res = await fetch('/api/resume/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: text })
      });
      const data = await res.json();
      if (data.status === 'success') {
        showNotification("Resume Parsed!", "Skills and experience populated into your candidate profile!");
        openProfileModal();
      }
    } catch (err) {
      showNotification("Upload Error", "Failed to parse resume file.", true);
    }
  };
  reader.readAsText(file);
}

/* PRD Feature 9 Application Tracker Kanban Board */
async function openTrackerModal() {
  const modal = document.getElementById('tracker-modal');
  modal.classList.add('open');
  fetchApplicationBoard();
}

function closeTrackerModal() {
  document.getElementById('tracker-modal').classList.remove('open');
}

async function fetchApplicationBoard() {
  const container = document.getElementById('tracker-board-container');
  container.innerHTML = '<div style="color:var(--text-muted); padding:20px;">Loading application tracker board...</div>';
  try {
    const res = await fetch('/api/applications');
    const data = await res.json();
    renderTrackerBoard(data.applications || []);
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; padding:20px;">Error loading tracker.</div>';
  }
}

function renderTrackerBoard(apps) {
  const container = document.getElementById('tracker-board-container');
  const statuses = [
    { key: 'Saved', title: '📌 Saved', color: '#a78bfa' },
    { key: 'Preparing', title: '📝 Preparing', color: '#fbbf24' },
    { key: 'Applied', title: '🚀 Applied', color: '#3b82f6' },
    { key: 'Interview', title: '🎙️ Interview', color: '#34d399' }
  ];

  container.innerHTML = statuses.map(s => {
    const items = apps.filter(a => (a.status || '').toLowerCase() === s.key.toLowerCase());
    const cards = items.map(item => `
      <div style="background:rgba(255,255,255,0.05); border:1px solid var(--border-card); border-radius:8px; padding:10px; margin-bottom:8px; font-size:12px;">
        <div style="font-weight:700; color:#fff; margin-bottom:4px;">${item.title}</div>
        <div style="color:var(--text-subtle); margin-bottom:6px;">📍 ${item.source_name || 'Source'}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="color:${s.color}; font-weight:600;">${item.status}</span>
          <button class="btn btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="updateItemStatus('${item.item_id}', 'Applied')">Mark Applied</button>
        </div>
      </div>
    `).join('');

    return `
      <div style="background:rgba(0,0,0,0.25); border-radius:10px; padding:12px; border:1px solid var(--border-card);">
        <div style="font-weight:700; font-size:14px; color:${s.color}; margin-bottom:10px; border-bottom:1px solid var(--border-card); padding-bottom:6px; display:flex; justify-content:space-between;">
          <span>${s.title}</span>
          <span>(${items.length})</span>
        </div>
        ${cards || '<div style="font-size:12px; color:var(--text-subtle); padding:10px; text-align:center;">No items saved</div>'}
      </div>
    `;
  }).join('');
}

async function updateItemStatus(itemId, status) {
  try {
    await fetch('/api/applications/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, status: status })
    });
    showNotification("Tracker Updated", `Opportunity status updated to ${status}!`);
    fetchApplicationBoard();
  } catch (err) {
    showNotification("Tracker Error", "Failed to update status.", true);
  }
}

async function downloadTailoredResume(itemId) {
  try {
    const res = await fetch('/api/generate-resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId })
    });
    const data = await res.json();
    const resumeText = data.tailored_resume || "Tailored CV";
    
    const blob = new Blob([resumeText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Tailored_CV_${itemId}.txt`;
    a.click();
    showNotification("CV Downloaded", "Tailored ATS CV file downloaded successfully!");
  } catch (err) {
    showNotification("Download Error", "Failed to generate downloadable CV.", true);
  }
}

/* AI Fit Score & Cover Letter Functions */
async function evaluateItemFit(itemId) {
  const fitModal = document.getElementById('fit-modal');
  const contentDiv = document.getElementById('fit-analysis-content');
  const letterArea = document.getElementById('cover-letter-text');
  
  contentDiv.innerHTML = '⏳ Calculating multi-factor match score (Skills 40%, Roles 25%, Education 10%)...';
  letterArea.value = '⏳ Generating tailored cover letter...';
  fitModal.classList.add('open');

  try {
    const [evalRes, letterRes] = await Promise.all([
      fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      }),
      fetch('/api/generate-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      })
    ]);

    const evalData = await evalRes.json();
    const letterData = await letterRes.json();

    const ev = evalData.evaluation || {};
    const score = ev.fit_score || 50;

    document.getElementById('fit-score-badge').innerText = `${score}%`;
    document.getElementById('fit-score-badge').style.color = score >= 70 ? 'var(--accent-emerald)' : score >= 50 ? 'var(--accent-amber)' : '#ef4444';

    let html = `
      <div style="font-weight:700; color:#fff; font-size:14px; margin-bottom:8px;">${ev.recommendation || ''}</div>
      <div style="margin-bottom:8px;"><strong style="color:var(--accent-emerald);">✅ Match Strengths:</strong><br>• ${ev.pros ? ev.pros.join('<br>• ') : 'Good baseline match.'}</div>
      <div style="margin-bottom:12px;"><strong style="color:var(--accent-amber);">⚠️ Missing Skill Gaps:</strong><br>• ${ev.cons ? ev.cons.join('<br>• ') : 'Check posting details.'}</div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-secondary" style="padding:6px 12px; font-size:12px;" onclick="updateItemStatus('${itemId}', 'Saved')">📌 Save to Tracker</button>
        <button class="btn btn-secondary" style="padding:6px 12px; font-size:12px;" onclick="downloadTailoredResume('${itemId}')">📥 Download Tailored CV</button>
      </div>
    `;
    contentDiv.innerHTML = html;
    letterArea.value = letterData.cover_letter || 'No letter generated.';

  } catch (err) {
    contentDiv.innerHTML = 'Failed to evaluate fit score.';
    letterArea.value = 'Failed to generate cover letter.';
  }
}

function closeFitModal() {
  document.getElementById('fit-modal').classList.remove('open');
}

function copyCoverLetter() {
  const text = document.getElementById('cover-letter-text');
  text.select();
  document.execCommand('copy');
  showNotification("Copied!", "Cover letter copied to clipboard.");
}

/* Candidate Profile Functions */
async function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  modal.classList.add('open');
  try {
    const res = await fetch('/api/profile');
    const result = await res.json();
    const p = result.profile || {};
    document.getElementById('prof-name').value = p.name || '';
    document.getElementById('prof-skills').value = (p.skills || []).join(', ');
    document.getElementById('prof-roles').value = (p.target_roles || []).join(', ');
    document.getElementById('prof-edu').value = p.education || '';
    document.getElementById('prof-exp').value = p.experience_summary || '';
  } catch (err) {
    console.error("Error loading profile:", err);
  }
}

function closeProfileModal() {
  document.getElementById('profile-modal').classList.remove('open');
}

async function saveProfile() {
  const payload = {
    name: document.getElementById('prof-name').value,
    skills: document.getElementById('prof-skills').value,
    target_roles: document.getElementById('prof-roles').value,
    education: document.getElementById('prof-edu').value,
    experience_summary: document.getElementById('prof-exp').value
  };

  try {
    await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    closeProfileModal();
    showNotification("Profile Saved", "Your candidate profile has been updated successfully.");
  } catch (err) {
    showNotification("Profile Error", "Failed to save candidate profile.", true);
  }
}

/* AI Fit Score & Cover Letter Functions */
async function evaluateItemFit(itemId) {
  const fitModal = document.getElementById('fit-modal');
  const contentDiv = document.getElementById('fit-analysis-content');
  const letterArea = document.getElementById('cover-letter-text');
  
  contentDiv.innerHTML = '⏳ Calculating match score and evaluating fit...';
  letterArea.value = '⏳ Generating tailored cover letter...';
  fitModal.classList.add('open');

  try {
    const [evalRes, letterRes] = await Promise.all([
      fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      }),
      fetch('/api/generate-letter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      })
    ]);

    const evalData = await evalRes.json();
    const letterData = await letterRes.json();

    const ev = evalData.evaluation || {};
    const score = ev.fit_score || 50;

    document.getElementById('fit-score-badge').innerText = `${score}%`;
    document.getElementById('fit-score-badge').style.color = score >= 70 ? 'var(--accent-emerald)' : score >= 50 ? 'var(--accent-amber)' : '#ef4444';

    let html = `
      <div style="font-weight:700; color:#fff; font-size:14px; margin-bottom:8px;">${ev.recommendation || ''}</div>
      <div style="margin-bottom:8px;"><strong style="color:var(--accent-emerald);">✅ Match Strengths:</strong><br>• ${ev.pros ? ev.pros.join('<br>• ') : 'Good baseline match.'}</div>
      <div><strong style="color:var(--accent-amber);">⚠️ Focus Areas:</strong><br>• ${ev.cons ? ev.cons.join('<br>• ') : 'Check posting details.'}</div>
    `;
    contentDiv.innerHTML = html;
    letterArea.value = letterData.cover_letter || 'No letter generated.';

  } catch (err) {
    contentDiv.innerHTML = 'Failed to evaluate fit score.';
    letterArea.value = 'Failed to generate cover letter.';
  }
}

function closeFitModal() {
  document.getElementById('fit-modal').classList.remove('open');
}

function copyCoverLetter() {
  const text = document.getElementById('cover-letter-text');
  text.select();
  document.execCommand('copy');
  showNotification("Copied!", "Cover letter copied to clipboard.");
}

/* Reactive Resume Multi-Template CV Builder Functions */
let currentCVTemplate = 'tech';
let currentCVHTML = '';
let currentCVJSON = null;

async function openCVBuilderModal(itemId = null) {
  const modal = document.getElementById('cv-builder-modal');
  modal.classList.add('open');
  fetchCVPreview(currentCVTemplate, itemId);
}

function closeCVBuilderModal() {
  document.getElementById('cv-builder-modal').classList.remove('open');
}

function selectCVTemplate(templateType, element) {
  currentCVTemplate = templateType;
  document.querySelectorAll('#cv-builder-modal button.tab-btn').forEach(btn => btn.classList.remove('active'));
  if (element) element.classList.add('active');
  fetchCVPreview(templateType);
}

async function fetchCVPreview(templateType = 'tech', itemId = null) {
  const container = document.getElementById('cv-preview-container');
  container.innerHTML = '<div style="color:#64748b; padding:30px; text-align:center;">⏳ Generating tailored ATS CV preview...</div>';

  try {
    const res = await fetch('/api/cv/builder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template_type: templateType, item_id: itemId })
    });
    const data = await res.json();
    currentCVHTML = data.html_cv || '';
    currentCVJSON = data.json_cv || {};

    const iframe = document.createElement('iframe');
    iframe.style.width = '100%';
    iframe.style.height = '480px';
    iframe.style.border = 'none';
    container.innerHTML = '';
    container.appendChild(iframe);

    const doc = iframe.contentWindow.document;
    doc.open();
    doc.write(currentCVHTML);
    doc.close();
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; padding:20px; text-align:center;">Failed to generate CV preview.</div>';
  }
}

function printPreviewCV() {
  if (!currentCVHTML) return;
  const printWindow = window.open('', '_blank');
  printWindow.document.write(currentCVHTML);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => printWindow.print(), 500);
}

function downloadCVFormat(format = 'json') {
  if (format === 'json' && currentCVJSON) {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentCVJSON, null, 2));
    const a = document.createElement('a');
    a.setAttribute("href", dataStr);
    a.setAttribute("download", `Reactive_Resume_${currentCVTemplate}.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
    showNotification("JSON Downloaded", "Reactive Resume JSON schema downloaded!");
  }
}

/* =========================================================
   Visitor Analytics & Metrics Intelligence Suite
   ========================================================= */
function getOrCreateVisitorId() {
  let vid = localStorage.getItem('opp_visitor_id');
  if (!vid) {
    vid = 'v_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
    localStorage.setItem('opp_visitor_id', vid);
  }
  return vid;
}

async function trackVisitorEvent(eventType, details = {}) {
  try {
    const vid = getOrCreateVisitorId();
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    const ref = document.referrer || '';
    
    await fetch('/api/analytics/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        visitor_id: vid,
        event_type: eventType,
        client_tz: tz,
        referrer: ref,
        details: details
      })
    });
  } catch (e) {
    // Silent fail for uninterrupted UX
  }
}

let analyticsData = null;
let currentAnalyticsTab = 'geo';

function getAdminToken() {
  return sessionStorage.getItem('opp_admin_token') || localStorage.getItem('opp_admin_token');
}

function setAdminToken(token) {
  sessionStorage.setItem('opp_admin_token', token);
  localStorage.setItem('opp_admin_token', token);
}

function clearAdminToken() {
  sessionStorage.removeItem('opp_admin_token');
  localStorage.removeItem('opp_admin_token');
}

function openAnalyticsModal() {
  const modal = document.getElementById('analytics-modal');
  modal.classList.add('open');
  
  const token = getAdminToken();
  const authView = document.getElementById('analytics-auth-view');
  const dashboardView = document.getElementById('analytics-dashboard-view');
  const errDiv = document.getElementById('admin-auth-error');
  if (errDiv) errDiv.style.display = 'none';

  if (token) {
    authView.style.display = 'none';
    dashboardView.style.display = 'block';
    loadAnalyticsDashboard();
  } else {
    authView.style.display = 'block';
    dashboardView.style.display = 'none';
    const passInput = document.getElementById('admin-passcode-input');
    if (passInput) {
      passInput.value = '';
      setTimeout(() => passInput.focus(), 150);
    }
  }
}

function closeAnalyticsModal() {
  document.getElementById('analytics-modal').classList.remove('open');
}

async function submitAdminLogin() {
  const passInput = document.getElementById('admin-passcode-input');
  const errDiv = document.getElementById('admin-auth-error');
  const password = (passInput ? passInput.value : '').trim();

  if (!password) {
    errDiv.innerText = 'Please enter the administrator passcode.';
    errDiv.style.display = 'block';
    return;
  }

  errDiv.style.display = 'none';

  try {
    const res = await fetch('/api/analytics/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });

    const data = await res.json();
    if (res.ok && data.status === 'success' && data.token) {
      setAdminToken(data.token);
      document.getElementById('analytics-auth-view').style.display = 'none';
      document.getElementById('analytics-dashboard-view').style.display = 'block';
      loadAnalyticsDashboard();
      showNotification("Authenticated", "Welcome to Visitor Intelligence Dashboard!");
    } else {
      errDiv.innerText = data.detail || 'Invalid admin passcode. Access denied.';
      errDiv.style.display = 'block';
    }
  } catch (err) {
    errDiv.innerText = 'Authentication server error. Please try again.';
    errDiv.style.display = 'block';
  }
}

function logoutAdminAuth() {
  clearAdminToken();
  document.getElementById('analytics-dashboard-view').style.display = 'none';
  document.getElementById('analytics-auth-view').style.display = 'block';
  const passInput = document.getElementById('admin-passcode-input');
  if (passInput) passInput.value = '';
  showNotification("Locked", "Logged out of Admin Analytics.");
}

async function loadAnalyticsDashboard() {
  const container = document.getElementById('analytics-tab-content');
  if (!container) return;
  container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-muted);">⏳ Loading real-time visitor analytics...</div>';
  
  const token = getAdminToken();
  if (!token) {
    logoutAdminAuth();
    return;
  }

  try {
    const res = await fetch('/api/analytics/summary', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (res.status === 401) {
      logoutAdminAuth();
      const errDiv = document.getElementById('admin-auth-error');
      if (errDiv) {
        errDiv.innerText = 'Session expired or unauthorized. Please re-authenticate.';
        errDiv.style.display = 'block';
      }
      return;
    }

    analyticsData = await res.json();

    // Update Top Key Metric Cards
    const totalViews = analyticsData.total_pageviews || 0;
    const unique = analyticsData.unique_visitors || 1;
    
    document.getElementById('metric-pageviews').innerText = totalViews.toLocaleString();
    document.getElementById('metric-unique-sub').innerText = `${unique.toLocaleString()} Unique Visitors`;
    
    const topCountry = (analyticsData.top_countries && analyticsData.top_countries[0]) ? analyticsData.top_countries[0] : null;
    if (topCountry) {
      document.getElementById('metric-top-country').innerText = `${topCountry.flag} ${topCountry.name}`;
      const pct = Math.round((topCountry.count / unique) * 100);
      document.getElementById('metric-country-sub').innerText = `${topCountry.count} visitors (${pct}%)`;
    } else {
      document.getElementById('metric-top-country').innerText = '🌐 Global';
    }

    const desktop = analyticsData.device_breakdown?.Desktop || 0;
    const mobile = (analyticsData.device_breakdown?.Mobile || 0) + (analyticsData.device_breakdown?.Tablet || 0);
    const totalDev = (desktop + mobile) || 1;
    document.getElementById('metric-device-split').innerText = `${Math.round((desktop / totalDev) * 100)}% / ${Math.round((mobile / totalDev) * 100)}%`;
    document.getElementById('metric-device-sub').innerText = `${desktop} Desktop • ${mobile} Mobile`;

    const returning = analyticsData.returning_visitors || 0;
    document.getElementById('metric-returning').innerText = `${Math.round((returning / unique) * 100)}%`;
    document.getElementById('metric-returning-sub').innerText = `${returning} Returning • ${analyticsData.new_visitors || 0} New`;

    renderAnalyticsTabContent();
  } catch (err) {
    container.innerHTML = '<div style="color:#ef4444; padding:20px; text-align:center;">Failed to load analytics data from server.</div>';
  }
}

function switchAnalyticsTab(tabName, btnEl) {
  currentAnalyticsTab = tabName;
  document.querySelectorAll('#analytics-modal .tab-btn').forEach(b => b.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');
  renderAnalyticsTabContent();
}

function renderAnalyticsTabContent() {
  if (!analyticsData) return;
  const container = document.getElementById('analytics-tab-content');
  const unique = analyticsData.unique_visitors || 1;

  if (currentAnalyticsTab === 'geo') {
    const countries = analyticsData.top_countries || [];
    let countriesHTML = countries.map(c => {
      const pct = Math.round((c.count / unique) * 100);
      return `
        <div class="metric-row">
          <div style="width:140px; display:flex; align-items:center; gap:8px;">
            <span style="font-size:18px;">${c.flag}</span>
            <span style="font-weight:600; color:#fff;">${c.name}</span>
          </div>
          <div class="metric-bar-container">
            <div class="metric-bar-fill" style="width:${Math.max(6, pct)}%;"></div>
          </div>
          <div style="width:80px; text-align:right; font-weight:700; color:var(--accent-emerald);">
            ${c.count} <span style="font-size:11px; color:var(--text-subtle); font-weight:400;">(${pct}%)</span>
          </div>
        </div>
      `;
    }).join('') || '<div style="color:var(--text-muted); padding:10px;">No geographic visitor data yet.</div>';

    container.innerHTML = `
      <div class="analytics-grid-2col">
        <div class="analytics-card-section">
          <div class="analytics-section-title">
            <span>🌍 Top Visitor Geographies</span>
            <span style="font-size:11px; color:var(--text-subtle);">By Country / Region</span>
          </div>
          ${countriesHTML}
        </div>
        <div class="analytics-card-section">
          <div class="analytics-section-title">
            <span>🔗 Inbound Traffic & Referrers</span>
            <span style="font-size:11px; color:var(--text-subtle);">Acquisition Channels</span>
          </div>
          ${(analyticsData.top_referrers || []).map(r => `
            <div class="metric-row">
              <span style="color:#fff; font-weight:500;">${r.source}</span>
              <span style="font-weight:700; color:#60a5fa;">${r.count} visits</span>
            </div>
          `).join('') || '<div style="color:var(--text-muted); padding:10px;">Direct traffic</div>'}
        </div>
      </div>
    `;
  } else if (currentAnalyticsTab === 'tech') {
    container.innerHTML = `
      <div class="analytics-grid-2col">
        <div class="analytics-card-section">
          <div class="analytics-section-title">📱 Devices & Platforms</div>
          ${Object.entries(analyticsData.device_breakdown || {}).map(([dev, count]) => `
            <div class="metric-row">
              <span style="color:#fff; font-weight:500;">${dev === 'Desktop' ? '💻' : '📱'} ${dev}</span>
              <span style="font-weight:700; color:#34d399;">${count} users</span>
            </div>
          `).join('')}
          <div style="margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            <div class="analytics-section-title" style="margin-bottom:8px;">💻 Operating Systems</div>
            ${Object.entries(analyticsData.os_breakdown || {}).map(([os, count]) => `
              <div class="metric-row">
                <span style="color:var(--text-muted);">${os}</span>
                <span style="font-weight:600; color:#fff;">${count}</span>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="analytics-card-section">
          <div class="analytics-section-title">🌐 Web Browsers</div>
          ${Object.entries(analyticsData.browser_breakdown || {}).map(([br, count]) => `
            <div class="metric-row">
              <span style="color:#fff; font-weight:500;">${br}</span>
              <span style="font-weight:700; color:#a78bfa;">${count} users</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } else if (currentAnalyticsTab === 'search') {
    const searches = analyticsData.top_searches || [];
    const opps = analyticsData.top_opportunities || [];
    container.innerHTML = `
      <div class="analytics-grid-2col">
        <div class="analytics-card-section">
          <div class="analytics-section-title">
            <span>🔍 Most Searched Terms</span>
            <span style="font-size:11px; color:var(--text-subtle);">Visitor Queries</span>
          </div>
          ${searches.map(s => `
            <div class="metric-row">
              <span style="color:#fff; font-weight:500;">"${s.query}"</span>
              <span style="font-weight:700; color:var(--accent-emerald);">${s.count} searches</span>
            </div>
          `).join('') || '<div style="color:var(--text-muted); padding:10px;">No search queries recorded yet.</div>'}
        </div>
        <div class="analytics-card-section">
          <div class="analytics-section-title">
            <span>🎯 High-Engagement Opportunities</span>
            <span style="font-size:11px; color:var(--text-subtle);">Views & Fits</span>
          </div>
          ${opps.map(o => `
            <div class="metric-row">
              <span style="color:#fff; font-size:12px; max-width:70%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${o.title}</span>
              <span style="font-weight:700; color:#60a5fa;">${o.count} views</span>
            </div>
          `).join('') || '<div style="color:var(--text-muted); padding:10px;">No opportunity views recorded yet.</div>'}
        </div>
      </div>
    `;
  } else if (currentAnalyticsTab === 'live') {
    const feed = analyticsData.live_feed || [];
    container.innerHTML = `
      <div class="analytics-card-section">
        <div class="analytics-section-title">
          <span>⚡ Live Visitor Activity Stream (Real-Time)</span>
          <span style="font-size:11px; color:var(--accent-emerald);">● Streaming Live</span>
        </div>
        ${feed.map(item => `
          <div class="live-stream-item">
            <span style="font-size:18px;">${item.flag}</span>
            <div style="flex:1;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
                <span style="font-weight:700; color:#fff; font-size:13px;">${item.location}</span>
                <span style="color:var(--text-subtle); font-size:11px;">${item.timestamp}</span>
              </div>
              <div style="color:var(--accent-emerald); font-weight:600; font-size:12px; margin-bottom:2px;">
                ${item.action}
              </div>
              <div style="display:flex; gap:8px; align-items:center; color:var(--text-subtle); font-size:11px;">
                <span>${item.device}</span>
                <span>•</span>
                <span>${item.browser}</span>
                <span>•</span>
                <span class="live-stream-badge">${item.referrer}</span>
              </div>
            </div>
          </div>
        `).join('') || '<div style="color:var(--text-muted); padding:20px; text-align:center;">No recent events recorded.</div>'}
      </div>
    `;
  }
}

/* =========================================================
   Mobile Hamburger Menu Navigation Handlers
   ========================================================= */
function toggleMobileMenu() {
  const drawer = document.getElementById('mobile-menu-drawer');
  const btn = document.getElementById('hamburger-btn');
  if (!drawer) return;
  
  const isOpen = drawer.classList.contains('open');
  if (isOpen) {
    closeMobileMenu();
  } else {
    drawer.classList.add('open');
    if (btn) btn.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeMobileMenu() {
  const drawer = document.getElementById('mobile-menu-drawer');
  const btn = document.getElementById('hamburger-btn');
  if (drawer) drawer.classList.remove('open');
  if (btn) btn.classList.remove('active');
  document.body.style.overflow = '';
}

function handleMobileBackdropClick(e) {
  if (e.target && e.target.id === 'mobile-menu-drawer') {
    closeMobileMenu();
  }
}

function mobileNavAction(callback) {
  closeMobileMenu();
  setTimeout(() => {
    if (typeof callback === 'function') {
      callback();
    }
  }, 200);
}

