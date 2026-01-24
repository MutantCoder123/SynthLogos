import subprocess
import os
import platform

class EngineBridge:
    def __init__(self):
        # 1. get the Absolute Path to the backend folder
        base_path = os.getcwd()
        self.backend_dir = os.path.join(base_path, "backend")
        # 2. define the Engine Path
        if platform.system() == "Windows":
            self.engine_path = os.path.join(self.backend_dir, "engine.exe")
        else:
            self.engine_path = os.path.join(self.backend_dir, "engine")
        # 3. validation
        if not os.path.exists(self.engine_path):
            print(f"[CRITICAL WARNING] Engine NOT found at: {self.engine_path}")
            print("Please check if 'engine.exe' is inside the 'backend' folder.")

    def search(self, query, llm_client=None):
        # 2. Neuro-Symbolic Step: get keywords
        if llm_client:
            keywords = llm_client.extract_search_terms(query)
            print(f"[DEBUG] AI decided to search for: {keywords}")
        else:
            # fallback: Manual split
            raw = query.lower().split()
            keywords = [w for w in raw]

        aggregated_results = []
        
        # 3. run C++ Engine for each keyword
        for word in keywords:
            raw_output = self._run_single_search(word)
            # parse and add to results
            parsed_batch = self._parse_output(raw_output)
            aggregated_results.extend(parsed_batch)
        
        return aggregated_results, keywords

    def _run_single_search(self, keyword):
        try:
            result = subprocess.run(
                [self.engine_path, "--query", keyword],
                cwd=self.backend_dir, 
                capture_output=True,
                check=True
            )
            return result.stdout.decode('utf-8', errors='ignore')
            
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            print(f"Engine Error: {err}")
            return ""
        except Exception as e:
            print(f"Bridge Error: {e}")
            return ""

    def _parse_output(self, raw_output):
        res = []
        if not raw_output:
            return res
            
        lines = [line for line in raw_output.strip().split("\n") if line.strip()]
        
        for line in lines:
            try:
                parts = line.split("|")
                # expecting: File | Score | Snippet | Keyword
                if len(parts) >= 4:
                    res.append({
                        "file": parts[0].strip(),
                        "score": parts[1].strip(),
                        "snippet": parts[2].strip(),
                        "keyword": parts[3].strip()
                    })
                # legacy support (3 parts)
                elif len(parts) == 3:
                     res.append({
                        "file": parts[0].strip(),
                        "score": parts[1].strip(),
                        "snippet": parts[2].strip(),
                        "keyword": "unknown"
                    })
            except Exception as e:
                print(f"Parsing Error on line: {line} -> {e}")
                continue
                
        return res