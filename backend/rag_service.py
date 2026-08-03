import re
import math
from typing import List, Dict

class RAGService:
    def __init__(self):
        self.documents: List[Dict] = []

    def index_documents(self, docs: List[Dict]):
        """Indexes parsed opportunities into memory for RAG queries."""
        self.documents = docs

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def _calculate_relevance(self, query: str, doc: Dict) -> float:
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return 0.0

        doc_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('eligibility', '')} {doc.get('funding_amount', '')} {doc.get('summary', '')} {doc.get('content', '')} {doc.get('region', '')}"
        doc_tokens = self._tokenize(doc_text)

        match_count = sum(1 for token in query_tokens if token in doc_tokens)
        score = match_count / len(query_tokens)

        # Bonus for category matches or exact title matches
        if any(cat.lower() in query.lower() for cat in [doc.get('category', '').lower()]):
            score += 0.3
        if doc.get('region', '').lower() in query.lower():
            score += 0.2

        return score

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Performs semantic relevance search over indexed opportunities."""
        if not self.documents:
            return []

        scored_docs = []
        for doc in self.documents:
            score = self._calculate_relevance(query, doc)
            scored_docs.append((score, doc))

        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs if score > 0][:limit] or self.documents[:limit]

    def answer_query(self, user_query: str) -> Dict:
        """
        Generates a RAG-grounded conversational response with cited source listings.
        """
        relevant_items = self.search(user_query, limit=3)
        
        if not relevant_items:
            return {
                "answer": "I searched our intelligence database but couldn't find exact matches for your prompt. Try searching for terms like 'Scholarship', 'Germany', 'Remote Job', or 'AI Grant'.",
                "citations": []
            }

        # Build RAG synthesized response
        response_lines = [
            f"Here are the top matches I discovered from our live web intelligence crawl for your request ('*{user_query}*'):\n"
        ]

        citations = []
        for idx, item in enumerate(relevant_items, 1):
            title = item.get('title', 'Opportunity')
            cat = item.get('category', 'Listing')
            funding = item.get('funding_amount', 'N/A')
            deadline = item.get('deadline', 'N/A')
            source = item.get('source_name', 'Web')
            apply_url = item.get('apply_url', '#')
            summary = item.get('summary', '')

            response_lines.append(
                f"**{idx}. [{cat}] {title}**\n"
                f"• **Funding/Salary:** {funding}\n"
                f"• **Deadline:** {deadline}\n"
                f"• **Source:** {source}\n"
                f"• **Summary:** {summary[:180]}...\n"
            )

            citations.append({
                "title": title,
                "category": cat,
                "url": apply_url,
                "funding": funding,
                "deadline": deadline
            })

        response_lines.append("\n*Tip: You can click the application link on any listing card to apply directly!*")

        return {
            "answer": "\n".join(response_lines),
            "citations": citations
        }
