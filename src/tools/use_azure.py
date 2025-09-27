import logging
import subprocess
from strands import tool

logger = logging.getLogger(__name__)


@tool
def use_azure(command: str) -> str:
    """
    Execute Azure CLI (az) commands for Azure operations.

    Args:
        command: Azure command to execute (without 'az' prefix)

    Returns:
        Command output or error message

    Examples:
        use_az("vm list")
        use_az("storage account list")
        use_az("aks list")
        use_az("resource list")
    """
    try:
        # Ensure az CLI is available
        subprocess.run(["az", "version"], capture_output=True, check=True)

        # Prepare the full az command
        cmd_parts = ["az"] + command.strip().split()

        # Add common flags for scripting
        if "--output" not in command and "-o" not in command:
            cmd_parts.extend(["--output", "json"])

        logger.info(f"Executing Azure command: {' '.join(cmd_parts)}")

        # Execute the command
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info("Azure command executed successfully")
            return result.stdout.strip()
        else:
            logger.error(f"Azure command failed: {result.stderr}")
            return f"Error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        logger.error("Azure command timed out")
        return "Error: Command timed out after 5 minutes"
    except FileNotFoundError:
        logger.error("az CLI not found")
        return "Error: az CLI not installed. Please install Azure CLI"
    except Exception as e:
        logger.error(f"Error executing Azure command: {str(e)}")
        return f"Error: {str(e)}"


@tool
def azure_auth_status() -> str:
    """
    Check Azure authentication status and active account.

    Returns:
        Current authentication status and active account info
    """
    try:
        result = subprocess.run(
            ["az", "account", "show", "--output", "json"],
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
def azure_set_subscription(subscription_id: str) -> str:
    """
    Set the active Azure subscription.

    Args:
        subscription_id: Azure subscription ID to set as active

    Returns:
        Success or error message
    """
    try:
        result = subprocess.run(
            ["az", "account", "set", "--subscription", subscription_id],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Successfully set subscription to: {subscription_id}"
        else:
            return f"Error setting subscription: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def azure_subscription_info() -> str:
    """
    Get current subscription information and configuration.

    Returns:
        Current subscription details and configuration
    """
    try:
        # Get current subscription
        result = subprocess.run(
            ["az", "account", "show", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Current Subscription Details:\n{result.stdout.strip()}"
        else:
            return f"Error getting subscription info: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def azure_list_subscriptions() -> str:
    """
    List all available Azure subscriptions.

    Returns:
        List of available subscriptions
    """
    try:
        result = subprocess.run(
            ["az", "account", "list", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Available Subscriptions:\n{result.stdout.strip()}"
        else:
            return f"Error listing subscriptions: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def azure_set_location(location: str) -> str:
    """
    Set the default Azure location/region.

    Args:
        location: Azure location/region to set as default (e.g., 'eastus', 'westus2')

    Returns:
        Success or error message
    """
    try:
        result = subprocess.run(
            ["az", "config", "set", f"defaults.location={location}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"Successfully set default location to: {location}"
        else:
            return f"Error setting location: {result.stderr.strip()}"

    except Exception as e:
        return f"Error: {str(e)}"