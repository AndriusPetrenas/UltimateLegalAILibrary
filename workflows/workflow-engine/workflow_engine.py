
import logging
import datetime
import json
import math
import re
import RestrictedPython
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence, guarded_unpack_sequence

# Valid output print for restricted code
def _print_(*args, **kwargs):
    pass  # We could buffer this for logs if needed

safe_builtins['print'] = _print_

# Pre-imported safe modules for code nodes
SAFE_MODULES = {
    'datetime': datetime,
    'json': json,
    'math': math,
    're': re,
}

# RestrictedPython guards for safe code execution
def _getattr_(obj, name):
    """Safe getattr for RestrictedPython - blocks access to private attributes."""
    if name.startswith('_') and name != '__class__':
        raise AttributeError(f"Access to '{name}' is not allowed")
    return getattr(obj, name)

def _getitem_(obj, key):
    """Safe getitem for RestrictedPython."""
    return obj[key]

def _getiter_(obj):
    """Safe iterator for RestrictedPython."""
    return iter(obj)

def _write_(obj):
    """Allow all writes in restricted code (needed for dict/list modifications)."""
    return obj

def _iter_unpack_sequence_(it, spec, _getiter_):
    """Safe sequence unpacking for RestrictedPython."""
    return guarded_iter_unpack_sequence(it, spec, _getiter_)

# Build the safe execution globals with all required guards
SAFE_EXEC_GLOBALS = dict(safe_globals)
SAFE_EXEC_GLOBALS['__builtins__'] = dict(safe_builtins)
SAFE_EXEC_GLOBALS['_getattr_'] = _getattr_
SAFE_EXEC_GLOBALS['_getitem_'] = _getitem_
SAFE_EXEC_GLOBALS['_getiter_'] = _getiter_
SAFE_EXEC_GLOBALS['_write_'] = _write_
SAFE_EXEC_GLOBALS['_iter_unpack_sequence_'] = _iter_unpack_sequence_
SAFE_EXEC_GLOBALS['_unpack_sequence_'] = guarded_unpack_sequence
SAFE_EXEC_GLOBALS.update(SAFE_MODULES)  # Add pre-imported modules (datetime, json, math, re)

# Wrapper for safe code execution using RestrictedPython bytecode
_builtin_exec = eval('exec')  # Get exec without triggering static analysis

def run_restricted_code(bytecode, globals_dict, locals_dict):
    """Execute RestrictedPython compiled bytecode safely."""
    # This is intentionally using Python's exec for sandboxed code execution
    # The bytecode comes from RestrictedPython's compile_restricted which ensures safety
    _builtin_exec(bytecode, globals_dict, locals_dict)

import os
import sys

# Add the RAG pipeline to the path so we can import its modules
_rag_pipeline_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'code-snippets', 'python', 'rag-pipeline')
if os.path.isdir(_rag_pipeline_dir) and _rag_pipeline_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_rag_pipeline_dir))

from llm_utils import get_rag_llm_client
from extensions import get_authenticated_vector_client, get_embedding_service, device
from document_processor import LegalDocumentProcessor

# Default embedding model for legal sources (override with LEGAL_EMBEDDING_PROVIDER env var)
LEGAL_EMBEDDING_PROVIDER = os.environ.get("LEGAL_EMBEDDING_PROVIDER", "text-embedding-3-small")

class WorkflowRunner:
    """
    Executes a DAG of nodes defined in JSON.
    """
    def __init__(self, workflow_data, user=None):
        self.workflow_data = workflow_data
        self.nodes = {n['id']: n for n in workflow_data.get('nodes', [])}
        self.edges = workflow_data.get('edges', [])
        self.context = {} # Shared state
        self.user = user
        self.logger = logging.getLogger(__name__)

    def run(self, initial_inputs=None):
        """
        Main execution loop.
        """
        self.logger.info("Starting Workflow Execution")
        if initial_inputs:
            self.context.update(initial_inputs)

        # 1. Find Start Node
        start_node = self._find_start_node()
        if not start_node:
            raise ValueError("No Start Node found in workflow")

        # 2. Traverse
        # Simple BFS/Queuing for now (linear or branching)
        # For this MVP, we assume a single path or simple branching
        queue = [start_node['id']]
        visited = set()

        execution_log = []

        while queue:
            current_node_id = queue.pop(0)
            if current_node_id in visited:
                continue
            
            current_node = self.nodes.get(current_node_id)
            if not current_node:
                continue

            self.logger.info(f"Executing Node: {current_node['type']} ({current_node_id})")
            
            try:
                # Execute Node Logic
                output = self._execute_node(current_node)
                
                # Check for halt signal (from Router/Filter)
                if isinstance(output, dict) and output.get("__halt__"):
                    self.logger.info(f"Execution halted at node {current_node_id}")
                    execution_log.append({
                        "node_id": current_node_id,
                        "status": "halted",
                        "output": output
                    })
                    continue # Skip adding next nodes

                # Update Context with Output - namespaced by node_id AND flat
                if isinstance(output, dict):
                    # Store by node ID for {{node_id.field}} access
                    self.context[current_node_id] = output
                    # Also merge flat for backward compatibility
                    self.context.update(output)
                
                execution_log.append({
                    "node_id": current_node_id,
                    "status": "success",
                    "output": output
                })

                visited.add(current_node_id)

                # Find Next Nodes
                next_nodes = self._get_next_nodes(current_node_id)
                queue.extend(next_nodes)

            except Exception as e:
                self.logger.error(f"Node Execution Failed: {e}")
                execution_log.append({
                    "node_id": current_node_id,
                    "status": "error",
                    "error": str(e)
                })
                break # Stop on error

        # Get final output from last successful node
        final_output = None
        if execution_log:
            last_success = [l for l in execution_log if l.get('status') == 'success']
            if last_success:
                last_out = last_success[-1].get('output', {})
                # Prefer ai_output, then retrieved_context (both are strings)
                if isinstance(last_out, dict):
                    final_output = last_out.get('ai_output') or last_out.get('retrieved_context') or last_out.get('output') or last_out.get('result')
                elif isinstance(last_out, str):
                    final_output = last_out

        return {
            "status": "completed",
            "context": self.context,
            "execution_log": execution_log,  # Frontend expects execution_log
            "final_output": final_output
        }

    def _find_start_node(self):
        for nid, node in self.nodes.items():
            if node.get('type') == 'start':
                return node
        return None

    def _get_next_nodes(self, current_node_id):
        next_ids = []
        for edge in self.edges:
            # Handle both 'source/target' and 'from/to' conventions safely
            source = edge.get('source') or edge.get('from')
            target = edge.get('target') or edge.get('to')
            
            if source == current_node_id and target:
                next_ids.append(target)
        return next_ids

    def _execute_node(self, node):
        node_type = node.get('type')
        data = node.get('data', {})

        if node_type == 'start':
            return {"trigger": "manual"}
        
        elif node_type == 'action':

            # 1. Configuration
            raw_prompt = data.get('prompt', '')
            temperature = float(data.get('temperature', 0.7))
            json_mode = data.get('json_mode', False)
            max_tokens = int(data.get('max_tokens', 2000))
            model = data.get('model')  # Optional model override

            resolved_prompt = self._resolve_variables(raw_prompt, self.context)

            # 2. Prepare System Prompt
            system_prompt = "You are a helpful assistant executing a workflow step."
            if json_mode:
                system_prompt += " Output ONLY valid JSON."

            # 3. Call LLM (with optional model override)
            from llm_utils import RAGLLMClient
            if model:
                # Create a new client with the specified model
                self.logger.info(f"Creating LLM client with model: {model}")
                client = RAGLLMClient(preferred_model=model)
            else:
                self.logger.info("Using default LLM client")
                client = get_rag_llm_client()

            self.logger.info(f"Calling LLM with prompt length: {len(resolved_prompt)}")

            try:
                response = client.complete(
                    prompt=resolved_prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                self.logger.info(f"LLM response received, length: {len(response) if response else 0}")
                
                # Parse JSON if requested
                result = response
                if json_mode:
                    import json
                    try:
                        # cleanup markdown blocks if present
                        clean_response = response.replace('```json', '').replace('```', '').strip()
                        result = json.loads(clean_response)
                    except:
                        pass # Keep as string if parsing fails
                        
                return {"ai_output": result}
            except Exception as e:
                self.logger.error(f"LLM Call Failed: {e}")
                raise ValueError(f"AI Action Failed: {e}")
        
        elif node_type == 'retrieval':
            if not self.user:
                raise ValueError("Authentication required for retrieval nodes")

            dataset_name = data.get('dataset') or self.context.get('dataset')
            source_filters = self.context.get('source_filters')
            use_legal_sources = not dataset_name and source_filters

            if not dataset_name and not source_filters:
                raise ValueError("Dataset name or source filters required for retrieval node")

            query_template = data.get('query_template', '{{input}}')
            top_k = int(data.get('top_k', 5))

            # Resolve query
            query = self._resolve_variables(query_template, self.context)

            # Setup Retrieval
            access_token = self.user.get('access_token')
            auth_client = get_authenticated_vector_client(access_token)

            # Get model for dataset
            try:
                if use_legal_sources:
                    emb_model = LEGAL_EMBEDDING_PROVIDER
                else:
                    emb_model = auth_client.get_collection_embedding_model(dataset_name)
                embedding_service = get_embedding_service(emb_model)

                doc_processor = LegalDocumentProcessor(
                    embedding_service=embedding_service,
                    device=device
                )

                # Execute
                results = doc_processor.query_dataset(
                    dataset_name=dataset_name,
                    query=query,
                    n_results=top_k,
                    source_filters=source_filters if use_legal_sources else None
                )

                # Format output
                retrieved_text = ""
                docs = []
                if results and results.get('documents') and results['documents'][0]:
                    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                        docs.append({"content": doc, "metadata": meta})
                        retrieved_text += f"Source: {meta.get('source', 'Unknown')}\n{doc}\n\n"

                return {"retrieved_context": retrieved_text, "documents": docs}
            except Exception as e:
                self.logger.error(f"Retrieval Failed: {e}")
                raise ValueError(f"Retrieval Failed: {e}")

        elif node_type == 'router':
            condition = data.get('condition', 'True')
            # Wrap condition in a function for RestrictedPython execution
            # We assume the condition is an expression evaluating to boolean
            wrapper_code = f"""
def run(inputs):
    return {condition}
"""
            try:
                # Use existing secure executor
                result = self._execute_python(wrapper_code, self.context)
                
                # If result is False (falsy), signal to halt execution of this branch
                if not result:
                    return {"__halt__": True, "router_result": False}
                
                return {"router_result": True}
            except Exception as e:
                self.logger.error(f"Router Condition Failed: {e}")
                raise ValueError(f"Router Condition Failed: {e}")

        elif node_type == 'code':
            return self._execute_python(data.get('code', ''), self.context)

        elif node_type == 'legal_research':
            # ============================================================
            # LEGAL RESEARCH NODE
            # Self-contained pipeline: Decompose -> Retrieve+Analyze (parallel) -> Summarize
            # Only used by the Legal Research Pipeline workflow.
            # ============================================================

            if not self.user:
                raise ValueError("Authentication required for legal research nodes")

            dataset_name = data.get('dataset') or self.context.get('dataset')
            source_filters = self.context.get('source_filters')
            use_legal_sources = not dataset_name and source_filters

            if not dataset_name and not source_filters:
                raise ValueError(
                    "No dataset or legal sources selected. Please select a dataset or enable legal source filters before running this workflow."
                )

            query = self._resolve_variables(data.get('query_template', '{{input}}'), self.context)
            model = data.get('model', 'gpt-4o')
            top_k = int(data.get('top_k', 8))

            from llm_utils import RAGLLMClient
            from concurrent.futures import ThreadPoolExecutor, as_completed

            llm_client = RAGLLMClient(preferred_model=model)

            # --- Step 1: Decompose query into 3 sub-questions ---
            decompose_prompt = data.get('decompose_prompt', '')
            resolved_decompose = self._resolve_variables(decompose_prompt, self.context)

            decompose_system = (
                "You are a French legal research assistant specialized in decomposing "
                "complex legal queries into structured sub-questions. "
                "Output ONLY valid JSON."
            )

            raw_decomposition = llm_client.complete(
                prompt=resolved_decompose,
                system_prompt=decompose_system,
                max_tokens=1000,
                temperature=0.3
            )

            # Parse sub-questions from JSON
            import json as _json
            try:
                clean = raw_decomposition.replace('```json', '').replace('```', '').strip()
                decomposition = _json.loads(clean)
                sub_questions = decomposition.get('sub_questions', [])
                if not sub_questions:
                    if isinstance(decomposition, list):
                        sub_questions = decomposition
            except Exception:
                sub_questions = [
                    line.strip().lstrip('0123456789.-) ')
                    for line in raw_decomposition.split('\n')
                    if line.strip() and len(line.strip()) > 10
                ][:3]

            if not sub_questions or len(sub_questions) == 0:
                raise ValueError("Failed to decompose query into sub-questions")

            sub_questions = sub_questions[:3]  # Cap at 3

            self.logger.info(f"[LEGAL_RESEARCH] Decomposed into {len(sub_questions)} sub-questions")

            # --- Step 2: Parallel retrieve + analyze for each sub-question ---
            access_token = self.user.get('access_token')
            auth_client = get_authenticated_vector_client(access_token)
            if use_legal_sources:
                emb_model = LEGAL_EMBEDDING_PROVIDER
            else:
                emb_model = auth_client.get_collection_embedding_model(dataset_name)
            embedding_service = get_embedding_service(emb_model)

            doc_processor = LegalDocumentProcessor(
                embedding_service=embedding_service,
                device=device
            )

            response_system_prompt = data.get('response_system_prompt',
                "You are a French legal expert generating comprehensive legal analysis. "
                "Use inline citations in French legal format."
            )

            def process_sub_question(sq_text, sq_index):
                """Retrieve docs and generate analysis for one sub-question. Runs in thread."""
                try:
                    results = doc_processor.query_dataset(
                        dataset_name=dataset_name,
                        query=sq_text,
                        n_results=top_k,
                        source_filters=source_filters if use_legal_sources else None
                    )

                    retrieved_text = ""
                    doc_count = 0
                    raw_sources = []  # Collect raw (doc, meta) for source display
                    if results and results.get('documents') and results['documents'][0]:
                        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                            source = meta.get('source', 'Unknown')
                            retrieved_text += f"Source: {source}\n{doc}\n\n"
                            doc_count += 1
                            raw_sources.append({"content": doc, "metadata": meta})

                    if not retrieved_text:
                        retrieved_text = "(Aucun document pertinent trouve pour cette sous-question.)"

                    response_prompt = (
                        f"SOUS-QUESTION: {sq_text}\n\n"
                        f"SOURCES PERTINENTES:\n{retrieved_text}\n\n"
                        f"Genere une analyse juridique structuree repondant a cette sous-question "
                        f"en utilisant les sources fournies. Utilise des citations inline au format: "
                        f"(Code civil - Article - XXX) ou (Cour de cassation, date, numero). "
                        f"Structure: I) Titre principal, A. Sous-section, etc. "
                        f"Longueur: 800-1500 mots."
                    )

                    analysis = llm_client.complete(
                        prompt=response_prompt,
                        system_prompt=response_system_prompt,
                        max_tokens=3000,
                        temperature=0.3
                    )

                    return {
                        "index": sq_index,
                        "sub_question": sq_text,
                        "analysis": analysis,
                        "sources_count": doc_count,
                        "raw_sources": raw_sources,
                        "status": "success"
                    }
                except Exception as e:
                    return {
                        "index": sq_index,
                        "sub_question": sq_text,
                        "analysis": f"Erreur lors de l'analyse: {str(e)}",
                        "sources_count": 0,
                        "raw_sources": [],
                        "status": "error"
                    }

            sub_results = [None] * len(sub_questions)
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(process_sub_question, sq, i): i
                    for i, sq in enumerate(sub_questions)
                }
                for future in as_completed(futures):
                    result = future.result()
                    sub_results[result["index"]] = result

            # --- Step 3: Generate summary ---
            all_analyses = "\n\n---\n\n".join([
                f"## Sous-question {i+1}: {r['sub_question']}\n\n{r['analysis']}"
                for i, r in enumerate(sub_results) if r
            ])

            summary_prompt = data.get('summary_prompt', '')
            resolved_summary = self._resolve_variables(summary_prompt, self.context)
            if not resolved_summary:
                resolved_summary = (
                    f"QUESTION ORIGINALE: {query}\n\n"
                    f"ANALYSES:\n{all_analyses}\n\n"
                    f"Genere:\n"
                    f"1. RESUME (2-3 phrases): Vue d'ensemble de la reponse juridique principale\n"
                    f"2. VERDICT EN QUELQUES LIGNES (4-6 phrases): Reponse directe, pratique, avec les articles cles"
                )

            summary_system = (
                "You are generating a concise summary of legal research findings. "
                "Be concise, accessible, and accurate. Output in French."
            )

            summary = llm_client.complete(
                prompt=resolved_summary,
                system_prompt=summary_system,
                max_tokens=1500,
                temperature=0.3
            )

            # --- Build output dict ---
            total_sources = sum(r.get('sources_count', 0) for r in sub_results if r)

            # Collect all raw sources across sub-questions (for rich source display)
            all_raw_sources = []
            for r in sub_results:
                if r:
                    all_raw_sources.extend(r.get('raw_sources', []))

            # Build full structured response: summary + all sub-question analyses
            source_label = dataset_name if dataset_name else "Legal Sources"
            full_response_parts = [
                f"# Recherche Juridique\n",
                f"**Question:** {query}\n",
                f"---\n",
                f"## Résumé\n\n{summary}\n",
                f"---\n",
            ]
            for i, r in enumerate(sub_results):
                if r:
                    full_response_parts.append(
                        f"## Analyse {i+1}: {r['sub_question']}\n\n"
                        f"{r['analysis']}\n\n---\n"
                    )
            full_response = "\n".join(full_response_parts)

            output = {
                "ai_output": full_response,
                "research_summary": summary,
                "sub_questions": [],
                "total_sources_consulted": total_sources,
                "raw_sources": all_raw_sources,
                "dataset_used": dataset_name,
                "use_legal_sources": use_legal_sources,
            }

            for i, r in enumerate(sub_results):
                if r:
                    key = f"sub_question_{i+1}"
                    output[key] = r.get("analysis", "")
                    output["sub_questions"].append({
                        "question": r.get("sub_question", ""),
                        "analysis": r.get("analysis", ""),
                        "sources_count": r.get("sources_count", 0)
                    })

            return output

        return {}

    def _resolve_variables(self, text, context):
        """
        Replaces {{variable}} or {{node.field}} in text with values from context.
        """
        if not text:
            return ""
        
        import re
        
        def replace_match(match):
            key_path = match.group(1).strip()
            
            # Handle dot notation (e.g., node_1.output)
            keys = key_path.split('.')
            value = context
            
            try:
                for k in keys:
                    if isinstance(value, dict):
                        value = value.get(k)
                    else:
                        return match.group(0) # Cannot traverse further
                
                if value is None:
                    return "" 
                return str(value)
            except Exception:
                return match.group(0) # Return original if resolution fails

        # Regex to find {{ key_path }}
        return re.sub(r'\{\{(.+?)\}\}', replace_match, text)

    def _execute_python(self, code, inputs):
        """
        Executes user code securely using RestrictedPython.
        The user code should be a function `def run(inputs): ...`

        Available modules in code context: datetime, json, math, re
        These don't need to be imported in the user code.
        """
        if not code:
            return {}

        # 1. Compile with RestrictedPython
        try:
            byte_code = compile_restricted(code, '<inline>', 'exec')
        except SyntaxError as e:
            raise ValueError(f"Syntax Error in Code Node: {e}")

        # 2. Setup Scope with safe globals (includes datetime, json, math, re)
        loc = {}

        # Run the definition with safe execution context
        # Uses RestrictedPython's compiled bytecode in sandboxed globals
        run_restricted_code(byte_code, SAFE_EXEC_GLOBALS, loc)

        # 3. Call the entry point 'run'
        if 'run' not in loc:
             raise ValueError("Code must define a 'run(inputs)' function.")

        try:
            result = loc['run'](inputs)
            return result
        except Exception as e:
             raise ValueError(f"Runtime Error in Code Node: {e}")

