# Jekyll serve

Correct command (note: **incremental**, not incemental):

```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4000 --incremental
```

- `_plugins/retry_eintr.rb` retries file writes on `Errno::EINTR` so builds are less likely to fail when interrupted.
- Sass deprecation warnings (`@import`) are harmless until Dart Sass 3.0.
