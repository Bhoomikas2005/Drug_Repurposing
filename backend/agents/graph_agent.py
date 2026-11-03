import csv
import networkx as nx
import os

class GraphAgent:
    def __init__(self, drug_gene_path="data/drug_gene.csv", gene_disease_path="data/gene_disease.csv"):
        self.dg_path = drug_gene_path
        self.gd_path = gene_disease_path
        self.G = nx.Graph()
        self.load_data()

    def load_data(self):
        if os.path.exists(self.dg_path) and os.path.exists(self.gd_path):
            # Build Knowledge Graph
            with open(self.dg_path, newline="", encoding="utf-8") as drug_gene_file:
                for row in csv.DictReader(drug_gene_file):
                    u, v = row['drug'], row['gene']
                    self.G.add_node(u, type="drug")
                    self.G.add_node(v, type="gene")
                    self.G.add_edge(u, v, weight=1, interaction=row['interaction'])

            with open(self.gd_path, newline="", encoding="utf-8") as gene_disease_file:
                for row in csv.DictReader(gene_disease_file):
                    u, v = row['gene'], row['disease']
                    self.G.add_node(u, type="gene")
                    self.G.add_node(v, type="disease")
                    self.G.add_edge(u, v, weight=1, association=row['association'])
        else:
            print("CSV datasets not found in data/")

    def build_evidence_graph(self, papers):
        graph = self.G.copy()
        node_index = {
            (data.get("type", "entity"), str(node).casefold()): node
            for node, data in graph.nodes(data=True)
        }

        def resolve_node(label, node_type):
            label = str(label).strip()
            if not label:
                return None
            key = (node_type, label.casefold())
            if key not in node_index:
                node_index[key] = label
                graph.add_node(label, type=node_type)
            return node_index[key]

        def add_evidence_edge(left, right, paper_id, attribute):
            if not left or not right:
                return
            edge = graph.get_edge_data(left, right, default={}).copy()
            paper_ids = set(edge.get("papers", []))
            if paper_id:
                paper_ids.add(paper_id)
            edge["papers"] = sorted(paper_ids)
            edge["weight"] = max(edge.get("weight", 1), len(paper_ids), 1)
            edge[attribute] = "reported in paper"
            graph.add_edge(left, right, **edge)

        for paper in papers:
            paper_id = paper.get("id")
            drugs = [resolve_node(name, "drug") for name in paper.get("drugs", [])]
            genes = [resolve_node(name, "gene") for name in paper.get("genes", [])]
            diseases = [resolve_node(name, "disease") for name in paper.get("diseases", [])]

            for drug in drugs:
                for gene in genes:
                    add_evidence_edge(drug, gene, paper_id, "interaction")
            for gene in genes:
                for disease in diseases:
                    add_evidence_edge(gene, disease, paper_id, "association")

        return graph

    def suggest_drugs(self, disease_name):
        suggestions = []
        if disease_name not in self.G:
            return suggestions
            
        # Traverse disease -> gene -> drug
        genes = [n for n in self.G.neighbors(disease_name) if self.G.nodes[n].get('type') == 'gene']
        
        for gene in genes:
            drugs = [n for n in self.G.neighbors(gene) if self.G.nodes[n].get('type') == 'drug']
            for drug in drugs:
                # Find interaction details
                interaction = self.G[drug][gene].get('interaction', 'affects')
                association = self.G[gene][disease_name].get('association', 'linked to')
                
                explanation = f"Drug {drug} {interaction} Gene {gene} {association} Disease {disease_name}"
                
                # Check for existing
                existing = next((item for item in suggestions if item["drug"] == drug), None)
                if not existing:
                    suggestions.append({
                        "drug": drug,
                        "score": 0.85, # Base score
                        "confidence": "High",
                        "explanation": explanation,
                        "path": f"{drug} -> {gene} -> {disease_name}",
                        "involved_nodes": [drug, gene, disease_name],
                        "clinical_trial": True,
                        "breakdown": explanation
                    })
        
        return suggestions

    def get_graph_data(self, disease_name=None, hops=2, graph=None):
        graph = graph or self.G
        if not disease_name or disease_name not in graph:
            # Return a small sample or empty if no disease context
            nodes = [{"id": n, "label": n, "type": graph.nodes[n].get("type", "entity")} for n in list(graph.nodes)[:50]]
            node_ids = {node["id"] for node in nodes}
            edges = [{"from": u, "to": v, "weight": d.get("weight", 1)} for u, v, d in graph.edges(data=True) if u in node_ids and v in node_ids]
            return {"nodes": nodes, "edges": edges}

        # Get subgraph of nodes within N hops
        relevant_nodes = {disease_name}
        for _ in range(hops):
            neighbors = set()
            for node in relevant_nodes:
                neighbors.update(graph.neighbors(node))
            relevant_nodes.update(neighbors)

        subG = graph.subgraph(relevant_nodes)
        nodes = [{"id": n, "label": n, "type": subG.nodes[n].get("type", "entity")} for n in subG.nodes]
        edges = [{"from": u, "to": v, "weight": d.get("weight", 1)} for u, v, d in subG.edges(data=True)]
        return {"nodes": nodes, "edges": edges}
