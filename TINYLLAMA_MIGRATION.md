# TinyLlama Integration for Invoice Approval

## Changes Made

### 1. Updated `services/approval_evaluator.py`

**Replaced OpenAI GPT-4 with TinyLlama (local open-source model)**

#### Key Changes:
- **Removed**: OpenAI API dependency and API key requirements
- **Added**: TinyLlama model integration using Hugging Face transformers
- **Model**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (1.1B parameter chat model)

#### Benefits:
- ✅ **No API costs** - runs completely locally
- ✅ **No API keys required** - no external service dependencies
- ✅ **Privacy** - all data stays on your machine
- ✅ **GPU acceleration** - uses CUDA if available, falls back to CPU
- ✅ **Fast inference** - optimized with fp16 on GPU

#### Configuration:
```python
# Model loads automatically on first use
# Uses GPU if available, otherwise CPU
# Configuration from genai_config.py:
- USE_GENAI: Enable/disable model (default: True)
- TEMPERATURE: 0.3 (controls randomness)
- MAX_TOKENS: 500 (max response length)
```

### 2. Dependencies

Already included in `requirements.txt`:
```
torch>=2.0.0
transformers>=4.30.0
```

### 3. New Test Script

Created `test_tinyllama_approval.py` to verify the integration:
```bash
python test_tinyllama_approval.py
```

## Installation

### Install Required Packages
```powershell
pip install torch transformers accelerate
```

### For GPU Support (NVIDIA CUDA)
```powershell
# Windows with CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Or CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

## Usage

The API remains the same - no code changes needed in your application:

```python
from services.approval_evaluator import ApprovalEvaluator

evaluator = ApprovalEvaluator()  # Model loads automatically

# Evaluate invoice
result = evaluator.evaluate_invoice(invoice_data, approval_criteria)

# Or use complete workflow with category
result = evaluator.evaluate_with_category(filename, invoice_data)

# Result format:
# {
#     'decision': 'Approved' | 'Pending' | 'Rejected',
#     'reasons': ['reason1', 'reason2', ...],
#     'category': 'CategoryName'  # if using evaluate_with_category
# }
```

## How It Works

1. **First Call**: TinyLlama model is downloaded (~2.2GB) and cached locally
2. **Subsequent Calls**: Model loads from cache (~5-10 seconds on CPU, ~2 seconds on GPU)
3. **Inference**: Evaluates invoices against criteria in ~1-2 seconds
4. **Response**: Returns structured JSON with decision and reasons

## Model Details

- **Model**: TinyLlama-1.1B-Chat-v1.0
- **Size**: ~2.2GB
- **Parameters**: 1.1 billion
- **Context Length**: 2048 tokens
- **Format**: Chat-tuned for instruction following
- **License**: Apache 2.0 (commercial use allowed)

## Performance

### GPU (NVIDIA):
- Model Load: ~2 seconds
- Inference: ~0.5-1 second per invoice
- Memory: ~3GB VRAM (fp16)

### CPU:
- Model Load: ~5-10 seconds
- Inference: ~2-5 seconds per invoice
- Memory: ~4GB RAM (fp32)

## Fallback Behavior

If model fails to load or parse response:
- Returns `'Pending'` decision
- Includes error message in reasons
- Allows manual review

## Testing

Run the test script to verify setup:
```powershell
python test_tinyllama_approval.py
```

Expected output:
- Model initialization confirmation
- Sample invoice evaluation
- Category-based evaluation
- Decision and reasoning display

## Migration from OpenAI

### Before (OpenAI GPT-4):
- Required `OPENAI_API_KEY` in `genai_config.py`
- API costs per request
- External service dependency
- Internet connection required

### After (TinyLlama):
- No API key required
- Zero cost after initial setup
- Runs completely offline
- Local data processing

## Troubleshooting

### Model Download Issues
```powershell
# Manually download model
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0')"
```

### CUDA/GPU Issues
```powershell
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Memory Issues
- Reduce `MAX_TOKENS` in `genai_config.py`
- Use CPU instead of GPU (automatic fallback)
- Close other applications

## Next Steps

1. Install dependencies: `pip install torch transformers accelerate`
2. Test the integration: `python test_tinyllama_approval.py`
3. Run the combined app: `python combined_app.py`
4. Monitor logs for model initialization and evaluation

## Notes

- First run downloads model (~2.2GB) - may take a few minutes
- Model is cached in `~/.cache/huggingface/` for reuse
- GPU acceleration significantly improves performance
- Model responses may vary slightly due to sampling
- JSON parsing includes fallback for malformed responses
