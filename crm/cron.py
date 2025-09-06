import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/order_reminders_log.txt"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def log_crm_heartbeat():
    """
    Log a heartbeat message and verify GraphQL endpoint is responsive.
    This function is called every 5 minutes by django-crontab.
    """

    try:
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

        # Log heartbeat
        message = f"{timestamp} CRM is alive"
        logger.info(message)

        try:
            transport = RequestsHTTPTransport(
                url="http://localhost:8000/graphql",
                verify=True,
                retries=3,
            )
            client = Client(transport=transport, fetch_schema_from_transport=True)

            query = gql(
                """
                query {
                    __schema {
                        types {
                            name
                        }
                    }
                }
            """
            )

            # Execute the query
            result = client.execute(query)
            if result:
                logger.info("GraphQL endpoint is responsive")

        except Exception as e:
            logger.error(f"Error connecting to GraphQL endpoint: {str(e)}")

    except Exception as e:
        logger.error(f"Error in heartbeat logging: {str(e)}")
        raise


def update_low_stock():
    """
    Update low-stock products via GraphQL mutation.
    Runs every 12 hours.
    """
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql(
            """
            mutation {
                updateLowStockProducts {
                    success
                    message
                }
            }
        """
        )

        # Execute the mutation
        result = client.execute(mutation)
        if result:
            logger.info("Low-stock products updated successfully")
        else:
            logger.warning("No response from low-stock update mutation")

    except Exception as e:
        logger.error(f"Error updating low-stock products: {str(e)}")
        raise
