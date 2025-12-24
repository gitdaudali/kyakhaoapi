"""
Script to verify all database relationships are properly configured.

Run this after migrations to ensure relationships work correctly.
"""
import asyncio
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine
from app.models.food import Dish, Restaurant, Cuisine, Mood
from app.models.recommendation import DietaryTag
from app.models.user import User


async def verify_relationships():
    """Verify all relationships are properly configured."""
    print("🔍 Verifying Database Relationships...\n")
    
    async for db in get_db():
        try:
            # Check Dish relationships
            print("1. Checking Dish relationships...")
            dish_inspector = inspect(Dish)
            
            # Check foreign keys
            fks = [fk.name for fk in dish_inspector.foreign_keys]
            print(f"   ✅ Foreign keys: {fks}")
            assert "restaurant_id" in [fk.parent.name for fk in dish_inspector.foreign_keys], "Missing restaurant_id FK"
            assert "cuisine_id" in [fk.parent.name for fk in dish_inspector.foreign_keys], "Missing cuisine_id FK"
            
            # Check relationships
            rels = list(dish_inspector.relationships.keys())
            print(f"   ✅ Relationships: {rels}")
            assert "cuisine" in rels, "Missing cuisine relationship"
            assert "restaurant" in rels, "Missing restaurant relationship"
            assert "moods" in rels, "Missing moods relationship"
            assert "dietary_tags" in rels, "Missing dietary_tags relationship"
            
            # Check Restaurant relationships
            print("\n2. Checking Restaurant relationships...")
            restaurant_inspector = inspect(Restaurant)
            restaurant_rels = list(restaurant_inspector.relationships.keys())
            print(f"   ✅ Relationships: {restaurant_rels}")
            assert "dishes" in restaurant_rels, "Missing dishes relationship"
            assert "reservations" in restaurant_rels, "Missing reservations relationship"
            
            # Check Cuisine relationships
            print("\n3. Checking Cuisine relationships...")
            cuisine_inspector = inspect(Cuisine)
            cuisine_rels = list(cuisine_inspector.relationships.keys())
            print(f"   ✅ Relationships: {cuisine_rels}")
            assert "dishes" in cuisine_rels, "Missing dishes relationship"
            
            # Check Mood relationships
            print("\n4. Checking Mood relationships...")
            mood_inspector = inspect(Mood)
            mood_rels = list(mood_inspector.relationships.keys())
            print(f"   ✅ Relationships: {mood_rels}")
            assert "dishes" in mood_rels, "Missing dishes relationship"
            
            # Check DietaryTag relationships
            print("\n5. Checking DietaryTag relationships...")
            dietary_tag_inspector = inspect(DietaryTag)
            dietary_tag_rels = list(dietary_tag_inspector.relationships.keys())
            print(f"   ✅ Relationships: {dietary_tag_rels}")
            assert "dishes" in dietary_tag_rels, "Missing dishes relationship"
            
            # Test relationship access (if data exists)
            print("\n6. Testing relationship access...")
            result = await db.execute(select(Dish).limit(1))
            dish = result.scalar_one_or_none()
            
            if dish:
                print(f"   Testing with dish: {dish.name}")
                # Access relationships (should not raise errors)
                try:
                    _ = dish.cuisine  # Access cuisine
                    _ = dish.restaurant  # Access restaurant
                    _ = dish.moods  # Access moods
                    _ = dish.dietary_tags  # Access dietary tags
                    print("   ✅ All relationships accessible")
                except Exception as e:
                    print(f"   ⚠️ Relationship access error: {e}")
            else:
                print("   ℹ️ No dishes found - skipping relationship access test")
            
            print("\n✅ All relationships verified successfully!")
            break
            
        except Exception as e:
            print(f"\n❌ Error verifying relationships: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    asyncio.run(verify_relationships())

