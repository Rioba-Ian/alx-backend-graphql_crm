import logging
import requests
from datetime import datetime

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from crm.models import Order

logger = logging.getLogger(__name__)


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    Logs the report to /tmp/crm_report_log.txt
    """
    try:
        # Get total number of customers
        total_customers = get_user_model().objects.filter(is_staff=False).count()

        # Get total number of orders and total revenue
        orders_summary = Order.objects.aggregate(
            total_orders=Count("id"), total_revenue=Sum("totalamount")
        )

        # Format the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{orders_summary['total_orders']} orders, "
            f"{orders_summary['total_revenue'] or 0:.2f} revenue\n"
        )

        # Log to file
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(report)

        logger.info("Successfully generated CRM report")
        return True

    except Exception as e:
        logger.error(f"Error generating CRM report: {str(e)}")
        return False
