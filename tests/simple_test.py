"""
Simple test to verify FAQ functionality without full app setup.
"""

import pytest
from app.models.faq import FAQ
from app.schemas.faq import FAQResponse, FAQListResponse, FAQQueryParams
from app.schemas.admin import FAQAdminCreate, FAQAdminUpdate, FAQAdminResponse


def test_faq_model_creation():
    """Test FAQ model can be created."""
    faq = FAQ(
        question="Test question?",
        answer="Test answer.",
        category="Test",
        is_active=True,
        is_featured=False,
        sort_order=1,
        view_count=0
    )
    
    assert faq.question == "Test question?"
    assert faq.answer == "Test answer."
    assert faq.category == "Test"
    assert faq.is_active is True
    assert faq.is_featured is False
    assert faq.sort_order == 1
    assert faq.view_count == 0


def test_faq_schemas():
    """Test FAQ schemas can be created."""
    # Test user FAQ response
    faq_response = FAQResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        question="Test question?",
        answer="Test answer.",
        category="Test",
        is_featured=False,
        sort_order=1,
        view_count=0,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    assert faq_response.question == "Test question?"
    assert faq_response.answer == "Test answer."
    
    # Test admin FAQ create
    faq_create = FAQAdminCreate(
        question="Admin question?",
        answer="Admin answer.",
        category="Admin",
        is_active=True,
        is_featured=True,
        sort_order=2
    )
    
    assert faq_create.question == "Admin question?"
    assert faq_create.is_featured is True
    
    # Test admin FAQ update
    faq_update = FAQAdminUpdate(
        question="Updated question?",
        is_featured=False
    )
    
    assert faq_update.question == "Updated question?"
    assert faq_update.is_featured is False


def test_faq_query_params():
    """Test FAQ query parameters."""
    params = FAQQueryParams(
        page=1,
        size=10,
        search="test",
        category="Test",
        featured_only=True,
        sort_by="sort_order",
        sort_order="asc"
    )
    
    assert params.page == 1
    assert params.size == 10
    assert params.search == "test"
    assert params.category == "Test"
    assert params.featured_only is True
    assert params.sort_by == "sort_order"
    assert params.sort_order == "asc"


def test_faq_list_response():
    """Test FAQ list response."""
    faq_items = [
        FAQResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            question="Question 1?",
            answer="Answer 1.",
            category="Test",
            is_featured=True,
            sort_order=1,
            view_count=5,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        ),
        FAQResponse(
            id="123e4567-e89b-12d3-a456-426614174001",
            question="Question 2?",
            answer="Answer 2.",
            category="Test",
            is_featured=False,
            sort_order=2,
            view_count=3,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ]
    
    list_response = FAQListResponse(
        items=faq_items,
        total=2,
        page=1,
        size=10,
        pages=1,
        has_next=False,
        has_prev=False
    )
    
    assert len(list_response.items) == 2
    assert list_response.total == 2
    assert list_response.page == 1
    assert list_response.size == 10
    assert list_response.pages == 1
    assert list_response.has_next is False
    assert list_response.has_prev is False


if __name__ == "__main__":
    pytest.main([__file__])
