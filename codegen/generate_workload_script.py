import os

def generate_workload_script(ai_cfg):
    ai_script = f"""#!/bin/bash
# AI Workload script
python {ai_cfg.script_path} {ai_cfg.script_args}
"""

    script_path = os.path.join(os.getcwd(), "ai_workload.sh")
    with open(script_path, "w") as file:
        file.write(ai_script)
    print(f"AI workload script generated at {script_path}")
