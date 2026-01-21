# Contributing to Hello World Batch Submitter

Thank you for your interest in contributing! This document provides guidelines and best practices for contributing to this ACTIVATE workflow example.

## Getting Started

### Prerequisites

- Access to a Parallel Works ACTIVATE environment
- Familiarity with YAML syntax
- Understanding of HPC job schedulers (SLURM/PBS) is helpful but not required

### Setting Up Your Development Environment

1. Clone or copy this workflow to your workspace
2. Review the existing `workflow.yaml` structure
3. Test changes on a non-production compute resource first

## How to Contribute

### Reporting Issues

If you encounter problems:

1. Check existing issues to avoid duplicates
2. Provide a clear description of the problem
3. Include relevant details:
   - Compute resource type (cloud, on-prem, scheduler type)
   - Error messages or unexpected output
   - Steps to reproduce

### Suggesting Enhancements

We welcome suggestions for:

- New example commands that demonstrate useful functionality
- Improved documentation
- Additional scheduler support
- Better error handling

### Submitting Changes

1. **Fork/Branch**: Create a branch for your changes
2. **Make Changes**: Follow the coding standards below
3. **Test**: Verify your changes work on at least one compute resource
4. **Document**: Update README.md if needed
5. **Submit**: Create a pull request with a clear description

## Coding Standards

### YAML Style Guide

```yaml
# Use 2-space indentation
jobs:
  my_job:
    name: My Job Name

# Add comments for non-obvious configurations
scheduler:
  type: boolean
  default: false  # Direct SSH by default

# Use meaningful variable names
custom_commands:  # Good
cmd:              # Avoid - too abbreviated

# Quote strings that might be interpreted as other types
time: "00:10:00"  # Good - clearly a string
time: 00:10:00    # Avoid - might be parsed incorrectly
```

### Workflow Structure

Follow this organization in `workflow.yaml`:

```yaml
# 1. Header comment with description
# ==============================================================================
# Workflow Title
# ==============================================================================

# 2. Jobs section
jobs:
  job_name:
    # Job configuration

# 3. Input definitions
"on":
  execute:
    inputs:
      # Inputs organized by category with comments
```

### Input Definition Guidelines

When adding new inputs:

```yaml
my_input:
  label: Human Readable Label    # Required: shown in UI
  type: string                   # Required: string, number, boolean, editor, etc.
  default: sensible_default      # Recommended: provide defaults
  optional: true                 # Set if not required
  tooltip: |                     # Recommended: help text
    Detailed explanation of what this input does
    and how to use it.
  hidden: ${{ condition }}       # Optional: conditionally show/hide
  ignore: ${{ .hidden }}         # Optional: exclude from job when hidden
```

### Documentation Standards

- Use clear, concise language
- Include examples for complex features
- Keep README.md updated with any new functionality
- Add inline comments in workflow.yaml for non-obvious logic

## Testing Your Changes

### Minimum Testing Requirements

Before submitting changes, test on at least one of:

1. **SSH Direct Mode**: Run without scheduler submission
2. **SLURM Mode**: If you have access to a SLURM cluster
3. **PBS Mode**: If you have access to a PBS cluster

### Test Checklist

- [ ] Workflow loads without YAML errors
- [ ] All inputs render correctly in the UI
- [ ] Default values work as expected
- [ ] Job executes successfully in at least one mode
- [ ] Output displays correctly in the ACTIVATE interface
- [ ] Cancellation works properly (if applicable)

### Testing Custom Commands

If adding new example commands:

```bash
# Test locally first if possible
hostname && date && whoami

# Consider edge cases
nvidia-smi || echo "No GPU"  # Handle missing commands gracefully
```

## Project Structure

```
activate-batch/
├── README.md           # User documentation
├── CONTRIBUTING.md     # This file
├── workflow.yaml       # Main workflow definition
└── .lanes/             # ACTIVATE internal directory (do not modify)
```

### File Descriptions

| File | Purpose | When to Modify |
|------|---------|----------------|
| `workflow.yaml` | Workflow definition | Adding features, fixing bugs |
| `README.md` | User guide | Documenting new features |
| `CONTRIBUTING.md` | Contributor guide | Updating contribution process |

## Common Patterns

### Adding a New Scheduler Option

```yaml
slurm:
  type: group
  items:
    new_option:
      label: New Option
      type: string
      optional: true
      tooltip: Description of what this option does
      ignore: ${{ inputs.resource.schedulerType != 'slurm' || inputs.scheduler == false }}
```

### Adding Conditional Display

```yaml
advanced_setting:
  label: Advanced Setting
  type: string
  hidden: ${{ inputs.show_advanced == false }}
  ignore: ${{ .hidden }}
```

### Using job_runner/v4.0 Features

Reference the job_runner documentation at `~/job_runner/v4.0.yaml` for:

- Available input parameters
- Scheduler directive options
- Output handling configuration

## Code of Conduct

- Be respectful and constructive in discussions
- Focus on the technical merits of contributions
- Help newcomers learn the workflow patterns

## Questions?

If you have questions about contributing:

1. Review existing documentation
2. Check the job_runner/v4.0.yaml for submitter capabilities
3. Open an issue for discussion

Thank you for contributing!
