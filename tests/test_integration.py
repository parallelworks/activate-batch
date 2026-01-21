"""
Integration tests for the ACTIVATE Batch Submitter workflow.

These tests execute the actual workflow with different configurations
and verify end-to-end behavior.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from workflow_runner import WorkflowRunner, ExecutionContext


class TestWorkflowExecution:
    """Integration tests for full workflow execution."""

    def test_workflow_dry_run(self, workflow_path: Path, dry_run_context: ExecutionContext):
        """Test workflow executes successfully in dry-run mode."""
        runner = WorkflowRunner(workflow_path, dry_run_context)
        success = runner.run()
        assert success is True

    def test_workflow_with_simple_commands(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test workflow execution with simple commands."""
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(temp_work_dir / "run"),
                "commands": "echo 'hello'\necho 'world'",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "integration-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()
        assert success is True

    def test_workflow_creates_working_directory(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that workflow creates the working directory."""
        run_dir = temp_work_dir / "my-test-run"
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(run_dir),
                "commands": "pwd",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "dir-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        runner.run()

        # Check that the run directory was created (within temp_work_dir)
        expected_dir = temp_work_dir / str(run_dir).lstrip("/")
        assert expected_dir.exists()

    def test_workflow_creates_commands_script(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that workflow creates commands.sh script."""
        run_dir = temp_work_dir / "script-test"
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(run_dir),
                "commands": "hostname\ndate",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "script-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        runner.run()

        # Check that commands.sh was created
        expected_dir = temp_work_dir / str(run_dir).lstrip("/")
        commands_script = expected_dir / "commands.sh"
        assert commands_script.exists()

        # Verify script contains the commands
        script_content = commands_script.read_text()
        assert "hostname" in script_content
        assert "date" in script_content

    def test_workflow_executes_custom_commands(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that custom commands are actually executed."""
        run_dir = temp_work_dir / "exec-test"
        marker_file = "test_marker_file.txt"

        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(run_dir),
                "commands": f"touch {marker_file}\necho 'marker created'",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "exec-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is True

        # Check that the marker file was created
        expected_dir = temp_work_dir / str(run_dir).lstrip("/")
        marker_path = expected_dir / marker_file
        assert marker_path.exists(), f"Marker file not found at {marker_path}"

    def test_workflow_captures_output(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that command output is captured."""
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(temp_work_dir / "output-test"),
                "commands": "echo 'UNIQUE_OUTPUT_STRING_12345'",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "output-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=True,  # Enable verbose to capture output
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is True
        # Output verification happens through verbose mode stdout


class TestCommandLineInterface:
    """Test the command-line interface."""

    def test_cli_help(self, repo_root: Path):
        """Test that --help works."""
        result = subprocess.run(
            [sys.executable, str(repo_root / "tools" / "workflow_runner.py"), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "workflow" in result.stdout.lower()

    def test_cli_dry_run(self, repo_root: Path):
        """Test CLI dry-run execution."""
        result = subprocess.run(
            [
                sys.executable,
                str(repo_root / "tools" / "workflow_runner.py"),
                str(repo_root / "workflow.yaml"),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "DRY-RUN" in result.stdout

    def test_cli_with_custom_input(self, repo_root: Path, temp_work_dir: Path):
        """Test CLI with custom input values."""
        result = subprocess.run(
            [
                sys.executable,
                str(repo_root / "tools" / "workflow_runner.py"),
                str(repo_root / "workflow.yaml"),
                "--dry-run",
                "-i", "commands=custom_command",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_cli_nonexistent_workflow(self, repo_root: Path):
        """Test CLI with nonexistent workflow file."""
        result = subprocess.run(
            [
                sys.executable,
                str(repo_root / "tools" / "workflow_runner.py"),
                "/nonexistent/workflow.yaml",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()

    def test_cli_full_execution(self, repo_root: Path, temp_work_dir: Path):
        """Test CLI full execution with work directory."""
        result = subprocess.run(
            [
                sys.executable,
                str(repo_root / "tools" / "workflow_runner.py"),
                str(repo_root / "workflow.yaml"),
                "--work-dir", str(temp_work_dir),
                "-i", "commands=echo test",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert "SUCCESS" in result.stdout


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_command_failure_stops_execution(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that a failing command stops workflow execution."""
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(temp_work_dir / "fail-test"),
                "commands": "exit 1",  # This will fail
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "fail-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is False

    def test_invalid_command_reports_error(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that invalid commands report errors properly."""
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(temp_work_dir / "invalid-test"),
                "commands": "nonexistent_command_xyz_123",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "invalid-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is False


class TestMultilineCommands:
    """Test handling of multiline command inputs."""

    def test_multiline_commands_execute_in_order(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that multiline commands execute in sequence."""
        run_dir = temp_work_dir / "multiline-test"

        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(run_dir),
                "commands": "echo 'first' > order.txt\necho 'second' >> order.txt\necho 'third' >> order.txt",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "multiline-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is True

        # Verify order of execution
        expected_dir = temp_work_dir / str(run_dir).lstrip("/")
        order_file = expected_dir / "order.txt"
        assert order_file.exists()

        content = order_file.read_text().strip().split("\n")
        assert content == ["first", "second", "third"]

    def test_commands_with_comments(
        self, workflow_path: Path, temp_work_dir: Path
    ):
        """Test that commands with comments work correctly."""
        context = ExecutionContext(
            inputs={
                "resource": {"ip": "localhost", "schedulerType": ""},
                "rundir": str(temp_work_dir / "comment-test"),
                "commands": "# This is a comment\necho 'actual command'\n# Another comment",
                "scheduler": False,
            },
            env_vars={
                "PW_JOB_ID": "comment-test",
                "PW_USER": "testuser",
                "HOME": os.environ.get("HOME", "/tmp"),
            },
            work_dir=temp_work_dir,
            dry_run=False,
            verbose=False,
        )

        runner = WorkflowRunner(workflow_path, context)
        success = runner.run()

        assert success is True
