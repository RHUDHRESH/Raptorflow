import os

from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


def visualize():

    print("Generating graph visualization...")
    try:
        # Generate Mermaid PNG
        png_data = moves_campaigns_orchestrator.get_graph().draw_mermaid_png()
        output_dir = "docs/graphs"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "moves_campaigns_orchestrator.png")
        with open(output_path, "wb") as f:
            f.write(png_data)

        print(f"Visualization saved to: {output_path}")

        # Also save as mermaid markdown for documentation
        mermaid_str = moves_campaigns_orchestrator.get_graph().draw_mermaid()
        md_path = os.path.join(output_dir, "moves_campaigns_orchestrator.md")
        with open(md_path, "w") as f:
            f.write("```mermaid\n")
            f.write(mermaid_str)
            f.write("\n```")
        print(f"Mermaid markdown saved to: {md_path}")

    except Exception as e:
        print(f"Error generating visualization: {e}")
        print("Falling back to Mermaid string output...")
        mermaid_str = moves_campaigns_orchestrator.get_graph().draw_mermaid()
        print("\n" + mermaid_str + "\n")


if __name__ == "__main__":
    visualize()
