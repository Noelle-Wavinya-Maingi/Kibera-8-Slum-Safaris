from . import ma
from myapp.models import User, Organization, Beneficiary, Story, Tours, Donation, Inventory, beneficiaries_organizations, user_tours

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
    role = ma.auto_field()

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class OrganizationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Organization

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    email = ma.auto_field()
    status = ma.auto_field()
    password = ma.auto_field()
    timestamp = ma.auto_field()

organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)

class BeneficiarySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Beneficiary

    id = ma.auto_field()
    name = ma.auto_field()
    age = ma.auto_field()
    gender = ma.auto_field()
    address = ma.auto_field()

beneficiary_schema = BeneficiarySchema()
beneficiaries_schema = BeneficiarySchema(many=True)

class StorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Story

    id = ma.auto_field()
    title = ma.auto_field()
    content = ma.auto_field()
    created_at = ma.auto_field()
    image = ma.auto_field()
    organization_id = ma.auto_field()

story_schema = StorySchema()
stories_schema = StorySchema(many=True)

class ToursSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tours

    id = ma.auto_field()
    name = ma.auto_field()
    image = ma.auto_field()
    price = ma.auto_field()

tours_schema = ToursSchema()
tours_schema = ToursSchema(many=True)

class DonationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Donation

    id = ma.auto_field()
    amount = ma.auto_field()
    donor_id = ma.auto_field()
    organization_id = ma.auto_field()
    is_anonymous = ma.auto_field()
    recurrence_interval = ma.auto_field()
    next_recurrence_date = ma.auto_field()
    created_at = ma.auto_field()

donation_schema = DonationSchema()
donations_schema = DonationSchema(many=True)

class InventorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Inventory

    id = ma.auto_field()
    name = ma.auto_field()
    quantity = ma.auto_field()
    beneficiary_id = ma.auto_field()

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
