import streamlit as st
import pandas as pd
import json
from typing import Dict, List, Any, Optional
import uuid
import plotly.graph_objects as go

# Sample data structure
class TreeNode:
    def __init__(self, name: str, description: str, category: str, 
                 values: List[float], children: List['TreeNode'] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category
        self.values = values  # 5 float values
        self.children = children or []
        self.expanded = False

# Sample data creation
def create_sample_data():
    root = TreeNode("Root", "Main root node", "System", [1.2, 3.4, 5.6, 7.8, 9.0])
    
    # Level 1 children
    node1 = TreeNode("Analytics", "Data analysis module", "Module", [2.1, 4.3, 6.5, 8.7, 1.9])
    node2 = TreeNode("Reporting", "Report generation", "Module", [3.2, 5.4, 7.6, 9.8, 2.1])
    
    # Level 2 children
    node1_1 = TreeNode("Sales Analytics", "Sales data processing", "Component", [4.3, 6.5, 8.7, 1.9, 3.2])
    node1_2 = TreeNode("Marketing Analytics", "Marketing metrics", "Component", [5.4, 7.6, 9.8, 2.1, 4.3])
    
    node2_1 = TreeNode("Monthly Reports", "Monthly summaries", "Component", [6.5, 8.7, 1.9, 3.2, 5.4])
    
    # Level 3 children
    node1_1_1 = TreeNode("Revenue Tracking", "Track sales revenue", "Feature", [7.6, 9.8, 2.1, 4.3, 6.5])
    node1_1_2 = TreeNode("Customer Metrics", "Customer analysis", "Feature", [8.7, 1.9, 3.2, 5.4, 7.6])
    
    # Build tree structure
    node1_1.children = [node1_1_1, node1_1_2]
    node1.children = [node1_1, node1_2]
    node2.children = [node2_1]
    root.children = [node1, node2]
    
    return root

def search_nodes(node: TreeNode, query: str) -> List[TreeNode]:
    """Search for nodes containing the query string"""
    results = []
    query_lower = query.lower()
    
    # Check current node
    if (query_lower in node.name.lower() or 
        query_lower in node.description.lower() or 
        query_lower in node.category.lower()):
        results.append(node)
    
    # Search children recursively
    for child in node.children:
        results.extend(search_nodes(child, query))
    
    return results

def display_node_details(node: TreeNode):
    """Display detailed information about a node"""
    st.write(f"**Name:** {node.name}")
    st.write(f"**Description:** {node.description}")
    st.write(f"**Category:** {node.category}")
    
    # Display float values in a nice format
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Value 1", f"{node.values[0]:.2f}")
    with col2:
        st.metric("Value 2", f"{node.values[1]:.2f}")
    with col3:
        st.metric("Value 3", f"{node.values[2]:.2f}")
    with col4:
        st.metric("Value 4", f"{node.values[3]:.2f}")
    with col5:
        st.metric("Value 5", f"{node.values[4]:.2f}")

def render_tree_node(node: TreeNode, level: int = 0, search_results: List[TreeNode] = None):
    """Recursively render tree nodes with expand/collapse functionality"""
    
    # Highlight if node is in search results
    is_highlighted = search_results and node in search_results
    
    # Create indentation based on level
    indent = "　" * level  # Using full-width space for better indentation
    
    # Create expandable section for nodes with children
    if node.children:
        # Create unique key for each node
        key = f"node_{node.id}_{level}"
        
        # Node header with expand/collapse
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📁" if not node.expanded else "📂", key=f"expand_{key}"):
                    node.expanded = not node.expanded
            with col2:
                if is_highlighted:
                    st.markdown(f"**🔍 {indent}{node.name}** - {node.description}")
                else:
                    st.write(f"{indent}**{node.name}** - {node.description}")
        
        # Show node details if expanded
        if node.expanded:
            with st.container():
                st.markdown("---")
                display_node_details(node)
                st.markdown("---")
            
            # Render children if expanded
            for child in node.children:
                render_tree_node(child, level + 1, search_results)
    else:
        # Leaf node - always show details when clicked
        key = f"leaf_{node.id}_{level}"
        if st.button(f"{indent}📄 {node.name} - {node.description}", key=key):
            st.session_state[f"selected_node"] = node.id
        
        # Show details if this node is selected
        if st.session_state.get("selected_node") == node.id:
            with st.container():
                st.markdown("---")
                display_node_details(node)
                st.markdown("---")
        
        if is_highlighted:
            st.markdown(f"**🔍 Found: {node.name}**")

def render_tree_node_explorer(node: TreeNode, level: int = 0, search_results: List[TreeNode] = None):
    """Render tree nodes for explorer left pane. Only select, don't show details here."""
    is_highlighted = search_results and node in search_results
    indent = "　" * level
    key = f"explorer_{node.id}_{level}"
    if node.children:
        # Expand/collapse logic
        if st.button(("📁" if not node.expanded else "📂") + f" {indent}{node.name}", key=f"expand_{key}"):
            node.expanded = not node.expanded
        if node.expanded:
            for child in node.children:
                render_tree_node_explorer(child, level + 1, search_results)
    else:
        if st.button(f"📄 {indent}{node.name}", key=key):
            st.session_state["selected_node"] = node.id
    # Allow selecting parent nodes as well
    if not node.children and st.session_state.get("selected_node") == node.id:
        st.markdown(f"<span style='color: #4F8BF9;'>Selected</span>", unsafe_allow_html=True)
    elif node.children and st.session_state.get("selected_node") == node.id:
        st.markdown(f"<span style='color: #4F8BF9;'>Selected</span>", unsafe_allow_html=True)
    # Allow selecting parent nodes for details
    if node.children:
        if st.button(f"Select {indent}{node.name}", key=f"select_{key}"):
            st.session_state["selected_node"] = node.id

def find_node_by_id(node: TreeNode, node_id: str) -> Optional[TreeNode]:
    if node.id == node_id:
        return node
    for child in node.children:
        found = find_node_by_id(child, node_id)
        if found:
            return found
    return None

def get_all_nodes(node: TreeNode) -> List[TreeNode]:
    nodes = [node]
    for child in node.children:
        nodes.extend(get_all_nodes(child))
    return nodes

def main():
    st.set_page_config(page_title="Hierarchical Data Visualizer", layout="wide")
    st.title("🌳 Hierarchical Data Visualizer")
    st.markdown("Interactive tree view with file-explorer layout")

    if 'tree_data' not in st.session_state:
        st.session_state.tree_data = create_sample_data()
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = st.session_state.tree_data.id

    with st.sidebar:
        st.header("🔧 Controls")
        st.subheader("🔍 Search")
        search_query = st.text_input("Search nodes:", placeholder="Enter search term...")
        search_results = []
        if search_query:
            search_results = search_nodes(st.session_state.tree_data, search_query)
            st.write(f"Found {len(search_results)} results")
            if search_results:
                st.subheader("Search Results:")
                for result in search_results:
                    st.write(f"• {result.name} ({result.category})")
        st.subheader("🌲 Tree Controls")
        if st.button("Expand All"):
            def expand_all(node):
                node.expanded = True
                for child in node.children:
                    expand_all(child)
            expand_all(st.session_state.tree_data)
            st.rerun()
        if st.button("Collapse All"):
            def collapse_all(node):
                node.expanded = False
                for child in node.children:
                    collapse_all(child)
            collapse_all(st.session_state.tree_data)
            st.rerun()
        st.subheader("📊 Statistics")
        def count_nodes(node):
            count = 1
            for child in node.children:
                count += count_nodes(child)
            return count
        total_nodes = count_nodes(st.session_state.tree_data)
        st.metric("Total Nodes", total_nodes)

    # File explorer layout
    left, right = st.columns([1, 2])
    with left:
        st.header("📁 Explorer")
        render_tree_node_explorer(st.session_state.tree_data, search_results=search_results)
    with right:
        st.header("📄 Node Details")
        selected_id = st.session_state.get("selected_node", st.session_state.tree_data.id)
        selected_node = find_node_by_id(st.session_state.tree_data, selected_id)
        if selected_node:
            display_node_details(selected_node)
        else:
            st.info("Select a node from the explorer to view details.")

    # Bottom anchored bar chart pane
    st.markdown("---")
    st.subheader("📊 Bar Chart: First Value of Each Node")
    all_nodes = get_all_nodes(st.session_state.tree_data)
    # Only show nodes that are visible in the explorer (expanded path)
    def get_visible_nodes(node):
        visible = [node]
        if getattr(node, 'expanded', False):
            for child in node.children:
                visible.extend(get_visible_nodes(child))
        return visible
    visible_nodes = get_visible_nodes(st.session_state.tree_data)
    # Highlight selected node
    bar_colors = ["#4F8BF9" if n.id == selected_id else "#A3C1DA" for n in visible_nodes]
    fig = go.Figure(data=[
        go.Bar(
            x=[n.name for n in visible_nodes],
            y=[n.values[0] for n in visible_nodes],
            marker_color=bar_colors
        )
    ])
    fig.update_layout(
        xaxis_title="Node Name",
        yaxis_title="First Value",
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ How to use"):
        st.markdown("""
        ### Navigation:
        - **📁/📂 buttons**: Click to expand/collapse nodes with children
        - **Select**: Click a node or 'Select' button to view details in the right pane
        - **Search**: Use the sidebar search to find specific nodes
        - **Tree Controls**: Use expand/collapse all buttons in sidebar
        
        ### Node Information:
        Each node contains:
        - **3 text fields**: Name, Description, Category
        - **5 float values**: Displayed as metrics when selected
        """)

if __name__ == "__main__":
    main()