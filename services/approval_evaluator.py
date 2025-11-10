"""
Approval Evaluator Service
Evaluates invoices against category-specific approval criteria
"""
from typing import Optional, Dict
from pathlib import Path
import sys
import os
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from category_service import CategoryService

# Load configuration
try:
    from genai_config import USE_GENAI, TEMPERATURE, MAX_TOKENS
except ImportError:
    USE_GENAI = True  # Enable by default for local model
    TEMPERATURE = 0.3
    MAX_TOKENS = 500

# TinyLlama model configuration
TINYLLAMA_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Check if transformers and TinyLlama are available
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    GENAI_AVAILABLE = USE_GENAI
    _model = None
    _tokenizer = None
    _generator = None
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("transformers library not available. Install with: pip install transformers torch")


class ApprovalEvaluator:
    """Service to evaluate invoice approval based on category criteria"""
    
    def __init__(self):
        self.category_service = CategoryService()
        self._init_model()
    
    def _init_model(self):
        """Initialize TinyLlama model lazily on first use."""
        global _model, _tokenizer, _generator
        
        if not GENAI_AVAILABLE:
            logger.warning("TinyLlama model initialization skipped - transformers not available")
            return
        
        if _generator is None:
            try:
                logger.info(f"Loading TinyLlama model: {TINYLLAMA_MODEL}")
                
                # Use GPU if available, otherwise CPU
                device = 0 if torch.cuda.is_available() else -1
                device_name = "GPU" if device == 0 else "CPU"
                logger.info(f"Using device: {device_name}")
                
                # Create text generation pipeline
                _generator = pipeline(
                    "text-generation",
                    model=TINYLLAMA_MODEL,
                    tokenizer=TINYLLAMA_MODEL,
                    device=device,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    max_new_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    do_sample=True,
                    top_p=0.95,
                )
                
                logger.info("TinyLlama model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load TinyLlama model: {str(e)}", exc_info=True)
                raise
    
    def extract_category_from_filename(self, filename: str) -> str:
        """Extract category from filename (format: PREFIX_CATEGORYNAME.ext)."""
        logger.info(f"[ENTER] extract_category_from_filename: filename='{filename}'")
        try:
            base_name = Path(filename).stem
            parts = base_name.split('_', 1)
            category = parts[1].strip() if len(parts) > 1 and parts[1].strip() else 'General'
            logger.info(f"[EXIT] extract_category_from_filename: category='{category}'")
            return category
        except Exception as e:
            logger.error(f"[ERROR] extract_category_from_filename: {type(e).__name__}: {str(e)}", exc_info=True)
            logger.info(f"[EXIT] extract_category_from_filename: category='General' (default)")
            return 'General'
    
    def get_category_approval_criteria(self, category_name: str) -> Optional[str]:
        """Get approval criteria for a category."""
        logger.info(f"[ENTER] get_category_approval_criteria: category_name='{category_name}'")
        try:
            category = self.category_service.get_category_by_name(category_name)
            if category:
                criteria = category.APPROVAL_CRITERIA
                logger.info(f"[EXIT] get_category_approval_criteria: criteria_found=True, length={len(criteria) if criteria else 0}")
                return criteria
            else:
                logger.warning(f"[EXIT] get_category_approval_criteria: category not found in database")
                return None
        except Exception as e:
            logger.error(f"[ERROR] get_category_approval_criteria: {type(e).__name__}: {str(e)}", exc_info=True)
            logger.info(f"[EXIT] get_category_approval_criteria: criteria=None (error)")
            return None
    
    def evaluate_invoice(self, invoice_data: Dict, approval_criteria: Optional[str] = None) -> Dict:
        """
        Evaluate invoice using GenAI.
        
        Args:
            invoice_data: Extracted invoice data
            approval_criteria: Approval criteria text from category
            
        Returns:
            Dict with 'decision' (Approved/Pending/Rejected) and 'reasons' (list)
        """
        amount = invoice_data.get('total_amount', 0)
        items_count = len(invoice_data.get('items', []) or [])
        logger.info(f"[ENTER] evaluate_invoice: amount={amount}, items_count={items_count}, criteria_provided={approval_criteria is not None}")
        
        # Category not matched → Rejected
        if not approval_criteria:
            result = {
                'decision': 'Rejected',
                'reasons': ['Category not found in database']
            }
            logger.info(f"[EXIT] evaluate_invoice: decision='Rejected' - category not found in database")
            return result
        
        # GenAI not available → Pending (for testing)
        if not GENAI_AVAILABLE or _generator is None:
            result = {
                'decision': 'Pending',
                'reasons': ['TinyLlama model not available. Install with: pip install transformers torch']
            }
            logger.warning(f"[EXIT] evaluate_invoice: decision='Pending' - TinyLlama not available (testing mode)")
            return result
        
        logger.info(f"[INFO] evaluate_invoice: calling TinyLlama for evaluation")
        result = self._evaluate_with_tinyllama(invoice_data, approval_criteria)
        logger.info(f"[EXIT] evaluate_invoice: decision='{result['decision']}', reasons={result['reasons']}")
        return result
    
    def _evaluate_with_tinyllama(self, invoice_data: Dict, approval_criteria: str) -> Dict:
        """Evaluate invoice using TinyLlama model."""
        logger.info(f"[ENTER] _evaluate_with_tinyllama: model='{TINYLLAMA_MODEL}'")
        try:
            if _generator is None:
                raise RuntimeError("TinyLlama model not initialized")
            
            # Prepare prompt in chat format for TinyLlama
            prompt = f"""<|system|>
You are a strict invoice approval system. Your task is to compare invoice details against approval criteria.

CRITICAL RULES:
1. If ANY criterion is NOT met, decision MUST be "Pending"
2. ONLY use "Approved" if ALL criteria are satisfied
3. Be strict and thorough in your evaluation
4. SPECIAL RULE: If the category is "CENTRICONOTCARES", ALWAYS set decision to "Pending" with reason "Criteria not met"
5. Respond ONLY with valid JSON in this exact format:
{{"decision": "Approved" or "Pending", "reasons": ["reason1", "reason2"]}}

DO NOT approve if criteria are not met.
</s>
<|user|>
Evaluate this invoice strictly against the approval criteria.

Invoice Details:
- Total Amount: {invoice_data.get('total_amount', 0):.2f}
- Number of Items: {len(invoice_data.get('items', []))}
- Items: {', '.join([item.get('description', 'N/A') for item in invoice_data.get('items', [])][:5])}

Approval Criteria:
{approval_criteria}

IMPORTANT: If ANY criterion is not met, set decision to "Pending". Only approve if ALL criteria are satisfied.

Respond with JSON only:
</s>
<|assistant|>
"""
            
            logger.debug(f"[INFO] _evaluate_with_tinyllama: sending request to TinyLlama")
            
            # Generate response
            outputs = _generator(
                prompt,
                max_new_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.95,
                return_full_text=False,
            )
            
            response_text = outputs[0]['generated_text'].strip()
            logger.debug(f"[INFO] _evaluate_with_tinyllama: raw response='{response_text}'")
            
            # Extract JSON from response (handle cases where model adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("[WARN] _evaluate_with_tinyllama: No valid JSON found in response, defaulting to Pending")
                return {
                    'decision': 'Pending',
                    'reasons': ['Unable to parse model response. Manual review required.']
                }
            
            json_text = response_text[json_start:json_end]
            result = json.loads(json_text)
            
            # Validate and normalize decision - BE STRICT
            decision = result.get('decision', 'Pending').strip()
            
            # Only accept exact matches, otherwise default to Pending
            if decision not in ['Approved', 'Pending', 'Rejected']:
                logger.warning(f"[WARN] Invalid decision '{decision}', defaulting to Pending")
                decision = 'Pending'
            
            # Extra safety: If reasons mention any failure/issue/not met, force to Pending
            reasons = result.get('reasons', ['Model evaluation completed'])
            reason_text = ' '.join(reasons).lower()
            if decision == 'Approved' and any(keyword in reason_text for keyword in 
                ['not met', 'does not meet', 'failed', 'exceeds', 'insufficient', 'missing', 'invalid', 'rejected']):
                logger.warning(f"[WARN] Decision was Approved but reasons indicate issues, forcing to Pending")
                decision = 'Pending'
                reasons.insert(0, 'Criteria not fully met - requires manual review')
            
            decision_result = {
                'decision': decision,
                'reasons': reasons
            }
            logger.info(f"[EXIT] _evaluate_with_tinyllama: decision='{decision_result['decision']}'")
            return decision_result
            
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] _evaluate_with_tinyllama: JSON parsing failed: {str(e)}", exc_info=True)
            return {
                'decision': 'Pending',
                'reasons': [f'JSON parsing error: {str(e)}. Manual review required.']
            }
        except Exception as e:
            logger.error(f"[ERROR] _evaluate_with_tinyllama: {type(e).__name__}: {str(e)}", exc_info=True)
            return {
                'decision': 'Pending',
                'reasons': [f'Model error: {str(e)}. Manual review required.']
            }
    
    def evaluate_with_category(self, filename: str, invoice_data: Dict) -> Dict:
        """
        Complete workflow: extract category → lookup in DB → evaluate invoice.
        
        Status outcomes:
        - Rejected: Category not found in database
        - Pending: GenAI not available (testing fallback) OR criteria not met
        - Approved: ALL criteria met
        
        Args:
            filename: Invoice filename
            invoice_data: Extracted invoice data
            
        Returns:
            Dict with 'decision' (Approved/Pending/Rejected), 'reasons' (list), 'category', 'category_found'
        """
        logger.info(f"[ENTER] evaluate_with_category: filename='{filename}'")
        try:
            category = self.extract_category_from_filename(filename)
            logger.info(f"[INFO] evaluate_with_category: extracted category='{category}'")
            
            # Special handling for CENTRICONOTCARES category - always Pending
            if category.upper() == 'CENTRICONOTCARES':
                logger.warning(f"[WARN] Category is CENTRICONOTCARES, forcing to Pending")
                final_result = {
                    'decision': 'Pending',
                    'reasons': ['Criteria not met'],
                    'category': category,
                    'category_found': True
                }
                logger.info(f"[EXIT] evaluate_with_category: final_decision='Pending' (CENTRICONOTCARES)")
                return final_result
            
            criteria = self.get_category_approval_criteria(category)
            category_found = criteria is not None
            logger.info(f"[INFO] evaluate_with_category: criteria_lookup_result={category_found}")
            
            result = self.evaluate_invoice(invoice_data, criteria)
            
            # Additional validation: Check category maximum amount
            if category_found and result['decision'] == 'Approved':
                category_obj = self.category_service.get_category_by_name(category)
                if category_obj and category_obj.MAXIMUMAMOUNT:
                    invoice_total = invoice_data.get('total_amount', 0)
                    max_amount = float(category_obj.MAXIMUMAMOUNT)
                    
                    if invoice_total > max_amount:
                        logger.warning(f"[WARN] Invoice amount {invoice_total} exceeds category max {max_amount}, forcing to Pending")
                        result['decision'] = 'Pending'
                        result['reasons'].insert(0, f'Invoice amount {invoice_total:.2f} exceeds category maximum {max_amount:.2f}')
            
            final_result = {
                'decision': result['decision'],
                'reasons': result['reasons'],
                'category': category,
                'category_found': category_found
            }
            logger.info(f"[EXIT] evaluate_with_category: final_decision='{final_result['decision']}', category='{category}', category_found={category_found}")
            return final_result
            
        except Exception as e:
            logger.error(f"[ERROR] evaluate_with_category: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
