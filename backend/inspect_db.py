import sqlite3
import json

conn = sqlite3.connect('exhacker.db')
c = conn.cursor()

try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print("Tables:", tables)

    c.execute("SELECT COUNT(*) FROM projects")
    print("Projects Count:", c.fetchone()[0])

    c.execute("SELECT id, project_id, status, current_stage, state_json FROM workflow_states")
    rows = c.fetchall()
    print("Workflows Count:", len(rows))
    for row in rows:
        wf_id, proj_id, status, current_stage, state_json_str = row
        print(f"\nWorkflow {wf_id} (Project {proj_id}): status={status}, stage={current_stage}")
        try:
            state = json.loads(state_json_str)
            print("  Selected Idea:", state.get("selected_idea"))
            print("  Has Architecture:", "architecture" in state and state["architecture"] is not None)
            print("  Has Tech Stack:", "tech_stack" in state and state["tech_stack"] is not None)
            print("  Has Build Package:", "build_package" in state and state["build_package"] is not None)
            print("  Has Presentation:", "presentation" in state and state["presentation"] is not None)
            print("  Has Pitch:", "pitch" in state and state["pitch"] is not None)
            print("  Has Exports:", "exports" in state and state["exports"] is not None)
            print("  Stage Metrics:")
            metrics = state.get("execution", {}).get("stage_metrics", [])
            for m in metrics:
                print(f"    - {m.get('stage')}: used_mock={m.get('used_mock')}, duration={m.get('duration_seconds')}s, attempts={m.get('attempts')}")
        except Exception as e:
            print("  Failed to parse state_json:", e)
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
