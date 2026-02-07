# Retry file writes on Errno::EINTR (Interrupted system call) and Errno::ECANCELED.
# EINTR: common when jekyll serve runs with file watchers or under load.
# ECANCELED: on macOS, can occur when cloud sync or IDE file watchers briefly interfere with writes.

require "jekyll"

RETRYABLE = [Errno::EINTR, Errno::ECANCELED].freeze

def retry_eintr(max_tries = 5)
  tries = 0
  begin
    yield
  rescue *RETRYABLE => e
    tries += 1
    raise if tries >= max_tries
    retry
  end
end

module Jekyll
  module Convertible
    def write(dest)
      path = destination(dest)
      FileUtils.mkdir_p(File.dirname(path))
      Jekyll.logger.debug "Writing:", path
      retry_eintr { File.write(path, output, :mode => "wb") }
      Jekyll::Hooks.trigger hook_owner, :post_write, self
    end
  end

  class Document
    def write(dest)
      path = destination(dest)
      FileUtils.mkdir_p(File.dirname(path))
      Jekyll.logger.debug "Writing:", path
      retry_eintr { File.write(path, output, :mode => "wb") }
      trigger_hooks(:post_write)
    end
  end
end
