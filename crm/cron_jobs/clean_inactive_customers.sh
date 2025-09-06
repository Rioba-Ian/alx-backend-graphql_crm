#!/bin/bash

# crm/cron_jobs/clean_inactive_customers.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Navigate to the project directory
cd "$PROJECT_DIR" || exit 1

# Try to find the appropriate Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found" >> /tmp/customer_cleanup_log.txt
    exit 1
fi

# Execute the Python command to delete inactive customers
DELETE_RESULT=$($PYTHON_CMD manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the past year
inactive_customers = Customer.objects.filter(
    orders__isnull=True
) | Customer.objects.filter(
    orders__order_date__lt=one_year_ago
).distinct()

count = inactive_customers.count()
inactive_customers.delete()

print(f'{count}')
")

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log the result
echo "[$TIMESTAMP] Deleted $DELETE_RESULT inactive customers" >> /tmp/customer_cleanup_log.txt