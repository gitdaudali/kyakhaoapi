"""
Training script for recommendation ML model.

Run this script daily/weekly to retrain the model:
    python -m app.ai.training_script

Or schedule with cron:
    0 2 * * * cd /path/to/kyakhao_API && python -m app.ai.training_script
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ai.ml_pipeline import MLModelTrainer
from app.core.database import get_db


async def main():
    """Main training function."""
    print("🚀 Starting ML model training...")
    
    # Get database session
    async for db in get_db():
        try:
            # Train model
            trainer = MLModelTrainer(model_type='random_forest')
            
            model_path = Path(__file__).parent / 'models' / 'recommendation_model.pkl'
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            print("📊 Preparing training data...")
            metrics = await trainer.train(db, model_save_path=str(model_path))
            
            print("✅ Training completed!")
            print(f"   Accuracy: {metrics['accuracy']:.3f}")
            print(f"   Precision: {metrics['precision']:.3f}")
            print(f"   Recall: {metrics['recall']:.3f}")
            print(f"   ROC-AUC: {metrics['roc_auc']:.3f}")
            print(f"   Model saved to: {metrics['model_path']}")
            
            break  # Exit after first iteration
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            print("   Need more user interaction data before training.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    asyncio.run(main())

