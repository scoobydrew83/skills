wrote: /Users/dkennedy/dev/projects/skills/skill-graph.md
rom the skill source directories._
_If this drifts from `COORDINATION-STATUS.md`, the source wins — update the doc._

## Phase × handoffs

| Skill | phase | hands_off_to | notes |
|---|---|---|---|
| `overwhelm-breakdown` | intake | agent-orchestration, neurodivergent-comms, session-bookend |  |
| `derisk-sequencer` | plan | experiment-designer, agent-orchestration |  |
| `experiment-designer` | plan | idea-validator, derisk-sequencer |  |
| `agent-orchestration` | execute | reality-check, drift-check, conductor-memory, session-bookend |  |
| `goal-builder` | execute | loop-creator |  |
| `loop-creator` | execute | reality-check, drift-check, goal-builder |  |
| `prompt-template-generator` | execute | drift-check, reality-check |  |
| `repo-troubleshooting-guide` | execute | drift-check |  |
| `system-prompt-builder` | execute | reality-check, drift-check, conductor-memory |  |
| `drift-check` | verify | reality-check, conductor-memory |  |
| `idea-validator` | verify | derisk-sequencer, experiment-designer |  |
| `reality-check` | verify | drift-check, conductor-memory |  |
| `neurodivergent-comms` | communicate | — |  |
| `conductor-memory` | bookend | session-continuity |  |
| `project-postmortem` | bookend | conductor-memory |  |
| `session-bookend` | bookend | overwhelm-breakdown, agent-orchestration, conductor-memory |  |
| `session-continuity` | bookend | session-bookend |  |
| `adaptive-communication` | meta | neurodivergent-comms | DEPRECATED tombstone |
| `task-decomposition` | meta | overwhelm-breakdown | DEPRECATED tombstone |

## Handoff graph

```mermaid
graph LR
  subgraph intake
    overwhelm-breakdown
  end
  subgraph plan
    derisk-sequencer
    experiment-designer
  end
  subgraph execute
    agent-orchestration
    goal-builder
    loop-creator
    prompt-template-generator
    repo-troubleshooting-guide
    system-prompt-builder
  end
  subgraph verify
    drift-check
    idea-validator
    reality-check
  end
  subgraph communicate
    neurodivergent-comms
  end
  subgraph bookend
    conductor-memory
    project-postmortem
    session-bookend
    session-continuity
  end
  subgraph meta
    adaptive-communication["adaptive-communication<br/><i>DEPRECATED</i>"]
    task-decomposition["task-decomposition<br/><i>DEPRECATED</i>"]
  end
  adaptive-communication --> neurodivergent-comms
  agent-orchestration --> reality-check
  agent-orchestration --> drift-check
  agent-orchestration --> conductor-memory
  agent-orchestration --> session-bookend
  conductor-memory --> session-continuity
  derisk-sequencer --> experiment-designer
  derisk-sequencer --> agent-orchestration
  drift-check --> reality-check
  drift-check --> conductor-memory
  experiment-designer --> idea-validator
  experiment-designer --> derisk-sequencer
  goal-builder --> loop-creator
  idea-validator --> derisk-sequencer
  idea-validator --> experiment-designer
  loop-creator --> reality-check
  loop-creator --> drift-check
  loop-creator --> goal-builder
  overwhelm-breakdown --> agent-orchestration
  overwhelm-breakdown --> neurodivergent-comms
  overwhelm-breakdown --> session-bookend
  project-postmortem --> conductor-memory
  prompt-template-generator --> drift-check
  prompt-template-generator --> reality-check
  reality-check --> drift-check
  reality-check --> conductor-memory
  repo-troubleshooting-guide --> drift-check
  session-bookend --> overwhelm-breakdown
  session-bookend --> agent-orchestration
  session-bookend --> conductor-memory
  session-continuity --> session-bookend
  system-prompt-builder --> reality-check
  system-prompt-builder --> drift-check
  system-prompt-builder --> conductor-memory
  task-decomposition --> overwhelm-breakdown
```

## Source

Generated 2026-06-29 10:40 CDT from 19 skill(s).
