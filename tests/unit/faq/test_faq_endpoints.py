"""
Unit tests for user FAQ endpoints.
"""

import pytest
from fastapi import status
from uuid import uuid4


class TestUserFAQList:
    """Test user FAQ list endpoint."""

    def test_get_faqs_success(self, client, multiple_test_faqs):
        """Test successful FAQ list retrieval for users."""
        response = client.get("/api/v1/faq/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "items" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert "pages" in response_data
        assert "has_next" in response_data
        assert "has_prev" in response_data
        assert len(response_data["items"]) == 3
        assert response_data["total"] == 3

    def test_get_faqs_only_active(self, client, test_faq, test_faq_inactive):
        """Test that only active FAQs are returned to users."""
        response = client.get("/api/v1/faq/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["is_active"] is True

    def test_get_faqs_with_pagination(self, client, multiple_test_faqs):
        """Test FAQ list with pagination."""
        response = client.get("/api/v1/faq/?page=1&size=2")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 2
        assert response_data["page"] == 1
        assert response_data["size"] == 2
        assert response_data["total"] == 3

    def test_get_faqs_with_search(self, client, multiple_test_faqs):
        """Test FAQ list with search."""
        response = client.get("/api/v1/faq/?search=password")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert "password" in response_data["items"][0]["question"].lower()

    def test_get_faqs_with_category_filter(self, client, multiple_test_faqs):
        """Test FAQ list with category filter."""
        response = client.get("/api/v1/faq/?category=Account")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["category"] == "Account"

    def test_get_faqs_with_featured_filter(self, client, test_faq, test_faq_featured):
        """Test FAQ list with featured filter."""
        response = client.get("/api/v1/faq/?featured_only=true")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["is_featured"] is True

    def test_get_faqs_sorted_by_sort_order(self, client, multiple_test_faqs):
        """Test FAQ list sorted by sort_order."""
        response = client.get("/api/v1/faq/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        items = response_data["items"]
        # Should be sorted by sort_order (1, 2, 3)
        assert items[0]["sort_order"] == 1
        assert items[1]["sort_order"] == 2
        assert items[2]["sort_order"] == 3

    def test_get_faqs_empty_result(self, client):
        """Test FAQ list with no FAQs."""
        response = client.get("/api/v1/faq/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 0
        assert response_data["total"] == 0

    def test_get_faqs_invalid_pagination(self, client, multiple_test_faqs):
        """Test FAQ list with invalid pagination parameters."""
        response = client.get("/api/v1/faq/?page=0&size=0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_faqs_large_page_size(self, client, multiple_test_faqs):
        """Test FAQ list with page size exceeding limit."""
        response = client.get("/api/v1/faq/?size=1000")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserFAQGet:
    """Test user FAQ get by ID endpoint."""

    def test_get_faq_success(self, client, test_faq):
        """Test successful FAQ retrieval by ID."""
        response = client.get(f"/api/v1/faq/{test_faq.id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == str(test_faq.id)
        assert response_data["question"] == test_faq.question
        assert response_data["answer"] == test_faq.answer
        assert response_data["category"] == test_faq.category
        assert response_data["is_featured"] == test_faq.is_featured
        assert response_data["sort_order"] == test_faq.sort_order
        assert response_data["view_count"] == test_faq.view_count + 1  # Should be incremented

    def test_get_faq_inactive_not_found(self, client, test_faq_inactive):
        """Test FAQ retrieval with inactive FAQ (should not be found)."""
        response = client.get(f"/api/v1/faq/{test_faq_inactive.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_get_faq_not_found(self, client):
        """Test FAQ retrieval with non-existent ID."""
        fake_id = uuid4()
        response = client.get(f"/api/v1/faq/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_get_faq_increments_view_count(self, client, test_faq):
        """Test that view count is incremented when FAQ is accessed."""
        initial_view_count = test_faq.view_count
        
        response = client.get(f"/api/v1/faq/{test_faq.id}")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["view_count"] == initial_view_count + 1


class TestUserFAQCategories:
    """Test user FAQ categories endpoint."""

    def test_get_categories_success(self, client, multiple_test_faqs):
        """Test successful categories retrieval."""
        response = client.get("/api/v1/faq/categories/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "categories" in response_data
        categories = response_data["categories"]
        assert "Account" in categories
        assert "Technical" in categories
        assert "Billing" in categories
        assert len(categories) == 3

    def test_get_categories_empty(self, client):
        """Test categories retrieval with no FAQs."""
        response = client.get("/api/v1/faq/categories/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "categories" in response_data
        assert len(response_data["categories"]) == 0

    def test_get_categories_excludes_inactive(self, client, test_faq, test_faq_inactive):
        """Test that categories exclude inactive FAQs."""
        response = client.get("/api/v1/faq/categories/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        categories = response_data["categories"]
        assert "General" in categories  # From active FAQ
        assert "Deprecated" not in categories  # From inactive FAQ


class TestUserFeaturedFAQs:
    """Test user featured FAQs endpoint."""

    def test_get_featured_faqs_success(self, client, test_faq, test_faq_featured):
        """Test successful featured FAQs retrieval."""
        response = client.get("/api/v1/faq/featured/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "items" in response_data
        assert "total" in response_data
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["is_featured"] is True
        assert response_data["total"] == 1

    def test_get_featured_faqs_with_pagination(self, client, test_faq_featured):
        """Test featured FAQs with pagination."""
        response = client.get("/api/v1/faq/featured/list?page=1&size=1")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["page"] == 1
        assert response_data["size"] == 1

    def test_get_featured_faqs_with_search(self, client, test_faq_featured):
        """Test featured FAQs with search."""
        response = client.get("/api/v1/faq/featured/list?search=started")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert "started" in response_data["items"][0]["question"].lower()

    def test_get_featured_faqs_with_category_filter(self, client, test_faq_featured):
        """Test featured FAQs with category filter."""
        response = client.get("/api/v1/faq/featured/list?category=Getting Started")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["category"] == "Getting Started"

    def test_get_featured_faqs_empty(self, client, test_faq):
        """Test featured FAQs with no featured FAQs."""
        response = client.get("/api/v1/faq/featured/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 0
        assert response_data["total"] == 0

    def test_get_featured_faqs_sorted(self, client, multiple_test_faqs):
        """Test featured FAQs are properly sorted."""
        response = client.get("/api/v1/faq/featured/list")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        items = response_data["items"]
        # Should be sorted by sort_order
        assert items[0]["sort_order"] == 1  # Account FAQ


class TestUserFAQEdgeCases:
    """Test user FAQ edge cases."""

    def test_get_faqs_with_special_characters_in_search(self, client, multiple_test_faqs):
        """Test FAQ search with special characters."""
        response = client.get("/api/v1/faq/?search=@#$%")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 0  # No matches

    def test_get_faqs_with_very_long_search(self, client, multiple_test_faqs):
        """Test FAQ search with very long search term."""
        long_search = "a" * 1000
        response = client.get(f"/api/v1/faq/?search={long_search}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_faqs_with_invalid_sort_order(self, client, multiple_test_faqs):
        """Test FAQ list with invalid sort order."""
        response = client.get("/api/v1/faq/?sort_by=invalid_field")

        assert response.status_code == status.HTTP_200_OK  # Should default to valid sort

    def test_get_faqs_with_invalid_sort_direction(self, client, multiple_test_faqs):
        """Test FAQ list with invalid sort direction."""
        response = client.get("/api/v1/faq/?sort_order=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_faqs_case_insensitive_search(self, client, multiple_test_faqs):
        """Test FAQ search is case insensitive."""
        response = client.get("/api/v1/faq/?search=PASSWORD")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert "password" in response_data["items"][0]["question"].lower()

    def test_get_faqs_partial_category_match(self, client, multiple_test_faqs):
        """Test FAQ category filter with partial match."""
        response = client.get("/api/v1/faq/?category=Acc")  # Partial match for "Account"

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 0  # Should be exact match only
