import argparse
import os

from . import ResearchAgent, ResearchAgentConfig


def main() -> int:
    p = argparse.ArgumentParser(
        description="Run the 300-iteration autonomous research agent"
    )
    p.add_argument(
        "--topic",
        default="autonomous research agent architectures",
        help="High-level research topic",
    )
    p.add_argument(
        "--iterations",
        type=int,
        default=12,
        help="Number of iterations (default: 12; use 300 for full run)",
    )
    p.add_argument(
        "--batch-size", type=int, default=6, help="Batch size for concurrent search"
    )
    p.add_argument(
        "--log-path",
        default="research_agent/output/research_log.jsonl",
        help="JSONL output path",
    )
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.log_path) or ".", exist_ok=True)

    cfg = ResearchAgentConfig(
        research_topic=args.topic,
        total_iterations=int(args.iterations),
        batch_size=int(args.batch_size),
        log_path=str(args.log_path),
    )
    agent = ResearchAgent(cfg)
    out_path = agent.run_sync()
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
