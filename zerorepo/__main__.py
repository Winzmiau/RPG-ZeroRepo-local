"""
ZeroRepo CLI Entry Point
Usage: python3 -m zerorepo --mission missions/osint_dashboard.yaml --phase 1
"""
import argparse
import yaml
import json
import sys
import os
from pathlib import Path

from .zerorepo import ZeroRepo


def main():
    parser = argparse.ArgumentParser(description="ZeroRepo - Autonomous Repository Generator")
    parser.add_argument("--mission", required=True, help="Path to mission YAML file")
    parser.add_argument("--phase", type=int, default=0, help="Phase to run (1=prop, 2=impl, 3=codegen, 0=all)")
    parser.add_argument("--config", default="configs/zerorepo_config.yaml", help="Path to ZeroRepo config")
    parser.add_argument("--checkpoint-dir", default="checkpoints", help="Checkpoint directory")
    parser.add_argument("--output-dir", default="output", help="Output repository directory")
    args = parser.parse_args()

    # Load mission file
    mission_path = Path(args.mission)
    if not mission_path.exists():
        print(f"❌ Mission file not found: {mission_path}")
        sys.exit(1)

    with open(mission_path, 'r') as f:
        mission = yaml.safe_load(f)

    mission_data = mission.get("mission", mission)
    print(f"\n🚀 EVE-INTEL ZeroRepo Engine")
    print(f"📋 Mission: {mission_data.get('name', 'Unknown')}")
    print(f"📝 Description: {mission_data.get('description', 'N/A')}")
    print(f"⚙️  Phase: {args.phase if args.phase > 0 else 'ALL'}")
    print(f"{'='*60}\n")

    # Convert mission to repo_data format expected by ZeroRepo
    repo_data = {
        "repository_name": mission_data.get("name", "osint-dashboard"),
        "description": mission_data.get("description", ""),
        "stack": mission_data.get("stack", {}),
        "features": mission_data.get("features", []),
        "deployment": mission_data.get("deployment", "local"),
    }

    # Save repo_data for ZeroRepo consumption
    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    repo_data_path = checkpoint_dir / "repo_data.json"
    with open(repo_data_path, 'w') as f:
        json.dump(repo_data, f, indent=2)
    print(f"✅ Mission data saved to {repo_data_path}")

    # Initialize ZeroRepo
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir) / mission_data.get("name", "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        engine = ZeroRepo(
            config_path=config_path,
            checkpoint_dir=checkpoint_dir,
            repo_path=output_dir,
        )
        print(f"✅ ZeroRepo engine initialized")
        print(f"📂 Output directory: {output_dir}")
        print(f"{'='*60}\n")

        if args.phase == 1:
            print("🔬 Phase 1: Property Level (Architectural Planning)...")
            engine.run_prop_level(repo_data)
            print("\n✅ Phase 1 Complete! Feature tree generated.")

        elif args.phase == 2:
            print("🏗️  Phase 2: Implementation Level (Design)...")
            engine.run_impl_level()
            print("\n✅ Phase 2 Complete! Implementation plan generated.")

        elif args.phase == 3:
            print("⚡ Phase 3: Code Generation...")
            plan_batches, skeleton, rpg, graph_data = engine.run_impl_level()
            engine.run_code_generation(plan_batches, skeleton, rpg, graph_data)
            print("\n✅ Phase 3 Complete! Code generated.")

        else:
            print("🌀 Running full pipeline (all phases)...")
            success = engine.run(repo_data)
            if success:
                print("\n✅ Full pipeline complete!")
            else:
                print("\n❌ Pipeline failed. Check logs.")
                sys.exit(1)

    except Exception as e:
        print(f"\n❌ Engine error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
