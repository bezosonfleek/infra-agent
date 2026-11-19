"""infra-agent: diagnose Docker container problems, rules first, LLM second."""

# Note: `classify` (the function) is deliberately NOT re-exported here. It would
# shadow the `infra_agent.classify` module. Use:
#   from infra_agent.classify import classify
__version__ = "0.1.0"
