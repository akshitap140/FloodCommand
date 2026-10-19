"""
Graph and Network Utilities for FloodCommand
Provides BFS road connectivity, Dijkstra shortest travel times,
and schematic watercraft travel modeling across the fictional valley.
"""

from __future__ import annotations

import heapq
import math
from collections import deque
from typing import Any


def build_road_graph(roads: list[dict[str, Any]], only_open: bool = True) -> dict[str, list[dict[str, Any]]]:
    """
    Builds an undirected adjacency list from road records.
    If only_open is True, ignores roads with status == 'blocked'.
    """
    graph: dict[str, list[dict[str, Any]]] = {}

    for road in roads:
        status = str(road.get("status", "open")).lower()
        if only_open and status == "blocked":
            continue

        u = str(road["from_id"])
        v = str(road["to_id"])
        travel_time = float(road.get("travel_minutes", 30))
        has_bridge = bool(road.get("has_bridge", False))

        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []

        graph[u].append({"to": v, "travel_minutes": travel_time, "has_bridge": has_bridge, "status": status})
        graph[v].append({"to": u, "travel_minutes": travel_time, "has_bridge": has_bridge, "status": status})

    return graph


def bfs_reachable_nodes(graph: dict[str, list[dict[str, Any]]], start_node: str) -> set[str]:
    """
    Uses Breadth-First Search (BFS) to find all nodes reachable from start_node via open roads.
    """
    if start_node not in graph:
        return {start_node}

    visited = {start_node}
    queue = deque([start_node])

    while queue:
        current = queue.popleft()
        for edge in graph.get(current, []):
            nxt = edge["to"]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    return visited


def is_village_cut_off(
    graph: dict[str, list[dict[str, Any]]],
    village_id: str,
    target_shelter_or_hospital_ids: list[str],
) -> bool:
    """
    Checks if a village has NO open road path to any shelter or hospital.
    Returns True if cut-off (isolated from all relief hubs).
    """
    reachable = bfs_reachable_nodes(graph, village_id)
    # If any shelter or hospital is reachable, it is NOT cut off
    for target in target_shelter_or_hospital_ids:
        if target in reachable:
            return False
    return True


def shortest_travel_time(
    graph: dict[str, list[dict[str, Any]]],
    start_node: str,
    end_node: str,
) -> float | None:
    """
    Computes shortest road travel time in minutes using Dijkstra's algorithm.
    Returns None if no road connection exists.
    """
    if start_node == end_node:
        return 0.0

    if start_node not in graph or end_node not in graph:
        return None

    # Priority queue: (cost, node)
    pq = [(0.0, start_node)]
    distances: dict[str, float] = {start_node: 0.0}

    while pq:
        curr_dist, u = heapq.heappop(pq)
        if curr_dist > distances.get(u, float("inf")):
            continue

        if u == end_node:
            return curr_dist

        for edge in graph.get(u, []):
            v = edge["to"]
            w = edge["travel_minutes"]
            new_dist = curr_dist + w
            if new_dist < distances.get(v, float("inf")):
                distances[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    return distances.get(end_node, None)


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Computes straight-line Euclidean distance on the 0-100 schematic grid."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def boat_travel_time(
    start_xy: tuple[float, float],
    dest_xy: tuple[float, float],
    speed_factor: float = 1.2,
) -> float:
    """
    Estimates boat / amphibious travel time in minutes based on grid distance and river speed factor.
    Baseline: 1 grid unit ~ 0.8 km, boat speed ~ 40 km/h with river current consideration.
    """
    dist = euclidean_distance(start_xy[0], start_xy[1], dest_xy[0], dest_xy[1])
    # 1.2 minutes per grid unit as schematic standard
    return round(dist * speed_factor, 1)
