---
layout: page
title: Software
description: "R packages (SpatPCA, SpatMCA, autoFRK), Python apps (KB Bridge, LLM Chatbot), and blockchain projects (Ethereum Account State, Metering Chain, Pay-As-You-Go)."
menu: main
permalink: /software/
---

<div class="software">

{% for section in site.data.software %}
{% assign section_data = section[1] %}
<section class="software-section">
  <header class="software-section-header">
    <h2 class="software-section-title">{{ section_data.title }}</h2>
    <p class="software-section-desc">{{ section_data.desc }}</p>
  </header>
  <div class="software-cards">
    {% for item in section_data.items %}
    {% include software_card.html item=item %}
    {% endfor %}
  </div>
</section>
{% endfor %}

</div>
