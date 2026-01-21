# Hello World Batch Submitter

A simple Parallel Works ACTIVATE workflow demonstrating batch job submission. This workflow accepts a series of commands, packages them into a script, transfers it to the remote system, and executes.

## Overview

This workflow serves as a "hello world" example for submitting batch jobs to HPC clusters through ACTIVATE. It executes user-provided commands (defaulting to basic system commands like `hostname`, `date`, `whoami`) to verify that job submission is working correctly on your compute resources.

The pattern used here—accepting commands as input and packaging them into a remote script—is designed to be compatible with future job_runner v5 load balancing capabilities.

## Features

- **Command Input**: Enter any commands to execute on the remote system
- **Script Generation**: Commands are packaged into a script on the remote host
- **Real-time Output**: See command output as it executes
- **Local Testing**: Run workflows locally without the ACTIVATE platform
- **Extensible Design**: Ready for integration with job_runner v5 load balancing

## Quick Start

### On ACTIVATE Platform

1. Navigate to this workflow in ACTIVATE
2. Select your compute resource from the dropdown
3. (Optional) Modify the commands in the editor
4. Click **Run**

### Local Execution (No ACTIVATE Required)

```bash
# Install dependencies
pip install pyyaml

# Run with defaults
./tools/run_local.sh

# Dry-run mode (see what would execute)
./tools/run_local.sh --dry-run

# Custom commands
python tools/workflow_runner.py workflow.yaml -i "commands=hostname
uptime
free -h"

# Verbose output
./tools/run_local.sh -v --keep-work-dir
```

## Configuration Options

### Core Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Compute Resource** | The target cluster/resource | Auto-selected |
| **Working Directory** | Where job files are created | `/tmp/hello-world-${PW_JOB_ID}` |

### Commands to Execute

The **Commands to Execute** editor allows you to specify shell commands that will be executed on the remote system. Each line is executed in sequence.

**Default commands:**
```bash
hostname
date
whoami
pwd
uname -a
echo "Environment variables:"
env | sort | head -20
```

**Example customizations:**
```bash
# Check available modules
module avail 2>&1 | head -20

# Show GPU information (if available)
nvidia-smi || echo "No GPUs available"

# Check available memory
free -h

# List available compilers
which gcc g++ gfortran python3
```

### Scheduler Settings

The workflow includes SLURM and PBS configuration options for future integration with the job_runner marketplace action.

## Local Development

### Directory Structure

```
activate-batch/
├── README.md              # This file
├── CONTRIBUTING.md        # Contributor guidelines
├── workflow.yaml          # Main workflow definition
├── requirements.txt       # Python dependencies
├── pytest.ini             # Test configuration
├── tools/
│   ├── workflow_runner.py # Local execution engine
│   ├── run_local.sh       # Convenience script for local runs
│   └── run_tests.sh       # Test runner script
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_workflow_runner.py  # Unit tests
│   └── test_integration.py      # Integration tests
└── .lanes/                # ACTIVATE internal directory
```

### Running Locally

The local workflow runner simulates ACTIVATE execution on your local machine:

```bash
# Basic execution
python tools/workflow_runner.py workflow.yaml

# With custom commands
python tools/workflow_runner.py workflow.yaml \
    -i "commands=echo hello
echo world"

# Dry-run (show what would execute without running)
python tools/workflow_runner.py workflow.yaml --dry-run

# Verbose output
python tools/workflow_runner.py workflow.yaml -v

# Specify working directory
python tools/workflow_runner.py workflow.yaml --work-dir /tmp/my-test

# Keep working directory for inspection
python tools/workflow_runner.py workflow.yaml --keep-work-dir
```

### Running Tests

```bash
# Run all tests
./tools/run_tests.sh

# Unit tests only
./tools/run_tests.sh --unit

# Integration tests only
./tools/run_tests.sh --integration

# With coverage report
./tools/run_tests.sh --coverage

# Run specific test
./tools/run_tests.sh -k test_workflow_dry_run
```

### Test Categories

**Unit Tests** (`tests/test_workflow_runner.py`):
- Variable substitution
- Expression evaluation
- Job dependency ordering
- Input parsing
- Workflow loading

**Integration Tests** (`tests/test_integration.py`):
- Full workflow execution
- Command-line interface
- Error handling
- Multiline commands

## Example Output

```
==============================================
  Hello World from Parallel Works ACTIVATE
==============================================

System Information:
  Hostname:    compute-node-001
  Date:        Wed Jan 21 12:00:00 UTC 2026
  User:        myuser
  Directory:   /tmp/hello-world-abc123

----------------------------------------------
  Executing Commands
----------------------------------------------

compute-node-001
Wed Jan 21 12:00:00 UTC 2026
myuser
/tmp/hello-world-abc123
Linux compute-node-001 5.15.0-generic x86_64 GNU/Linux
Environment variables:
HOME=/home/myuser
HOSTNAME=compute-node-001
...

----------------------------------------------
  All commands completed
----------------------------------------------

Finished at: Wed Jan 21 12:00:01 UTC 2026
==============================================
```

## How It Works

1. **Setup**: Creates the working directory on the remote system
2. **Script Generation**: Packages your commands into `commands.sh` with:
   - A bash header with `set -e` for error handling
   - System information display
   - Your custom commands
   - Completion footer with timestamp
3. **Execution**: Runs the script via SSH and streams output

## Integration with job_runner

This workflow is designed to be compatible with the `job_runner` marketplace action. To add scheduler support (SLURM/PBS), the workflow can be extended to use:

```yaml
jobs:
  execute:
    uses: marketplace/job_runner/v4.0
    with:
      resource: ${{ inputs.resource }}
      rundir: ${{ inputs.rundir }}
      scheduler: ${{ inputs.scheduler }}
      use_existing_script: true
      script_path: ${{ inputs.rundir }}/commands.sh
      slurm:
        partition: ${{ inputs.slurm.partition }}
        time: ${{ inputs.slurm.time }}
```

See `~/job_runner/v4.0.yaml` for full documentation on the job_runner action.

## Troubleshooting

### Permission denied errors
- Ensure the working directory path is writable
- Check that you have SSH access to the compute resource

### Commands not found
- Verify the command exists on the remote system
- Check if modules need to be loaded first (`module load ...`)

### Script fails immediately
- The script uses `set -e` so any command failure stops execution
- Check the output for the specific failing command
- Use `|| true` after commands that may fail: `nvidia-smi || true`

### Local runner issues
- Ensure PyYAML is installed: `pip install pyyaml`
- Check Python version (requires Python 3.10+)
- Use `--verbose` flag for detailed output

## Next Steps

After verifying this hello world example works:

1. **Add your commands**: Replace defaults with your actual workflow commands
2. **Enable scheduler**: Use job_runner integration for SLURM/PBS submission
3. **Scale up**: Use job_runner v5 for load-balanced multi-task execution

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this workflow.

## License

This example workflow is provided as-is for educational and testing purposes.
