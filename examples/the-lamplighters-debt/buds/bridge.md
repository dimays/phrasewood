---
id: bridge
once: true
choices:
  - label: Offer your lantern as payment
    do: trust += 3; ferryman.mood = 'warm'
    goto: ferry
  - label: Ask how he knows your name
    do: trust += 1
    goto: ferry
---
The bridge is out. Rain needles the lantern glass, and the river runs black and
fast. At the dock a ferryman waits beneath a hood — and when he looks up, he says
your name.
