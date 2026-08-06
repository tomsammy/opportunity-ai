// Override native browser alert with dark glassmorphism modal
window.alert = function(message) {
  showNotification("System Notification", message);
};

let currentCategory = 'All';
let opportunitiesData = [];

document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
  fetchOpportunities();
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

          <div class="card-footer">
            <span class="source-badge">📍 ${item.source_name || 'Verified Web'}</span>
            <div style="display:flex; gap:6px;">
              <button class="btn btn-secondary" style="padding:6px 10px; font-size:12px;" onclick="evaluateItemFit('${item.id}')">
                🎯 Evaluate Fit
              </button>
              <a href="${item.apply_url || '#'}" target="_blank" class="btn btn-primary" style="padding:6px 14px; font-size:13px; text-decoration:none;">
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
}

let searchTimeout;
function handleSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchOpportunities();
  }, 300);
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
