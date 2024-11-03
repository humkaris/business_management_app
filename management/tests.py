from django.test import TestCase
from django.utils import timezone
from .models import Quotation  # Adjust the import path as needed
from django.core.exceptions import ValidationError


class QuotationModelTests(TestCase):

    def setUp(self):
        # Optional setup if you need to create test data beforehand
        pass
    
    def test_generate_unique_quote_number(self):
        quote1 = Quotation.objects.create(
            client_name="Client A",
            client_email="clientA@example.com",
            client_phone_number="1234567890",
            client_address="123 Test St",
            date_created=timezone.now()
        )
        quote2 = Quotation.objects.create(
            client_name="Client B",
            client_email="clientB@example.com",
            client_phone_number="0987654321",
            client_address="456 Example Ave",
            date_created=timezone.now()
        )
            
            # Check format for the first quote number
        self.assertTrue(quote1.quote_number.startswith("QUOTE-"))
        self.assertEqual(quote1.quote_number.count("-"), 2)
            
        # Check that quote numbers are unique
        self.assertNotEqual(quote1.quote_number, quote2.quote_number)

    def test_manual_quote_number_insertion(self):
        old_quote_number = "2023-OLD-12345"
        quote = Quotation.objects.create(
            client_name="Client C",
            client_email="clientC@example.com",
            client_phone_number="5555555555",
            client_address="789 Another Rd",
            date_created=timezone.now(),
            original_quote_number=old_quote_number
        )
        
        # Ensure original_quote_number retains the old format
        self.assertEqual(quote.original_quote_number, old_quote_number)
        
        # Ensure new quote numbers use the new format
        self.assertTrue(quote.quote_number.startswith("QUOTE-"))
    
    def test_default_date_field(self):
        quote = Quotation.objects.create(
            client_name="Client D",
            client_email="clientD@example.com",
            client_phone_number="9876543210",
            client_address="111 New Lane"
        )
        
        # Check if date was set to a non-None value
        self.assertIsNotNone(quote.date_created)
    
    def test_required_fields(self):
    # Test for missing client_name
        with self.assertRaises(ValidationError):
            Quotation.objects.create(
                client_email="client@example.com",
                client_address="123 Test Street",
                client_phone_number="123456789",
            )

        # Test for missing client_email
        with self.assertRaises(ValidationError):
            Quotation.objects.create(
                client_name="Client Name",
                client_address="123 Test Street",
                client_phone_number="123456789",
            )

        # Test for missing client_address
        with self.assertRaises(ValidationError):
            Quotation.objects.create(
                client_name="Client Name",
                client_email="client@example.com",
                client_phone_number="123456789",
            )

        # Test for missing client_phone_number
        with self.assertRaises(ValidationError):
            Quotation.objects.create(
                client_name="Client Name",
                client_email="client@example.com",
                client_address="123 Test Street",
            )

        

    def test_invalid_email(self):
    # Attempt to create a Quotation with an invalid email format
        with self.assertRaises(ValidationError):
            Quotation.objects.create(
                client_name="Client Test",
                client_email="invalid-email",  # Invalid email
                client_address="123 Test Street",
                client_phone_number="123456789",
            )
    

    def test_update_quotation(self):
        quote = Quotation.objects.create(
            client_name="Client G",
            client_email="clientG@example.com",
            client_phone_number="1112223333",
            client_address="222 Update Rd",
            date_created=timezone.now()
        )
        
        # Update the client's name and check
        quote.client_name = "Updated Client G"
        quote.save()
        
        updated_quote = Quotation.objects.get(id=quote.id)
        self.assertEqual(updated_quote.client_name, "Updated Client G")
    

    def test_string_representation(self):
        quote = Quotation.objects.create(
            client_name="Client H",
            client_email="clientH@example.com",
            client_phone_number="3334445555",
            client_address="333 Str Rd"
        )
        
        expected_string = f"Quotation {quote.quote_number} for {quote.client_name}"
        self.assertEqual(str(quote), expected_string)





