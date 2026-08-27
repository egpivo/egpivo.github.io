---
layout: page
title: About
hide_title: true
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
          <p class="profile-title">Machine Learning Engineer &amp; Researcher</p>
          <p class="profile-subtitle">Ph.D. in Statistics • 10+ Years in Production ML</p>
          <div class="profile-highlights">
            <span class="highlight-tag">AI Product Engineering</span>
            <span class="highlight-tag">Research &amp; Development</span>
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
I'm a machine learning engineer with nearly ten years of hands-on experience and a Ph.D. in Statistics. I build end-to-end systems that combine solid modeling with reliable data and infrastructure — and make sure they work at scale. Lately, I've been working on agentic workflows, RAG systems, and spatiotemporal modeling, blending practical engineering with research. My current focus is on building statistical boosters around pretrained models — things like conformal prediction and low-rank adapters — so that complex systems become both more trustworthy and easier to reason about.
        </p>
        <p class="intro-paragraph">
More recently, I've been focusing on <strong>blockchain infrastructure and on-chain markets</strong>—using statistics, ML, and systems thinking to study market structure, execution, and liquidity, and to reconstruct and audit the infrastructure behind prices from public on-chain data.
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
          <p>Entity linking for news analytics; RAG + MCP Q&amp;A for an energy client.</p>
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
          <p>Large-scale recommendation systems from scratch.</p>
          <div class="tech-tags">
            <span class="tech-tag">Recommendation Systems</span>
            <span class="tech-tag">Large Scale</span>
          </div>
        </div>
      </div>

      <div class="experience-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-title">
            <h3>Data Science &amp; ML</h3>
            <span class="card-period">Earlier</span>
          </div>
        </div>
        <div class="card-content">
          <p>NLP and time-series modeling across industries.</p>
          <div class="tech-tags">
            <span class="tech-tag">NLP</span>
            <span class="tech-tag">Time Series</span>
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
          <p>Bayesian diffusion models; interpretable geospatial ML.</p>
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

  <!-- Publications -->
  <section class="about-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-book"></i>
        Publications
      </h2>
    </div>
    <div class="content-card">
      <ul class="publication-list">
        {% for pub in site.data.publications %}
        <li class="publication-item">
          {% if pub.url %}
          <a class="publication-title" href="{% if pub.url contains '://' %}{{ pub.url }}{% else %}{{ site.baseurl }}{{ pub.url }}{% endif %}" rel="noopener noreferrer" target="_blank">{{ pub.title }}</a>
          {% else %}
          <span class="publication-title">{{ pub.title }}</span>
          {% endif %}
          <span class="publication-meta">{{ pub.authors }} · {{ pub.venue }}, {{ pub.year }}</span>
          {% if pub.software %}
          <span class="publication-software">
            <i class="fab fa-github" aria-hidden="true"></i>
            {% if pub.software.url %}
            <a href="{{ pub.software.url }}" rel="noopener noreferrer" target="_blank">{{ pub.software.name }}</a>
            {% else %}
            <a href="{{ pub.software.github }}" rel="noopener noreferrer" target="_blank">{{ pub.software.name }}</a>
            {% endif %}
            · <a href="{{ pub.software.github }}" rel="noopener noreferrer" target="_blank">GitHub</a>
          </span>
          {% endif %}
        </li>
        {% endfor %}
      </ul>
      <p class="publication-more">
        <a href="https://scholar.google.com/citations?user=GAKosCMAAAAJ" rel="noopener noreferrer" target="_blank">Google Scholar →</a>
        · <a href="{{ site.baseurl }}/software/">Software →</a>
      </p>
    </div>
  </section>
</div>
