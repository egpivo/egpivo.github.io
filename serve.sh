#!/usr/bin/env bash
# Build Jekyll _site to a local path (outside iCloud) to avoid ETIMEDOUT when repo is in iCloud Drive.
set -e
cd "$(dirname "$0")"
bundle exec jekyll serve --future --destination /tmp/egpivo_jekyll_site "$@"
