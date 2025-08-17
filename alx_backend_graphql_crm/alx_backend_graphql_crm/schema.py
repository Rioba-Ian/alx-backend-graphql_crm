import graphene
from crm.schema import Query as CrmQuery, Mutation as CrmMutation


class Query(CrmQuery, graphene.ObjectType):
    """
    The main query class that combines all queries from different modules.
    """

    pass


class Mutation(CrmMutation, graphene.ObjectType):
    """
    The main mutation class that combines all mutations from different modules.
    """

    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
