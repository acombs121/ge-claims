import json
import itertools
import math
import random

# Coordinates strictly on land in Boston
# Coordinates strictly on land in Boston, spread out
LAND_COORDINATES = [
    [42.3554, -71.0664], # Boston Common area
    [42.3584, -71.0597], # Faneuil Hall
    [42.3600, -71.0560], # North End
    [42.3555, -71.0500], # Seaport
    [42.3650, -71.0700], # West End / TD Garden
    [42.3605, -71.0800], # Cambridge side (close to land)
    [42.3526, -71.0550], # Financial District
    [42.3450, -71.0750], # Back Bay
    [42.3680, -71.0650], # North Station area
    [42.3450, -71.0600]  # South End
]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def greedy_tsp(points):
    if not points:
        return []
    unvisited = list(points)
    current = unvisited.pop(0)
    path = [current]
    while unvisited:
        next_point = min(unvisited, key=lambda p: distance((current['lat'], current['lng']), (p['lat'], p['lng'])))
        unvisited.remove(next_point)
        path.append(next_point)
        current = next_point
    return path

industries = ['Finance', 'Healthcare', 'Tech', 'Retail']
prioritizations = ['Account Size', 'Churn Risk', 'Upsell Potential']

FINANCE_NAMES = ["Apex Capital", "Summit Partners", "Beacon Trading", "Vertex Investments", "Nexus Wealth", "Quantum Finance"]
HEALTHCARE_NAMES = ["Nexus Pharma", "Vertex Labs", "CarePoint Health", "Beacon Medical", "Summit Health", "Apex Diagnostics"]
TECH_NAMES = ["Quantum Systems", "CloudScale AI", "Innovatech", "Summit Tech", "Beacon Data", "Nexus Robotics"]
RETAIL_NAMES = ["Urban Style", "StyleSource", "DailyNeeds", "Summit Retail", "Beacon Goods", "Nexus Mart"]

accounts = []
account_id = 1

# Generate 6 accounts per industry
for ind in industries:
    for i in range(6):
        coord = LAND_COORDINATES[(account_id - 1) % len(LAND_COORDINATES)]
        
        if ind == 'Finance':
            name = FINANCE_NAMES[i]
        elif ind == 'Healthcare':
            name = HEALTHCARE_NAMES[i]
        elif ind == 'Tech':
            name = TECH_NAMES[i]
        elif ind == 'Retail':
            name = RETAIL_NAMES[i]
            
        acc = {
            "id": f"AC{account_id:03d}",
            "name": name,
            "arr": random.randint(50000, 500000),
            "churn_risk": random.choice(['Low', 'Medium', 'High']),
            "risk_score": random.randint(10, 100),
            "upsell_potential": random.randint(10000, 100000),
            "industry": ind,
            "territory": "Northeast",
            "sub_region": "Boston Metro",
            "lat": coord[0],
            "lng": coord[1],
            "intensity": 0.5, # Default intensity
            "last_visited": random.choice(["2 weeks ago", "1 month ago", "3 months ago", "Never"]),
            "status": random.choice(["Active", "At Risk", "Prospect"]),
            "priority": random.choice(["High", "Medium", "Low"])
        }
        accounts.append(acc)
        account_id += 1

# Save accounts
with open('data/accounts.json', 'w') as f:
    json.dump(accounts, f, indent=2)

recommendations = {}
routes = {}

for ind in industries:
    ind_accs = [acc for acc in accounts if acc['industry'] == ind]
    
    for prio in prioritizations:
        # Sort based on prioritization
        if prio == 'Account Size':
            sorted_accs = sorted(ind_accs, key=lambda x: x['arr'], reverse=True)
        elif prio == 'Churn Risk':
            sorted_accs = sorted(ind_accs, key=lambda x: x['risk_score'], reverse=True)
        elif prio == 'Upsell Potential':
            sorted_accs = sorted(ind_accs, key=lambda x: x['upsell_potential'], reverse=True)
            
        # Take top 4 as independent copies to avoid rationale/intensity overwrite
        selected = [dict(acc) for acc in sorted_accs[:4]]
        
        # Generate rationale and intensity
        for rank, acc in enumerate(selected):
            acc['intensity'] = [1.0, 0.5, 0.2, 0.1][rank] # Make differences more pronounced
            name = acc.get('name', 'This account')
            if prio == 'Account Size':
                templates = [
                    f"{name} holds significant tier-1 enterprise ARR. An onsite touchpoint with their VP of Engineering will accelerate the upcoming Q3 renewal process and align on joint strategic goals.",
                    f"As a flagship {ind} deployment, {name}'s annual volume is critical. Proactively auditing their current integration architecture can lock in renewal confidence and cement platform stickiness.",
                    f"{name} has scaled rapidly over the last two quarters. Reviewing their custom SLAs and premium support package in person is highly recommended to maximize partnership value.",
                    f"Representing a major anchor in our Northeast footprint, {name}'s upcoming expansion plans make them a vital visit to discuss long-term volume discounting and roadmap alignment."
                ]
                acc['rationale'] = templates[rank % 4]
            elif prio == 'Churn Risk':
                templates = [
                    f"Recent API error logs for {name} indicate integration bottlenecks. An immediate onsite support session is critical to unblocking their dev team and mitigating active churn risk.",
                    f"{name}'s platform engagement dropped by 15% last month. Scheduling a personalized health check to re-train their key power users will directly address their utilization concerns.",
                    f"With recent executive turnover at {name}, our original champion has left. Meeting the new incoming VP is essential to re-establish strategic buy-in and secure the renewal.",
                    f"{name} has submitted multiple severity-2 tickets regarding performance tuning. A direct meeting with their infrastructure leads will demonstrate our commitment to their operational success."
                ]
                acc['rationale'] = templates[rank % 4]
            elif prio == 'Upsell Potential':
                templates = [
                    f"{name} has saturated their current compute tier limits. Pitching our newly released AI predictive add-on can seamlessly unlock a lucrative 20% upsell expansion.",
                    f"Following their recent M&A announcement, {name} is expanding their regional footprint. Proposing an enterprise site license upgrade will cover their new added users effectively.",
                    f"Usage metrics show {name} heavily leveraging our standard reporting tools. Introducing our premium advanced analytics module aligns perfectly with their upcoming quarterly audit needs.",
                    f"{name} expressed early interest in our beta features during the last sync. Demonstrating the production-ready capabilities in person is highly likely to close an immediate expansion package."
                ]
                acc['rationale'] = templates[rank % 4]
                
        key = f"{ind}_{prio}"
        recommendations[key] = selected
        
        # Generate Routes
        # 1. Shortest Distance
        shortest_path = greedy_tsp(selected)
        if [acc['id'] for acc in shortest_path] == [acc['id'] for acc in selected]:
            print(f"DEBUG: Shortest path and Priority path are the same for {key}")
        routes[f"{key}_shortest"] = {
            "distance": f"{round(sum(distance((p1['lat'], p1['lng']), (p2['lat'], p2['lng'])) * 69 for p1, p2 in zip(shortest_path, shortest_path[1:])), 1)} miles",
            "duration": f"{len(shortest_path) * 5} mins",
            "coordinates": [[acc['lat'], acc['lng']] for acc in shortest_path]
        }
        
        # 2. Priority (Keep order from selection, force divergence if identical)
        if [acc['id'] for acc in shortest_path] == [acc['id'] for acc in selected] and len(selected) >= 4:
            selected[1], selected[2] = selected[2], selected[1]
            
        routes[f"{key}_priority"] = {
            "distance": f"{round(sum(distance((p1['lat'], p1['lng']), (p2['lat'], p2['lng'])) * 69 for p1, p2 in zip(selected, selected[1:])), 1)} miles",
            "duration": f"{len(selected) * 7} mins",
            "coordinates": [[acc['lat'], acc['lng']] for acc in selected]
        }

# Save recommendations
with open('data/recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

# Save routes
with open('data/routes.json', 'w') as f:
    json.dump(routes, f, indent=2)

print(f"Generated {len(accounts)} accounts.")
print(f"Generated {len(recommendations)} recommendation sets.")
print(f"Generated {len(routes)} routes.")
