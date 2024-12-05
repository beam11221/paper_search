from fastapi import APIRouter, HTTPException
from confluent_kafka import Producer
import json
import uuid
from qdrant_client import QdrantClient
import numpy as np
import networkx as nx
from sklearn.neighbors import NearestNeighbors

from backend.app.models.paper import Paper
from backend.app.models.query import Query
from backend.app.services.openai_handler import OpenAIHandler
from backend.app.core.config import settings

router = APIRouter()

# Initialize services
producer = Producer({
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
})

qdrant = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

@router.post("/add_paper")
async def add_paper(paper: Paper):
    try:
        paper_id = str(uuid.uuid4())
        
        # Prepare message for Kafka
        message = {
            "paper_id": paper_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "published": paper.published,
            "link": paper.link
        }
        # Send to Kafka topic
        producer.produce(
            'paper_processing',
            json.dumps(message).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)
        
        return {"paper_id": paper_id, "status": "processing"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_papers(query: Query):
    try:
        # Generate embedding for query
        query_embedding = OpenAIHandler.generate_embedding(query.query_text)
        
        # Search in Qdrant
        search_results = qdrant.search(
            collection_name='papers',
            query_vector=query_embedding,
            limit=query.top_k
        )
        
        # Format results
        results = []
        for match in search_results:
            results.append({
                'paper_id': str(match.id),
                'title': match.payload['title'],
                'abstract': match.payload['abstract'],
                'link': match.payload['link'],
                'similarity': float(match.score)
            })
        
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_graph")
async def get_search_graph(query: Query):
    try:
        # First get search results
        query_embedding = OpenAIHandler.generate_embedding(query.query_text)
        search_results = qdrant.search(
            collection_name=settings.VECTOR_DB_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=query.top_k,
            with_vectors=True  # Make sure to get vectors
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No results found")
        results = []
        for match in search_results:
            results.append({
                'paper_id': str(match.id),
                'title': match.payload['title'],
                'abstract': match.payload['abstract'],
                'link': match.payload['link'],
                'similarity': float(match.score)
            })
        
        # Extract vectors and metadata from search results
        # Reshape vectors to 2D array
        vectors = np.array([result.vector for result in search_results])
        if vectors.ndim == 1:
            vectors = vectors.reshape(-1, 1)  # Reshape to 2D array
            
        titles = [result.payload["title"][:50] + "..." if len(result.payload["title"]) > 50 
                 else result.payload["title"] for result in search_results]
        paper_ids = [result.id for result in search_results]
        
        # Make sure we have enough samples for k neighbors
        n_neighbors = min(5, len(vectors))
        if n_neighbors < 2:
            # If we have too few results, return simple data without graph
            return {
                "message": "Not enough results for graph visualization",
                "results": [{"title": title, "id": paper_id} 
                           for title, paper_id in zip(titles, paper_ids)]
            }
            
        nn = NearestNeighbors(n_neighbors=n_neighbors)
        nn.fit(vectors)
        distances, indices = nn.kneighbors(vectors)
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for i, (title, paper_id) in enumerate(zip(titles, paper_ids)):
            G.add_node(
                i,
                title=title,
                paper_id=paper_id,
                size=10
            )
        
        # Add edges with similarity weights
        for i, neighbors in enumerate(indices):
            for j, dist in zip(neighbors[1:], distances[i][1:]):
                similarity = 1 - dist
                if similarity > 0.5:  # Only show strong connections
                    G.add_edge(i, j, weight=similarity)
        
        # Calculate node sizes based on connections
        for node in G.nodes():
            G.nodes[node]['size'] = 10 + 5 * G.degree(node)
        
        # Get positions
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=100, seed=42)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = G.edges[edge]['weight']
            
            edge_trace = {
                'x': [x0, x1, None],
                'y': [y0, y1, None],
                'mode': 'lines',
                'line': {
                    'width': weight * 3,
                    'color': f'rgba(70, 130, 180, {weight})'
                },
                'hoverinfo': 'none'
            }
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_trace = {
            'x': [pos[node][0] for node in G.nodes()],
            'y': [pos[node][1] for node in G.nodes()],
            'mode': 'markers+text',
            'marker': {
                'size': [G.nodes[node]['size'] for node in G.nodes()],
                'color': '#1f77b4',
                'line': {'width': 1, 'color': 'white'},
                'opacity': 0.8
            },
            'text': titles,
            'textposition': 'top center',
            'textfont': {'size': 10, 'color': '#666'},
            'hovertext': [
                f"Title: {title}<br>"
                f"ID: {paper_id}<br>"
                f"Connections: {G.degree(i)}"
                for i, (title, paper_id) in enumerate(zip(titles, paper_ids))
            ],
            'hoverinfo': 'text'
        }
        
        # Create layout
        layout = {
            'showlegend': False,
            'hovermode': 'closest',
            'margin': {'b': 40, 'l': 40, 'r': 40, 't': 40},
            'title': {
                'text': f'Paper Similarity Network for "{query.query_text}"',
                'font': {'size': 24, 'color': '#333'}
            },
            'plot_bgcolor': '#fff',
            'paper_bgcolor': '#fff',
            'xaxis': {
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False,
                'showline': False
            },
            'yaxis': {
                'showgrid': False,
                'zeroline': False,
                'showticklabels': False,
                'showline': False
            },
            'height': 800,
            'width': 1000
        }
        
        fig = {
            'data': edge_traces + [node_trace],
            'layout': layout
        }
        
        return {
            "graph_data": fig,
            "node_count": len(G.nodes()),
            "edge_count": len(G.edges()),
            "query": query.query_text,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector_graph")
async def get_vector_graph():
    try:
        # Get all papers and their vectors
        points = qdrant.scroll(
            collection_name=settings.VECTOR_DB_COLLECTION_NAME,
            limit=100000,
            with_payload=True,
            with_vectors=True
        )[0]
        
        if not points:
            raise HTTPException(status_code=404, detail="No papers found")
        
        # Extract vectors and metadata
        vectors = np.array([point.vector for point in points])
        titles = [point.payload["title"] for point in points]
        paper_ids = [point.id for point in points]
        
        # Find nearest neighbors
        n_neighbors = min(5, len(vectors))  # Adjust number of connections
        nn = NearestNeighbors(n_neighbors=n_neighbors)
        nn.fit(vectors)
        distances, indices = nn.kneighbors(vectors)
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for i, (title, paper_id) in enumerate(zip(titles, paper_ids)):
            G.add_node(i, title=title, paper_id=paper_id)
        
        # Add edges
        for i, neighbors in enumerate(indices):
            for j, dist in zip(neighbors[1:], distances[i][1:]):  # Skip self-connection
                G.add_edge(i, j, weight=1-dist)  # Convert distance to similarity
        
        # Get node positions using force-directed layout
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
        
        # Create visualization data
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        # Create plot
        edge_trace = {
            'x': edge_x,
            'y': edge_y,
            'mode': 'lines',
            'line': {'width': 0.5, 'color': '#888'},
            'hoverinfo': 'none'
        }
        
        node_trace = {
            'x': node_x,
            'y': node_y,
            'mode': 'markers+text',
            'marker': {
                'size': 10,
                'color': '#007bff'
            },
            'text': titles,
            'hovertext': [f"Title: {title}<br>ID: {paper_id}" 
                         for title, paper_id in zip(titles, paper_ids)],
            'hoverinfo': 'text'
        }
        
        layout = {
            'showlegend': False,
            'hovermode': 'closest',
            'margin': {'b': 20, 'l': 5, 'r': 5, 't': 40},
            'title': 'Paper Vector Relationship Graph',
            'xaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False},
            'yaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False}
        }
        
        fig = {
            'data': [edge_trace, node_trace],
            'layout': layout
        }
        
        return {
            "graph_data": fig,
            "node_count": len(G.nodes()),
            "edge_count": len(G.edges())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))