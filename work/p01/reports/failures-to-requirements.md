**Test:** test_scores_found_and_missed_facts.  
**Failing because:** score_summary stub  
**PROJECT.md requirement:** Step 3: Complete automatic scoring  
**File to implement:** evaluate.py
_______________________________________________________

**Test:** test_flags_only_supplied_forbidden_phrases.  
**Failing because:** score_summary stub  
**PROJECT.md requirement:** Step 3: Complete automatic scoring  
**File to implement:** evaluate.py
_______________________________________________________

**Test:** test_responses_skips_non_message_items_and_preserves_usage.  
**Failing because:** normalize_openai_responses stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Responses output items  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_missing_text_is_explicit[normalize_openai_responses-payload0].  
**Failing because:** normalize_openai_responses stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Responses output items  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_chat_extracts_message_content.  
**Failing because:** normalize_openai_chat stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Chat Completions message content  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_missing_text_is_explicit[normalize_openai_chat-payload1].  
**Failing because:** normalize_openai_chat stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Chat Completions message content  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_anthropic_joins_all_text_blocks.  
**Failing because:** normalize_anthropic_messages stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Anthropic content blocks  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_missing_text_is_explicit[normalize_anthropic_messages-payload2].  
**Failing because:** normalize_anthropic_messages stub  
**PROJECT.md requirement:** Step 2: Offline normalization — Anthropic content blocks  
**File to implement:** normalize.py
_______________________________________________________

**Test:** test_offline_experiment_runs_all_fixture_records.  
**Failing because:** run_offline depends on all three normalize_* functions and score_summary  
**PROJECT.md requirement:** Steps 2 and 3 combined — no separate code, resolves once normalize.py and evaluate.py are implemented  
**File to implement:** experiment.py (no changes needed directly)
_______________________________________________________
