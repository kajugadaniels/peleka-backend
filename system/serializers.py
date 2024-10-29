import random
from rest_framework import serializers
from system.models import *

class RiderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rider model.
    Includes auto-generated, read-only code based on name initials and a unique 8-digit number.
    """
    code = serializers.CharField(read_only=True)  # Code is read-only

    class Meta:
        model = Rider
        fields = ['id', 'name', 'phone_number', 'address', 'code', 'nid']
        read_only_fields = ['code']

    def generate_unique_code(self, name):
        """
        Generates a unique code based on name initials and a random 8-digit number.
        Ensures uniqueness by checking against existing codes in the Rider model.
        """
        # Extract initials (first letters of each name)
        initials = ''.join([part[0].upper() for part in name.split() if part])[:2]  # Only the first 2 initials

        # Generate a unique code by appending an 8-digit random number
        while True:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            code = f"{initials}{random_number}"

            # Check if the generated code is unique
            if not Rider.objects.filter(code=code).exists():
                return code

    def create(self, validated_data):
        """
        Overrides create method to generate and set a unique code for each Rider.
        """
        # Extract name from validated data to generate the code
        name = validated_data.get('name', '')
        validated_data['code'] = self.generate_unique_code(name)

        # Create and return the Rider instance
        return super().create(validated_data)
