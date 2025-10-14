"""
Integration tests for FAQ workflow.
"""

import pytest
from fastapi import status
from uuid import uuid4


class TestFAQCompleteWorkflow:
    """Test complete FAQ workflow from creation to user access."""

    def test_complete_faq_workflow(self, client, admin_auth_headers):
        """Test complete FAQ workflow: create -> update -> feature -> user access -> delete."""
        
        # Step 1: Create FAQ as admin
        create_data = {
            "question": "How do I reset my password?",
            "answer": "Click on 'Forgot Password' and follow the instructions.",
            "category": "Account",
            "is_active": True,
            "is_featured": False,
            "sort_order": 1
        }
        
        create_response = client.post("/api/v1/admin/faq/", json=create_data, headers=admin_auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        faq_data = create_response.json()
        faq_id = faq_data["id"]
        
        # Step 2: Update FAQ as admin
        update_data = {
            "answer": "Click on 'Forgot Password' link and follow the step-by-step instructions.",
            "is_featured": True
        }
        
        update_response = client.put(f"/api/v1/admin/faq/{faq_id}", json=update_data, headers=admin_auth_headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_faq = update_response.json()
        assert updated_faq["is_featured"] is True
        
        # Step 3: Verify FAQ is visible to users
        user_list_response = client.get("/api/v1/faq/")
        assert user_list_response.status_code == status.HTTP_200_OK
        user_faqs = user_list_response.json()
        assert len(user_faqs["items"]) == 1
        assert user_faqs["items"][0]["id"] == faq_id
        
        # Step 4: Access specific FAQ as user (should increment view count)
        user_get_response = client.get(f"/api/v1/faq/{faq_id}")
        assert user_get_response.status_code == status.HTTP_200_OK
        user_faq = user_get_response.json()
        assert user_faq["view_count"] == 1  # Should be incremented from 0
        
        # Step 5: Verify FAQ appears in featured list
        featured_response = client.get("/api/v1/faq/featured/list")
        assert featured_response.status_code == status.HTTP_200_OK
        featured_faqs = featured_response.json()
        assert len(featured_faqs["items"]) == 1
        assert featured_faqs["items"][0]["id"] == faq_id
        
        # Step 6: Deactivate FAQ as admin
        toggle_response = client.patch(f"/api/v1/admin/faq/{faq_id}/toggle-active", headers=admin_auth_headers)
        assert toggle_response.status_code == status.HTTP_200_OK
        
        # Step 7: Verify FAQ is no longer visible to users
        user_list_response_after = client.get("/api/v1/faq/")
        assert user_list_response_after.status_code == status.HTTP_200_OK
        user_faqs_after = user_list_response_after.json()
        assert len(user_faqs_after["items"]) == 0
        
        # Step 8: Verify FAQ is not accessible by users
        user_get_response_after = client.get(f"/api/v1/faq/{faq_id}")
        assert user_get_response_after.status_code == status.HTTP_404_NOT_FOUND
        
        # Step 9: Delete FAQ as admin
        delete_response = client.delete(f"/api/v1/admin/faq/{faq_id}", headers=admin_auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Step 10: Verify FAQ is completely gone
        admin_get_response = client.get(f"/api/v1/admin/faq/{faq_id}", headers=admin_auth_headers)
        assert admin_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_faq_search_and_filter_workflow(self, client, admin_auth_headers):
        """Test FAQ search and filtering workflow."""
        
        # Create multiple FAQs with different categories
        faqs_data = [
            {
                "question": "How to create an account?",
                "answer": "Click sign up and fill the form.",
                "category": "Account",
                "is_active": True,
                "is_featured": True,
                "sort_order": 1
            },
            {
                "question": "What devices are supported?",
                "answer": "All major devices and browsers.",
                "category": "Technical",
                "is_active": True,
                "is_featured": False,
                "sort_order": 2
            },
            {
                "question": "How to cancel subscription?",
                "answer": "Go to account settings.",
                "category": "Billing",
                "is_active": True,
                "is_featured": False,
                "sort_order": 3
            }
        ]
        
        created_faqs = []
        for faq_data in faqs_data:
            response = client.post("/api/v1/admin/faq/", json=faq_data, headers=admin_auth_headers)
            assert response.status_code == status.HTTP_200_OK
            created_faqs.append(response.json())
        
        # Test user can see all active FAQs
        user_response = client.get("/api/v1/faq/")
        assert user_response.status_code == status.HTTP_200_OK
        user_faqs = user_response.json()
        assert len(user_faqs["items"]) == 3
        
        # Test search functionality
        search_response = client.get("/api/v1/faq/?search=account")
        assert search_response.status_code == status.HTTP_200_OK
        search_faqs = search_response.json()
        assert len(search_faqs["items"]) == 1
        assert "account" in search_faqs["items"][0]["question"].lower()
        
        # Test category filtering
        category_response = client.get("/api/v1/faq/?category=Technical")
        assert category_response.status_code == status.HTTP_200_OK
        category_faqs = category_response.json()
        assert len(category_faqs["items"]) == 1
        assert category_faqs["items"][0]["category"] == "Technical"
        
        # Test featured filtering
        featured_response = client.get("/api/v1/faq/?featured_only=true")
        assert featured_response.status_code == status.HTTP_200_OK
        featured_faqs = featured_response.json()
        assert len(featured_faqs["items"]) == 1
        assert featured_faqs["items"][0]["is_featured"] is True
        
        # Test categories list
        categories_response = client.get("/api/v1/faq/categories/list")
        assert categories_response.status_code == status.HTTP_200_OK
        categories = categories_response.json()["categories"]
        assert "Account" in categories
        assert "Technical" in categories
        assert "Billing" in categories

    def test_faq_pagination_workflow(self, client, admin_auth_headers):
        """Test FAQ pagination workflow."""
        
        # Create 5 FAQs
        for i in range(5):
            faq_data = {
                "question": f"Question {i+1}?",
                "answer": f"Answer {i+1}.",
                "category": f"Category {i+1}",
                "is_active": True,
                "is_featured": i < 2,  # First 2 are featured
                "sort_order": i + 1
            }
            response = client.post("/api/v1/admin/faq/", json=faq_data, headers=admin_auth_headers)
            assert response.status_code == status.HTTP_200_OK
        
        # Test pagination for users
        page1_response = client.get("/api/v1/faq/?page=1&size=2")
        assert page1_response.status_code == status.HTTP_200_OK
        page1_data = page1_response.json()
        assert len(page1_data["items"]) == 2
        assert page1_data["page"] == 1
        assert page1_data["size"] == 2
        assert page1_data["total"] == 5
        assert page1_data["has_next"] is True
        assert page1_data["has_prev"] is False
        
        # Test second page
        page2_response = client.get("/api/v1/faq/?page=2&size=2")
        assert page2_response.status_code == status.HTTP_200_OK
        page2_data = page2_response.json()
        assert len(page2_data["items"]) == 2
        assert page2_data["page"] == 2
        assert page2_data["has_next"] is True
        assert page2_data["has_prev"] is True
        
        # Test third page
        page3_response = client.get("/api/v1/faq/?page=3&size=2")
        assert page3_response.status_code == status.HTTP_200_OK
        page3_data = page3_response.json()
        assert len(page3_data["items"]) == 1
        assert page3_data["page"] == 3
        assert page3_data["has_next"] is False
        assert page3_data["has_prev"] is True

    def test_faq_view_count_tracking(self, client, admin_auth_headers):
        """Test FAQ view count tracking."""
        
        # Create FAQ
        faq_data = {
            "question": "Test question?",
            "answer": "Test answer.",
            "category": "Test",
            "is_active": True,
            "is_featured": False,
            "sort_order": 1
        }
        
        create_response = client.post("/api/v1/admin/faq/", json=faq_data, headers=admin_auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        faq_id = create_response.json()["id"]
        
        # Verify initial view count is 0
        admin_response = client.get(f"/api/v1/admin/faq/{faq_id}", headers=admin_auth_headers)
        assert admin_response.status_code == status.HTTP_200_OK
        assert admin_response.json()["view_count"] == 0
        
        # Access FAQ multiple times as user
        for i in range(3):
            user_response = client.get(f"/api/v1/faq/{faq_id}")
            assert user_response.status_code == status.HTTP_200_OK
            user_faq = user_response.json()
            assert user_faq["view_count"] == i + 1
        
        # Verify final view count in admin
        final_admin_response = client.get(f"/api/v1/admin/faq/{faq_id}", headers=admin_auth_headers)
        assert final_admin_response.status_code == status.HTTP_200_OK
        assert final_admin_response.json()["view_count"] == 3

    def test_faq_admin_unauthorized_access(self, client, test_faq):
        """Test that regular users cannot access admin endpoints."""
        
        # Test all admin endpoints with regular user
        admin_endpoints = [
            ("GET", "/api/v1/admin/faq/"),
            ("POST", "/api/v1/admin/faq/"),
            ("GET", f"/api/v1/admin/faq/{test_faq.id}"),
            ("PUT", f"/api/v1/admin/faq/{test_faq.id}"),
            ("DELETE", f"/api/v1/admin/faq/{test_faq.id}"),
            ("PATCH", f"/api/v1/admin/faq/{test_faq.id}/toggle-active"),
            ("PATCH", f"/api/v1/admin/faq/{test_faq.id}/toggle-featured"),
        ]
        
        for method, endpoint in admin_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={"question": "Test", "answer": "Test"})
            elif method == "PUT":
                response = client.put(endpoint, json={"question": "Test"})
            elif method == "DELETE":
                response = client.delete(endpoint)
            elif method == "PATCH":
                response = client.patch(endpoint)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_faq_data_consistency(self, client, admin_auth_headers):
        """Test data consistency between admin and user views."""
        
        # Create FAQ
        faq_data = {
            "question": "Consistency test question?",
            "answer": "Consistency test answer.",
            "category": "Test",
            "is_active": True,
            "is_featured": True,
            "sort_order": 5
        }
        
        create_response = client.post("/api/v1/admin/faq/", json=faq_data, headers=admin_auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        faq_id = create_response.json()["id"]
        
        # Get FAQ from admin endpoint
        admin_response = client.get(f"/api/v1/admin/faq/{faq_id}", headers=admin_auth_headers)
        assert admin_response.status_code == status.HTTP_200_OK
        admin_faq = admin_response.json()
        
        # Get FAQ from user endpoint
        user_response = client.get(f"/api/v1/faq/{faq_id}")
        assert user_response.status_code == status.HTTP_200_OK
        user_faq = user_response.json()
        
        # Compare relevant fields (user view should not include admin-only fields)
        assert admin_faq["id"] == user_faq["id"]
        assert admin_faq["question"] == user_faq["question"]
        assert admin_faq["answer"] == user_faq["answer"]
        assert admin_faq["category"] == user_faq["category"]
        assert admin_faq["is_featured"] == user_faq["is_featured"]
        assert admin_faq["sort_order"] == user_faq["sort_order"]
        
        # User view should not include admin-only fields
        assert "is_active" not in user_faq
        assert "is_deleted" not in user_faq
        assert "created_at" in user_faq  # User can see creation time
        assert "updated_at" in user_faq  # User can see update time
