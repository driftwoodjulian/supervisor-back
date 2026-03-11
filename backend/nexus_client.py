import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to get credentials from environment
NEXUS_BASIC_AUTH_USER = os.getenv("NEXUS_BASIC_AUTH_USER", "towebs")
NEXUS_BASIC_AUTH_PASS = os.getenv("NEXUS_BASIC_AUTH_PASS", "satancojealpapa")
NEXUS_BASE_URL = os.getenv("NEXUS_BASE_URL", "https://nexus.towebs.com")


def verify_domain_in_nexus(domain: str) -> Optional[Dict[str, Any]]:
    """
    Queries the legacy api-client-info on nexus.towebs.com for a given domain and returns
    the formatted context for the AI, or None if the domain is invalid/not found.
    """
    if not domain:
        return None

    try:
        url = f"{NEXUS_BASE_URL}/api-client-info/"
        params = {"domain": domain}
        auth = (NEXUS_BASIC_AUTH_USER, NEXUS_BASIC_AUTH_PASS)

        # The legacy endpoint throws a 404 naturally when domain is totally missing/unregistered
        response = requests.get(url, params=params, auth=auth, timeout=10)
        
        # In this legacy endpoint, the 200 JSON holds the data dictionary directly usually
        if response.status_code == 200:
            data = response.json()
            if data and data.get("website"):
                context = {
                    "domain": data.get("website"),
                    "owner_name": data.get("nombre", "Unknown"), 
                    "plan_name": data.get("plan", "Unknown Plan"),
                    "server": data.get("servidor", "Unknown Server"),
                    "status": data.get("status", "Unknown Status"),
                    "debit_active": data.get("debito", False)
                }
                return context
            else:
                return None
        elif response.status_code == 404:
            logger.info(f"Domain {domain} not found in Nexus.")
            return None
        elif response.status_code == 401 or response.status_code == 403:
            logger.error("Nexus Wrapper Authentication Failed. Please check NEXUS_BASIC_AUTH variables.")
            return None
        else:
            logger.error(f"Nexus Wrapper returned unexpected status code: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while verifying domain {domain} with Nexus Wrapper.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception while verifying domain {domain} with Nexus Wrapper: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while verifying domain {domain}: {e}")
        return None

