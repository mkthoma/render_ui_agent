"""Session 14 UI layer, folded into the Session 13 runtime.

Turns an S13 graph outcome into a declarative A2UI surface, streams the S13
journal as AG-UI events, and carries user actions back as validated events.
The runtime and this UI ship as one service; the UI reads the runtime's graph
in-process and executes none of the agent's text.
"""

__version__ = "0.1.0"
