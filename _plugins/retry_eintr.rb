# Retry file writes on Errno::EINTR (Interrupted system call).
# Common when jekyll serve runs with file watchers or under load.
# Patches Convertible (pages) and Document (posts) since both define write.

require "jekyll"

def retry_eintr(max_tries = 5)
  tries = 0
  begin
    yield
  rescue Errno::EINTR
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
