import ciw
from typing import Dict, Any, List, Optional
from .schema import ProcessModel

class CiwConverter:
    def __init__(self, model):
        self.model = model

    def generate_params(self) -> dict:
        """
        Converts the agnostic ProcessModel into a dictionary of parameters 
        compatible with ciw.create_network(**params).
        """
        
        # 1. Map Activity Names to Integer Indices
        # Ciw networks are index-based (0, 1, 2...), but our JSON is name-based.
        # We assume the order in the list is the order of the nodes.
        node_map = {act.name: i for i, act in enumerate(self.model.activities)}
        n_nodes = len(self.model.activities)

        # 2. Initialize Lists for Ciw Arguments
        number_of_servers = []
        service_distributions = []
        arrival_distributions = []

        # 3. Iterate through Activities to build Node properties
        for act in self.model.activities:
            # -- Resources (Servers) --
            number_of_servers.append(act.resource.capacity)

            # -- Service Distribution (Mandatory) --
            service_distributions.append(self._make_ciw_dist(act.service_distribution))

            # -- Arrival Distribution (Optional) --
            if act.arrival_distribution:
                arrival_distributions.append(self._make_ciw_dist(act.arrival_distribution))
            else:
                # If no arrival distribution is specified in JSON, it means no external arrivals
                # None = old NoArrivals pre ciw v3
                arrival_distributions.append(None)

        # 4. Build Routing Matrix (Process Flow -> Probability Matrix)
        # Initialize an N x N matrix with 0.0
        routing = [[0.0] * n_nodes for _ in range(n_nodes)]
        
        for t in self.model.transitions:
            # We only care about transitions between internal nodes.
            # Transitions to "Exit" are implicit in Ciw (1.0 - sum(row)).
            if t.target != "Exit":
                # Validate that nodes exist (Pydantic validates types, but not logic across lists)
                if t.source not in node_map or t.target not in node_map:
                    raise ValueError(f"Transition references unknown node: {t.source} -> {t.target}")
                
                u_idx = node_map[t.source]
                v_idx = node_map[t.target]
                routing[u_idx][v_idx] = t.probability

        # 5. Return the Dictionary
        return {
            "number_of_servers": number_of_servers,
            "arrival_distributions": arrival_distributions,
            "service_distributions": service_distributions,
            "routing": routing
        }

    def _make_ciw_dist(self, dist_obj):
        """Helper to convert Pydantic Distribution model to Ciw Object"""
        p = dist_obj.parameters
        
        if dist_obj.type == "exponential":
            return ciw.dists.Exponential(1/p["rate"])
        elif dist_obj.type == "triangular":
            return ciw.dists.Triangular(p["min"], p["mode"], p["max"])
        elif dist_obj.type == "uniform":
            return ciw.dists.Uniform(p["min"], p["max"])
        elif dist_obj.type == "deterministic":
             return ciw.dists.Deterministic(p["value"])
        # TO DO: Add more mappings as needed (Lognormal, Gamma, etc.)
        else:
             raise ValueError(f"Unsupported distribution type for Ciw: {dist_obj.type}")