import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

Customer.objects.create(
    name="John Doe",
    email="johndoe@example.com",
    phone="+1234567890",
)

Product.objects.create(
    name="Sample Product",
    price=19.99,
    stock=100,
)

Order.objects.create(
    customer=Customer.objects.first(),
    products=Product.objects.first(),
    total_amount=19.99,
)
print("Database seeded successfully.")
