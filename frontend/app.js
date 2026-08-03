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
            <a href="${item.apply_url || '#'}" target="_blank" class="btn btn-primary" style="padding:6px 14px; font-size:13px; text-decoration:none;">
              ${buttonText}
            </a>
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
    alert(result.message || "Crawl complete!");
    fetchStats();
    fetchOpportunities();
  } catch (err) {
    alert("Error triggering web crawl.");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
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
