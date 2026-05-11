from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from ..models.product import Product
from ..models.search_request import SearchRequest
import logging
import json
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QualityAgent(BaseAgent):
    """
    QualityAgent specializes in assessing product quality and detecting issues.
    
    Responsibilities:
    - Analyze product descriptions for red flags
    - Assess photo quality and authenticity
    - Evaluate seller reputation signals
    - Detect scam indicators
    - Rate product condition
    - Provide safety recommendations
    
    Attributes:
        RED_FLAG_KEYWORDS: Common scam/problem indicators
        POSITIVE_KEYWORDS: Quality indicators
        MIN_DESCRIPTION_LENGTH: Minimum acceptable description length
    """
    
    # Class constants
    RED_FLAG_KEYWORDS = [
        'urgent', 'must sell today', 'cash only', 'no refunds', 'as-is',
        'broken', 'not working', 'for parts', 'damaged', 'cracked',
        'wire transfer', 'western union', 'gift card', 'prepaid',
        'too good to be true', 'limited time', 'act now'
    ]
    
    POSITIVE_KEYWORDS = [
        'excellent condition', 'like new', 'barely used', 'well maintained',
        'original box', 'warranty', 'receipt', 'smoke free', 'pet free',
        'detailed photos', 'happy to answer questions', 'test before buying'
    ]
    
    MIN_DESCRIPTION_LENGTH = 50
    MIN_PHOTOS = 2
    def _extract_json_from_response(self, content: str) -> Dict:
        """
        Extract JSON from LLM response, handling markdown code blocks and extra text.
        
        Args:
            content: Raw LLM response
            
        Returns:
            Parsed JSON dictionary
        """
        if not content or not content.strip():
            logger.error("Empty response from LLM")
            raise ValueError("Empty response from LLM")
        
        # Strip whitespace
        content = content.strip()
        
        try:
            # First, try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parse failed: {e}")
        
        # Try to extract JSON from markdown code blocks
        # Look for ```json ... ``` or ``` ... ```
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                logger.debug(f"Markdown JSON parse failed: {e}")
        
        # Look for JSON object anywhere in the text (greedy match)
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"Extracted JSON parse failed: {e}, JSON: {json_str[:200]}")
        
        # Try to find JSON between any text
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                # Found potential JSON start, try to parse from here
                remaining = '\n'.join(lines[i:])
                json_match = re.search(r'\{.*\}', remaining, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        continue
        
        # If all else fails, log the full content and raise
        logger.error(f"Could not extract JSON from LLM response. Full content ({len(content)} chars): {content}")
        raise ValueError(f"Could not parse JSON from response: {content[:200]}")

    
    async def perceive(self, environment: Dict) -> Dict:
        """
        Extract quality-relevant information from environment.
        
        Args:
            environment: Dictionary containing:
                - product: Product to assess
                - seller_history: Optional seller information
                
        Returns:
            Dictionary with quality observations
        """
        product = environment.get('product')
        
        if not product:
            logger.warning("No product provided to QualityAgent.perceive()")
            return {}
        
        # Extract product details
        description = str(getattr(product, 'description', ''))
        title = str(getattr(product, 'title', ''))
        image_url = getattr(product, 'image_url', None)
        platform = str(getattr(product, 'platform', ''))
        
        observations = {
            'product': product,
            'title': title,
            'description': description,
            'has_image': bool(image_url),
            'image_url': image_url,
            'platform': platform,
            'description_length': len(description),
            'red_flags_found': self._detect_red_flags(title, description),
            'positive_signals': self._detect_positive_signals(title, description),
            'description_quality': self._assess_description_quality(description),
            'title_quality': self._assess_title_quality(title)
        }
        
        return observations
    
    async def decide(self, observations: Dict) -> Dict:
        """
        Decide on product quality and safety.
        
        Args:
            observations: Quality observations from perceive()
            
        Returns:
            Dictionary with quality decision
        """
        product = observations.get('product')
        
        if not product:
            logger.error("No product in observations")
            return self._get_default_assessment()
        
        # Perform comprehensive quality assessment
        assessment = await self.assess_quality(
            product=product,
            red_flags=observations.get('red_flags_found', []),
            positive_signals=observations.get('positive_signals', []),
            description_quality=observations.get('description_quality', {}),
            title_quality=observations.get('title_quality', {})
        )
        
        return assessment
    
    async def act(self, decision: Dict) -> Dict[str, Any]:
        """
        Execute quality decision (log warnings, prepare alerts).
        
        Args:
            decision: Quality decision from decide()
            
        Returns:
            Dictionary with action results
        """
        logger.info(f"QualityAgent acting on decision: {decision.get('recommendation')}")
        
        results = {
            'action_taken': None,
            'warning_issued': False,
            'logged': False
        }
        
        try:
            # Log decision to memory
            self.add_to_memory({
                'action': 'quality_assessment',
                'timestamp': json.dumps(decision.get('timestamp', '')),
                'quality_rating': decision.get('quality_rating'),
                'recommendation': decision.get('recommendation'),
                'red_flags_count': len(decision.get('red_flags', [])),
                'confidence': decision.get('confidence')
            })
            results['logged'] = True
            
            # Determine action based on recommendation
            recommendation = decision.get('recommendation', 'proceed_with_caution')
            red_flags = decision.get('red_flags', [])
            
            if recommendation == 'avoid' or len(red_flags) >= 3:
                results['action_taken'] = 'block_listing'
                results['warning_issued'] = True
                logger.warning(f"High-risk product detected: {len(red_flags)} red flags")
            elif recommendation == 'proceed_with_caution' or len(red_flags) > 0:
                results['action_taken'] = 'warn_user'
                results['warning_issued'] = True
                logger.info(f"Caution advised: {len(red_flags)} red flags found")
            else:
                results['action_taken'] = 'approve'
                logger.info("Product passed quality assessment")
            
        except Exception as e:
            logger.error(f"Error in QualityAgent.act(): {e}")
            results['error'] = str(e)
        
        return results
    
    async def assess_quality(
        self,
        product: Product,
        red_flags: Optional[List[str]] = None,
        positive_signals: Optional[List[str]] = None,
        description_quality: Optional[Dict] = None,
        title_quality: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive quality assessment using LLM and rule-based analysis.
        
        Args:
            product: Product to assess
            red_flags: List of detected red flags
            positive_signals: List of positive indicators
            description_quality: Description quality metrics
            title_quality: Title quality metrics
            
        Returns:
            Dictionary with assessment results:
                - quality_score: float (0-100)
                - quality_rating: str
                - red_flags: List[str]
                - positive_signals: List[str]
                - condition_assessment: str
                - seller_trustworthiness: float (0-1)
                - recommendation: str
                - confidence: float (0-1)
                - reasoning: str
        """
        red_flags = red_flags or []
        positive_signals = positive_signals or []
        description_quality = description_quality or {}
        title_quality = title_quality or {}
        
        # Calculate initial quality score
        base_score = 50.0
        
        # Adjust for red flags (each -10 points)
        base_score -= len(red_flags) * 10
        
        # Adjust for positive signals (each +5 points)
        base_score += len(positive_signals) * 5
        
        # Adjust for description quality
        if description_quality.get('is_detailed'):
            base_score += 10
        if description_quality.get('is_too_short'):
            base_score -= 15
        
        # Adjust for photos
        if getattr(product, 'image_url', None):
            base_score += 10
        else:
            base_score -= 20
        
        # Clamp score
        quality_score = max(0, min(100, base_score))
        
        # Determine initial rating
        if quality_score >= 80:
            initial_rating = 'excellent'
            initial_recommendation = 'safe_to_buy'
        elif quality_score >= 60:
            initial_rating = 'good'
            initial_recommendation = 'safe_to_buy'
        elif quality_score >= 40:
            initial_rating = 'fair'
            initial_recommendation = 'proceed_with_caution'
        elif quality_score >= 20:
            initial_rating = 'poor'
            initial_recommendation = 'proceed_with_caution'
        else:
            initial_rating = 'suspicious'
            initial_recommendation = 'avoid'
        
        # Build LLM prompt for deeper analysis
        prompt = self._build_quality_assessment_prompt(
            product=product,
            red_flags=red_flags,
            positive_signals=positive_signals,
            description_quality=description_quality,
            initial_score=quality_score,
            initial_rating=initial_rating
        )
        
        try:
            # Get LLM analysis using the generate method
            content = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent JSON
                max_tokens=500
            )
            
            # Extract JSON from response (handle markdown code blocks)
            llm_assessment = self._extract_json_from_response(content)
            
            # Merge LLM analysis with rule-based analysis
            assessment = {
                'quality_score': llm_assessment.get('quality_score', quality_score),
                'quality_rating': llm_assessment.get('quality_rating', initial_rating),
                'red_flags': red_flags,
                'positive_signals': positive_signals,
                'condition_assessment': llm_assessment.get('condition_assessment', 'unknown'),
                'seller_trustworthiness': llm_assessment.get('seller_trustworthiness', 0.5),
                'recommendation': llm_assessment.get('recommendation', initial_recommendation),
                'confidence': llm_assessment.get('confidence', 0.6),
                'reasoning': llm_assessment.get('reasoning', 'Rule-based analysis'),
                'scam_probability': llm_assessment.get('scam_probability', 0.0)
            }
            
            # Validate assessment
            if not self._validate_assessment(assessment):
                logger.warning("Invalid LLM assessment, using rule-based fallback")
                return self._get_rule_based_assessment(
                    product, quality_score, initial_rating, 
                    initial_recommendation, red_flags, positive_signals
                )
            
            return assessment
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_rule_based_assessment(
                product, quality_score, initial_rating,
                initial_recommendation, red_flags, positive_signals
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_rule_based_assessment(
                product, quality_score, initial_rating,
                initial_recommendation, red_flags, positive_signals
            )
    
    def _detect_red_flags(self, title: str, description: str) -> List[str]:
        """
        Detect red flags in title and description.
        
        Args:
            title: Product title
            description: Product description
            
        Returns:
            List of detected red flags
        """
        text = f"{title} {description}".lower()
        found_flags = []
        
        for keyword in self.RED_FLAG_KEYWORDS:
            if keyword in text:
                found_flags.append(keyword)
        
        # Additional pattern-based red flags
        if re.search(r'\b(wire|transfer|western\s+union)\b', text):
            found_flags.append('suspicious_payment_method')
        
        if re.search(r'\b(no\s+returns?|no\s+refunds?|as\s*-?\s*is)\b', text):
            found_flags.append('no_returns_policy')
        
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            found_flags.append('insufficient_description')
        
        # Check for excessive urgency
        urgency_words = ['urgent', 'hurry', 'quick', 'fast', 'now', 'today']
        urgency_count = sum(1 for word in urgency_words if word in text)
        if urgency_count >= 3:
            found_flags.append('excessive_urgency')
        
        return list(set(found_flags))  # Remove duplicates
    
    def _detect_positive_signals(self, title: str, description: str) -> List[str]:
        """
        Detect positive quality signals.
        
        Args:
            title: Product title
            description: Product description
            
        Returns:
            List of positive signals
        """
        text = f"{title} {description}".lower()
        found_signals = []
        
        for keyword in self.POSITIVE_KEYWORDS:
            if keyword in text:
                found_signals.append(keyword)
        
        # Additional positive patterns
        if re.search(r'\b(original\s+box|original\s+packaging)\b', text):
            found_signals.append('has_original_packaging')
        
        if re.search(r'\b(warranty|guaranteed)\b', text):
            found_signals.append('has_warranty')
        
        if re.search(r'\b(receipt|proof\s+of\s+purchase)\b', text):
            found_signals.append('has_receipt')
        
        if len(description) > 200:
            found_signals.append('detailed_description')
        
        return list(set(found_signals))
    
    def _assess_description_quality(self, description: str) -> Dict:
        """
        Assess description quality.
        
        Args:
            description: Product description
            
        Returns:
            Dictionary with quality metrics
        """
        length = len(description)
        word_count = len(description.split())
        
        return {
            'length': length,
            'word_count': word_count,
            'is_too_short': length < self.MIN_DESCRIPTION_LENGTH,
            'is_detailed': length > 200,
            'has_specifics': word_count > 30,
            'quality_level': 'good' if length > 200 else 'poor' if length < 50 else 'fair'
        }
    
    def _assess_title_quality(self, title: str) -> Dict:
        """
        Assess title quality.
        
        Args:
            title: Product title
            
        Returns:
            Dictionary with quality metrics
        """
        length = len(title)
        word_count = len(title.split())
        has_caps = title.isupper()
        
        return {
            'length': length,
            'word_count': word_count,
            'is_descriptive': word_count >= 4,
            'excessive_caps': has_caps,
            'quality_level': 'good' if 4 <= word_count <= 15 and not has_caps else 'poor'
        }
    
    def _build_quality_assessment_prompt(
        self,
        product: Product,
        red_flags: List[str],
        positive_signals: List[str],
        description_quality: Dict,
        initial_score: float,
        initial_rating: str
    ) -> str:
        """Build comprehensive prompt for LLM quality assessment."""
        
        title = str(getattr(product, 'title', ''))
        description = str(getattr(product, 'description', ''))
        platform = str(getattr(product, 'platform', ''))
        price = float(getattr(product, 'price', 0))
        has_image = bool(getattr(product, 'image_url', None))
        
        # Truncate for token efficiency
        title_short = title[:50]
        desc_short = description[:150]
        
        return f"""
Assess quality:
Title: {title_short}
Price: ${price} | Platform: {platform}
Score: {initial_score}/100 ({initial_rating})

Red flags: {', '.join(red_flags[:3]) if red_flags else 'None'}
Positive: {', '.join(positive_signals[:3]) if positive_signals else 'None'}
Desc: {desc_short}

Respond ONLY with JSON:

## Your Task
Provide a comprehensive quality assessment considering:

1. **Scam Indicators**: Look for common scam patterns
   - Vague descriptions
   - Pressure tactics
   - Suspicious payment requests
   - Too-good-to-be-true pricing

2. **Product Condition**: Assess likely condition
   - Honest about flaws?
   - Realistic description?
   - Appropriate for price?

3. **Seller Trustworthiness**: Evaluate seller signals
   - Communication style
   - Transparency
   - Professionalism
   - Red flags in behavior

4. **Overall Safety**: Should buyer proceed?
   - Safe to buy
   - Proceed with caution
   - Avoid

## Response Format
Respond in JSON:
{{
    "quality_score": 0-100,
    "quality_rating": "excellent" | "good" | "fair" | "poor" | "suspicious",
    "condition_assessment": "like_new" | "good" | "fair" | "poor" | "unknown",
    "seller_trustworthiness": 0.0-1.0,
    "scam_probability": 0.0-1.0,
    "recommendation": "safe_to_buy" | "proceed_with_caution" | "avoid",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of your assessment"
}}
"""
    
    def _validate_assessment(self, assessment: Dict) -> bool:
        """Validate quality assessment structure."""
        required_fields = [
            'quality_score', 'quality_rating', 'recommendation', 
            'confidence', 'seller_trustworthiness'
        ]
        
        if not all(field in assessment for field in required_fields):
            return False
        
        valid_ratings = ['excellent', 'good', 'fair', 'poor', 'suspicious']
        if assessment['quality_rating'] not in valid_ratings:
            return False
        
        valid_recommendations = ['safe_to_buy', 'proceed_with_caution', 'avoid']
        if assessment['recommendation'] not in valid_recommendations:
            return False
        
        if not (0 <= assessment['confidence'] <= 1):
            return False
        
        if not (0 <= assessment['seller_trustworthiness'] <= 1):
            return False
        
        return True
    
    def _get_rule_based_assessment(
        self,
        product: Product,
        quality_score: float,
        initial_rating: str,
        initial_recommendation: str,
        red_flags: List[str],
        positive_signals: List[str]
    ) -> Dict:
        """Fallback rule-based assessment when LLM fails."""
        
        # Calculate seller trustworthiness based on signals
        trust_score = 0.5
        trust_score -= len(red_flags) * 0.1
        trust_score += len(positive_signals) * 0.05
        trust_score = max(0.0, min(1.0, trust_score))
        
        # Calculate scam probability
        scam_prob = len(red_flags) * 0.15
        scam_prob = max(0.0, min(1.0, scam_prob))
        
        return {
            'quality_score': quality_score,
            'quality_rating': initial_rating,
            'red_flags': red_flags,
            'positive_signals': positive_signals,
            'condition_assessment': 'unknown',
            'seller_trustworthiness': trust_score,
            'recommendation': initial_recommendation,
            'confidence': 0.6,
            'reasoning': f'Rule-based analysis: {len(red_flags)} red flags, {len(positive_signals)} positive signals',
            'scam_probability': scam_prob
        }
    
    def _get_default_assessment(self) -> Dict:
        """Default assessment when analysis fails."""
        return {
            'quality_score': 50.0,
            'quality_rating': 'unknown',
            'red_flags': [],
            'positive_signals': [],
            'condition_assessment': 'unknown',
            'seller_trustworthiness': 0.5,
            'recommendation': 'proceed_with_caution',
            'confidence': 0.0,
            'reasoning': 'Insufficient data for assessment',
            'scam_probability': 0.5
        }

# Made with Bob
