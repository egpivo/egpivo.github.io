---
layout: page
title: Reading List
menu: main
permalink: /books/
---

<p style="color:#666;margin-top:0">Note: This is a personal reading list of books I recommend or have read. All books are authored by their respective writers — not by me.</p>

<style>
  .category {
    margin-top: 0;
  }

  .book-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 20px;
  }

  .book {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: calc(25% - 20px);
    font-size: 0.9rem; /* slightly smaller base for book blocks */
  }

  .book-image {
    max-width: 100%;
    border-radius: 5px;
  }

  .book-title {
    font-weight: bold;
    margin-top: 10px;
    font-size: 1rem; /* reduce title size */
  }

  .book-author {
    color: #888;
    font-size: 0.85rem; /* smaller author text */
  }
</style>

<script async src="https://www.googletagmanager.com/gtag/js?id=G-SDL912WM98"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);} 
  gtag('js', new Date());
  gtag('config', 'G-SDL912WM98');
  
  // Sort books in each container by data-pub (descending)
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.book-container').forEach(function(container) {
      const books = Array.from(container.querySelectorAll('.book'));
      books.sort((a, b) => {
        const da = new Date(a.getAttribute('data-pub') || '1900-01-01');
        const db = new Date(b.getAttribute('data-pub') || '1900-01-01');
        return db - da;
      });
      books.forEach(book => container.appendChild(book));
    });
  });
  
</script>

Over the last 7 years in the tech industry, I've immersed myself in a diverse range of books, from technical gems to personal development classics like "High Performance Habits."
These readings symbolize my dual commitment to tech excellence and personal growth. Each book has been a stepping stone in shaping both my professional and personal trajectory.

<!-- Tech Section -->
<div class="category">
    <h4>Tech</h4>
    <div class="book-container">
        <div class="book" data-pub="2016-11-18">
            <img class="book-image" src="{{ site.url }}/assets/books/deep-learning.png" alt="TBook 1">
            <div class="book-title">Deep Learning</div>
            <div class="book-author">Ian Goodfellow, Yoshua Bengio & Aaron Courville</div>
        </div>
        <div class="book" data-pub="2018-10-15">
            <img class="book-image" src="{{ site.url }}/assets/books/introduction-to-reinforcement-learning.png" alt="TBook 2">
            <div class="book-title">Reinforcement Learning: An Introduction</div>
            <div class="book-author">Richard Sutton & Andrew Barto </div>
        </div>
        <div class="book" data-pub="2020-01-10">
            <img class="book-image" src="{{ site.url }}/assets/books/mining-massive-dataset.png" alt="TBook 2">
            <div class="book-title">Mining Massive Dataset</div>
            <div class="book-author">Jure Leskovec, Anand Rajaraman, & Jeffrey David Ullman</div>
        </div>
        <div class="book" data-pub="2020-08-01">
            <img class="book-image" src="{{ site.url }}/assets/books/machine-learning-design-patterns.png" alt="TBook 3">
            <div class="book-title">Machine Learning Design Patterns: Solutions to Common Challenges in Data Preparation, Model Building, and MLOps</div>
            <div class="book-author">Valliappa Lakshmanan, Sara Robinson & Michael Munn</div>
        </div>
        <div class="book" data-pub="2022-05-01">
            <img class="book-image" src="{{ site.url }}/assets/books/designing-machine-learning-systems.png" alt="TBook 3">
            <div class="book-title">Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications</div>
            <div class="book-author">Chip Huyen</div>
        </div>
        <div class="book" data-pub="2018-12-24">
            <img class="book-image" src="{{ site.url }}/assets/books/clean-code-in-python.png" alt="TBook 4">
            <div class="book-title">Clean Code in Python: Refactor your legacy code base</div>
            <div class="book-author">Mariano Anaya</div>
        </div>
        <div class="book" data-pub="2017-05-10">
            <img class="book-image" src="{{ site.url }}/assets/books/high-performance-spark.png" alt="TBook 5">
            <div class="book-title">High Performance Spark: Best Practices for Scaling and Optimizing Apache Spark</div>
            <div class="book-author">Tomasz Drabas & Denny Lee</div>
        </div>
        <div class="book" data-pub="2016-07-01">
            <img class="book-image" src="{{ site.url }}/assets/books/data-analytics-with-hadoop.png" alt="TBook 6">
            <div class="book-title">Data Analytics with Hadoop: An Introduction for Data Scientists</div>
            <div class="book-author"> Benjamin Bengfort & Jenny Kim</div>
        </div>
        <div class="book" data-pub="2017-03-16">
            <img class="book-image" src="{{ site.url }}/assets/books/designing-data-intensive-applications.png" alt="TBook 7">
            <div class="book-title">Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems</div>
            <div class="book-author">Martin Kleppmannn</div>
        </div>
        <div class="book" data-pub="2013-11-01">
            <img class="book-image" src="{{ site.url }}/assets/books/redis-in-action.png" alt="TBook 8">
            <div class="book-title">Redis in Action</div>
            <div class="book-author">Josiah Carlson</div>
        </div>
        <div class="book" data-pub="2022-10-01">
            <img class="book-image" src="{{ site.url }}/assets/books/ai-engineering.png" alt="TBook 9" />
            <div class="book-title"> AI Engineering: Building Applications with Foundation Models </div>
            <div class="book-author">Chip Huyen</div>
        </div>  
    </div>
</div>

<!-- Non-Tech Section -->
<body class="category">
    <h4>Non-Tech</h4>
    <div class="book-container">
        <div class="book" data-pub="2017-09-19">
            <img class="book-image" src="{{ site.url }}/assets/books/high-performance-habits.png" alt="Book 1">
            <div class="book-title">High Performance Habits</div>
            <div class="book-author">Brendon Burchard</div>
        </div>

        <div class="book" data-pub="2006-02-28">
            <img class="book-image" src="{{ site.url }}/assets/books/mindset.png" alt="Book 2">
            <div class="book-title">Mindset</div>
            <div class="book-author">Carol Dweck</div>
        </div>

        <div class="book" data-pub="2016-09-13">
            <img class="book-image" src="{{ site.url }}/assets/books/the-subtle-art-of-not-giving-a-fuck.png" alt="Book 3">
            <div class="book-title">The Subtle Art of Not Giving A Fxck</div>
            <div class="book-author">Mark Manson</div>
        </div>

        <div class="book" data-pub="2014-04-15">
            <img class="book-image" src="{{ site.url }}/assets/books/essentialism.png" alt="Book 4">
            <div class="book-title">Essentialism: The Disciplined Pursuit of Less</div>
            <div class="book-author">Greg McKeown</div>
        </div>

        <div class="book" data-pub="2017-04-04">
            <img class="book-image"
                 src="{{ site.url }}/assets/books/make-your-bed-little-things-that-can-change-your-life.png" alt="Book 5">
            <div class="book-title">Make Your Bed: Little Things That Can Change Your Life... and Maybe the Worlds</div>
            <div class="book-author">Admiral William H. McRaven</div>
        </div>
        <div class="book" data-pub="1997-10-06">
            <img class="book-image" src="{{ site.url }}/assets/books/the-power-of-now.png" alt="Book 6">
            <div class="book-title">The Power of Now</div>
            <div class="book-author">Eckhart Tolle</div>
        </div>
        <div class="book" data-pub="2018-10-16">
            <img class="book-image" src="{{ site.url }}/assets/books/atomic-habits.jpg" alt="Book 7">
            <div class="book-title">Atomic Habits</div>
            <div class="book-author">James Clear</div>
        </div>
        <div class="book" data-pub="2017-06-06">
            <img class="book-image" src="{{ site.url }}/assets/books/peak-performance.png" alt="Book 8">
            <div class="book-title">Peak Performance: Elevate Your Game, Avoid Burnout, and Thrive with the New Science of Success</div>
            <div class="book-author">Brad Stulberg & Steve Magness</div>
        </div>
        <div class="book" data-pub="2021-05-25">
            <img class="book-image" src="{{ site.url }}/assets/books/staff-engineer.png" alt="Book 9">
            <div class="book-title">Staff Engineer: Leadership beyond the management track</div>
            <div class="book-author">Will Larson & Tanya Reilly </div>
        </div>
        <div class="book" data-pub="2011-01-10">
            <img class="book-image" src="{{ site.url }}/assets/books/the-millionaire-fastlane.png" alt="Book 10">
            <div class="book-title">The Millionaire Fastlane</div>
            <div class="book-author">MJ DeMarco</div>
        </div>
        <div class="book" data-pub="1988-01-01">
            <img class="book-image" src="{{ site.url }}/assets/books/the-alchemist.png" alt="Book 11">
            <div class="book-title">The Alchemist</div>
            <div class="book-author">Paulo Coelho </div>
        </div>
        <div class="book" data-pub="2020-06-01">
            <img class="book-image" src="{{ site.url }}/assets/books/the-mountain-is-you.png" alt="Book 12 - 2024/01">
            <div class="book-title">The Mountain Is You</div>
            <div class="book-author">Brianna Wiest</div>
        </div>
        <div class="book" data-pub="2013-05-30">
            <img class="book-image" src="{{ site.url }}/assets/books/12-week-year.png" alt="Book 13 - 2024/02">
            <div class="book-title">The 12 Week Year: Get More Done in 12 Weeks than Others Do in 12 Months</div>
            <div class="book-author">Brian Morgan & Michael Lennington</div>
        </div>
        <div class="book" data-pub="2020-09-08">
            <img class="book-image" src="{{ site.url }}/assets/books/psychology-of-money.png" alt="Book 14- 2024/03">
            <div class="book-title">The Psychology of Money: Timeless lessons on wealth, greed, and happiness</div>
            <div class="book-author">Morgan Housel</div>
        </div>
        <div class="book" data-pub="2008-11-18">
            <img class="book-image" src="{{ site.url }}/assets/books/outliers.jpeg" alt="Book 15 - 2024/04">
            <div class="book-title">Outliers: The Story of Success</div>
            <div class="book-author">Malcolm Gladwell</div>
        </div>
        <div class="book" data-pub="2007-10-03">
            <img class="book-image" src="{{ site.url }}/assets/books/untethered-soul.jpg" alt="Book 16 - 2024/06">
            <div class="book-title">The Untethered Soul: The Journey Beyond Yourself</div>
            <div class="book-author">Michael Alan Singer</div>
        </div>
        <div class="book" data-pub="1997-08-18">
            <img class="book-image" src="{{ site.url }}/assets/books/tuesdays-with-morrie.png" alt="Book 17 - 2024/08">
            <div class="book-title">Tuesdays with Morrie </div>
            <div class="book-author">Mitch Albom</div>
        </div>
        <div class="book" data-pub="2023-05-09">
            <img class="book-image" src="{{ site.url }}/assets/books/10x-is-easier-than-2x.jpg" alt="Book 18 - 2025/01">
            <div class="book-title">10x Is Easier Than 2x: How World-Class Entrepreneurs Achieve More by Doing Less </div>
            <div class="book-author">Dan Sullivan & Benjamin Hardy Jr.</div>
        </div>
        <div class="book" data-pub="2022-01-01">
            <img class="book-image" src="{{ site.url }}/assets/books/the-pathless-path.jpg" alt="Book 18 - 2025/06">
            <div class="book-title">The Pathless Path </div>
            <div class="book-author">Paul Millerd</div>
        </div>        
    </div>
</body>
