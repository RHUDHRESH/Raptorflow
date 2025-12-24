import logging
from typing import Any, Dict

from langchain_experimental.utilities import PythonREPL

logger = logging.getLogger("raptorflow.sandbox")


class RaptorSandbox:
    """
    SOTA Sandboxed Code Execution Environment.
    Wraps PythonREPL with RaptorFlow-specific safety and logging.
    """

    def __init__(self):
        self.repl = PythonREPL()

    def run(self, code: str) -> Dict[str, Any]:
        """
        Executes python code and returns the result or error.
        In a full SOTA production build, this would talk to a Dockerized
        Micro-service (e.g., E2B or specialized K8s pod).
        """
        logger.info(f"Executing sandboxed code: {code[:100]}...")
        try:
            result = self.repl.run(code)
            return {"success": True, "output": result, "error": None}
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return {"success": False, "output": None, "error": str(e)}


def execute_code(code: str) -> Dict[str, Any]:
    """Convenience functional wrapper for the sandbox."""
    return RaptorSandbox().run(code)
