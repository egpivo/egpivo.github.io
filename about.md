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
I’m a machine learning engineer with nearly ten years of hands-on experience and a Ph.D. in Statistics. I build end-to-end systems that combine solid modeling with reliable data and infrastructure — and make sure they work at scale. Lately, I’ve been working on <span class="kw">agentic workflows</span>, <span class="kw">RAG systems</span>, and <span class="kw">spatiotemporal modeling</span>, blending practical engineering with research. My current focus is on building statistical boosters around pretrained models — things like <span class="kw">conformal prediction</span> and <span class="kw">low-rank adapters</span> — so that complex systems become both more trustworthy and easier to reason about.
        </p>
      </div>
    </div>
  </section>

  <!-- Writing (Medium) -->
  {% if site.medium_url %}
  <section class="about-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fab fa-medium"></i>
        Writing
      </h2>
    </div>
    <div class="content-card">
      <p class="intro-paragraph">
        Long-form posts live on this site first. I also publish on
        <a href="{{ site.medium_url }}" rel="noopener noreferrer" target="_blank">Medium</a>
        for reach and editorial distribution. Recent blockchain and protocol writing has mostly run through
        <a href="https://blog.blockmagnates.com/" rel="noopener noreferrer" target="_blank">Block Magnates</a>,
        <a href="https://coinsbench.com/" rel="noopener noreferrer" target="_blank">CoinsBench</a>, and
        <a href="https://medium.com/coinmonks" rel="noopener noreferrer" target="_blank">Coinmonks</a>.
      </p>
    </div>
  </section>
  {% endif %}

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
          <span class="skill-tag">AWS/Azure</span>
          <span class="skill-tag">FastAPI/FastMCP</span>
          <span class="skill-tag">Docker</span>
          <span class="skill-tag">Kubernetes</span>
          <span class="skill-tag">Solidity</span>
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
