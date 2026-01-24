import networkx as nx
import matplotlib.pyplot as plt

class GraphVisualizer:
    def __init__(self):
        # using DiGraph (Directed Graph) to show flow from Query to Docs
        self.G = nx.DiGraph()

    def build_from_results(self, query, results):
        self.G.clear()
        short_q = query[:20] + "..." if len(query) > 20 else query
        self.G.add_node(short_q, color="#F90734", label="Query")

        for item in results:
            doc_name = item['file']
            score = float(item['score']) 
            # get the keyword that found this
            new_keyword = item.get('keyword','match')
            self.G.add_node(doc_name, color="#FF8800", label="Doc")
            
            if self.G.has_edge(short_q, doc_name):
                edge_data = self.G[short_q][doc_name]
                current_label = edge_data.get('label', '')
                # Check if this keyword is already listed to avoid duplicates
                if new_keyword not in current_label:
                    updated_label = f"{current_label}, {new_keyword}"
                    # update the edge
                    self.G[short_q][doc_name]['label'] = updated_label
                    # update the weight to the HIGHEST score found
                    if score > edge_data['weight']:
                         self.G[short_q][doc_name]['weight'] = score
            else:
                # if edge doesn't exist add one
                self.G.add_edge(short_q, doc_name, weight=score, label=new_keyword)

    def render(self):
        if self.G.number_of_nodes() == 0:
            return None    
        plt.figure(figsize=(8, 6))
        # 1. calculate Layout (Use weight to pull relevant nodes closer)
        pos = nx.spring_layout(self.G, k=0.5, weight='weight', seed=42) 
        # 2. draw Nodes & Lines
        colors = [self.G.nodes[n].get('color', 'skyblue') for n in self.G.nodes]
        nx.draw(self.G, pos, with_labels=True, node_color=colors, edge_color="#1609A0", node_size=1500, font_size=9)
        # labeling edge
        edge_labels = nx.get_edge_attributes(self.G, 'label') 
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=8, font_color="#9A0000")
        
        return plt.gcf()