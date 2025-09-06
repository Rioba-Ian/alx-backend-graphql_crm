#!/usr/bin/env python3
"""
Order Reminder Script

This script queries the GraphQL API for recent orders and sends reminders.
It's designed to be run as a daily cron job.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import django
from django.utils import timezone
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()


# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# GraphQL endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


def get_recent_orders():
    """Query the GraphQL API for recent orders (last 7 days)."""
    # Calculate date 7 days ago
    one_week_ago = (timezone.now() - timedelta(days=7)).isoformat()

    # GraphQL query
    query = gql(
        """
    query GetRecentOrders($since: DateTime!) {
      allOrders(filter: {orderDateGte: $since}, orderBy: "orderDate") {
        edges {
          node {
            id
            orderDate
            customer {
              email
              name
            }
            totalAmount
          }
        }
      }
    }
    """
    )

    # Set up the GraphQL client
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    try:
        # Execute the query
        result = client.execute(query, variable_values={"since": one_week_ago})
        return result.get("allOrders", {}).get("edges", [])
    except Exception as e:
        logging.error(f"Error fetching orders: {str(e)}")
        return []


def main():
    """Main function to process order reminders."""
    try:
        orders = get_recent_orders()

        if not orders:
            logging.info("No recent orders found.")
            print("Order reminders processed! (No recent orders found)")
            return

        # Process each order
        for edge in orders:
            order = edge.get("node", {})
            order_id = order.get("id", "N/A")
            customer = order.get("customer", {})
            email = customer.get("email", "no-email")
            name = customer.get("name", "Customer")
            order_date = order.get("orderDate", "N/A")
            total = order.get("totalAmount", "0.00")

            # Log the reminder
            log_message = (
                f"Reminder: Order ID: {order_id}, "
                f"Customer: {name} <{email}>, "
                f"Date: {order_date}, "
                f"Total: ${total}"
            )
            logging.info(log_message)

        print("Order reminders processed!")

    except Exception as e:
        error_msg = f"Error in order reminder script: {str(e)}"
        logging.error(error_msg)
        print(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
