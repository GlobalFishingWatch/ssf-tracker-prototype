---
SSF Tracker State Transition Diagram
---

```mermaid
flowchart TD
  start([Start]) --> setup([Setup])
  setup -. timeout .-> sleep([Sleep])
  setup -- activity --> setup
  sleep -- double press --> setup
  sleep -. timer .-> log_gps([Log GPS])
  log_gps --> sleep
  log_gps -- buffer full --> transmit([Transmit])
  transmit --> sleep
  sleep -- short press --> status([Status])
  status -. timeout .-> sleep
  sleep -- long press --> warn_gps([Warn GPS])
  warn_gps -. timeout .-> sos([SOS])
  warn_gps -- long press --> sleep
  sos -- long press --> sleep
```