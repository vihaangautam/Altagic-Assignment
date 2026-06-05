import React, { useState, useEffect } from 'react';
import './App.css';

// Seed prospects to use as a fallback if prospects.json is not found
const SEED_PROSPECTS = [
  {
    "publisher_name": "Backlinko",
    "domain": "backlinko.com",
    "category": "SEO & Search Marketing",
    "why_relevant": "As a site focused deeply on search engine optimization and analytics, backlinko.com has a highly-targeted audience of practitioners who actively buy SEO suites.",
    "evidence_url": "https://backlinko.com/seo-tools",
    "page_rank": 8.2,
    "relevance_score": 10,
    "quality_score": 9,
    "contact_email": "brian@backlinko.com",
    "contact_page": "https://backlinko.com/about",
    "linkedin_url": "https://www.linkedin.com/company/backlinko",
    "status": "scored",
    "outreach_angle": "Focus on Semrush's advanced keyword index and site audit capabilities. Offer exclusive trial codes to share with their SEO readers."
  },
  {
    "publisher_name": "Neil Patel",
    "domain": "neilpatel.com",
    "category": "SEO & Search Marketing",
    "why_relevant": "Neil Patel is one of the most prominent voices in online marketing. His readers are looking for recommended tools to perform site audits and keyword searches.",
    "evidence_url": "https://neilpatel.com/blog/best-seo-tools/",
    "page_rank": 8.5,
    "relevance_score": 9,
    "quality_score": 9,
    "contact_email": "support@neilpatel.com",
    "contact_page": "https://neilpatel.com/contact/",
    "linkedin_url": "https://www.linkedin.com/company/neil-patel-digital",
    "status": "scored",
    "outreach_angle": "Highlight Semrush's advanced API integration and client reporting tools. Offer custom webinars for their agency readers."
  },
  {
    "publisher_name": "ShoutMeLoud",
    "domain": "shoutmeloud.com",
    "category": "Blogging & Affiliate Marketing",
    "why_relevant": "Caters to professional bloggers and internet marketers looking to generate passive income. Semrush is the primary software recommended for niche research.",
    "evidence_url": "https://www.shoutmeloud.com/semrush-review.html",
    "page_rank": 6.8,
    "relevance_score": 9,
    "quality_score": 8,
    "contact_email": "harsh@shoutmeloud.com",
    "contact_page": "https://www.shoutmeloud.com/contact",
    "linkedin_url": "https://www.linkedin.com/company/shoutmeloud",
    "status": "scored",
    "outreach_angle": "Emphasize Semrush's high affiliate payouts ($200 per sale, $10 per lead). Pitch a co-branded tutorial review."
  },
  {
    "publisher_name": "WPBeginner",
    "domain": "wpbeginner.com",
    "category": "WordPress & Site Building",
    "why_relevant": "WPBeginner is the largest free WordPress resource site for beginners. Their audience needs tools to monitor keyword performance and perform SEO audits.",
    "evidence_url": "https://www.wpbeginner.com/showcase/best-seo-tools-for-wordpress/",
    "page_rank": 7.9,
    "relevance_score": 8,
    "quality_score": 8,
    "contact_email": "support@wpbeginner.com",
    "contact_page": "https://www.wpbeginner.com/contact-us/",
    "linkedin_url": "https://www.linkedin.com/company/wpbeginner",
    "status": "scored",
    "outreach_angle": "Pitch the Semrush WordPress plugin integration and competitor content analysis tool. Offer a video review sponsorship."
  },
  {
    "publisher_name": "Authority Hacker",
    "domain": "Blogging & Affiliate Marketing",
    "why_relevant": "Educates affiliate website creators on how to scale authority portals. The audience relies on SEM tools for keyword discovery and link auditing.",
    "evidence_url": "https://www.authorityhacker.com/semrush-review/",
    "page_rank": 7.2,
    "relevance_score": 10,
    "quality_score": 8,
    "contact_email": "support@authorityhacker.com",
    "contact_page": "https://www.authorityhacker.com/contact/",
    "linkedin_url": "https://www.linkedin.com/company/authority-hacker",
    "status": "scored",
    "outreach_angle": "Emphasize Semrush's generous affiliate payout ($200 per sale, $10 per trial). Suggest a dedicated tool comparison review."
  }
];

function App() {
  const [prospects, setProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [sortBy, setSortBy] = useState('quality');
  const [reviewState, setReviewState] = useState({});

  useEffect(() => {
    // Load review status mapping from localStorage on startup
    const savedReviews = localStorage.getItem('altagic_prospect_reviews');
    if (savedReviews) {
      setReviewState(JSON.parse(savedReviews));
    }

    // Fetch prospects.json
    fetch('/prospects.json')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Local prospects.json not found or could not be loaded.');
        }
        return res.json();
      })
      .then((data) => {
        setProspects(data);
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Could not load prospects.json, using seed fallbacks: ', err);
        // Fall back to seed prospects
        setProspects(SEED_PROSPECTS);
        setLoading(false);
      });
  }, []);

  // Update status (Approve / Reject) in local state & save to local storage
  const handleReviewAction = (domain, status) => {
    const updatedReviews = { ...reviewState, [domain]: status };
    setReviewState(updatedReviews);
    localStorage.setItem('altagic_prospect_reviews', JSON.stringify(updatedReviews));
  };

  // Reset all review actions
  const resetReviews = () => {
    if (window.confirm("Are you sure you want to reset all approved/rejected decisions?")) {
      setReviewState({});
      localStorage.removeItem('altagic_prospect_reviews');
    }
  };

  // Force load pre-seeded prospects (even if empty)
  const loadSeedData = () => {
    setProspects(SEED_PROSPECTS);
  };

  // Get active status of a prospect, overriding default from JSON with local decisions
  const getProspectStatus = (prospect) => {
    return reviewState[prospect.domain] || prospect.status || 'scored';
  };

  // Calculate statistics based on current reviews
  const stats = prospects.reduce((acc, p) => {
    const status = getProspectStatus(p);
    if (status === 'approved') acc.approved++;
    else if (status === 'rejected') acc.rejected++;
    else acc.pending++;
    
    acc.totalPageRank += p.page_rank || 0.0;
    acc.totalQualityScore += p.quality_score || 0;
    return acc;
  }, { approved: 0, rejected: 0, pending: 0, totalPageRank: 0, totalQualityScore: 0 });

  const avgPR = prospects.length ? (stats.totalPageRank / prospects.length).toFixed(1) : '0.0';
  const avgQuality = prospects.length ? (stats.totalQualityScore / prospects.length).toFixed(1) : '0.0';

  // Get unique list of categories for filter dropdown
  const categories = ['all', ...new Set(prospects.map(p => p.category || 'SEO & Marketing'))];

  // Filtering & Sorting
  const filteredProspects = prospects
    .filter((p) => {
      // 1. Search Query filter (checks Domain or Name)
      const query = searchQuery.toLowerCase();
      const matchQuery = 
        p.domain.toLowerCase().includes(query) || 
        (p.publisher_name && p.publisher_name.toLowerCase().includes(query));
      
      // 2. Category Filter
      const cat = p.category || 'SEO & Marketing';
      const matchCategory = selectedCategory === 'all' || cat === selectedCategory;
      
      // 3. Status Filter (Approved, Rejected, Pending)
      const currentStatus = getProspectStatus(p);
      let matchStatus = true;
      if (selectedStatus === 'approved') matchStatus = currentStatus === 'approved';
      else if (selectedStatus === 'rejected') matchStatus = currentStatus === 'rejected';
      else if (selectedStatus === 'pending') matchStatus = currentStatus !== 'approved' && currentStatus !== 'rejected';
      
      return matchQuery && matchCategory && matchStatus;
    })
    .sort((a, b) => {
      // Sort logic
      if (sortBy === 'quality') {
        return (b.quality_score || 0) - (a.quality_score || 0);
      } else if (sortBy === 'relevance') {
        return (b.relevance_score || 0) - (a.relevance_score || 0);
      } else if (sortBy === 'pagerank') {
        return (b.page_rank || 0) - (a.page_rank || 0);
      }
      return 0;
    });

  // Export Curated List to JSON file
  const exportCuratedJSON = () => {
    const curated = prospects.map(p => ({
      ...p,
      curation_status: getProspectStatus(p)
    }));
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(curated, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "curated_prospects.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (loading) {
    return (
      <div className="dashboard-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontFamily: 'Outfit, sans-serif', color: '#ff6422', marginBottom: '1rem' }}>Analyzing Candidates...</h2>
          <p style={{ color: '#94a3b8' }}>Gathering and evaluating affiliate prospects</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="brand-section">
          <h1>AI Publisher Discovery</h1>
          <p>Automated Affiliate Acquisition Pipeline & Review System</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className="campaign-tag">Semrush Campaign</span>
          {Object.keys(reviewState).length > 0 && (
            <button className="contact-link" onClick={resetReviews} style={{ border: '1px dashed #ef4444', color: '#ef4444', background: 'transparent', cursor: 'pointer' }}>
              Reset Actions
            </button>
          )}
        </div>
      </header>

      {/* Stats Board */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total Scoped</span>
          <span className="stat-value">{prospects.length}</span>
          <span className="stat-sub">Discovered candidates</span>
        </div>
        <div className="stat-card" style={{ borderLeft: '4px solid #10b981' }}>
          <span className="stat-label">Approved</span>
          <span className="stat-value" style={{ color: '#10b981' }}>{stats.approved}</span>
          <span className="stat-sub">Ready for outreach</span>
        </div>
        <div className="stat-card" style={{ borderLeft: '4px solid #ef4444' }}>
          <span className="stat-label">Rejected</span>
          <span className="stat-value" style={{ color: '#ef4444' }}>{stats.rejected}</span>
          <span className="stat-sub">Unmatched audience</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Avg Quality Score</span>
          <span className="stat-value">{avgQuality} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>/10</span></span>
          <span className="stat-sub">LLM Content Score</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Avg PR / DR Score</span>
          <span className="stat-value">{avgPR} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>/10</span></span>
          <span className="stat-sub">Domain authority metric</span>
        </div>
      </section>

      {/* Controls Bar */}
      <section className="controls-bar">
        <div className="search-wrapper">
          <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Search domain or publisher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          {/* Category Filter */}
          <select 
            className="filter-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">All Niches</option>
            {categories.filter(c => c !== 'all').map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          {/* Status Filter */}
          <select 
            className="filter-select"
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            <option value="all">All Reviews</option>
            <option value="pending">Pending Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          {/* Sorting */}
          <select 
            className="filter-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="quality">Sort: Quality (1-10)</option>
            <option value="relevance">Sort: Relevance (1-10)</option>
            <option value="pagerank">Sort: Domain Rank (OPR)</option>
          </select>

          {/* Export Button */}
          <button className="action-btn-export" onClick={exportCuratedJSON}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '4px' }}>
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export Curated
          </button>
        </div>
      </section>

      {/* Prospects Grid */}
      {filteredProspects.length > 0 ? (
        <section className="prospects-grid">
          {filteredProspects.map((prospect) => {
            const currentStatus = getProspectStatus(prospect);
            const isApproved = currentStatus === 'approved';
            const isRejected = currentStatus === 'rejected';
            
            // Score color styles
            const qScore = prospect.quality_score || 0;
            const rScore = prospect.relevance_score || 0;
            const pRank = prospect.page_rank || 0.0;
            
            const qClass = qScore >= 8 ? 'high' : qScore >= 6 ? 'med' : 'low';
            const rClass = rScore >= 8 ? 'high' : rScore >= 6 ? 'med' : 'low';
            const pClass = pRank >= 7.0 ? 'high' : pRank >= 5.0 ? 'med' : 'low';

            return (
              <div 
                key={prospect.domain} 
                className={`prospect-card ${isApproved ? 'is-approved' : ''} ${isRejected ? 'is-rejected' : ''}`}
              >
                {/* Status Overlay Ribbon */}
                {currentStatus !== 'scored' && currentStatus !== 'discovered' && (
                  <span className={`status-badge ${currentStatus}`}>
                    {currentStatus}
                  </span>
                )}

                <div className="card-header">
                  <span className="category-pill">{prospect.category || 'SEO & Marketing'}</span>
                  <h3 className="publisher-name">{prospect.publisher_name || prospect.domain}</h3>
                  <a href={`https://${prospect.domain}`} target="_blank" rel="noopener noreferrer" className="publisher-domain">
                    {prospect.domain}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                  </a>
                </div>

                {/* Metrics */}
                <div className="metrics-row">
                  <div className="metric-item">
                    <div className="metric-label">Quality</div>
                    <div className={`metric-val-badge ${qClass}`}>{qScore}/10</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">Relevance</div>
                    <div className={`metric-val-badge ${rClass}`}>{rScore}/10</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">OPR Rank</div>
                    <div className={`metric-val-badge ${pClass}`}>{pRank}</div>
                  </div>
                </div>

                {/* Descriptions */}
                <div className="card-content-section">
                  <div className="section-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    Why Relevant
                  </div>
                  <p className="section-text">{prospect.why_relevant || "Evaluating site niche matching Semrush core audience segments."}</p>
                </div>

                <div className="card-content-section">
                  <div className="section-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>
                    Outreach Angle
                  </div>
                  <p className="section-text-angle">{prospect.outreach_angle || "Invite webmaster to test Semrush content suite using lead-generating review copy."}</p>
                </div>

                {/* Contacts / Links */}
                <div className="contact-row">
                  {prospect.evidence_url && (
                    <a href={prospect.evidence_url} target="_blank" rel="noopener noreferrer" className="contact-link evidence">
                      <span>Evidence URL</span>
                    </a>
                  )}
                  {prospect.contact_email && (
                    <a href={`mailto:${prospect.contact_email}`} className="contact-link">
                      <span>📧 {prospect.contact_email}</span>
                    </a>
                  )}
                  {prospect.contact_page && (
                    <a href={prospect.contact_page} target="_blank" rel="noopener noreferrer" className="contact-link">
                      <span>📄 Contact Page</span>
                    </a>
                  )}
                  {prospect.linkedin_url && (
                    <a href={prospect.linkedin_url} target="_blank" rel="noopener noreferrer" className="contact-link">
                      <span>🔗 LinkedIn</span>
                    </a>
                  )}
                </div>

                {/* Approve / Reject Actions */}
                <div className="card-actions">
                  <button 
                    className="btn-action btn-approve"
                    onClick={() => handleReviewAction(prospect.domain, isApproved ? 'pending' : 'approved')}
                  >
                    {isApproved ? 'Approved ✓' : 'Approve'}
                  </button>
                  <button 
                    className="btn-action btn-reject"
                    onClick={() => handleReviewAction(prospect.domain, isRejected ? 'pending' : 'rejected')}
                  >
                    {isRejected ? 'Rejected ✗' : 'Reject'}
                  </button>
                </div>
              </div>
            );
          })}
        </section>
      ) : (
        <div className="empty-state">
          <h3>No prospects found</h3>
          <p>No candidates matched your search criteria. Try modifying your search term or selecting a different niche/status filter.</p>
          <button className="btn-seed" onClick={() => { setSearchQuery(''); setSelectedCategory('all'); setSelectedStatus('all'); }}>
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
