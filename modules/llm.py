import os
import google.generativeai as genai
from dotenv import load_dotenv
class GeminiClient:
    def __init__(self, api_key=None):
        # 1. Auth setup
        load_dotenv()
        self.api_key = os.environ["Gemini_API"]
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # using 2.5-flash model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            print("[WARN] No API Key provided. LLM disabled.")

    def extract_search_terms(self, user_query):
        """
        Extract the keywords from the query.
        """
        if not self.api_key:
            # Fallback if no key: just return the last word
            return [user_query.split()[-1]]
        # simple prompt to force keyword extraction
        prompt = f"""
        You are given a user query and your task is to analyze the query and extract list of suitable keywords that carries the significance of answering the query. Do not generate *uneccessary* *common* (such as : is,are,the,in,a,of,for etc.) keywords which poses no uniqueness in answering the query.
        Return *ONLY* the keywords separated by spaces. Do not explain.
        
        Question: {user_query}
        """

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            # cleaning up the response
            keywords = raw_text.lower().split()
            # removing punctuation 
            clean_keys = []
            for k in keywords:
                w = "".join([c for c in k if c.isalnum()])
                if w: 
                    clean_keys.append(w)
            return clean_keys

        except Exception as e:
            print(f"[WARN] Keyword extraction failed: {e}")
            return user_query.split()

    def query_with_context(self, user_query, retrieved_chunks):
        if not self.api_key:
            return "Error: API Key missing. Please config in sidebar."

        # 2. strict Check
        if not retrieved_chunks or len(retrieved_chunks.strip()) == 0:
            return "I could not find any relevant documents in the database to answer this question."
        # 3. prompt Engineering 
        # injecting retrieved C++ snippets into context with strict rules so that it does not hallucinate.
        prompt = f"""
        You are supposed answer only from the context given to you. Carefully *analyze* the context given to you and on the basis of that generate a full reponse (response length is decided on the amount of useful context regarding the query) using your analysis. Do not add extra information which is not provided to you through context.
        
        Context:
        {retrieved_chunks}
        
        Question: {user_query}
        """

        try:
            # 4. generation
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"[ERROR] Gemini API Failed: {e}"