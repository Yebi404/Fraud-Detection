import os, json, math, time
import pandas as pd
import numpy as np

try:
    from tqdm import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable

try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except Exception:
    _GROQ_AVAILABLE = False


class VerifierConfig:
    # Adjusted thresholds to get realistic numbers: ~500 flags, ~20 denies
    # Based on analysis: ML scores range 0.013-0.890, ring scores are all ~0.81
    # Combined scores range 0.332-0.858, so we need thresholds around 0.50-0.70
    
    # ML score thresholds (primary differentiator)
    ml_score_flag = 0.50        # Flag transactions with ML score >= 0.50
    ml_score_deny = 0.70        # Deny transactions with ML score >= 0.70
    
    # Ring score thresholds (all scores are similar ~0.81, so keep high)
    ring_score_flag = 0.90      # High threshold since ring scores don't vary much
    ring_score_deny = 0.95      # Keep very high
    
    # Combined score thresholds - this is the key control
    combined_score_flag = 0.50   # Flag threshold based on analysis
    combined_score_deny = 0.70   # Deny threshold based on analysis
    
    velocity_window_steps = 6
    velocity_flag = 3
    velocity_deny = 10
    amount_hi_quantile = 0.99
    weight_ml = 0.6
    weight_ring = 0.4
    enable_llm = True
    llm_provider = "groq"  # NEW: Using Groq instead of Gemini
    llm_model_name = "llama-3.1-8b-instant"  # Fast and free
    llm_temperature = 0.3
    llm_max_tokens = 1000 # Increased from 160 to get fuller explanations
    # Batch processing configuration
    batch_size = 10  # Groq can handle more
    requests_per_minute = 25  # Groq free tier: 30 RPM, use 25 to be safe


class TransactionVerifierAgent:
    def __init__(self, ring_csv, ml_csv, output_json, blacklist_csv=None, cfg=None):
        self.ring_csv = ring_csv
        self.ml_csv = ml_csv
        self.output_json = output_json
        self.blacklist_csv = blacklist_csv
        self.cfg = cfg or VerifierConfig()
        self.daily_quota_file = "models/.llm_quota_tracker.json"

    def _load_quota_tracker(self):
        """Load today's API usage"""
        if not os.path.exists(self.daily_quota_file):
            return {"date": time.strftime("%Y-%m-%d"), "count": 0}
        
        try:
            with open(self.daily_quota_file, "r") as f:
                data = json.load(f)
                # Reset if it's a new day
                if data.get("date") != time.strftime("%Y-%m-%d"):
                    return {"date": time.strftime("%Y-%m-%d"), "count": 0}
                return data
        except:
            return {"date": time.strftime("%Y-%m-%d"), "count": 0}

    def _save_quota_tracker(self, count):
        """Save today's API usage"""
        os.makedirs(os.path.dirname(self.daily_quota_file), exist_ok=True)
        with open(self.daily_quota_file, "w") as f:
            json.dump({"date": time.strftime("%Y-%m-%d"), "count": count}, f)

    def _batch_llm_explanations(self, transactions_batch):
        """Generate explanations for multiple transactions in one API call"""
        prompt = (
            "You are a fraud analysis assistant. For each transaction below, provide a simple, user-friendly "
            "explanation (1-2 sentences) without technical jargon. Use plain language that anyone can understand.\n"
            "Explain what makes this transaction risky in everyday terms.\n\n"
            "Examples of good explanations:\n"
            "- 'This transaction looks unusual compared to your typical activity and may be linked to suspicious accounts.'\n"
            "- 'The transaction amount and timing don't match your usual spending patterns, suggesting potential fraud.'\n"
            "- 'This transaction is connected to accounts known for suspicious activity.'\n"
            "- 'Multiple unusual changes in your transaction behavior at once raise concerns about account security.'\n\n"
            "Avoid technical terms like 'ML score', 'ring score', 'statistical anomalies', 'network-based risk', etc.\n"
            "Instead use everyday language like 'unusual activity', 'suspicious patterns', 'atypical behavior', etc.\n\n"
            "Provide DIFFERENT explanations for each transaction based on the specific risk level - don't repeat the same message.\n\n"
            "Transactions to analyze:\n\n"
        )
        
        for row in transactions_batch:
            prompt += (
                f"Transaction {int(row['idx'])}:\n"
                f"  ml_score: {row['ml_score']:.3f}\n"
                f"  ring_score: {row['ring_score']:.3f}\n"
                f"  combined_score: {row['combined_score']:.3f}\n"
                f"  status: {row['status']}\n\n"
            )
        
        prompt += (
            "\nRespond with JSON array format:\n"
            '[{"idx": 994335, "explanation": "This transaction looks unusual compared to your typical activity..."}, '
            '{"idx": 2725849, "explanation": "The timing and amount of this transaction don\'t match your normal patterns..."}]\n'
            'IMPORTANT: Use the EXACT transaction idx numbers shown above, not 1, 2, 3!\n'
            'IMPORTANT: Provide different, user-friendly explanations for each transaction based on their risk patterns!\n'
            'IMPORTANT: Use simple language without technical terms like "ML score", "ring score", "statistical anomalies", etc.'
        )
        
        return prompt

    def run(self):
        # Read input files
        ring_df = pd.read_csv(self.ring_csv)
        ml_df = pd.read_csv(self.ml_csv)

        # Ensure ml_score exists
        if "ml_score" not in ml_df.columns:
            numeric_cols = ml_df.drop(columns=["idx"]).select_dtypes(include=[np.number])
            ml_df["ml_score"] = numeric_cols.mean(axis=1)

        # Create a combined ring_score
        if "ring_score_7d" in ring_df.columns and "ring_score_30d" in ring_df.columns:
            ring_df["ring_score"] = (ring_df["ring_score_7d"] + ring_df["ring_score_30d"]) / 2
        elif "ring_score_7d" in ring_df.columns:
            ring_df["ring_score"] = ring_df["ring_score_7d"]
        elif "ring_score_30d" in ring_df.columns:
            ring_df["ring_score"] = ring_df["ring_score_30d"]
        else:
            ring_df["ring_score"] = 0.0

        # Merge on 'idx'
        df = pd.merge(ring_df, ml_df, on="idx", how="inner")

        # Calculate combined score
        df["combined_score"] = (self.cfg.weight_ml * df["ml_score"] +
                                self.cfg.weight_ring * df["ring_score"])

        # Determine status based on combined score thresholds
        df["status"] = "pass"
        df.loc[df["combined_score"] >= self.cfg.combined_score_deny, "status"] = "deny"
        df.loc[df["combined_score"].between(self.cfg.combined_score_flag, self.cfg.combined_score_deny), "status"] = "flag"

        # Print status summary
        print("\n📊 Status Summary:")
        deny_count = sum(df["status"] == "deny")
        flag_count = sum(df["status"] == "flag")
        pass_count = sum(df["status"] == "pass")
        total = len(df)
        
        print(f"   • DENY: {deny_count} transactions ({deny_count/total*100:.2f}%)")
        print(f"   • FLAG: {flag_count} transactions ({flag_count/total*100:.2f}%)")
        print(f"   • PASS: {pass_count} transactions ({pass_count/total*100:.2f}%)")
        
        # Print score distribution
        print(f"\n📈 Score Distribution:")
        print(f"   ML Score    - Min: {df['ml_score'].min():.3f}, Max: {df['ml_score'].max():.3f}, Mean: {df['ml_score'].mean():.3f}")
        print(f"   Ring Score  - Min: {df['ring_score'].min():.3f}, Max: {df['ring_score'].max():.3f}, Mean: {df['ring_score'].mean():.3f}")
        print(f"   Combined    - Min: {df['combined_score'].min():.3f}, Max: {df['combined_score'].max():.3f}, Mean: {df['combined_score'].mean():.3f}")

        # Create explanations
        df["explanation"] = df.apply(
            lambda r: (f"Transaction {r['idx']} has ml_score={r['ml_score']:.2f}, "
                       f"ring_score={r['ring_score']:.2f}, "
                       f"combined_score={r['combined_score']:.2f}, status={r['status']}"), axis=1
        )

        # LLM explanations with GROQ
        df["llm_explanation"] = ""
        use_llm = bool(self.cfg.enable_llm)
        api_key = os.getenv("GROQ_API_KEY")

        if use_llm and _GROQ_AVAILABLE and api_key:
            needs_explanation = df[df["status"].isin(["flag", "deny"])].copy()
            llm_needed_count = len(needs_explanation)

            if llm_needed_count > 0:
                # Load quota tracker
                quota_data = self._load_quota_tracker()
                api_calls_today = quota_data["count"]
                max_daily_calls = 14400  # Groq free tier: 14,400 requests/day
                remaining_calls = max_daily_calls - api_calls_today

                print(f"🤖 Starting LLM explanation generation with Groq...")
                print(f"   Processing {llm_needed_count} transactions (flagged/denied only)")
                print(f"   Skipping {len(df) - llm_needed_count} passed transactions")
                print(f"   📊 API calls used today: {api_calls_today}/{max_daily_calls}")
                print(f"   📊 Remaining calls: {remaining_calls}")
                
                # Calculate how many we can process with batching
                estimated_batches = math.ceil(llm_needed_count / self.cfg.batch_size)
                print(f"   📦 Estimated API calls needed: {estimated_batches} (batch size: {self.cfg.batch_size})")
                if estimated_batches > remaining_calls:
                    print(f"   ⚠ Can only process ~{remaining_calls * self.cfg.batch_size} transactions today")

                try:
                    client = Groq(api_key=api_key)

                    success_count = 0
                    error_count = 0
                    skipped_count = 0
                    batch_count = 0
                    
                    print("=" * 70)

                    # Process in batches
                    transactions_list = needs_explanation.to_dict('records')
                    total_batches = math.ceil(len(transactions_list) / self.cfg.batch_size)
                    
                    # Calculate delay between requests to respect RPM
                    delay_between_requests = 60.0 / self.cfg.requests_per_minute

                    # Use tqdm for progress bar
                    for batch_idx in tqdm(range(0, len(transactions_list), self.cfg.batch_size), 
                                         desc="Processing batches", 
                                         total=total_batches,
                                         unit="batch"):
                        batch = transactions_list[batch_idx:batch_idx + self.cfg.batch_size]
                        batch_num = (batch_idx // self.cfg.batch_size) + 1
                        
                        # Check if we've hit daily quota
                        if api_calls_today >= max_daily_calls:
                            print(f"\n⚠ Daily quota limit reached ({max_daily_calls} calls)")
                            for txn in transactions_list[batch_idx:]:
                                idx = txn['idx']
                                df.at[idx, "llm_explanation"] = "[Quota exceeded - resume tomorrow]"
                                skipped_count += 1
                            break

                        # Generate batch prompt
                        prompt = self._batch_llm_explanations(batch)
                        
                        # Call Groq API with retry logic
                        response_text = None
                        max_retries = 3
                        backoff = 2.0
                        
                        for attempt in range(max_retries):
                            try:
                                chat_completion = client.chat.completions.create(
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": prompt,
                                        }
                                    ],
                                    model=self.cfg.llm_model_name,
                                    temperature=self.cfg.llm_temperature,
                                    max_tokens=self.cfg.llm_max_tokens,
                                )
                                response_text = chat_completion.choices[0].message.content
                                
                                # DEBUG: Print first batch details
                                if batch_num == 1:
                                    print("\n" + "="*70)
                                    print("🔍 DEBUG - FIRST BATCH PROCESSING")
                                    print("="*70)
                                    print(f"📝 Transactions in batch: {len(batch)}")
                                    for i, txn in enumerate(batch[:3], 1):  # Show first 3
                                        print(f"\n   Transaction {i}:")
                                        print(f"   • idx: {txn['idx']} (type: {type(txn['idx'])})")
                                        print(f"   • ml_score: {txn['ml_score']:.3f}")
                                        print(f"   • ring_score: {txn['ring_score']:.3f}")
                                        print(f"   • status: {txn['status']}")
                                    
                                    print(f"\n📤 Prompt sent to Groq (first 600 chars):")
                                    print(f"   {prompt[:600]}...")
                                    
                                    print(f"\n📥 Raw API Response (first 1500 chars):")
                                    print(f"   {response_text[:1500]}")
                                    print("\n📥 Full API Response:")
                                    print(f"   {response_text}")
                                    print("="*70 + "\n")
                                
                                if response_text:
                                    batch_count += 1
                                    api_calls_today += 1
                                    break
                            except Exception as e:
                                msg = str(e)
                                if "rate_limit" in msg.lower() or "429" in msg:
                                    if attempt < max_retries - 1:
                                        print(f"⏳ Rate limit hit, waiting {backoff}s... (attempt {attempt+1}/{max_retries})")
                                        time.sleep(backoff)
                                        backoff = min(backoff * 2.0, 30.0)
                                    else:
                                        print(f"❌ Rate limit persists after {max_retries} retries")
                                        response_text = None
                                        break
                                else:
                                    print(f"❌ API Error: {str(e)[:100]}")
                                    break
                        
                        # Parse batch response
                        if response_text:
                            try:
                                # Try to extract JSON from response
                                json_start = response_text.find('[')
                                json_end = response_text.rfind(']') + 1
                                if json_start >= 0 and json_end > json_start:
                                    explanations = json.loads(response_text[json_start:json_end])
                                    
                                    # Create mapping of idx to explanation
                                    expl_map = {}
                                    for expl in explanations:
                                        idx = expl.get('idx')
                                        text = expl.get('explanation', '')
                                        if idx is not None and text:
                                            # Handle both int and float idx
                                            expl_map[float(idx)] = text
                                    
                                    # Assign explanations to matching transactions
                                    for txn in batch:
                                        txn_idx = float(txn['idx'])
                                        if txn_idx in expl_map:
                                            df.loc[df['idx'] == txn_idx, 'llm_explanation'] = expl_map[txn_idx]
                                            success_count += 1
                                        else:
                                            # If no match, use generic response
                                            df.loc[df['idx'] == txn_idx, 'llm_explanation'] = response_text[:200]
                                            success_count += 1
                                    
                                    # DEBUG: Show results for first batch
                                    if batch_num == 1:
                                        print("\n🔍 DEBUG - PARSING RESULTS")
                                        print("="*70)
                                        print(f"✅ Parsed {len(expl_map)} explanations from JSON")
                                        print(f"📋 Explanation map keys: {list(expl_map.keys())[:5]}")
                                        print(f"\n💾 Checking first 3 transactions in DataFrame:")
                                        for i, txn in enumerate(batch[:3], 1):
                                            txn_idx = float(txn['idx'])
                                            stored_expl = df.loc[df['idx'] == txn_idx, 'llm_explanation'].values
                                            print(f"\n   Transaction {i} (idx={txn_idx}):")
                                            if len(stored_expl) > 0 and stored_expl[0]:
                                                print(f"   ✅ Explanation stored: {stored_expl[0][:100]}...")
                                            else:
                                                print(f"   ❌ No explanation stored!")
                                        print("="*70 + "\n")
                                else:
                                    # Fallback: assign same explanation to all in batch
                                    for txn in batch:
                                        df.loc[df['idx'] == float(txn['idx']), 'llm_explanation'] = response_text[:200]
                                        success_count += 1
                            except json.JSONDecodeError:
                                # Fallback: use raw response for all
                                for txn in batch:
                                    df.loc[df['idx'] == float(txn['idx']), 'llm_explanation'] = response_text[:200]
                                    success_count += 1
                        else:
                            for txn in batch:
                                df.loc[df['idx'] == float(txn['idx']), 'llm_explanation'] = "[API error or quota exceeded]"
                                error_count += 1

                        # Progress update every 5 batches
                        if batch_num % 5 == 0 or batch_num == total_batches:
                            processed = min(batch_idx + self.cfg.batch_size, len(transactions_list))
                            pct = (processed / llm_needed_count) * 100.0
                            est_remaining = ((llm_needed_count - processed) / self.cfg.batch_size) * delay_between_requests / 60.0
                            
                            print(f"\n✓ Progress: {processed}/{llm_needed_count} ({pct:.1f}%)")
                            print(f"  ✅ Success: {success_count} | ❌ Errors: {error_count} | ⏭ Skipped: {skipped_count}")
                            print(f"  📊 API calls today: {api_calls_today}/{max_daily_calls}")
                            print(f"  ⏱ Est. time remaining: {est_remaining:.1f} minutes")
                            print("-" * 70)
                        
                        # Respect rate limits
                        if batch_num < total_batches:
                            time.sleep(delay_between_requests)

                    # Save updated quota
                    self._save_quota_tracker(api_calls_today)

                    # Mark passed transactions
                    df.loc[df["status"] == "pass", "llm_explanation"] = "[Passed - no detailed explanation needed]"

                    print("=" * 70)
                    print(f"✅ LLM generation complete!")
                    print(f"   Total needed: {llm_needed_count}")
                    print(f"   ✅ Success: {success_count} | ❌ Errors: {error_count} | ⏭ Skipped: {skipped_count}")
                    print(f"   📊 API calls used today: {api_calls_today}/{max_daily_calls}")
                    if success_count > 0:
                        print(f"   Success Rate: {(success_count/llm_needed_count*100):.1f}%")
                    if skipped_count > 0:
                        print(f"   ⚠ Quota limit reached. Resume tomorrow to process remaining {skipped_count} transactions")
                    print("=" * 70)

                except Exception as e:
                    print(f"\n❌ LLM initialization failed: {e}")
                    df.loc[df["status"].isin(["flag", "deny"]), "llm_explanation"] = "[LLM unavailable]"
                    df.loc[df["status"] == "pass", "llm_explanation"] = "[Passed - no detailed explanation needed]"
            else:
                print("✅ No flagged or denied transactions - skipping LLM explanations")
                df["llm_explanation"] = "[Passed - no detailed explanation needed]"
        else:
            if use_llm:
                if not _GROQ_AVAILABLE:
                    print("⚠ LLM enabled but groq library not installed. Run: pip install groq")
                if not api_key:
                    print("⚠ LLM enabled but GROQ_API_KEY not set")
            df["llm_explanation"] = "[LLM disabled]"

        # Generate report
        report = {
            "meta": {
                "total": len(df),
                "deny": int(sum(df["status"] == "deny")),
                "flag": int(sum(df["status"] == "flag")),
                "pass": int(sum(df["status"] == "pass")),
            },
            "data": df[["idx", "status", "ml_score", "ring_score", "combined_score",
                        "explanation", "llm_explanation"]].to_dict(orient="records")
        }

        os.makedirs(os.path.dirname(self.output_json), exist_ok=True)
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return self.output_json