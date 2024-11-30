# API Configuration
API_URL = "http://localhost:7890"

# Graph Visualization Settings
GRAPH_OPTIONS = {
    "physics": {
        "forceAtlas2Based": {
            "springLength": 200,
            "springConstant": 0.2,
            "damping": 0.4,
            "avoidOverlap": 0.8
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based",
        "stabilization": {
            "enabled": True,
            "iterations": 1000,
            "updateInterval": 50
        }
    },
    "interaction": {
        "hover": True,
        "tooltipDelay": 200,
        "zoomView": True,
        "dragView": True,
        "navigationButtons": True
    },
    "nodes": {
        "font": {
            "size": 12,
            "face": "arial",
            "strokeWidth": 2,
            "strokeColor": "#ffffff"
        },
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "margin": 10,
        "shape": "box"
    },
    "edges": {
        "color": {
            "color": "#848484",
            "highlight": "#1B5299"
        },
        "smooth": {
            "type": "continuous",
            "roundness": 0.5
        },
        "width": 1,
        "selectionWidth": 2,
        "arrows": {
            "to": {
                "enabled": False
            }
        }
    },
    "layout": {
        "improvedLayout": True,
        "hierarchical": {
            "enabled": False,
            "levelSeparation": 150,
            "nodeSpacing": 200,
            "blockShifting": True,
            "edgeMinimization": True,
            "direction": "UD"
        }
    }
}

NODE_COLORS = {
    "root": "#4299e1",    # Blue
    "expanded": "#48bb78", # Green
    "related": "#a0aec0"  # Gray
}

NODE_SIZES = {
    "large": 35,
    "small": 25
}

FONT_SIZES = {
    "large": 16,
    "small": 12
}