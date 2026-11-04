#!/usr/bin/env ruby
# Anthropic Agent Skills authoring checks for one SKILL.md.
# Prints "PASS|FAIL|WARN<TAB>check<TAB>message" lines; never exits nonzero itself.
#
#   FAIL  description over 1,024 characters (hard limit in the Agent Skills spec)
#   FAIL  SKILL.md body over 500 lines (keep the entry file lean; split to references/)
#   FAIL  name not lowercase-hyphen, over 64 chars, or uses a reserved word
#   WARN  description not written in third person ("Makes your…", "Use…", "You…")
#   WARN  a references/*.md file over 100 lines has no table of contents

require "yaml"

path = ARGV.fetch(0)
text = File.read(path, encoding: "UTF-8")
match = text.match(/\A---\s*\n(.*?)^---\s*$\n?(.*)\z/m)
exit 0 unless match
data = YAML.safe_load(match[1], permitted_classes: [], aliases: false) rescue exit(0)
body = match[2]

def out(status, check, msg = "")
  puts [status, check, msg].join("\t")
end

desc = data["description"].to_s
if desc.length > 1024
  out "FAIL", "description-length", "#{desc.length} chars > 1024 (Agent Skills limit)"
else
  out "PASS", "description-length (#{desc.length})"
end

if desc.strip.match?(/\A(Makes your|Use\b|You\b|Your\b|I\b)/)
  out "WARN", "description-third-person", "opens with \"#{desc.strip[0, 20]}…\" — start with what the skill does, in third person"
end

name = data["name"].to_s
if name.match?(/\A[a-z0-9]+(-[a-z0-9]+)*\z/) && name.length <= 64 && !name.match?(/anthropic|claude/)
  out "PASS", "name-format"
else
  out "FAIL", "name-format", "name must be lowercase-hyphen, <= 64 chars, without 'anthropic' or 'claude'"
end

lines = body.lines.count
if lines > 500
  out "FAIL", "body-length", "#{lines} lines > 500 — move detail into references/"
else
  out "PASS", "body-length (#{lines})"
end

Dir.glob(File.join(File.dirname(path), "references", "*.md")).sort.each do |ref|
  ref_lines = File.readlines(ref, encoding: "UTF-8")
  next if ref_lines.length <= 100
  head = ref_lines.first(40).join
  unless head.match?(/^#+\s*(Contents|Table of contents|TOC)\b/i)
    out "WARN", "reference-toc", "#{File.basename(ref)} is #{ref_lines.length} lines with no Contents heading near the top"
  end
end
