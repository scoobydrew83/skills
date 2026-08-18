#!/usr/bin/env ruby
# Strict YAML frontmatter parser for portable SKILL.md files.

require "yaml"

path = ARGV.fetch(0)
text = File.read(path, encoding: "UTF-8")
match = text.match(/\A---\s*\n(.*?)^---\s*$/m)
abort "no YAML frontmatter block" unless match

begin
  data = YAML.safe_load(match[1], permitted_classes: [], aliases: false)
rescue Psych::Exception => error
  abort "invalid YAML: #{error.message.lines.first.strip}"
end

abort "frontmatter must be a mapping" unless data.is_a?(Hash)
abort "name must be a string" unless data["name"].is_a?(String)
abort "description must be a string" unless data["description"].is_a?(String)
puts "valid YAML"
