"""
Unit tests for admin FAQ endpoints.
"""

import pytest
from fastapi import status
from uuid import uuid4


class TestAdminFAQCreate:
    """Test admin FAQ creation endpoint."""

    def test_create_faq_success(self, client, admin_auth_headers):
        """Test successful FAQ creation."""
        data = {
            "question": "How do I create an account?",
            "answer": "Click on the sign up button and follow the instructions.",
            "category": "Account",
            "is_active": True,
            "is_featured": False,
            "sort_order": 1
        }

        response = client.post("/api/v1/admin/faq/", json=data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["question"] == data["question"]
        assert response_data["answer"] == data["answer"]
        assert response_data["category"] == data["category"]
        assert response_data["is_active"] == data["is_active"]
        assert response_data["is_featured"] == data["is_featured"]
        assert response_data["sort_order"] == data["sort_order"]
        assert response_data["view_count"] == 0
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_create_faq_minimal_data(self, client, admin_auth_headers):
        """Test FAQ creation with minimal required data."""
        data = {
            "question": "What is this service?",
            "answer": "A streaming service for movies and TV shows."
        }

        response = client.post("/api/v1/admin/faq/", json=data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["question"] == data["question"]
        assert response_data["answer"] == data["answer"]
        assert response_data["is_active"] is True  # Default value
        assert response_data["is_featured"] is False  # Default value
        assert response_data["sort_order"] == 0  # Default value

    def test_create_faq_unauthorized(self, client):
        """Test FAQ creation without authentication."""
        data = {
            "question": "Test question?",
            "answer": "Test answer."
        }

        response = client.post("/api/v1/admin/faq/", json=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_faq_regular_user(self, client, auth_headers):
        """Test FAQ creation with regular user (should fail)."""
        data = {
            "question": "Test question?",
            "answer": "Test answer."
        }

        response = client.post("/api/v1/admin/faq/", json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_faq_invalid_data(self, client, admin_auth_headers):
        """Test FAQ creation with invalid data."""
        data = {
            "question": "",  # Empty question
            "answer": "Test answer."
        }

        response = client.post("/api/v1/admin/faq/", json=data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_faq_missing_required_fields(self, client, admin_auth_headers):
        """Test FAQ creation with missing required fields."""
        data = {
            "question": "Test question?"
            # Missing answer
        }

        response = client.post("/api/v1/admin/faq/", json=data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminFAQList:
    """Test admin FAQ list endpoint."""

    def test_get_faqs_success(self, client, admin_auth_headers, multiple_test_faqs):
        """Test successful FAQ list retrieval."""
        response = client.get("/api/v1/admin/faq/", headers=admin_auth_headers)

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

    def test_get_faqs_with_pagination(self, client, admin_auth_headers, multiple_test_faqs):
        """Test FAQ list with pagination."""
        response = client.get("/api/v1/admin/faq/?page=1&size=2", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 2
        assert response_data["page"] == 1
        assert response_data["size"] == 2
        assert response_data["total"] == 3

    def test_get_faqs_with_search(self, client, admin_auth_headers, multiple_test_faqs):
        """Test FAQ list with search."""
        response = client.get("/api/v1/admin/faq/?search=password", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert "password" in response_data["items"][0]["question"].lower()

    def test_get_faqs_with_category_filter(self, client, admin_auth_headers, multiple_test_faqs):
        """Test FAQ list with category filter."""
        response = client.get("/api/v1/admin/faq/?category=Account", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["category"] == "Account"

    def test_get_faqs_with_active_filter(self, client, admin_auth_headers, test_faq, test_faq_inactive):
        """Test FAQ list with active status filter."""
        response = client.get("/api/v1/admin/faq/?is_active=true", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["is_active"] is True

    def test_get_faqs_with_featured_filter(self, client, admin_auth_headers, test_faq, test_faq_featured):
        """Test FAQ list with featured status filter."""
        response = client.get("/api/v1/admin/faq/?is_featured=true", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["items"]) == 1
        assert response_data["items"][0]["is_featured"] is True

    def test_get_faqs_unauthorized(self, client, multiple_test_faqs):
        """Test FAQ list without authentication."""
        response = client.get("/api/v1/admin/faq/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_faqs_regular_user(self, client, auth_headers, multiple_test_faqs):
        """Test FAQ list with regular user (should fail)."""
        response = client.get("/api/v1/admin/faq/", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminFAQGet:
    """Test admin FAQ get by ID endpoint."""

    def test_get_faq_success(self, client, admin_auth_headers, test_faq):
        """Test successful FAQ retrieval by ID."""
        response = client.get(f"/api/v1/admin/faq/{test_faq.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == str(test_faq.id)
        assert response_data["question"] == test_faq.question
        assert response_data["answer"] == test_faq.answer
        assert response_data["category"] == test_faq.category

    def test_get_faq_not_found(self, client, admin_auth_headers):
        """Test FAQ retrieval with non-existent ID."""
        fake_id = uuid4()
        response = client.get(f"/api/v1/admin/faq/{fake_id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_get_faq_unauthorized(self, client, test_faq):
        """Test FAQ retrieval without authentication."""
        response = client.get(f"/api/v1/admin/faq/{test_faq.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_faq_regular_user(self, client, auth_headers, test_faq):
        """Test FAQ retrieval with regular user (should fail)."""
        response = client.get(f"/api/v1/admin/faq/{test_faq.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminFAQUpdate:
    """Test admin FAQ update endpoint."""

    def test_update_faq_success(self, client, admin_auth_headers, test_faq):
        """Test successful FAQ update."""
        update_data = {
            "question": "Updated question?",
            "answer": "Updated answer.",
            "category": "Updated Category",
            "is_featured": True
        }

        response = client.put(f"/api/v1/admin/faq/{test_faq.id}", json=update_data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["question"] == update_data["question"]
        assert response_data["answer"] == update_data["answer"]
        assert response_data["category"] == update_data["category"]
        assert response_data["is_featured"] == update_data["is_featured"]

    def test_update_faq_partial(self, client, admin_auth_headers, test_faq):
        """Test partial FAQ update."""
        update_data = {
            "question": "Partially updated question?"
        }

        response = client.put(f"/api/v1/admin/faq/{test_faq.id}", json=update_data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["question"] == update_data["question"]
        assert response_data["answer"] == test_faq.answer  # Should remain unchanged

    def test_update_faq_not_found(self, client, admin_auth_headers):
        """Test FAQ update with non-existent ID."""
        fake_id = uuid4()
        update_data = {"question": "Updated question?"}

        response = client.put(f"/api/v1/admin/faq/{fake_id}", json=update_data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_update_faq_unauthorized(self, client, test_faq):
        """Test FAQ update without authentication."""
        update_data = {"question": "Updated question?"}

        response = client.put(f"/api/v1/admin/faq/{test_faq.id}", json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_faq_regular_user(self, client, auth_headers, test_faq):
        """Test FAQ update with regular user (should fail)."""
        update_data = {"question": "Updated question?"}

        response = client.put(f"/api/v1/admin/faq/{test_faq.id}", json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_faq_invalid_data(self, client, admin_auth_headers, test_faq):
        """Test FAQ update with invalid data."""
        update_data = {
            "question": "",  # Empty question
            "answer": "Updated answer."
        }

        response = client.put(f"/api/v1/admin/faq/{test_faq.id}", json=update_data, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminFAQDelete:
    """Test admin FAQ delete endpoint."""

    def test_delete_faq_success(self, client, admin_auth_headers, test_faq):
        """Test successful FAQ deletion."""
        response = client.delete(f"/api/v1/admin/faq/{test_faq.id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "FAQ deleted successfully" in response.json()["message"]

    def test_delete_faq_not_found(self, client, admin_auth_headers):
        """Test FAQ deletion with non-existent ID."""
        fake_id = uuid4()
        response = client.delete(f"/api/v1/admin/faq/{fake_id}", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_delete_faq_unauthorized(self, client, test_faq):
        """Test FAQ deletion without authentication."""
        response = client.delete(f"/api/v1/admin/faq/{test_faq.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_faq_regular_user(self, client, auth_headers, test_faq):
        """Test FAQ deletion with regular user (should fail)."""
        response = client.delete(f"/api/v1/admin/faq/{test_faq.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminFAQToggleActive:
    """Test admin FAQ toggle active endpoint."""

    def test_toggle_faq_active_success(self, client, admin_auth_headers, test_faq):
        """Test successful FAQ active status toggle."""
        response = client.patch(f"/api/v1/admin/faq/{test_faq.id}/toggle-active", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert "faq" in response_data
        assert response_data["faq"]["is_active"] is False  # Should be toggled

    def test_toggle_faq_active_not_found(self, client, admin_auth_headers):
        """Test FAQ active toggle with non-existent ID."""
        fake_id = uuid4()
        response = client.patch(f"/api/v1/admin/faq/{fake_id}/toggle-active", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_toggle_faq_active_unauthorized(self, client, test_faq):
        """Test FAQ active toggle without authentication."""
        response = client.patch(f"/api/v1/admin/faq/{test_faq.id}/toggle-active")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminFAQToggleFeatured:
    """Test admin FAQ toggle featured endpoint."""

    def test_toggle_faq_featured_success(self, client, admin_auth_headers, test_faq):
        """Test successful FAQ featured status toggle."""
        response = client.patch(f"/api/v1/admin/faq/{test_faq.id}/toggle-featured", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert "faq" in response_data
        assert response_data["faq"]["is_featured"] is True  # Should be toggled

    def test_toggle_faq_featured_not_found(self, client, admin_auth_headers):
        """Test FAQ featured toggle with non-existent ID."""
        fake_id = uuid4()
        response = client.patch(f"/api/v1/admin/faq/{fake_id}/toggle-featured", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "FAQ not found" in response.json()["detail"]

    def test_toggle_faq_featured_unauthorized(self, client, test_faq):
        """Test FAQ featured toggle without authentication."""
        response = client.patch(f"/api/v1/admin/faq/{test_faq.id}/toggle-featured")

        assert response.status_code == status.HTTP_403_FORBIDDEN
