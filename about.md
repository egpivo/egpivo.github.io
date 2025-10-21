---
layout: page
title: About
menu: main
permalink: /about/
---

<div class="about-page">
  <!-- Hero Section -->
  <section class="about-hero">
    <div class="hero-content">
      <div class="profile-section">
        <div class="profile-info">
          <h1 class="profile-name">Wen-Ting (Joseph) Wang</h1>
          <p class="profile-title">Machine Learning Engineer & Researcher</p>
          <p class="profile-subtitle">Ph.D. in Statistics • 10+ Years in Production ML</p>
          <div class="profile-highlights">
            <span class="highlight-tag">AI Product Engineering</span>
            <span class="highlight-tag">Research & Development</span>
            <span class="highlight-tag">End-to-End ML Systems</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- About Me Section -->
  <section class="about-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-user-circle"></i>
        About Me
      </h2>
    </div>
    <div class="content-card">
      <div class="intro-text">
        <p class="intro-paragraph">
I’m a machine learning engineer with nearly ten years of hands-on experience and a Ph.D. in Statistics. I build end-to-end systems that combine solid modeling with reliable data and infrastructure — and make sure they work at scale. Lately, I’ve been working on <span class="kw">agentic workflows</span>, <span class="kw">RAG systems</span>, and <span class="kw">spatiotemporal modeling</span>, blending practical engineering with research. My current focus includes <span class="kw">conditional diffusion models</span> and <span class="kw">spatiotemporal learning methods</span>, aiming to make complex models both more useful and more interpretable.
        </p>
      </div>
    </div>
  </section>

  <!-- Experience Section -->
  <section class="about-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-briefcase"></i>
        Professional Experience
      </h2>
    </div>
    
    <div class="experience-grid">
      <div class="experience-card featured">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-brain"></i>
          </div>
          <div class="card-title">
            <h3>AI Product Engineering</h3>
            <span class="card-period">Recent</span>
          </div>
        </div>
        <div class="card-content">
          <p>Built an entity linking system for news analytics and assistants, and delivered a RAG + MCP Q&amp;A system for an energy client to support domain-specific search.</p>
          <div class="tech-tags">
            <span class="tech-tag">RAG</span>
            <span class="tech-tag">NLP</span>
          </div>
        </div>
      </div>

      <div class="experience-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-shopping-cart"></i>
          </div>
          <div class="card-title">
            <h3>E-commerce</h3>
            <span class="card-period">Previous</span>
          </div>
        </div>
        <div class="card-content">
          <p>Built large-scale recommendation systems from scratch, handling millions of users and products.</p>
          <div class="tech-tags">
            <span class="tech-tag">Recommendation Systems</span>
            <span class="tech-tag">Large Scale</span>
            <span class="tech-tag">ML Engineering</span>
          </div>
        </div>
      </div>

      <div class="experience-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-title">
            <h3>Data Science & ML</h3>
            <span class="card-period">Earlier</span>
          </div>
        </div>
        <div class="card-content">
          <p>Data science/ML roles focused on NLP and time-series modeling across various industries.</p>
          <div class="tech-tags">
            <span class="tech-tag">NLP</span>
            <span class="tech-tag">Time Series</span>
            <span class="tech-tag">Data Science</span>
          </div>
        </div>
      </div>

      <div class="experience-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-flask"></i>
          </div>
          <div class="card-title">
            <h3>Research</h3>
            <span class="card-period">Ongoing</span>
          </div>
        </div>
        <div class="card-content">
          <p>Work on Bayesian diffusion models and interpretable geospatial modeling, integrating statistical methods with modern deep learning.</p>
          <div class="tech-tags">
            <span class="tech-tag">Bayesian</span>
            <span class="tech-tag">Geospatial</span>
            <span class="tech-tag">Diffusion</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Skills Section -->
  <section class="about-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-tools"></i>
        Technical Expertise
      </h2>
    </div>
    
    <div class="skills-container">
      <div class="skill-category">
        <h3>Machine Learning</h3>
        <div class="skill-tags">
          <span class="skill-tag">Deep Learning</span>
          <span class="skill-tag">NLP</span>
          <span class="skill-tag">Time Series</span>
          <span class="skill-tag">Recommendation Systems</span>
        </div>
      </div>
      
      <div class="skill-category">
        <h3>Technologies</h3>
        <div class="skill-tags">
          <span class="skill-tag">Python</span>
          <span class="skill-tag">PySpark</span>
          <span class="skill-tag">PyTorch</span>
          <span class="skill-tag">TensorFlow</span>
          <span class="skill-tag">AWS</span>
          <span class="skill-tag">Docker</span>
          <span class="skill-tag">Kubernetes</span>
        </div>
      </div>
      
      <div class="skill-category">
        <h3>Research Areas</h3>
        <div class="skill-tags">
          <span class="skill-tag">Diffusion Models</span>
          <span class="skill-tag">Geospatial ML</span>
          <span class="skill-tag">Bayesian Methods</span>
        </div>
      </div>
    </div>
  </section>
</div>

<style>
.about-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Hide the layout's default page title on this page (fixes low-contrast "About" in dark mode) */
h1.page-title:has(+ .about-page),
h1.post-title:has(+ .about-page) {
  display: none;
}
/* Fallback for browsers without :has() — scope to this page only by reducing space and dimming */
@supports not (selector(:has(*))) {
  h1.page-title, h1.post-title {
    color: var(--text-secondary);
    opacity: .6;
  }
}

/* Hero Section */
.about-hero {
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-1xl);
  margin-bottom: var(--spacing-3xl);
  text-align: center;
}

.profile-section {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.profile-info {
  text-align: center;
  max-width: 800px;
}

.profile-name {
  font-size: var(--font-size-1xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  line-height: 1.2;
}

.profile-title {
  font-size: var(--font-size-lg);
  color: var(--accent-primary);
  font-weight: 600;
  margin: 0 0 var(--spacing-xs) 0;
}

.profile-subtitle {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin: 0 0 var(--spacing-lg) 0;
}

.profile-highlights {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.highlight-tag {
  background: transparent;
  color: var(--text-secondary);
  padding: 0;
  border-radius: 0;
  font-size: var(--font-size-sm);
  font-weight: 400;
}

.highlight-tag:hover {
  text-decoration: underline;
}

/* Section Styles */
.about-section {
  margin-bottom: var(--spacing-3xl);
}

.section-header {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.section-title i {
  color: var(--accent-primary);
  font-size: var(--font-size-lg);
}

/* Content Card */
.content-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow);
}

.intro-text {
  font-size: var(--font-size-sm);
  line-height: 1.7;
  color: var(--text-primary);
  margin: 0;
  font-weight: 400;
}

.intro-paragraph {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--font-size-sm);
  line-height: 1.7;
  color: var(--text-primary);
}

.intro-paragraph:last-child {
  margin-bottom: 0;
}

/* Inline keyword accent (avoid .highlight to not clash with Jekyll/Rouge) */
.kw {
  font-weight: 600;
  color: color-mix(in oklab, var(--text-primary) 88%, var(--accent-primary) 12%);
}
@supports not (color-mix(in oklab, black 10%, white)) {
  .kw {
    color: var(--accent-primary);
    opacity: .9;
  }
}

/* Experience Grid */
.experience-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-xl);
}

.experience-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.experience-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--accent-primary);
}

.experience-card.featured {
  border-color: var(--accent-primary);
  background: linear-gradient(135deg, var(--bg-primary) 0%, rgba(13, 110, 253, 0.02) 100%);
}

.experience-card.featured::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.card-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.card-title h3 {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.card-period {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  font-weight: 500;
}

.card-content p {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  margin: 0 0 var(--spacing-md) 0;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.tech-tag {
  background: transparent;
  color: var(--text-secondary);
  padding: 0;
  border-radius: 0;
  font-size: var(--font-size-sm);
  font-weight: 400;
  border: none;
}

/* Skills Container */
.skills-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-xl);
}

.skill-category h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.skill-tag {
  background: transparent;
  color: var(--text-secondary);
  padding: 0;
  border-radius: 0;
  font-size: var(--font-size-sm);
  font-weight: 400;
  border: none;
}

.skill-tag:hover {
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-section {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-info {
    text-align: center;
  }
  
  .experience-grid,
  .skills-container {
    grid-template-columns: 1fr;
  }
  
  .skills-container {
    grid-template-columns: 1fr;
  }
  
  .profile-name {
    font-size: var(--font-size-3xl);
  }
  
  .section-title {
    font-size: var(--font-size-2xl);
  }
}
</style>
