from . import ma
from myapp.models import User, Organization, Beneficiary, Story, Tours, Donation, Inventory, beneficiaries_organizations, user_tours

# Define a Marshmalllow schema for the User model
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    # Define fields to be included in the schema    
    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
    role = ma.auto_field()

# Create an instance of the UserSchema for single and multiple user objects 
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Define a Marshmalllow schema for the Organization model
class OrganizationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Organization

    # Define fields to be included in the schema
    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    email = ma.auto_field()
    status = ma.auto_field()
    password = ma.auto_field()
    timestamp = ma.auto_field()

# Create an instance of the UserSchema for single and multiple organization objects 
organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)

# Define a Marshmalllow schema for the Beneficiary model
class BeneficiarySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Beneficiary

    # Define fields to be included in the schema
    id = ma.auto_field()
    name = ma.auto_field()
    age = ma.auto_field()
    gender = ma.auto_field()
    address = ma.auto_field()

# Create an instance of the UserSchema for single and multiple beneficiary objects 
beneficiary_schema = BeneficiarySchema()
beneficiaries_schema = BeneficiarySchema(many=True)

# Define a Marshmalllow schema for the Story model
class StorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Story

    # Define fields to be included in the schema
    id = ma.auto_field()
    title = ma.auto_field()
    content = ma.auto_field()
    created_at = ma.auto_field()
    image = ma.auto_field()
    organization_id = ma.auto_field()

# Create an instance of the UserSchema for single and multiple story objects 
story_schema = StorySchema()
stories_schema = StorySchema(many=True)

# Define a Marshmalllow schema for the Tours model
class ToursSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tours
    
    # Define fields to be included in the schema
    id = ma.auto_field()
    name = ma.auto_field()
    image = ma.auto_field()
    price = ma.auto_field()

# Create an instance of the UserSchema for single and multiple tours objects 
tours_schema = ToursSchema()
tours_schema = ToursSchema(many=True)

# Define a Marshmalllow schema for the Donation model
class DonationSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Donation
    
    # Define fields to be included in the schema
    id = ma.auto_field()
    amount = ma.auto_field()
    donor_id = ma.auto_field()
    organization_id = ma.auto_field()
    is_anonymous = ma.auto_field()
    recurrence_interval = ma.auto_field()
    next_recurrence_date = ma.auto_field()
    created_at = ma.auto_field()

# Create an instance of the UserSchema for single and multiple donation objects 
donation_schema = DonationSchema()
donations_schema = DonationSchema(many=True)

# Define a Marshmalllow schema for the Inventory model
class InventorySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Inventory
    
    # Define fields to be included in the schema
    id = ma.auto_field()
    name = ma.auto_field()
    quantity = ma.auto_field()
    beneficiary_id = ma.auto_field()

# Create an instance of the UserSchema for single and multiple inventory objects 
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

# Define a Marshmallow schema for the beneficiaries_organizations model
class BeneficiariesOrganizationsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = beneficiaries_organizations

    # Define fields to be included in the schema
    beneficiary_id = ma.auto_field()
    organization_id = ma.auto_field()

# Create an instance of the BeneficiariesOrganizationsSchema for single and multiple objects
beneficiaries_organizations_schema = BeneficiariesOrganizationsSchema()
beneficiaries_organizations_schema = BeneficiariesOrganizationsSchema(many=True)

# Define a Marshmallow schema for the user_tours model
class UserToursSchema(ma.SQLAlchemySchema):
    class Meta:
        model = user_tours

    # Define fields to be included in the schema
    user_id = ma.auto_field()
    tour_id = ma.auto_field()
    tour_date = ma.auto_field()

# Create an instance of the UserToursSchema for single and multiple objects
user_tours_schema = UserToursSchema()
user_tours_schema = UserToursSchema(many=True)
