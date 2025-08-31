---
layout: page
title: Posts
menu: main
permalink: /posts/
---

<h4>Blog Posts</h4>

Here you'll find my thoughts on machine learning, statistics, and data science.

{% for post in site.posts %}
<div class="post-preview">
  <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
  <p class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</p>
  {% if post.excerpt %}
  <p>{{ post.excerpt }}</p>
  {% endif %}
</div>
{% endfor %}
