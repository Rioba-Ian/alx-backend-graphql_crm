import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from crm.models import Customer, Product, Order
from django.utils import timezone


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class Customerinput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class Productinput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)


class Orderinput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    total_amount = graphene.Float()


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = Customerinput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone,
        )
        try:
            customer.full_clean()
            customer.save()

            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                errors=None,
            )
        except ValidationError as e:
            raise Exception(f"Validation error: {e}")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(Customerinput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, inputs):
        created_customers = []
        errors = []

        for cust_data in input:
            try:
                if Customer.objects.filter(email=cust_data.email).exists():
                    errors.append(
                        f"Customer with email {cust_data.email} already exists."
                    )
                    continue
                customer = Customer(
                    name=cust_data.name,
                    email=cust_data.email,
                    phone=cust_data.phone,
                )
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except ValidationError as e:
                errors.append(f"Validation error for {cust_data.email}: {e}")

        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors if errors else None,
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = Productinput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        product = Product(
            name=input.name,
            price=input.price,
            stock=input.stock,
        )
        try:
            product.full_clean()
            product.save()

            return CreateProduct(
                product=product,
                message="Product created successfully",
                errors=None,
            )
        except ValidationError as e:
            raise Exception(f"Validation error: {e}")


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = Orderinput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except ObjectDoesNotExist:
            raise Exception("Customer not found")

        products = Product.objects.filter(id__in=input.product_ids)
        if not products:
            raise Exception("No valid products found")

        total_amount = sum(product.price for product in products)

        order = Order(
            customer=customer,
            total_amount=total_amount,
            order_date=timezone.now(),
        )
        order.save()
        order.products.set(products)

        return CreateOrder(order=order, errors=None)


class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
