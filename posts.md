---
layout: page
title: Posts
menu: main
permalink: /posts/
---

<h4>Blog Posts</h4>

Here you'll find my thoughts on machine learning, statistics, and data science.

{% for post in paginator.posts %}
<div class="post-preview">
  <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
  <p class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</p>
  {% if post.excerpt %}
  <p>{{ post.excerpt }}</p>
  {% endif %}
</div>
{% endfor %}

<nav class="pagination" role="navigation" aria-label="Pagination" style="margin-top: 1.5rem; display:flex; gap:12px; align-items:center;">
  {% if paginator.previous_page %}
    <a class="btn btn-outline" href="{{ paginator.previous_page_path | prepend: site.baseurl }}">Newer</a>
  {% else %}
    <span class="btn btn-outline" style="opacity:.5; pointer-events:none;">Newer</span>
  {% endif %}

  <span>Page {{ paginator.page }} of {{ paginator.total_pages }}</span>

  {% if paginator.next_page %}
    <a class="btn btn-outline" href="{{ paginator.next_page_path | prepend: site.baseurl }}">Older</a>
  {% else %}
    <span class="btn btn-outline" style="opacity:.5; pointer-events:none;">Older</span>
  {% endif %}
</nav>
