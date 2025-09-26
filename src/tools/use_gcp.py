import logging
import subprocess
from strands import tool

logger = logging.getLogger(__name__)


@tool
def use_gcp(command: str) -> str:
    """
    Execute Google Cloud CLI (gcloud) commands for GCP operations.

    Args:
        command: GCP command to execute (without 'gcloud' prefix)

    Returns:
        Command output or error message

    Examples:
        use_gcp("compute instances list")
        use_gcp("storage buckets list")
        use_gcp("container clusters list")
    """
    try:
        # Ensure gcloud is available
        subprocess.run(["gcloud", "version"], capture_output=True, check=True)

        # Prepare the full gcloud command
        cmd_parts = ["gcloud"] + command.strip().split()

        # Add common flags for scripting
        if "--format" not in command:
            cmd_parts.extend(["--format", "json"])
        if "--quiet" not in command and "-q" not in command:
            cmd_parts.append("--quiet")

        logger.info(f"Executing GCP command: {' '.join(cmd_parts)}")

        # Execute the command
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info("GCP command executed successfully")
            return result.stdout.strip()
        else:
            logger.error(f"GCP command failed: {result.stderr}")
            return f"Error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        logger.error("GCP command timed out")
        return "Error: Command timed out after 5 minutes"
    except FileNotFoundError:
        logger.error("gcloud CLI not found")
        return "Error: gcloud CLI not installed. Please install Google Cloud SDK"
    except Exception as e:
        logger.error(f"Error executing GCP command: {str(e)}")
        return f"Error: {str(e)}"


@tool
def gcp_auth_status() -> str:
    """
    Check GCP authentication status and active account.

    Returns:
        Current authentication status and active account info
    """
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Authentication Status:\n{result.stdout.strip()}"
        else:
            return f"Error checking auth status: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def gcp_set_project(project_id: str) -> str:
    """
    Set the active GCP project.

    Args:
        project_id: GCP project ID to set as active

    Returns:
        Success or error message
    """
    try:
        result = subprocess.run(
            ["gcloud", "config", "set", "project", project_id],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Successfully set project to: {project_id}"
        else:
            return f"Error setting project: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"




@tool
def gcp_project_info() -> str:
    """
    Get current project information and configuration.

    Returns:
        Current project details and configuration
    """
    try:
        # Get current project
        project_result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Get project details
        if project_result.returncode == 0:
            project_id = project_result.stdout.strip()
            details_result = subprocess.run(
                ["gcloud", "projects", "describe", project_id, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if details_result.returncode == 0:
                return f"Current Project Details:\n{details_result.stdout.strip()}"
            else:
                return f"Current Project: {project_id}\nError getting details: {details_result.stderr.strip()}"
        else:
            return f"Error getting project info: {project_result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"